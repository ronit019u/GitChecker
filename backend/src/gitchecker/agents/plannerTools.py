from contextvars import ContextVar
from pathlib import Path

from langchain_core.tools import tool

# ContextVar automatically isolates its value per async task — each concurrent pipeline()
# call gets its own view of _current_repo_path, even though they're all running the same module-level code. No cross-contamination between concurrent requests.

# ContextVar fixes the problem when two users trying to use the gitchecker it donot
# endup with user B repo inside the user A path
_current_repo_path: ContextVar[Path | None] = ContextVar(
    "_current_repo_path", default=None
)


def set_repo_context(repo_path: Path) -> None:
    """called once per check before the agent runs so tools know which repo to work on"""
    _current_repo_path.set(repo_path)


@tool
def list_files() -> list[str]:
    """Returns a list of all files in the repository relative to the repository root"""
    repo_path = _current_repo_path.get()
    if repo_path is None:
        return []

    # it runs a recursive in build function of pathlib's rglob() to give list of all the files
    # even in the nested repo and it excludes the .git from returning it
    return [
        str(p.relative_to(repo_path))
        for p in repo_path.rglob("*")
        if p.is_file() and ".git" not in p.parts
    ]


@tool
def read_repo_file(file_path: str) -> str:
    """Reads and return the context of the specific file in the repository. Pass a relative path"""
    repo_path = _current_repo_path.get()
    if repo_path is None:
        return "Error: no repo to read"

    target = (repo_path / file_path).resolve()

    # preventing access outside the repo folder
    if not str(target).startswith(str(repo_path.resolve())):
        return "Error: access outside the repo is not allowed"

    # hallucinate a file that does not exist
    if not target.exists():
        return f"Error: file {file_path} does not exist"

    # read the content of the file
    try:
        return target.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading file: {e}"
