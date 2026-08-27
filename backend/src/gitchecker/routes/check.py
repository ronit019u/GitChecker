import asyncio
import shutil
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.gitchecker.agents.coder import coder_execute
from src.gitchecker.agents.planner import planner_execute
from src.gitchecker.auth.dependencies import get_currentUser_id
from src.gitchecker.core.repo_clonner import RepoCloneError, repoCloner
from src.gitchecker.core.sandbox.runner import run_sandbox
from src.gitchecker.database.db import get_session
from src.gitchecker.database.models import History
from src.gitchecker.schema.check import (
    CheckRequest,
    FixRequest,
    HistoryData,
    SaveUnsupported,
)

router = APIRouter(prefix="/check", tags=["check"])


@router.post("/start")
async def start_check(
    request: CheckRequest, user_id: str = Depends(get_currentUser_id)
):
    loop = asyncio.get_event_loop()
    try:
        repo_path = await loop.run_in_executor(
            None, lambda: repoCloner(request.repo_url)
        )
        planner_response = await planner_execute(repo_path, request.task)
        return {"issues": planner_response.issues}
    except RepoCloneError as e:
        raise HTTPException(status_code=400, detail=f"Failed to clone repo: {e}")
    finally:
        shutil.rmtree(repo_path, ignore_errors=True)


@router.post("/fix")
async def fix_issue(
    request: FixRequest,
    user_id: str = Depends(get_currentUser_id),
    db: AsyncSession = Depends(get_session),
):
    loop = asyncio.get_event_loop()
    try:
        repo_path = await loop.run_in_executor(
            None, lambda: repoCloner(request.repo_url)
        )
        coder_response = await coder_execute(repo_path, request.issue)
        verification = await loop.run_in_executor(
            None,
            lambda: run_sandbox(
                coder_response.file_path, repo_path, coder_response.fix_code
            ),
        )
        if verification.status != "unsupported":
            check = History(
                user_id=uuid.UUID(user_id),
                repo_url=request.repo_url,
                task_description=request.task,
                planner_response=request.issue.bug_summary,
                coder_response=coder_response.fix_code,
                file_path=coder_response.file_path,
                detected_language=verification.detected_lang,
                status=verification.status,
            )
            db.add(check)
            await db.commit()
        return {"coder": coder_response, "verify": verification}
    except RepoCloneError as e:
        raise HTTPException(status_code=400, detail=f"Failed to clone the repo: {e}")
    finally:
        if repo_path is not None:
            shutil.rmtree(repo_path, ignore_errors=True)


@router.post("/save")
async def unsupported_save(
    data: SaveUnsupported,
    user_id: str = Depends(get_currentUser_id),
    db: AsyncSession = Depends(get_session),
):
    check = History(
        user_id=uuid.UUID(user_id),
        repo_url=data.repo_url,
        task_description=data.task,
        planner_response=data.bug_summary,
        coder_response=data.fix_code,
        file_path=data.file_path,
        detected_language=data.detected_lang,
        status="unverified",
    )
    db.add(check)
    await db.commit()

    return {"message": "Fix saved to your history"}


@router.get("/history")
async def get_history(
    user_id: str = Depends(get_currentUser_id), db: AsyncSession = Depends(get_session)
):
    result = await db.execute(
        select(History)
        .where(History.user_id == uuid.UUID(user_id))
        .order_by(History.created_at.desc())
    )
    checks = result.scalars().all()

    return [
        HistoryData(
            id=str(check.id),
            repo_url=check.repo_url,
            task_description=check.task_description,
            bug_summary=check.planner_response,
            fix_code=check.coder_response,
            file_path=check.file_path,
            detected_lang=check.detected_language,
            status=check.status,
            created_at=check.created_at,
        )
        for check in checks
    ]


@router.delete("/history/{history_id}")
async def delete_history(
    history_id: uuid.UUID,
    user_id: str = Depends(get_currentUser_id),
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(select(History).where(History.id == history_id))
    check = result.scalar_one_or_none()

    if check is None or check.user_id != uuid.UUID(user_id):
        raise HTTPException(status_code=404, detail="History of the check not found")

    await db.delete(check)
    await db.commit()
    return {"message": "History check deleted"}
