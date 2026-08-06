"""Command construction and validation for PyInstaller builds."""

from __future__ import annotations

import importlib.util
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BuildOptions:
    script: Path
    destination: Path
    one_file: bool = True
    windowed: bool = True
    clean: bool = True
    name: str | None = None
    icon: Path | None = None


def pyinstaller_available() -> bool:
    return importlib.util.find_spec("PyInstaller") is not None


def validate_options(options: BuildOptions) -> BuildOptions:
    script = options.script.expanduser().resolve()
    destination = options.destination.expanduser().resolve()
    if not script.is_file():
        raise ValueError("Select an existing Python file.")
    if script.suffix.lower() != ".py":
        raise ValueError("The source file must end in .py.")
    if not destination.exists() or not destination.is_dir():
        raise ValueError("Select an existing destination folder.")

    name = options.name.strip() if options.name else script.stem
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", name):
        raise ValueError("The app name may contain letters, numbers, dots, hyphens and underscores.")

    icon = options.icon.expanduser().resolve() if options.icon else None
    if icon is not None and not icon.is_file():
        raise ValueError("The selected icon does not exist.")

    return BuildOptions(
        script=script,
        destination=destination,
        one_file=options.one_file,
        windowed=options.windowed,
        clean=options.clean,
        name=name,
        icon=icon,
    )


def build_command(options: BuildOptions) -> list[str]:
    options = validate_options(options)
    work_dir = options.destination / ".pyinstaller" / options.name
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--distpath",
        str(options.destination),
        "--workpath",
        str(work_dir / "build"),
        "--specpath",
        str(work_dir),
        "--name",
        options.name or options.script.stem,
    ]
    command.append("--onefile" if options.one_file else "--onedir")
    command.append("--windowed" if options.windowed else "--console")
    if options.clean:
        command.append("--clean")
    if options.icon is not None:
        command.extend(["--icon", str(options.icon)])
    command.append(str(options.script))
    return command
