"""Graphical PyInstaller front end with validation and build logs."""

from __future__ import annotations

import platform
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from builder import BuildOptions, build_command, pyinstaller_available
from ui_theme import apply_theme, text_style


class PackagerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Python App Packager")
        self.root.geometry("820x600")
        self.root.minsize(700, 520)
        self.colors = apply_theme(root, "#b77900")
        self.process: subprocess.Popen[str] | None = None
        self.build_in_progress = False
        self.cancel_requested = threading.Event()

        self.script_var = tk.StringVar()
        self.destination_var = tk.StringVar(value=str(Path.home() / "Desktop"))
        self.name_var = tk.StringVar()
        self.icon_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="onefile")
        self.console_var = tk.BooleanVar(value=False)
        self.clean_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Ready.")

        self._build_ui()
        self._show_platform_note()

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=18)
        container.pack(fill="both", expand=True)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(7, weight=1)

        ttk.Label(container, text="Python App Packager", style="Title.TLabel").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 4)
        )
        self.note = ttk.Label(container, wraplength=760)
        self.note.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 14))

        self._path_row(container, 2, "Python script", self.script_var, self.choose_script)
        self._path_row(container, 3, "Destination", self.destination_var, self.choose_destination)
        self._path_row(container, 4, "Icon (optional)", self.icon_var, self.choose_icon)

        ttk.Label(container, text="Application name").grid(row=5, column=0, sticky="w", pady=6)
        ttk.Entry(container, textvariable=self.name_var).grid(row=5, column=1, columnspan=2, sticky="ew", pady=6)

        options = ttk.Frame(container)
        options.grid(row=6, column=0, columnspan=3, sticky="ew", pady=8)
        ttk.Radiobutton(options, text="Single file", variable=self.mode_var, value="onefile").pack(side="left")
        ttk.Radiobutton(options, text="Folder", variable=self.mode_var, value="onedir").pack(side="left", padx=12)
        ttk.Checkbutton(options, text="Console application", variable=self.console_var).pack(side="left", padx=12)
        ttk.Checkbutton(options, text="Clean cache", variable=self.clean_var).pack(side="left")

        log_frame = ttk.LabelFrame(container, text="Build log", padding=8)
        log_frame.grid(row=7, column=0, columnspan=3, sticky="nsew", pady=(6, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.log = tk.Text(log_frame, wrap="word", state="disabled", font=("Consolas", 10))
        self.log.grid(row=0, column=0, sticky="nsew")
        text_style(self.log, self.colors, readonly=True)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log.configure(yscrollcommand=scrollbar.set)

        actions = ttk.Frame(container)
        actions.grid(row=8, column=0, columnspan=3, sticky="ew")
        self.build_button = ttk.Button(actions, text="Build application", style="Accent.TButton", command=self.start_build)
        self.build_button.pack(side="left")
        self.cancel_button = ttk.Button(actions, text="Cancel", command=self.cancel_build, state="disabled")
        self.cancel_button.pack(side="left", padx=8)
        ttk.Label(actions, textvariable=self.status_var).pack(side="right")

    def _path_row(self, parent, row: int, label: str, variable: tk.StringVar, command) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=6)
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", padx=(8, 6), pady=6)
        ttk.Button(parent, text="Browse…", command=command).grid(row=row, column=2, sticky="ew", pady=6)

    def _show_platform_note(self) -> None:
        system = platform.system()
        suffix = ".exe" if system == "Windows" else "a native binary for this operating system"
        availability = "PyInstaller is installed." if pyinstaller_available() else "PyInstaller is not installed yet."
        self.note.configure(
            text=(
                f"Current platform: {system}. PyInstaller builds {suffix}; it does not cross-compile Windows EXE files "
                f"from Linux or macOS. {availability}"
            )
        )

    def choose_script(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if path:
            self.script_var.set(path)
            if not self.name_var.get().strip():
                self.name_var.set(Path(path).stem)

    def choose_destination(self) -> None:
        path = filedialog.askdirectory()
        if path:
            self.destination_var.set(path)

    def choose_icon(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Icon files", "*.ico *.png"), ("All files", "*.*")])
        if path:
            self.icon_var.set(path)

    def _options(self) -> BuildOptions:
        icon = Path(self.icon_var.get()) if self.icon_var.get().strip() else None
        return BuildOptions(
            script=Path(self.script_var.get()),
            destination=Path(self.destination_var.get()),
            one_file=self.mode_var.get() == "onefile",
            windowed=not self.console_var.get(),
            clean=self.clean_var.get(),
            name=self.name_var.get(),
            icon=icon,
        )

    def _append_log(self, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", text)
        self.log.see("end")
        self.log.configure(state="disabled")

    def start_build(self) -> None:
        if self.build_in_progress:
            return
        try:
            command = build_command(self._options())
        except ValueError as exc:
            messagebox.showerror("Invalid configuration", str(exc))
            return
        if not pyinstaller_available():
            messagebox.showerror(
                "PyInstaller is missing",
                "Install it in this Python environment with: python -m pip install pyinstaller",
            )
            return

        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        self._append_log("Command:\n" + subprocess.list2cmdline(command) + "\n\n")
        self.status_var.set("Building…")
        self.build_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.build_in_progress = True
        self.cancel_requested.clear()

        threading.Thread(target=self._run_build, args=(command,), daemon=True).start()

    def _run_build(self, command: list[str]) -> None:
        return_code = -1
        process: subprocess.Popen[str] | None = None
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
            self.process = process
            if self.cancel_requested.is_set():
                process.terminate()
            assert process.stdout is not None
            for line in process.stdout:
                self.root.after(0, self._append_log, line)
            return_code = process.wait()
        except OSError as exc:
            self.root.after(0, self._append_log, f"\nCould not start PyInstaller: {exc}\n")
        finally:
            was_cancelled = self.cancel_requested.is_set()
            self.process = None
            self.root.after(0, self._finish_build, return_code, was_cancelled)

    def _finish_build(self, return_code: int, was_cancelled: bool) -> None:
        self.build_in_progress = False
        self.cancel_requested.clear()
        self.build_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")
        if was_cancelled:
            self.status_var.set("Build cancelled.")
            self._append_log("\nBuild cancelled by the user.\n")
        elif return_code == 0:
            self.status_var.set("Build completed.")
            self._append_log("\nBuild completed successfully.\n")
            messagebox.showinfo("Build complete", f"Output saved in:\n{self.destination_var.get()}")
        else:
            self.status_var.set(f"Build failed (code {return_code}).")

    def cancel_build(self) -> None:
        if not self.build_in_progress:
            return
        self.cancel_requested.set()
        self.status_var.set("Cancelling…")
        process = self.process
        if process is not None and process.poll() is None:
            try:
                process.terminate()
            except OSError:
                pass


def main() -> None:
    root = tk.Tk()
    PackagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
