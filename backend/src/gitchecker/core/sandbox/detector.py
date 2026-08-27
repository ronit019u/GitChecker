import json
from pathlib import Path

SUPPORTED_LANGUAGES = {"python", "javascript", "typescript"}


def find_dir(repo_path: Path, file_path: Path, files_names: list[str]) -> Path | None:

    if file_path:
        start_dirc = (repo_path / file_path).parent
    else:
        start_dirc = repo_path

    current = start_dirc.resolve()
    root = repo_path.resolve()
    while True:
        for file_name in files_names:
            if (current / file_name).is_file():
                return current
        if current == current.parent or current == root:
            break
        current = current.parent
    return None


def detect_lang_fromFile(file_path: str) -> str:
    """
    detects language directly from the fixed file's extension
    more accurately than scanning the whole repo for the full stack project
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    extension_map = {
        ".py": "python",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".jsx": "javascript",
        ".mjs": "javascript",
        ".cjs": "javascript",
    }

    return extension_map.get(ext, "unknown")


def detect_lang(repo_path: Path) -> str:
    """
    fallback language detection scan repo root for config files used when fixed file
    extension is like .json, .toml, yml, etc simplified priority check using the file extension
    to handle full stack repos
    """

    has_python = (
        (repo_path / "pyproject.toml").exists()
        or (repo_path / "requirements.txt").exists()
        or (repo_path / "setup.py").exists()
    )

    has_js = (repo_path / "package.json").exists()

    if has_python:
        return "python"

    if has_js:
        # conditional expression  "value_if_true if condition else value_if_false"
        return "typescript" if (repo_path / "tsconfig.json").exists() else "javascript"

    # detect for unsupported

    if (repo_path / "Makefile").exists() or (repo_path / "CMakeLists.txt").exists():
        return "cpp"

    if (repo_path / "go.mod").exists():
        return "go"

    if (repo_path / "Cargo.toml").exists():
        return "rust"

    if (repo_path / "pom.xml").exists() or (repo_path / "build.gradle").exists():
        return "java"

    if (repo_path / "bun.lockb").exists():
        return "bun"

    return "unknown"


def detect_lang_forSandbox(file_path: str, repo_path: Path) -> str:
    """
    Primary signal: fixed file extension
    Fallback: repo root scan for config files like .json, .yml, .env
    """

    ext_lang = detect_lang_fromFile(file_path)

    if ext_lang != "unknown":
        return ext_lang

    return detect_lang(repo_path)


def detect_install_cmd(lang: str, repo_path: Path, file_path: Path) -> str | None:
    """
    Returns the shell command to install the dependencies inside the docker
    returns None if no dependency files found
    """
    if lang == "python":
        cloned_dirc_py = find_dir(
            repo_path,
            file_path,
            ["uv.lock", "requirements.txt", "pyproject.toml", "setup.py"],
        )
        if cloned_dirc_py is None:
            return None
        if (cloned_dirc_py / "uv.lock").exists():
            return "pip install -e . pytest --root-user-action=ignore"
        if (cloned_dirc_py / "requirements.txt").exists():
            return "pip install -r requirements.txt pytest --quiet"
        if (cloned_dirc_py / "pyproject.toml").exists() or (
            cloned_dirc_py / "setup.py"
        ).exists():
            return "pip install -e . pytest --quiet"
        return None

    if lang in ("javascript", "typescript"):
        cloned_dirc_web = find_dir(repo_path, file_path, ["package.json"])
        if cloned_dirc_web is not None:
            # yarn project — install yarn first, then use it
            if (cloned_dirc_web / "yarn.lock").exists():
                return "npm install -g yarn --silent && yarn install --frozen-lockfile --silent"
            # pnpm project — install pnpm first, then use it
            if (cloned_dirc_web / "pnpm-lock.yaml").exists():
                return "npm install -g pnpm --silent && pnpm install --frozen-lockfile --silent"
            # default npm
        return "npm install --silent"

    return None


def detect_test_cmd(lang: str, repo_path: Path, file_path: Path) -> str | None:
    """
    returns command to run the test or None if no tests found in the repo
    """

    if lang == "python":
        test_py = find_dir(
            repo_path,
            file_path,
            ["uv.lock", "requirements.txt", "pyproject.toml", "setup.py"],
        )
        search_dir = test_py if test_py is not None else repo_path

        # fallback

        has_testFiles = list(search_dir.rglob("test_*.py")) + list(
            search_dir.rglob("*_test.py")
        )

        has_test_dir = (search_dir / "tests").exists() or (search_dir / "test").exists()

        if has_testFiles or has_test_dir:
            return "python -m pytest --tb=short"

        return None

    if lang in ("javascript", "typescript"):
        test_script = find_dir(repo_path, file_path, ["package.json"])
        if test_script is None:
            return None
        pkg = test_script / "package.json"
        if pkg.exists():
            try:
                data = json.loads(pkg.read_text(encoding="utf-8"))
                scripts = data.get("scripts", {})
                if "test" in scripts:
                    if (test_script / "yarn.lock").exists():
                        return "yarn test"
                    if (test_script / "pnpm-lock.yaml").exists():
                        return "pnpm test"
                    return "npm test"
                return None
            except json.JSONDecodeError:
                return None
    return None


def detect_entryPoint(lang: str, repo_path: Path, file_path: Path) -> str | None:
    """
    if no test found then run the main entry point of the repo
    """
    if lang == "python":
        entryPoint_py = find_dir(
            repo_path,
            file_path,
            ["uv.lock", "requirements.txt", "pyproject.toml", "setup.py"],
        )
        search_dir = entryPoint_py if entryPoint_py is not None else repo_path

        for entry in ["main.py", "app.py", "run.py", "src/main.py", "src/app.py"]:
            if (search_dir / entry).exists():
                return f"python {entry}"
        return None

    if lang in ("javascript", "typescript"):
        entryPoint_script = find_dir(repo_path, file_path, ["package.json"])
        if entryPoint_script is None:
            return None
        pkg = entryPoint_script / "package.json"
        if pkg.exists():
            try:
                data = json.loads(pkg.read_text(encoding="utf-8"))
                scripts = data.get("scripts", {})
                if "start" in scripts:
                    if (entryPoint_script / "yarn.lock").exists():
                        return "yarn start"
                    if (entryPoint_script / "pnpm-lock.yaml").exists():
                        return "pnpm start"
                    return "npm start"
            except json.JSONDecodeError:
                pass
            return None
