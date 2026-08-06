from pathlib import Path
import sys

from builder import BuildOptions, build_command, validate_options


def test_command_is_argument_list_without_shell(tmp_path):
    script = tmp_path / "hello.py"
    script.write_text("print('hello')", encoding="utf-8")
    destination = tmp_path / "dist"
    destination.mkdir()
    command = build_command(BuildOptions(script, destination, name="hello-app"))
    assert command[:3] == [sys.executable, "-m", "PyInstaller"]
    assert "--onefile" in command
    assert "--windowed" in command
    assert str(script.resolve()) == command[-1]


def test_console_folder_mode(tmp_path):
    script = tmp_path / "cli.py"
    script.write_text("print('ok')", encoding="utf-8")
    destination = tmp_path / "dist"
    destination.mkdir()
    command = build_command(
        BuildOptions(script, destination, one_file=False, windowed=False, clean=False)
    )
    assert "--onedir" in command
    assert "--console" in command
    assert "--clean" not in command


def test_rejects_missing_script(tmp_path):
    destination = tmp_path / "dist"
    destination.mkdir()
    try:
        validate_options(BuildOptions(tmp_path / "missing.py", destination))
    except ValueError as exc:
        assert "existing Python file" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_rejects_unsafe_name(tmp_path):
    script = tmp_path / "app.py"
    script.write_text("", encoding="utf-8")
    destination = tmp_path / "dist"
    destination.mkdir()
    try:
        validate_options(BuildOptions(script, destination, name="bad name"))
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")
