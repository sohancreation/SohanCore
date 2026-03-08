import os
import sys
import json
import subprocess
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import psutil

STATE_FILE = "temp/ui_state.json"
ENV_FILE = ".env"
LOG_FILE = "sohan_ai.log"


class SohanCoreUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.root_dir = self._detect_root_dir()
        self.workspace_dir = self._detect_workspace_dir()
        self.title("SohanCore Control Panel")
        self.geometry("1080x760")
        self.minsize(980, 680)

        self.agent_pid = None
        self.log_seek = 0
        self.env_fields = {}
        self.wizard_items = []
        self._last_discovery_check = 0.0
        self._log_initialized = False

        self._build_style()
        self._build_ui()
        self._load_state()
        self._load_env()
        self._refresh_status()
        self.after(1200, self._poll_logs)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _detect_root_dir(self):
        if getattr(sys, "frozen", False):
            return Path(sys.executable).resolve().parent
        return Path(__file__).resolve().parent

    def _detect_workspace_dir(self):
        candidates = [
            self.root_dir,
            self.root_dir.parent,
            self.root_dir / "SohanCore",
            self.root_dir / "dist" / "SohanCore",
            self.root_dir.parent / "SohanCore",
            self.root_dir.parent.parent if self.root_dir.parent else self.root_dir,
        ]
        seen = set()
        for c in candidates:
            if not c:
                continue
            p = c.resolve()
            if p in seen:
                continue
            seen.add(p)
            if (p / "main.py").exists() or (p / ".env").exists() or (p / "run_sohancore_background.bat").exists():
                return p
        return self.root_dir

    def _resolve_backend(self):
        main_py = self.workspace_dir / "main.py"
        if main_py.exists() and not getattr(sys, "frozen", False):
            return [sys.executable, str(main_py)], self.workspace_dir

        exe_candidates = [
            self.workspace_dir / "dist" / "SohanCore" / "SohanCore.exe",
            self.workspace_dir / "SohanCore.exe",
            self.root_dir / "SohanCore.exe",
            self.root_dir / "SohanCore" / "SohanCore.exe",
            self.root_dir.parent / "SohanCore" / "SohanCore.exe",
        ]
        for exe in exe_candidates:
            if exe.exists():
                return [str(exe)], self.workspace_dir

        if main_py.exists():
            return [sys.executable, str(main_py)], self.workspace_dir
        return None, None

    def _build_style(self):
        self.palette = {
            "bg": "#0b1118",
            "surface": "#111a24",
            "surface_soft": "#162230",
            "border": "#243447",
            "text": "#e9eef5",
            "muted": "#9db0c4",
            "accent": "#d7b66f",
            "accent_hover": "#e4c681",
            "danger": "#b54a4a",
        }
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        self.configure(bg=self.palette["bg"])

        style.configure(
            ".",
            background=self.palette["bg"],
            foreground=self.palette["text"],
            fieldbackground=self.palette["surface_soft"],
            bordercolor=self.palette["border"],
            lightcolor=self.palette["surface_soft"],
            darkcolor=self.palette["surface_soft"],
            troughcolor=self.palette["surface_soft"],
        )
        style.configure("TFrame", background=self.palette["bg"])
        style.configure("Card.TFrame", background=self.palette["surface"], padding=16, relief="solid", borderwidth=1)
        style.configure("Title.TLabel", background=self.palette["bg"], foreground=self.palette["text"], font=("Segoe UI Variable Display", 20, "bold"))
        style.configure("Section.TLabel", background=self.palette["surface"], foreground=self.palette["text"], font=("Segoe UI Variable Display", 18, "bold"))
        style.configure("Body.TLabel", background=self.palette["surface"], foreground=self.palette["muted"], font=("Segoe UI", 10))
        style.configure("Label.TLabel", background=self.palette["bg"], foreground=self.palette["muted"], font=("Segoe UI", 10))
        style.configure("Status.TLabel", background=self.palette["surface_soft"], foreground=self.palette["accent"], font=("Segoe UI", 10, "bold"), padding=(12, 6))

        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=(14, 8), background=self.palette["accent"], foreground="#141414", borderwidth=0)
        style.map("Accent.TButton", background=[("active", self.palette["accent_hover"])], foreground=[("disabled", "#5a6572")])
        style.configure("Secondary.TButton", font=("Segoe UI", 10), padding=(14, 8), background=self.palette["surface_soft"], foreground=self.palette["text"], borderwidth=0)
        style.map("Secondary.TButton", background=[("active", "#203243")])
        style.configure("Danger.TButton", font=("Segoe UI", 10), padding=(14, 8), background=self.palette["danger"], foreground="#fff3f3", borderwidth=0)
        style.map("Danger.TButton", background=[("active", "#c35a5a")])

        style.configure("TNotebook", background=self.palette["bg"], borderwidth=0, tabmargins=(0, 0, 0, 0))
        style.configure("TNotebook.Tab", background=self.palette["surface_soft"], foreground=self.palette["muted"], padding=(18, 10), font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", self.palette["surface"]), ("active", "#223346")], foreground=[("selected", self.palette["accent"]), ("active", self.palette["text"])])

        style.configure("TLabelframe", background=self.palette["surface"], foreground=self.palette["muted"], bordercolor=self.palette["border"], borderwidth=1)
        style.configure("TLabelframe.Label", background=self.palette["surface"], foreground=self.palette["muted"], font=("Segoe UI", 10, "bold"))
        style.configure("TEntry", fieldbackground=self.palette["surface_soft"], foreground=self.palette["text"], bordercolor=self.palette["border"], insertcolor=self.palette["text"], padding=6)

    def _build_ui(self):
        container = ttk.Frame(self, padding=14)
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container)
        header.pack(fill="x", pady=(0, 12))
        ttk.Label(header, text="SohanCore", style="Title.TLabel").pack(side="left")
        ttk.Label(header, text="Control Panel", style="Label.TLabel").pack(side="left", padx=(10, 0), pady=(6, 0))
        self.status_label = ttk.Label(header, text="Status: Checking...", style="Status.TLabel")
        self.status_label.pack(side="right")

        notebook = ttk.Notebook(container)
        notebook.pack(fill="both", expand=True)

        tab_dashboard = ttk.Frame(notebook)
        tab_setup = ttk.Frame(notebook)
        tab_config = ttk.Frame(notebook)
        tab_logs = ttk.Frame(notebook)

        notebook.add(tab_dashboard, text="Dashboard")
        notebook.add(tab_setup, text="Setup Wizard")
        notebook.add(tab_config, text="Configuration")
        notebook.add(tab_logs, text="Live Logs")

        self._build_dashboard(tab_dashboard)
        self._build_setup(tab_setup)
        self._build_config(tab_config)
        self._build_logs(tab_logs)

    def _build_dashboard(self, parent):
        panel = ttk.Frame(parent, style="Card.TFrame")
        panel.pack(fill="both", expand=True, padx=10, pady=10)

        title = ttk.Label(panel, text="Agent Control", style="Section.TLabel")
        title.pack(anchor="w", pady=(0, 12))
        ttk.Label(panel, text="Start, monitor, and manage your agent from one place.", style="Body.TLabel").pack(anchor="w", pady=(0, 14))

        buttons = ttk.Frame(panel)
        buttons.pack(fill="x", pady=(0, 14))

        ttk.Button(buttons, text="Start Agent", style="Accent.TButton", command=self._start_agent).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="Stop Agent", style="Danger.TButton", command=self._stop_agent).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="Run In Background", style="Secondary.TButton", command=self._run_background).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="Open Projects Folder", style="Secondary.TButton", command=self._open_projects).pack(side="left")

        quick = ttk.LabelFrame(panel, text="Quick Paths")
        quick.pack(fill="x", pady=(8, 16))
        ttk.Button(quick, text="Open .env", style="Secondary.TButton", command=self._open_env_file).pack(side="left", padx=8, pady=10)
        ttk.Button(quick, text="Open Logs", style="Secondary.TButton", command=self._open_logs_file).pack(side="left", padx=8, pady=10)
        ttk.Button(quick, text="Open Dist", style="Secondary.TButton", command=self._open_dist).pack(side="left", padx=8, pady=10)

        self.status_text = ScrolledText(panel, height=16, wrap="word")
        self.status_text.pack(fill="both", expand=True)
        self.status_text.configure(
            bg="#0f1721",
            fg=self.palette["text"],
            insertbackground=self.palette["text"],
            selectbackground="#2b3f55",
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.palette["border"],
            font=("Consolas", 10),
            padx=10,
            pady=10,
        )
        self.status_text.insert("end", "SohanCore Control Panel ready.\n")
        self.status_text.configure(state="disabled")

    def _build_setup(self, parent):
        panel = ttk.Frame(parent, style="Card.TFrame")
        panel.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(panel, text="First-Time Setup", style="Section.TLabel").pack(anchor="w", pady=(0, 12))
        ttk.Label(panel, text="Follow this checklist to configure SohanCore correctly.", style="Body.TLabel").pack(anchor="w", pady=(0, 10))

        steps = [
            "1. Create a Telegram bot with @BotFather and copy token.",
            "2. Add TELEGRAM_BOT_TOKEN and ALLOWED_USER_IDS in Configuration tab.",
            "3. Choose provider: API key (OpenRouter/OpenAI) or local Ollama.",
            "4. Click Save Configuration.",
            "5. Click Start Agent from Dashboard.",
            "6. Open Telegram and send /start to your bot.",
            "7. Optional: Use Run In Background for headless mode.",
        ]

        box = tk.Listbox(panel, height=10, activestyle="none")
        box.pack(fill="x")
        box.configure(
            bg="#0f1721",
            fg=self.palette["text"],
            selectbackground="#243447",
            selectforeground=self.palette["accent"],
            highlightthickness=1,
            highlightbackground=self.palette["border"],
            relief="flat",
            font=("Segoe UI", 10),
        )
        for item in steps:
            box.insert("end", "[ ] " + item)
        self.wizard_items = steps
        self.wizard_list = box

        controls = ttk.Frame(panel)
        controls.pack(fill="x", pady=8)
        ttk.Button(controls, text="Mark Selected Done", style="Accent.TButton", command=self._mark_step_done).pack(side="left")
        ttk.Button(controls, text="Reset Checklist", style="Secondary.TButton", command=self._reset_steps).pack(side="left", padx=(8, 0))

        help_text = (
            "Tip: Your Telegram numeric user id can be found from @userinfobot.\n"
            "For Ollama, install it and ensure OLLAMA_BASE_URL is reachable."
        )
        ttk.Label(panel, text=help_text, style="Body.TLabel").pack(anchor="w", pady=(10, 0))

    def _build_config(self, parent):
        panel = ttk.Frame(parent, style="Card.TFrame")
        panel.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(panel, text="Configuration (.env)", style="Section.TLabel").pack(anchor="w", pady=(0, 12))
        ttk.Label(panel, text="Manage tokens, providers, and runtime preferences.", style="Body.TLabel").pack(anchor="w", pady=(0, 10))

        fields = [
            ("TELEGRAM_BOT_TOKEN", False),
            ("ALLOWED_USER_IDS", False),
            ("OPENROUTER_API_KEY", True),
            ("OPENAI_API_KEY", True),
            ("GEMINI_API_KEY", True),
            ("GROK_API_KEY", True),
            ("DEEPSEEK_API_KEY", True),
            ("LLM_PROVIDER_ORDER", False),
            ("OLLAMA_BASE_URL", False),
            ("OLLAMA_MODEL_FAST", False),
            ("OLLAMA_MODEL_CODE", False),
        ]

        form = ttk.Frame(panel)
        form.pack(fill="both", expand=True)
        form.columnconfigure(1, weight=1)

        for row, (key, masked) in enumerate(fields):
            ttk.Label(form, text=key + ":", style="Label.TLabel").grid(row=row, column=0, sticky="w", padx=(0, 8), pady=5)
            var = tk.StringVar()
            entry = ttk.Entry(form, textvariable=var, show="*" if masked else "")
            entry.grid(row=row, column=1, sticky="ew", pady=5)
            self.env_fields[key] = (var, masked, entry)

        actions = ttk.Frame(panel)
        actions.pack(fill="x", pady=(10, 0))
        ttk.Button(actions, text="Save Configuration", style="Accent.TButton", command=self._save_env).pack(side="left")
        ttk.Button(actions, text="Reload", style="Secondary.TButton", command=self._load_env).pack(side="left", padx=(8, 0))
        ttk.Button(actions, text="Show/Hide Keys", style="Secondary.TButton", command=self._toggle_secrets).pack(side="left", padx=(8, 0))

    def _build_logs(self, parent):
        panel = ttk.Frame(parent, style="Card.TFrame")
        panel.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(panel, text="Live Agent Logs", style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        self.log_view = ScrolledText(panel, wrap="none")
        self.log_view.pack(fill="both", expand=True)
        self.log_view.configure(
            bg="#0f1721",
            fg=self.palette["text"],
            insertbackground=self.palette["text"],
            selectbackground="#2b3f55",
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.palette["border"],
            font=("Consolas", 10),
            padx=10,
            pady=10,
        )
        self.log_view.configure(state="disabled")

        actions = ttk.Frame(panel)
        actions.pack(fill="x", pady=(8, 0))
        ttk.Button(actions, text="Refresh", style="Secondary.TButton", command=self._force_log_refresh).pack(side="left")
        ttk.Button(actions, text="Clear View", style="Secondary.TButton", command=self._clear_log_view).pack(side="left", padx=(8, 0))

    def _log(self, text):
        self.status_text.configure(state="normal")
        self.status_text.insert("end", text + "\n")
        self.status_text.see("end")
        self.status_text.configure(state="disabled")

    def _read_env(self):
        path = self.workspace_dir / ENV_FILE
        data = {}
        if not path.exists():
            return data
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.strip().startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            data[key.strip()] = value.strip()
        return data

    def _write_env(self, data):
        lines = [f"{k}={v}" for k, v in data.items()]
        (self.workspace_dir / ENV_FILE).write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _load_env(self):
        data = self._read_env()
        for key, (var, _, _) in self.env_fields.items():
            var.set(data.get(key, ""))
        self._log("Configuration loaded.")

    def _save_env(self):
        current = self._read_env()
        for key, (var, _, _) in self.env_fields.items():
            current[key] = var.get().strip()
        self._write_env(current)
        self._log("Configuration saved to .env.")
        messagebox.showinfo("Saved", "Configuration saved successfully.")

    def _toggle_secrets(self):
        for _, (_, masked, entry) in self.env_fields.items():
            if not masked:
                continue
            entry_show = entry.cget("show")
            entry.configure(show="" if entry_show == "*" else "*")

    def _load_state(self):
        state_path = self.root_dir / STATE_FILE
        if state_path.exists():
            try:
                data = json.loads(state_path.read_text(encoding="utf-8"))
                self.agent_pid = data.get("agent_pid")
            except Exception:
                self.agent_pid = None

    def _save_state(self):
        state_path = self.root_dir / STATE_FILE
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps({"agent_pid": self.agent_pid}, indent=2), encoding="utf-8")

    def _is_running(self):
        if not self.agent_pid:
            return False
        try:
            p = psutil.Process(int(self.agent_pid))
            return p.is_running() and p.status() != psutil.STATUS_ZOMBIE
        except Exception:
            return False

    def _discover_backend_pid(self):
        cmd, _ = self._resolve_backend()
        if not cmd:
            return None
        target = Path(cmd[0]).name.lower()
        if not target:
            return None

        target_main = (self.workspace_dir / "main.py").resolve()
        best_pid = None
        best_ctime = 0.0

        try:
            for p in psutil.process_iter(["pid", "name", "exe", "cmdline", "create_time"]):
                info = p.info
                name = (info.get("name") or "").lower()
                exe = (info.get("exe") or "").lower()
                cmdline = [str(x).lower() for x in (info.get("cmdline") or [])]
                matches = False

                if target.endswith(".exe"):
                    matches = name == target or exe.endswith("\\" + target)
                else:
                    # dev mode: python + main.py
                    if name.startswith("python"):
                        for part in cmdline:
                            if part.endswith("main.py"):
                                try:
                                    if Path(part).resolve() == target_main:
                                        matches = True
                                        break
                                except Exception:
                                    continue

                if not matches:
                    continue
                ctime = float(info.get("create_time") or 0.0)
                if ctime >= best_ctime:
                    best_ctime = ctime
                    best_pid = int(info["pid"])
        except Exception:
            return None
        return best_pid

    def _adopt_backend_pid(self):
        if not sys.platform.startswith("win"):
            return
        pid = self._discover_backend_pid()
        if pid:
            self.agent_pid = pid
            self._save_state()
            self._refresh_status()

    def _start_agent(self):
        if self._is_running():
            messagebox.showinfo("Running", f"Agent already running (PID {self.agent_pid}).")
            return
        cmd, cwd = self._resolve_backend()
        if not cmd:
            messagebox.showerror("Error", "Backend not found. Place SohanCore.exe or main.py in workspace.")
            return
        creationflags = 0
        if sys.platform.startswith("win"):
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
        proc = subprocess.Popen(
            cmd,
            cwd=str(cwd),
            creationflags=creationflags,
        )
        self.agent_pid = proc.pid
        self._save_state()
        self._log(f"Agent started (PID {self.agent_pid}) using: {' '.join(cmd)}")
        self._refresh_status()
        self.after(900, self._adopt_backend_pid)

    def _stop_agent(self):
        if not self._is_running():
            self.agent_pid = None
            self._save_state()
            self._refresh_status()
            messagebox.showinfo("Stopped", "Agent is not running.")
            return
        try:
            if sys.platform.startswith("win"):
                subprocess.run(
                    ["taskkill", "/PID", str(self.agent_pid), "/T", "/F"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                )
            else:
                os.kill(self.agent_pid, 15)
        finally:
            self._log(f"Agent stopped (PID {self.agent_pid}).")
            self.agent_pid = None
            self._save_state()
            self._refresh_status()

    def _refresh_status(self):
        if self._is_running():
            self.status_label.config(text=f"Status: Running (PID {self.agent_pid})")
        else:
            now = time.monotonic()
            if sys.platform.startswith("win") and now - self._last_discovery_check >= 5.0:
                self._last_discovery_check = now
                pid = self._discover_backend_pid()
                if pid:
                    self.agent_pid = pid
                    self._save_state()
                    self.status_label.config(text=f"Status: Running (PID {self.agent_pid})")
                    return
            self.status_label.config(text="Status: Stopped")

    def _run_background(self):
        bat_candidates = [
            self.workspace_dir / "run_sohancore_background.bat",
            self.root_dir / "run_sohancore_background.bat",
        ]
        for bat in bat_candidates:
            if bat.exists():
                subprocess.Popen(["cmd", "/c", str(bat)], cwd=str(self.workspace_dir))
                self._log(f"Background launcher triggered: {bat}")
                self.after(900, self._adopt_backend_pid)
                return

        cmd, cwd = self._resolve_backend()
        if not cmd:
            messagebox.showerror("Error", "No background launcher or backend executable found.")
            return
        creationflags = 0
        if sys.platform.startswith("win"):
            creationflags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        proc = subprocess.Popen(cmd, cwd=str(cwd), creationflags=creationflags)
        self.agent_pid = proc.pid
        self._save_state()
        self._log(f"Background started (PID {self.agent_pid}) using: {' '.join(cmd)}")
        self.after(900, self._adopt_backend_pid)

    def _open_env_file(self):
        subprocess.Popen(["notepad.exe", str(self.workspace_dir / ENV_FILE)])

    def _open_logs_file(self):
        subprocess.Popen(["notepad.exe", str(self.workspace_dir / LOG_FILE)])

    def _open_projects(self):
        path = self.workspace_dir / "projects"
        path.mkdir(parents=True, exist_ok=True)
        subprocess.Popen(["explorer", str(path)])

    def _open_dist(self):
        path = self.workspace_dir / "dist"
        path.mkdir(parents=True, exist_ok=True)
        subprocess.Popen(["explorer", str(path)])

    def _mark_step_done(self):
        sel = self.wizard_list.curselection()
        if not sel:
            return
        idx = sel[0]
        text = self.wizard_items[idx]
        self.wizard_list.delete(idx)
        self.wizard_list.insert(idx, "[x] " + text)

    def _reset_steps(self):
        self.wizard_list.delete(0, "end")
        for item in self.wizard_items:
            self.wizard_list.insert("end", "[ ] " + item)

    def _append_log_text(self, data):
        self.log_view.configure(state="normal")
        self.log_view.insert("end", data)
        self.log_view.see("end")
        self.log_view.configure(state="disabled")

    def _poll_logs(self):
        try:
            log_path = self.workspace_dir / LOG_FILE
            if log_path.exists():
                size = log_path.stat().st_size
                if not self._log_initialized:
                    # Avoid freezing UI by loading a huge historic log on first paint.
                    self.log_seek = size
                    self._log_initialized = True
                if self.log_seek > size:
                    self.log_seek = 0
                with log_path.open("r", encoding="utf-8", errors="replace") as f:
                    f.seek(self.log_seek)
                    chunk = f.read(65536)
                    self.log_seek = f.tell()
                if chunk:
                    self._append_log_text(chunk)
        except Exception:
            pass
        self._refresh_status()
        self.after(1200, self._poll_logs)

    def _force_log_refresh(self):
        self.log_seek = 0
        self.log_view.configure(state="normal")
        self.log_view.delete("1.0", "end")
        self.log_view.configure(state="disabled")
        self._poll_logs()

    def _clear_log_view(self):
        self.log_view.configure(state="normal")
        self.log_view.delete("1.0", "end")
        self.log_view.configure(state="disabled")

    def _on_close(self):
        self._save_state()
        self.destroy()


if __name__ == "__main__":
    app = SohanCoreUI()
    app.mainloop()
