"""Wajeeha Transcribe (Phonon-2) - Windows GUI for Fermion Research's Phonon-2.

Audio in: browse a file (wav, flac, ogg, aiff) or record from the microphone.
Output: transcript saved to a .txt file you choose.
Phonon-2 handles long files itself (it cuts them at pauses), so no length limit here.
The model lives in the "models" folder next to the exe.
"""
import os
import io
import sys
import time
import wave
import tempfile
import threading
import contextlib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_NAME = "Wajeeha Transcribe"      # change the window title here
MODEL = "phonon-2"
SR = 16000

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")


def hide_console_if_alone():
    """The exe is built as a console app (the engine needs valid std handles).
    Hide that console when we are the only process using it (double-click launch)."""
    if not getattr(sys, "frozen", False):
        return
    try:
        import ctypes
        k32 = ctypes.windll.kernel32
        procs = (ctypes.c_uint * 4)()
        if k32.GetConsoleProcessList(procs, 4) <= 1:
            hwnd = k32.GetConsoleWindow()
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 0)
    except Exception:
        pass


# ---------- locations & environment ----------
def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


APP_DIR = app_dir()


def models_present(dest):
    total = 0
    for root, _, files in os.walk(os.path.join(dest, "models")):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total > 100 * 1024 * 1024      # Phonon-2 is ~164 MB


def setup_env(dest=None):
    """Keep every download inside <dest>\\models so the folder is portable."""
    dest = dest or APP_DIR
    models = os.path.join(dest, "models")
    os.makedirs(models, exist_ok=True)
    os.environ["FERMION_CACHE_DIR"] = models
    os.environ["HF_HOME"] = os.path.join(models, "hf")
    if models_present(dest):
        os.environ["HF_HUB_OFFLINE"] = "1"
    else:
        os.environ.pop("HF_HUB_OFFLINE", None)


# ---------- audio helpers ----------
def write_wav(path, a):
    import numpy as np
    pcm = (np.clip(a, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


# ---------- run the fermion command in-process ----------
def run_fermion(args):
    """Runs the same code as the `fermion` command. Returns the transcript text."""
    import importlib.metadata as md
    eps = {e.name: e for e in md.entry_points(group="console_scripts")}
    if "fermion" in eps:
        main, argv = eps["fermion"].load(), ["fermion"] + args
    elif "phonon" in eps:                     # `phonon transcribe file.wav`
        main, argv = eps["phonon"].load(), ["phonon"] + [a for a in args if a != MODEL]
    else:
        raise RuntimeError("The fermion command was not found inside this build.")
    out, err = io.StringIO(), io.StringIO()
    old_argv, code = sys.argv, 0
    sys.argv = argv
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = main()
            except SystemExit as e:
                code = e.code
    finally:
        sys.argv = old_argv
    if code not in (None, 0):
        tail = (err.getvalue() or out.getvalue()).strip().splitlines()[-4:]
        raise RuntimeError("\n".join(tail) or f"fermion exited with code {code}")
    return out.getvalue().strip()


def prepare(dest, log=print):
    """Make sure the Phonon-2 weights are in <dest>\\models (downloads once, ~164 MB)."""
    setup_env(dest)
    if models_present(dest):
        return True
    log("First run: downloading Phonon-2 (164 MB, needs internet)...")
    tmp = os.path.join(tempfile.mkdtemp(), "silence.wav")
    import numpy as np
    write_wav(tmp, np.zeros(SR, dtype=np.float32))
    try:
        run_fermion(["transcribe", MODEL, tmp])
    except Exception as e:
        log(f"(note) {e}")
    setup_env(dest)
    ok = models_present(dest)
    log("Phonon-2 saved next to the exe." if ok else "Download did not finish.")
    return ok


# ---------- GUI ----------
def resource_path(name):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


BG, CARD, FG, MUTED = "#f3f5fa", "#ffffff", "#1f2937", "#6b7280"
ACCENT, ACCENT_H, DANGER, BORDER = "#2563eb", "#1d4ed8", "#dc2626", "#d6dbe6"
FONT = "Segoe UI"


class App:
    def __init__(self, root):
        self.root = root
        root.title(APP_NAME)
        root.configure(bg=BG)
        root.geometry("600x560")
        root.minsize(560, 520)
        self.recording = False
        self.frames = []
        self.stream = None
        self.busy = False
        self.set_icon()
        self.build_styles()
        self.build_ui()

        if models_present(APP_DIR):
            self.log("Ready. Phonon-2 found next to the exe.", clear=True)
        else:
            self.set_busy(True)
            self.log("First run: setting up Phonon-2 next to the exe...", clear=True)
            threading.Thread(target=self.prep_worker, daemon=True).start()

    # ----- look & feel -----
    def set_icon(self):
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("wajeeha.transcribe.phonon")
        except Exception:
            pass
        ico, png = resource_path("WT.ico"), resource_path("WT.png")
        try:
            if os.path.getsize(ico) > 0:
                self.root.iconbitmap(ico)
                return
        except Exception:
            pass
        try:
            if os.path.getsize(png) > 0:
                self._logo = tk.PhotoImage(file=png)
                self.root.iconphoto(True, self._logo)
        except Exception:
            pass

    def build_styles(self):
        st = ttk.Style(self.root)
        st.theme_use("clam")
        st.configure("TFrame", background=BG)
        st.configure("TLabel", background=BG, foreground=FG, font=(FONT, 10))
        st.configure("Section.TLabel", font=(FONT, 10, "bold"), foreground=FG)
        st.configure("Muted.TLabel", foreground=MUTED, font=(FONT, 9))
        st.configure("Field.TEntry", fieldbackground=CARD, foreground=FG, bordercolor=BORDER,
                     lightcolor=BORDER, darkcolor=BORDER, padding=8, font=(FONT, 10))
        st.map("Field.TEntry", bordercolor=[("focus", ACCENT)], lightcolor=[("focus", ACCENT)],
               darkcolor=[("focus", ACCENT)])
        base = dict(font=(FONT, 10, "bold"), padding=(16, 8), borderwidth=0, focusthickness=0, relief="flat")
        st.configure("Primary.TButton", background=ACCENT, foreground="white", **base)
        st.map("Primary.TButton", background=[("disabled", "#9ca3af"), ("active", ACCENT_H)],
               foreground=[("disabled", "#f3f4f6")])
        st.configure("Secondary.TButton", background="#e6ecff", foreground=ACCENT, **base)
        st.map("Secondary.TButton", background=[("active", "#d3deff")])
        st.configure("Rec.TButton", background="#fee2e2", foreground=DANGER, **base)
        st.map("Rec.TButton", background=[("active", "#fecaca")])
        st.configure("RecOn.TButton", background=DANGER, foreground="white", **base)
        st.map("RecOn.TButton", background=[("active", "#b91c1c")])
        st.configure("Bar.Horizontal.TProgressbar", troughcolor="#e5e9f2", background=ACCENT,
                     bordercolor="#e5e9f2", lightcolor=ACCENT, darkcolor=ACCENT, thickness=5)

    def build_ui(self):
        main = ttk.Frame(self.root, padding=(24, 20, 24, 14))
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(6, weight=1)

        ttk.Label(main, text="Audio file", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        row = ttk.Frame(main)
        row.grid(row=1, column=0, sticky="ew", pady=(6, 18))
        row.columnconfigure(0, weight=1)
        self.audio_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.audio_var, style="Field.TEntry")\
            .grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(row, text="Browse", style="Secondary.TButton", command=self.browse_audio)\
            .grid(row=0, column=1, padx=(0, 8))
        self.rec_btn = ttk.Button(row, text="\u25cf  Record", style="Rec.TButton", command=self.toggle_record)
        self.rec_btn.grid(row=0, column=2)

        ttk.Label(main, text="Save transcript to", style="Section.TLabel").grid(row=2, column=0, sticky="w")
        row2 = ttk.Frame(main)
        row2.grid(row=3, column=0, sticky="ew", pady=(6, 18))
        row2.columnconfigure(0, weight=1)
        self.save_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.save_var, style="Field.TEntry")\
            .grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(row2, text="Browse", style="Secondary.TButton", command=self.browse_save)\
            .grid(row=0, column=1)

        self.run_btn = ttk.Button(main, text="Run transcription", style="Primary.TButton", command=self.run)
        self.run_btn.grid(row=4, column=0, sticky="ew", ipady=4)

        top = ttk.Frame(main)
        top.grid(row=5, column=0, sticky="ew", pady=(20, 6))
        top.columnconfigure(1, weight=1)
        ttk.Label(top, text="Status", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        self.bar = ttk.Progressbar(top, mode="indeterminate", style="Bar.Horizontal.TProgressbar", length=140)
        self.bar.grid(row=0, column=1, sticky="e")

        box = tk.Frame(main, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        box.grid(row=6, column=0, sticky="nsew")
        self.status = tk.Text(box, height=6, wrap="word", relief="flat", bg=CARD, fg=FG,
                              font=(FONT, 10), padx=12, pady=10, state="disabled", bd=0)
        sb = ttk.Scrollbar(box, command=self.status.yview)
        self.status.config(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.status.pack(side="left", fill="both", expand=True)

        ttk.Label(main, text="Works with wav, flac, ogg and aiff files (English). Long files are fine.\n"
                  "mp3 / m4a: convert to wav first. The first transcription loads the engine (10-40 s).",
                  style="Muted.TLabel", justify="left").grid(row=7, column=0, sticky="w", pady=(12, 0))

    # status helpers (safe from worker threads)
    def log(self, msg, clear=False):
        def _do():
            self.status.config(state="normal")
            if clear:
                self.status.delete("1.0", "end")
            self.status.insert("end", msg + "\n")
            self.status.see("end")
            self.status.config(state="disabled")
        self.root.after(0, _do)

    def set_busy(self, b):
        self.busy = b

        def _do():
            self.run_btn.config(state="disabled" if b else "normal")
            if b:
                self.bar.start(12)
            else:
                self.bar.stop()
        self.root.after(0, _do)

    # pickers
    def browse_audio(self):
        p = filedialog.askopenfilename(title="Select audio", filetypes=[
            ("Audio", "*.wav *.flac *.ogg *.aiff *.aif"), ("All files", "*.*")])
        if p:
            self.audio_var.set(p)
            if not self.save_var.get():
                self.save_var.set(os.path.splitext(p)[0] + ".txt")

    def browse_save(self):
        p = filedialog.asksaveasfilename(title="Save transcript", defaultextension=".txt",
                                         filetypes=[("Text file", "*.txt")])
        if p:
            self.save_var.set(p)

    # recording
    def toggle_record(self):
        if not self.recording:
            try:
                import sounddevice as sd
                self.frames = []
                self.stream = sd.InputStream(samplerate=SR, channels=1, dtype="float32",
                                             callback=lambda d, n, t, s: self.frames.append(d.copy()))
                self.stream.start()
            except Exception as e:
                messagebox.showerror("Microphone error", str(e))
                return
            self.recording = True
            self.rec_btn.config(text="\u25a0  Stop", style="RecOn.TButton")
            self.log("Recording... press Stop when done.", clear=True)
        else:
            self.stream.stop()
            self.stream.close()
            self.recording = False
            self.rec_btn.config(text="\u25cf  Record", style="Rec.TButton")
            if not self.frames:
                self.log("Nothing recorded.")
                return
            import numpy as np
            a = np.concatenate(self.frames).reshape(-1)
            d = os.path.join(os.path.expanduser("~"), "Documents", "WajeehaTranscribe")
            os.makedirs(d, exist_ok=True)
            p = os.path.join(d, time.strftime("recording_%Y%m%d_%H%M%S.wav"))
            write_wav(p, a)
            self.audio_var.set(p)
            if not self.save_var.get():
                self.save_var.set(p[:-4] + ".txt")
            self.log(f"Recorded {len(a)/SR:.1f} s. Saved to {p}\nPress Run to transcribe.")

    # setup + transcription
    def prep_worker(self):
        try:
            ok = prepare(APP_DIR, self.log)
            self.log("Ready." if ok else "Setup incomplete. Check your internet and restart the app.")
        except Exception as e:
            self.log(f"Setup failed: {e}")
        finally:
            self.set_busy(False)

    def run(self):
        if self.busy:
            return
        if self.recording:
            messagebox.showinfo("Recording", "Press Stop first.")
            return
        audio, out = self.audio_var.get().strip(), self.save_var.get().strip()
        if not audio or not os.path.isfile(audio):
            messagebox.showwarning("Audio file", "Choose or record an audio file first.")
            return
        if not out:
            messagebox.showwarning("Save path", "Choose where to save the transcript.")
            return
        self.set_busy(True)
        self.log("Starting...", clear=True)
        threading.Thread(target=self.worker, args=(audio, out), daemon=True).start()

    def worker(self, audio, out):
        try:
            setup_env(APP_DIR)
            self.log("Transcribing with Phonon-2 (the first run loads the engine, 10-40 s)...")
            t0 = time.time()
            text = run_fermion(["transcribe", MODEL, audio])
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(text + "\n")
            preview = text if len(text) < 400 else text[:400] + "..."
            self.log(f"Done in {time.time()-t0:.1f} s. Saved to {out}\n\n"
                     f"{preview if text else '(No speech detected)'}")
        except Exception as e:
            self.log(f"FAILED: {e}")
        finally:
            self.set_busy(False)


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    if len(sys.argv) >= 3 and sys.argv[1] == "--prepare":      # used by build.bat
        sys.exit(0 if prepare(sys.argv[2]) else 1)
    hide_console_if_alone()
    root = tk.Tk()
    App(root)
    root.mainloop()
