import json

import pytest

from src.gitchecker.core.sandbox.detector import (
    detect_entryPoint,
    detect_install_cmd,
    detect_lang,
    detect_lang_forSandbox,
    detect_lang_fromFile,
    detect_test_cmd,
)

# detect_lang


@pytest.mark.parametrize(
    "file_path,expected",
    [
        ("main.py", "python"),
        ("src/App.tsx", "typescript"),
        ("src/App.ts", "typescript"),
        ("index.js", "javascript"),
        ("component.jsx", "javascript"),
        ("server.mjs", "javascript"),
        ("config.cjs", "javascript"),
        ("README.md", "unknown"),
        ("Dockerfile", "unknown"),
    ],
)
def test_detect_lang_fromFile(file_path, expected):
    assert detect_lang_fromFile(file_path) == expected


def test_detect_lang_fromFile_case_insensitive():
    assert detect_lang_fromFile("Main.PY") == "python"


def test_detect_lang_python_via_pyproject(tmp_path):
    (tmp_path / "pyproject.toml").touch()
    assert detect_lang(tmp_path) == "python"


def test_detect_lang_python_via_requirements(tmp_path):
    (tmp_path / "requirements.txt").touch()
    assert detect_lang(tmp_path) == "python"


def test_detect_lang_javascript_default(tmp_path):
    (tmp_path / "package.json").touch()
    assert detect_lang(tmp_path) == "javascript"


def test_detect_lang_typescript_when_tsconfig_present(tmp_path):
    (tmp_path / "package.json").touch()
    (tmp_path / "tsconfig.json").touch()
    assert detect_lang(tmp_path) == "typescript"


def test_detect_lang_python_takes_priority_over_js(tmp_path):
    (tmp_path / "pyproject.toml").touch()
    (tmp_path / "package.json").touch()
    assert detect_lang(tmp_path) == "python"


def test_detect_lang_cpp(tmp_path):
    (tmp_path / "CMakeLists.txt").touch()
    assert detect_lang(tmp_path) == "cpp"


def test_detect_lang_unknown_when_nothing_matches(tmp_path):
    assert detect_lang(tmp_path) == "unknown"


# tests detect lang for sandbox


def test_detect_lang_forSandbox_prefers_file_extension(tmp_path):
    (tmp_path / "package.json").touch()
    assert detect_lang_forSandbox("scripts/build.py", tmp_path) == "python"


def test_detect_lang_forSandbox_falls_back_to_repo_scan(tmp_path):
    (tmp_path / "pyproject.toml").touch()
    assert detect_lang_forSandbox("config.yml", tmp_path) == "python"


# tests install command detection


def test_js_yarn(tmp_path):
    (tmp_path / "frontend").mkdir()
    (tmp_path / "frontend" / "package.json").write_text("{}")
    (tmp_path / "frontend" / "yarn.lock").touch()

    cmd = detect_install_cmd("javascript", tmp_path, "frontend/src/App.jsx")
    assert "yarn install" in cmd


def test_js_npm(tmp_path):
    (tmp_path / "frontend").mkdir()
    (tmp_path / "frontend" / "package.json").write_text("{}")

    cmd = detect_install_cmd("javascript", tmp_path, "frontend/src/App.jsx")
    assert cmd == "npm install --silent"


def test_python_uv(tmp_path):
    (tmp_path / "backend").mkdir()
    (tmp_path / "backend" / "uv.lock").touch()

    cmd = detect_install_cmd("python", tmp_path, "backend/app/service.py")
    assert "pytest" in cmd


# tests test command detection
def test_python_tests(tmp_path):
    (tmp_path / "backend").mkdir()
    (tmp_path / "backend" / "tests").mkdir()
    (tmp_path / "backend" / "requirements.txt").touch()

    cmd = detect_test_cmd("python", tmp_path, "backend/app/service.py")
    assert cmd == "python -m pytest --tb=short"


def test_js(tmp_path):
    (tmp_path / "frontend").mkdir()
    pkg = {"scripts": {"test": "jest"}}
    (tmp_path / "frontend" / "package.json").write_text(json.dumps(pkg))

    cmd = detect_test_cmd("javascript", tmp_path, "frontend/src/App.jsx")
    assert cmd == "npm test"


# tests entrypoint detection
def test_entrypoint_py(tmp_path):
    (tmp_path / "backend").mkdir()
    (tmp_path / "backend" / "main.py").touch()
    (tmp_path / "backend" / "pyproject.toml").touch()

    cmd = detect_entryPoint("python", tmp_path, "backend/app/service.py")
    assert cmd == "python main.py"
