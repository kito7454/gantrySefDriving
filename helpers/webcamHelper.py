#!/usr/bin/env python3
"""
Webcam recorder: Tkinter GUI + TCP control port.

GUI features
    * Start/Stop camera (live preview, toggleable independently of recording)
    * Start/Stop recording, with optional auto-stop timeout
    * Snapshot button

Remote control (default 127.0.0.1:9004, newline-terminated ASCII):
    START [seconds]   begin recording (opens the camera if needed)
    STOP              stop recording
    CAMERA ON|OFF     open/close the capture device
    SNAP [path]       save a still image
    STATUS            report current state
    PING              health check
    QUIT              close the application

    e.g.  printf 'START 10\n' | nc 127.0.0.1 9004

Requires: opencv-python (Pillow optional, used for nicer preview scaling).
"""

import argparse
import os
import queue
import socket
import threading
import time
from datetime import datetime

import cv2
import tkinter as tk
from tkinter import ttk

try:
    from PIL import Image, ImageTk
    _HAVE_PIL = True
except ImportError:  # fall back to Tk's built-in PPM decoder
    _HAVE_PIL = False


def unique_path(path):
    """Return `path`, or `name_2.ext`, `name_3.ext`... if it already exists."""
    if not os.path.exists(path):
        return path
    stem, ext = os.path.splitext(path)
    n = 2
    while os.path.exists(f"{stem}_{n}{ext}"):
        n += 1
    return f"{stem}_{n}{ext}"


class WebcamHelper:
    """Owns the capture device, a grab thread, and the video writer."""

    def __init__(self, output_path="C:\\Users\\v_zor\\OneDrive\\Desktop\\gantry videos\\output_video.avi", fallback_fps=10.0):
        self.output_path = output_path
        self.fallback_fps = fallback_fps

        self.cam = None
        self.camera_index = None
        self.writer = None
        self.current_file = None
        self.record_started_at = None
        self.timeout_seconds = None
        self.frames_written = 0

        self._frame_lock = threading.Lock()
        self._writer_lock = threading.Lock()
        self._latest_frame = None
        self._capture_thread = None
        self._running = threading.Event()
        self._recording = threading.Event()

        # Called from the capture thread -> must be thread-safe (we push to a queue).
        self.on_event = None

    # ---------------------------------------------------------------- events
    def _emit(self, kind, message):
        if self.on_event:
            try:
                self.on_event(kind, message)
            except Exception:
                pass

    # ---------------------------------------------------------------- device
    def is_open(self):
        return self.cam is not None and self.cam.isOpened()

    def is_recording(self):
        return self._recording.is_set()

    def open_webcam(self, camera_index=0):
        if self.is_open():
            if camera_index == self.camera_index:
                return
            self.close_webcam()

        cam = cv2.VideoCapture(camera_index)
        if not cam.isOpened():
            cam.release()
            raise RuntimeError(f"could not open camera {camera_index}")

        self.cam = cam
        self.camera_index = camera_index
        self._running.set()
        self._capture_thread = threading.Thread(
            target=self._capture_loop, name="capture", daemon=True)
        self._capture_thread.start()
        self._emit("camera", f"camera {camera_index} opened")

    def close_webcam(self):
        self.stop_recording(reason="camera closed")
        self._running.clear()
        thread, self._capture_thread = self._capture_thread, None
        if thread and thread.is_alive():
            thread.join(timeout=2.0)
        if self.cam is not None:
            self.cam.release()
            self.cam = None
        with self._frame_lock:
            self._latest_frame = None
        self._emit("camera", "camera closed")

    def get_frame(self):
        with self._frame_lock:
            return None if self._latest_frame is None else self._latest_frame.copy()

    # Kept for API compatibility with the original class.
    def snap(self):
        return self.get_frame()

    # ------------------------------------------------------------- recording
    def start_recording(self, path=None, timeout=None):
        if not self.is_open():
            raise RuntimeError("camera is not open")
        if self.is_recording():
            return self.current_file

        width = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if width <= 0 or height <= 0:
            frame = self.get_frame()
            if frame is None:
                raise RuntimeError("no frames available yet, try again in a moment")
            height, width = frame.shape[:2]

        fps = self.cam.get(cv2.CAP_PROP_FPS)
        if not (1.0 <= fps <= 120.0):
            fps = self.fallback_fps

        path = unique_path(path or self.output_path)
        ext = os.path.splitext(path)[1].lower()
        fourcc = cv2.VideoWriter_fourcc(*("mp4v" if ext in (".mp4", ".m4v") else "XVID"))
        writer = cv2.VideoWriter(path, fourcc, fps, (width, height))
        if not writer.isOpened():
            writer.release()
            raise RuntimeError(f"could not open video writer for {path}")

        with self._writer_lock:
            self.writer = writer
            self.current_file = path
            self.frames_written = 0
        self.timeout_seconds = timeout if timeout and timeout > 0 else None
        self.record_started_at = time.time()
        self._recording.set()
        self._emit("recording_started",
                   f"recording to {path} ({width}x{height} @ {fps:.1f} fps)")
        return path

    def stop_recording(self, reason="user"):
        if not self._recording.is_set():
            return None
        self._recording.clear()
        with self._writer_lock:
            writer, self.writer = self.writer, None
            path, frames = self.current_file, self.frames_written
            if writer is not None:
                writer.release()
        self._emit("recording_stopped",
                   f"stopped ({reason}): {frames} frames saved to {path}")
        return path

    def elapsed(self):
        if not self.is_recording() or self.record_started_at is None:
            return 0.0
        return time.time() - self.record_started_at

    def save_snapshot(self, path=None):
        frame = self.get_frame()
        if frame is None:
            raise RuntimeError("no frame available")
        path = path or datetime.now().strftime("snapshot_%Y%m%d_%H%M%S.png")
        if not cv2.imwrite(path, frame):
            raise RuntimeError(f"could not write {path}")
        self._emit("snapshot", f"snapshot saved to {path}")
        return path

    # ------------------------------------------------------------ grab thread
    def _capture_loop(self):
        misses = 0
        while self._running.is_set():
            ok, frame = self.cam.read()
            if not ok:
                misses += 1
                if misses > 50:
                    self._emit("error", "camera stopped delivering frames")
                    self._recording.clear()
                    break
                time.sleep(0.02)
                continue
            misses = 0

            with self._frame_lock:
                self._latest_frame = frame

            if self._recording.is_set():
                with self._writer_lock:
                    if self.writer is not None:
                        self.writer.write(frame)
                        self.frames_written += 1
                if self.timeout_seconds and self.elapsed() > self.timeout_seconds:
                    self.stop_recording(reason="timeout")


class ControlServer(threading.Thread):
    """Accepts TCP commands and hands them to the GUI thread for execution."""

    def __init__(self, command_queue, host="127.0.0.1", port=9004):
        super().__init__(name="control-server", daemon=True)
        self.command_queue = command_queue
        self.host, self.port = host, port
        self._stop = threading.Event()
        self._sock = None
        self.error = None

    def run(self):
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._sock.bind((self.host, self.port))
            self._sock.listen(5)
            self._sock.settimeout(0.5)
        except OSError as exc:
            self.error = str(exc)
            self.command_queue.put(("__error__", None))
            return

        while not self._stop.is_set():
            try:
                conn, _ = self._sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            threading.Thread(target=self._handle, args=(conn,), daemon=True).start()

        try:
            self._sock.close()
        except OSError:
            pass

    def shutdown(self):
        self._stop.set()

    def _handle(self, conn):
        with conn:
            conn.settimeout(5.0)
            try:
                data = conn.recv(4096).decode("utf-8", "replace")
            except OSError:
                return
            for line in data.splitlines():
                line = line.strip()
                if not line:
                    continue
                reply_box = queue.Queue(maxsize=1)
                self.command_queue.put((line, reply_box))
                try:
                    reply = reply_box.get(timeout=5.0)
                except queue.Empty:
                    reply = "ERR application not responding"
                try:
                    conn.sendall((reply + "\n").encode("utf-8"))
                except OSError:
                    return


class WebcamApp:
    PREVIEW_MS = 100     # ~10 fps preview refresh
    POLL_MS = 150        # queue polling interval

    def __init__(self, root, camera_index=0, port=9004, output="C:\\Users\\v_zor\\OneDrive\\Desktop\\gantry videos\\output_video.avi"):
        self.root = root
        self.root.title("Webcam Recorder")
        self.root.minsize(720, 620)

        self.command_queue = queue.Queue()
        self.event_queue = queue.Queue()

        self.helper = WebcamHelper(output_path=output)
        self.helper.on_event = lambda kind, msg: self.event_queue.put((kind, msg))

        self.camera_index = tk.IntVar(value=camera_index)
        self.timeout_var = tk.StringVar(value="0")
        self.filename_var = tk.StringVar(value=output)
        self.preview_var = tk.BooleanVar(value=True)

        self._photo = None  # keep a reference or Tk garbage-collects the image

        self._build_ui()

        self.server = ControlServer(self.command_queue, port=port)
        self.server.start()
        self.log(f"control port listening on 127.0.0.1:{port}")

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(self.PREVIEW_MS, self._update_preview)
        self.root.after(self.POLL_MS, self._poll_queues)

    # ------------------------------------------------------------------- UI
    def _build_ui(self):
        controls = ttk.Frame(self.root, padding=8)
        controls.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(controls, text="Camera").pack(side=tk.LEFT)
        ttk.Spinbox(controls, from_=0, to=9, width=3,
                    textvariable=self.camera_index).pack(side=tk.LEFT, padx=(4, 10))

        self.camera_btn = ttk.Button(controls, text="Start Camera",
                                     command=self.toggle_camera)
        self.camera_btn.pack(side=tk.LEFT)

        ttk.Checkbutton(controls, text="Show preview",
                        variable=self.preview_var).pack(side=tk.LEFT, padx=10)

        self.record_btn = ttk.Button(controls, text="Start Recording",
                                     command=self.toggle_recording)
        self.record_btn.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(controls, text="Snapshot",
                   command=self.take_snapshot).pack(side=tk.LEFT)

        options = ttk.Frame(self.root, padding=(8, 0, 8, 8))
        options.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(options, text="Auto-stop after (s, 0 = never)").pack(side=tk.LEFT)
        ttk.Entry(options, width=6,
                  textvariable=self.timeout_var).pack(side=tk.LEFT, padx=(4, 12))
        ttk.Label(options, text="Output file").pack(side=tk.LEFT)
        ttk.Entry(options, width=32,
                  textvariable=self.filename_var).pack(side=tk.LEFT, padx=4)

        self.video_label = tk.Label(self.root, bg="black", fg="#888",
                                    text="camera off", width=320, height=240)
        self.video_label.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8)

        self.status = ttk.Label(self.root, text="idle", anchor=tk.W, padding=(8, 4))
        self.status.pack(side=tk.TOP, fill=tk.X)

        log_frame = ttk.Frame(self.root, padding=(8, 0, 8, 8))
        log_frame.pack(side=tk.TOP, fill=tk.X)
        self.log_text = tk.Text(log_frame, height=6, state=tk.DISABLED, wrap=tk.WORD)
        scroll = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scroll.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def log(self, message):
        stamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{stamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    # -------------------------------------------------------------- actions
    def start_camera(self):
        if self.helper.is_open():
            return "camera already running"
        self.helper.open_webcam(self.camera_index.get())
        self.camera_btn.configure(text="Stop Camera")
        return "camera started"

    def stop_camera(self):
        if not self.helper.is_open():
            return "camera already stopped"
        self.helper.close_webcam()
        self.camera_btn.configure(text="Start Camera")
        self.record_btn.configure(text="Start Recording")
        self.video_label.configure(image="", text="camera off")
        self._photo = None
        return "camera stopped"

    def toggle_camera(self):
        try:
            self.log(self.stop_camera() if self.helper.is_open() else self.start_camera())
        except Exception as exc:
            self.log(f"error: {exc}")

    def start_recording(self, timeout=None):
        if self.helper.is_recording():
            return "already recording"
        if not self.helper.is_open():
            self.start_camera()
            time.sleep(0.3)  # let the first frames arrive
        if timeout is None:
            try:
                timeout = float(self.timeout_var.get() or 0)
            except ValueError:
                timeout = 0
        base = self.filename_var.get().strip() or self.helper.output_path
        path = self.helper.start_recording(stamped_path(base), timeout=timeout)
        self.record_btn.configure(text="Stop Recording")
        return f"recording to {path}"

    def stop_recording(self, reason="user"):
        if not self.helper.is_recording():
            return "not recording"
        path = self.helper.stop_recording(reason=reason)
        self.record_btn.configure(text="Start Recording")
        return f"saved {path}"

    def toggle_recording(self):
        try:
            if self.helper.is_recording():
                self.log(self.stop_recording())
            else:
                self.log(self.start_recording())
        except Exception as exc:
            self.log(f"error: {exc}")

    def take_snapshot(self, path=None):
        try:
            return self.helper.save_snapshot(path)
        except Exception as exc:
            self.log(f"error: {exc}")
            raise

    # ---------------------------------------------------------- remote input
    def _handle_command(self, line):
        parts = line.split()
        cmd, args = parts[0].upper(), parts[1:]
        try:
            if cmd == "PING":
                return "OK pong"
            if cmd in ("START", "RECORD"):
                timeout = float(args[0]) if args else None
                return "OK " + self.start_recording(timeout)
            if cmd == "STOP":
                return "OK " + self.stop_recording(reason="network")
            if cmd == "CAMERA":
                if not args:
                    return "ERR usage: CAMERA ON|OFF"
                if args[0].upper() == "ON":
                    return "OK " + self.start_camera()
                if args[0].upper() == "OFF":
                    return "OK " + self.stop_camera()
                return "ERR usage: CAMERA ON|OFF"
            if cmd == "SNAP":
                return "OK saved " + self.take_snapshot(args[0] if args else None)
            if cmd == "STATUS":
                return ("OK camera={} recording={} file={} elapsed={:.1f}".format(
                    "on" if self.helper.is_open() else "off",
                    "on" if self.helper.is_recording() else "off",
                    self.helper.current_file if self.helper.is_recording() else "-",
                    self.helper.elapsed()))
            if cmd in ("QUIT", "SHUTDOWN"):
                self.root.after(200, self.on_close)
                return "OK shutting down"
            return f"ERR unknown command '{cmd}'"
        except Exception as exc:
            return f"ERR {exc}"

    def _poll_queues(self):
        try:
            while True:
                kind, message = self.event_queue.get_nowait()
                self.log(message)
                if kind in ("recording_stopped", "error"):
                    self.record_btn.configure(text="Start Recording")
        except queue.Empty:
            pass

        try:
            while True:
                line, reply_box = self.command_queue.get_nowait()
                if line == "__error__":
                    self.log(f"control port unavailable: {self.server.error}")
                    continue
                reply = self._handle_command(line)
                self.log(f"remote '{line}' -> {reply}")
                if reply_box is not None:
                    try:
                        reply_box.put_nowait(reply)
                    except queue.Full:
                        pass
        except queue.Empty:
            pass

        self.root.after(self.POLL_MS, self._poll_queues)

    # -------------------------------------------------------------- preview
    def _to_photo(self, frame_bgr):
        if _HAVE_PIL:
            rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            return ImageTk.PhotoImage(Image.fromarray(rgb), master=self.root)
        ok, buf = cv2.imencode(".ppm", frame_bgr)
        if not ok:
            return None
        return tk.PhotoImage(data=buf.tobytes(), master=self.root)

    def _update_preview(self):
        try:
            if self.helper.is_open() and self.preview_var.get():
                frame = self.helper.get_frame()
                if frame is not None:
                    box_w = max(self.video_label.winfo_width(), 160)
                    box_h = max(self.video_label.winfo_height(), 120)
                    h, w = frame.shape[:2]
                    scale = min(box_w / w, box_h / h)
                    if scale < 1.0 or scale > 1.05:
                        frame = cv2.resize(frame, (max(int(w * scale), 1),
                                                   max(int(h * scale), 1)),
                                           interpolation=cv2.INTER_AREA)
                    if self.helper.is_recording():
                        cv2.circle(frame, (18, 18), 8, (0, 0, 255), -1)
                    photo = self._to_photo(frame)
                    if photo is not None:
                        self._photo = photo
                        self.video_label.configure(image=photo, text="")
            elif self.helper.is_open():
                self.video_label.configure(image="", text="preview hidden")
                self._photo = None

            if self.helper.is_recording():
                limit = self.helper.timeout_seconds
                tail = f" / {limit:.0f}s" if limit else ""
                self.status.configure(
                    text=f"RECORDING {self.helper.elapsed():.1f}s{tail}  "
                         f"->  {self.helper.current_file}")
            elif self.helper.is_open():
                self.status.configure(text=f"camera {self.helper.camera_index} live")
            else:
                self.status.configure(text="idle")
        except Exception as exc:
            self.log(f"preview error: {exc}")

        self.root.after(self.PREVIEW_MS, self._update_preview)

    # ---------------------------------------------------------------- close
    def on_close(self):
        self.server.shutdown()
        self.helper.close_webcam()
        self.root.destroy()


def main():
    parser = argparse.ArgumentParser(description="Tkinter webcam recorder")
    parser.add_argument("--camera", type=int, default=0, help="camera index")
    parser.add_argument("--port", type=int, default=9004, help="control port")
    parser.add_argument("--output", default="C:\\Users\\v_zor\\OneDrive\\Desktop\\gantry videos\\output_video.avi", help="output file")
    args = parser.parse_args()

    root = tk.Tk()
    WebcamApp(root, camera_index=args.camera, port=args.port, output=args.output)
    root.mainloop()

def stamped_path(path):
    """Insert a YYYYMMDD_HHMMSS timestamp before the file extension."""
    stem, ext = os.path.splitext(path)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{stem}_{ts}{ext}"

if __name__ == "__main__":
    main()