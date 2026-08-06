# Python EXE Builder

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
