import shutil
import tempfile
import traceback
from dataclasses import dataclass
from pathlib import Path

import docker
from docker.errors import DockerException

from src.gitchecker.core.sandbox.detector import (
    SUPPORTED_LANGUAGES,
    detect_entryPoint,
    detect_install_cmd,
    detect_lang_forSandbox,
    detect_test_cmd,
    find_dir,
)


# this is needed for the check api and work on the desired outcome after receiving the
# sandbox result
@dataclass
class SandboxResult:
    status: str
    output: str
    exit_code: int | None = None
    detail: str | None = None
    requires_confirmation: bool = False
    detected_lang: str | None = None


DOCKER_IMAGE = {
    "python": "python:3.13-slim",
    "javascript": "node:22-slim",
    "typescript": "node:22-slim",
}


def apply_fix(repo_path: Path, file_path: str, fix_code: str) -> Path:
    """
    Creates a copy of the repo and writes the complete corrected file into the cloned repo
    """

    copy_dir = Path(tempfile.mkdtemp(prefix="gitchecker_fixed_"))
    shutil.copytree(repo_path, copy_dir, dirs_exist_ok=True)

    target = copy_dir / file_path
    if not target.exists():
        raise ValueError(f"File at {file_path} does not exist")

    target.write_text(fix_code, encoding="utf-8")
    return copy_dir


def start_container(image: str, full_cmd: str, repo_copy: Path) -> str:
    client = docker.from_env(timeout=300)
    volume_mount = {str(repo_copy.resolve()): {"bind": "/app", "mode": "rw"}}

    container = client.containers.run(
        image=image,
        command=full_cmd,
        volumes=volume_mount,
        working_dir="/app",
        mem_limit="1g",
        stderr=True,
        detach=True,
    )
    try:
        result = container.wait(timeout=300)
        exit_code = result["StatusCode"]
        logs = container.logs(stdout=True, stderr=True).decode("utf-8")
        return logs, exit_code
    finally:
        container.remove(force=True)


# . If you write async def run_sandbox() but the body still calls container.wait() (a genuinely blocking call), you've gained nothing — the function still freezes the whole event loop the instant it hits that line,
# exactly the same as if it were sync. The async keyword doesn't make blocking code non-blocking; it just changes syntax, not behavior.
def run_sandbox(file_path: Path, repo_path: Path, fix_code: str) -> SandboxResult:
    is_test = False
    fixed_repo = None
    lang = None
    try:
        lang = detect_lang_forSandbox(file_path, repo_path)

        if lang not in SUPPORTED_LANGUAGES:
            return SandboxResult(
                status="unsupported",
                output="",
                detail=f"{lang} detected fix proposed but cannot be verified through sandbox",
                requires_confirmation=True,
                detected_lang=lang,
            )

        fixed_repo = apply_fix(repo_path, file_path, fix_code)
        install_cmd = detect_install_cmd(lang, fixed_repo, file_path)
        test_command = detect_test_cmd(lang, fixed_repo, file_path)
        run_cmd = test_command or detect_entryPoint(lang, fixed_repo, file_path)
        is_test = test_command is not None

        if not run_cmd:
            return SandboxResult(
                status="not_runnable",
                output="",
                detail="No tests and entry point found",
                detected_lang=lang,
            )

        manifest_names = (
            ["uv.lock", "requirements.txt", "pyproject.toml", "setup.py"]
            if lang == "python"
            else ["package.json"]
        )
        manifest_dir = find_dir(fixed_repo, file_path, manifest_names)
        if manifest_dir:
            relative_dir = manifest_dir.resolve().relative_to(fixed_repo.resolve())
        else:
            relative_dir = Path(".")

        parts = list(filter(None, [install_cmd, run_cmd]))
        full_cmd = f"sh -c 'cd {relative_dir} && {' && '.join(parts)}'"

        output, exit_code = start_container(
            image=DOCKER_IMAGE[lang], full_cmd=full_cmd, repo_copy=fixed_repo
        )

        print("EXIT CODE:", exit_code)

        # only exit code 0 because all the other exit code have same answer coder fix did not work
        if exit_code == 0:
            return SandboxResult(
                status="successful",
                output=output,
                exit_code=exit_code,
                detail="Test passed" if is_test else "Entry point ran successfully",
                detected_lang=lang,
            )

        return SandboxResult(
            status="failed",
            output=output,
            exit_code=exit_code,
            detail="Test ran but failed" if is_test else "Entry point crashed",
            detected_lang=lang,
        )

    except ValueError as e:
        return SandboxResult(
            status="error",
            output="",
            detail=f"could not apply fix: {e!s}",
            detected_lang=lang,
        )

    except DockerException as e:
        return SandboxResult(
            status="error",
            output="",
            detail=f"Docker error: {e!s}",
            detected_lang=lang,
        )

    except Exception as e:
        traceback.print_exc()
        return SandboxResult(
            status="error",
            output="",
            detail=f"unexpected error: {e!s}",
            detected_lang=lang,
        )
    finally:
        if fixed_repo is not None:
            shutil.rmtree(fixed_repo, ignore_errors=True)
