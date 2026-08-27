import shutil
import tempfile
from pathlib import Path

from git import GitCommandError, Repo


# Custom error so callers can catch clone failures specifically,
# without accidentally catching unrelated exceptions too
class RepoCloneError(Exception):
    pass


# this clones the repo from the url whith or without branch
def repoCloner(repo_url: str, branch: str | None = None):

    temp_dir = Path(tempfile.mkdtemp(prefix="gitchecker_"))
    try:
        clone_repo = {"depth": 1}
        if branch:
            clone_repo["branch"] = branch
        Repo.clone_from(repo_url, temp_dir, **clone_repo)
        return temp_dir
    # when ever an error occurs related to git clone it does not crash instead
    # deletes the temp folder and raise the RepoCloneError
    except GitCommandError as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise RepoCloneError(f"failed to clone {repo_url}: {e}") from e


# to delete the repo folder
def cleanup_repo(temp_folder: Path):
    shutil.rmtree(temp_folder, ignore_errors=True)
