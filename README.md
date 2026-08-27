# Python App Packager

A safer graphical front end for PyInstaller.

## Improvements over the original draft

- Uses `python -m PyInstaller` and an argument list (`shell=False`)
- Validates source, destination, icon and application name
- Supports one-file/folder and console/windowed builds
- Runs in a background thread, streams logs and supports cancellation
- Explains that PyInstaller builds for the current operating system
- Includes unit tests for command construction

## Run

```bash
python -m pip install -r requirements.txt
python main.py
```

---

## Live demo

**[Open the live demo](https://mateotrucco.github.io/python_app_packager/)**

The demo runs the repository’s Python validation/command-building logic in the browser with Pyodide 314.0.4. It intentionally does not execute PyInstaller or create an executable.

## Repository setup

This separated repository also includes:

- MIT license
- project-specific `.gitignore`
- automated tests / CI
- GitHub Pages deployment for the demo
- `screenshots/` placeholder for portfolio images

The source files from the cleaned portfolio base were preserved unless a web-demo integration file had to be added.

