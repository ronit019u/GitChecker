from datetime import datetime

from pydantic import BaseModel


class CheckRequest(BaseModel):
    repo_url: str
    task: str


class Issue(BaseModel):
    id: int
    files_checked: list[str]
    bug_summary: str
    suggested_fix_direction: str


class FixRequest(BaseModel):
    repo_url: str
    task: str
    issue: Issue


class CheckResponse(BaseModel):
    success: bool
    check_id: str | None = None
    bug_summary: str | None = None
    files_checked: list[str] | None = None
    fix_code: str | None = None
    file_path: str | None = None
    reason: str | None = None
    sandbox_status: str | None = None
    sandbox_output: str | None = None
    sandbox_detail: str | None = None
    requires_user_confirmation: bool = False
    detected_lang: str | None = None
    error: str | None = None


class SaveUnsupported(BaseModel):
    repo_url: str
    task: str
    bug_summary: str
    fix_code: str
    file_path: str
    detected_lang: str | None = None


class HistoryData(BaseModel):
    id: str
    repo_url: str
    task_description: str
    bug_summary: str
    fix_code: str | None
    file_path: str | None
    detected_lang: str | None
    status: str
    created_at: datetime
