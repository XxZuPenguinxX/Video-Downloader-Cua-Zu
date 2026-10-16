from __future__ import annotations

import os
import queue
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any

import yt_dlp

from app_settings import (
    default_download_dir,
    load_download_dir,
    load_language,
    save_download_dir,
    save_language,
)
from download_core import DownloadCancelled, download_video, get_ffmpeg_path

LANGUAGE_NAMES = {"en": "English", "vi": "Tiếng Việt"}


TRANSLATIONS = {
    "en": {
        "app_title": "Video Downloader Của Zu",
        "subtitle": "Save videos from supported websites, directly to your device.",
        "language_label": "Language",
        "url_label": "Video link",
        "paste": "Paste",
        "folder_label": "Save to",
        "choose_folder": "Choose folder",
        "quality_label": "Maximum resolution",
        "quality_best": "Best available",
        "download": "Download video",
        "cancel": "Cancel",
        "open_folder": "Open downloads folder",
        "disclaimer": "Only download content you have permission to save. This app does not bypass DRM or access restrictions.",
        "ready": "Paste a video link to get started.",
        "ffmpeg_ready": "FFmpeg: ready",
        "ffmpeg_missing": "FFmpeg not found · high-quality downloads may be limited",
        "clipboard_missing": "No link found in the clipboard.",
        "choose_folder_title": "Choose a download folder",
        "save_settings_error_title": "Could not save settings",
        "save_settings_error": "The download can continue, but the default folder could not be saved:\n{error}",
        "save_language_error": "The language changed for this session, but could not be saved:\n{error}",
        "url_required": "Enter a video link first.",
        "folder_required": "Choose a folder to save the video.",
        "connecting": "Connecting and checking the video…",
        "finishing": "Finishing the video file…",
        "download_error": "Could not download the video.",
        "download_error_title": "Download failed",
        "fallback_download_error": "The website refused the download.",
        "unexpected_error": "Unexpected error: {error}",
        "cancelled": "Download cancelled.",
        "downloading": "Downloading · {details}",
        "remaining": "remaining {duration}",
        "finished": "Downloaded: {title}",
        "done": "Done",
        "cancel_in_progress": "Cancelling…",
        "quit_title": "Download in progress",
        "quit_confirmation": "Exit the app and cancel the current download?",
        "open_folder_error_title": "Could not open folder",
        "bytes_status": "{downloaded} / {total}",
    },
    "vi": {
        "app_title": "Video Downloader Của Zu",
        "subtitle": "Lưu video từ các trang web được hỗ trợ, ngay trên máy của bạn.",
        "language_label": "Ngôn ngữ",
        "url_label": "Liên kết video",
        "paste": "Dán",
        "folder_label": "Thư mục lưu",
        "choose_folder": "Chọn thư mục",
        "quality_label": "Độ phân giải tối đa",
        "quality_best": "Tốt nhất",
        "download": "Tải video",
        "cancel": "Hủy",
        "open_folder": "Mở thư mục tải",
        "disclaimer": "Chỉ tải nội dung bạn có quyền lưu. Ứng dụng không vượt DRM hay giới hạn truy cập.",
        "ready": "Dán liên kết video để bắt đầu.",
        "ffmpeg_ready": "FFmpeg: đã sẵn sàng",
        "ffmpeg_missing": "Chưa có FFmpeg · chất lượng cao có thể bị giới hạn",
        "clipboard_missing": "Không tìm thấy liên kết trong bộ nhớ tạm.",
        "choose_folder_title": "Chọn thư mục lưu video",
        "save_settings_error_title": "Không thể lưu tùy chọn",
        "save_settings_error": "Ứng dụng vẫn có thể tải video, nhưng không lưu được thư mục mặc định:\n{error}",
        "save_language_error": "Ngôn ngữ đã đổi trong phiên này nhưng không thể lưu:\n{error}",
        "url_required": "Hãy dán liên kết video trước.",
        "folder_required": "Hãy chọn thư mục lưu video.",
        "connecting": "Đang kết nối và kiểm tra video…",
        "finishing": "Đang hoàn tất tệp video…",
        "download_error": "Không thể tải video.",
        "download_error_title": "Tải video thất bại",
        "fallback_download_error": "Trang web từ chối tải video.",
        "unexpected_error": "Lỗi không mong đợi: {error}",
        "cancelled": "Đã hủy tải xuống.",
        "downloading": "Đang tải · {details}",
        "remaining": "còn {duration}",
        "finished": "Đã tải xong: {title}",
        "done": "Xong",
        "cancel_in_progress": "Đang hủy…",
        "quit_title": "Đang tải video",
        "quit_confirmation": "Thoát ứng dụng và hủy lần tải đang chạy?",
        "open_folder_error_title": "Không thể mở thư mục",
        "bytes_status": "{downloaded} / {total}",
    },
}


class VideoDownloaderApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.language = tk.StringVar(value=load_language())
        self.language_choice = tk.StringVar(value=LANGUAGE_NAMES[self.language.get()])
        self.translations = TRANSLATIONS[self.language.get()]
        self.root.title(self._t("app_title"))
        self.root.geometry("820x590")
        self.root.minsize(700, 530)
        self.destination = tk.StringVar(value=str(load_download_dir()))
        self.quality = tk.StringVar(value=self._t("quality_best"))
        self.url = tk.StringVar()
        self.status = tk.StringVar(value=self._t("ready"))
        self.progress_value = tk.DoubleVar(value=0)
        self.events: queue.Queue[tuple[str, Any]] = queue.Queue()
        self.cancel_event = threading.Event()
        self.downloading = False
        self.last_download_dir: Path | None = None
        self.translatable_widgets: dict[str, ttk.Widget] = {}

        self._configure_styles()
        self._build_interface()
        self.root.after(100, self._process_events)
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        self.root.configure(bg="#f2f5f4")
        style.configure("App.TFrame", background="#f2f5f4")
        style.configure("Panel.TFrame", background="#ffffff")
        style.configure("Title.TLabel", background="#f2f5f4", foreground="#12211d",
                        font=("TkDefaultFont", 23, "bold"))
        style.configure("Body.TLabel", background="#f2f5f4", foreground="#52615c",
                        font=("TkDefaultFont", 10))
        style.configure("Section.TLabel", background="#ffffff", foreground="#172620",
                        font=("TkDefaultFont", 11, "bold"))
        style.configure("PanelText.TLabel", background="#ffffff", foreground="#52615c",
                        font=("TkDefaultFont", 9))
        style.configure("Action.TButton", background="#167a5a", foreground="#ffffff",
                        font=("TkDefaultFont", 10, "bold"), padding=(18, 11))
        style.map("Action.TButton", background=[("active", "#116548"), ("disabled", "#9ebbb0")])
        style.configure("Secondary.TButton", padding=(12, 8))
        style.configure("Horizontal.TProgressbar", troughcolor="#e7eeeb",
                        background="#167a5a", bordercolor="#e7eeeb", lightcolor="#167a5a",
                        darkcolor="#167a5a", thickness=10)

    def _t(self, key: str, **values: Any) -> str:
        return self.translations[key].format(**values)

    def _register_text(self, key: str, widget: ttk.Widget) -> None:
        self.translatable_widgets[key] = widget

    def change_language(self, _event: object = None) -> None:
        language = {name: code for code, name in LANGUAGE_NAMES.items()}[
            self.language_choice.get()
        ]
        self.language.set(language)
        self.translations = TRANSLATIONS[language]
        try:
            save_language(language)
        except OSError as exc:
            messagebox.showerror(
                self._t("save_settings_error_title"),
                self._t("save_language_error", error=exc),
                parent=self.root,
            )
        self.root.title(self._t("app_title"))
        for key, widget in self.translatable_widgets.items():
            widget.configure(text=self._t(key))
        quality_names = {
            "Tốt nhất": self._t("quality_best"),
            "1080p": "1080p",
            "720p": "720p",
            "480p": "480p",
            "360p": "360p",
        }
        self.quality_box.configure(values=tuple(quality_names.values()))
        current_quality = self._quality_key(self.quality.get())
        self.quality.set(quality_names[current_quality])
        self.language_choice.set(LANGUAGE_NAMES[language])
        if not self.downloading:
            self.status.set(self._t("ready"))
        self._update_ffmpeg_label()

    def _quality_key(self, label: str) -> str:
        if label in ("Tốt nhất", "Best available"):
            return "Tốt nhất"
        if label in ("1080p", "720p", "480p", "360p"):
            return label
        raise ValueError(f"Unsupported quality: {label}")

    def _build_interface(self) -> None:
        shell = ttk.Frame(self.root, style="App.TFrame", padding=(30, 26))
        shell.pack(fill="both", expand=True)
        shell.columnconfigure(0, weight=1)

        header = ttk.Frame(shell, style="App.TFrame")
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        title = ttk.Label(header, text=self._t("app_title"), style="Title.TLabel")
        title.grid(row=0, column=0, sticky="w")
        language_row = ttk.Frame(header, style="App.TFrame")
        language_row.grid(row=0, column=1, sticky="e")
        language_label = ttk.Label(
            language_row, text=self._t("language_label"), style="Body.TLabel"
        )
        language_label.pack(side="left", padx=(0, 8))
        self.language_box = ttk.Combobox(
            language_row,
            textvariable=self.language_choice,
            values=tuple(LANGUAGE_NAMES.values()),
            state="readonly",
            width=8,
        )
        self.language_box.pack(side="left")
        self.language_box.bind("<<ComboboxSelected>>", self.change_language)
        self._register_text("app_title", title)
        self._register_text("language_label", language_label)
        subtitle = ttk.Label(
            shell,
            text=self._t("subtitle"),
            style="Body.TLabel",
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(5, 22))
        self._register_text("subtitle", subtitle)

        panel = ttk.Frame(shell, style="Panel.TFrame", padding=22)
        panel.grid(row=2, column=0, sticky="ew")
        panel.columnconfigure(0, weight=1)

        url_label = ttk.Label(panel, text=self._t("url_label"), style="Section.TLabel")
        url_label.grid(row=0, column=0, sticky="w")
        self._register_text("url_label", url_label)
        url_row = ttk.Frame(panel, style="Panel.TFrame")
        url_row.grid(row=1, column=0, sticky="ew", pady=(9, 20))
        url_row.columnconfigure(0, weight=1)
        self.url_entry = ttk.Entry(url_row, textvariable=self.url, font=("TkDefaultFont", 11))
        self.url_entry.grid(row=0, column=0, sticky="ew", ipady=7)
        self.url_entry.bind("<Return>", lambda _event: self.start_download())
        self.paste_button = ttk.Button(
            url_row, text=self._t("paste"), style="Secondary.TButton", command=self.paste_url
        )
        self.paste_button.grid(row=0, column=1, padx=(9, 0))
        self._register_text("paste", self.paste_button)

        folder_label = ttk.Label(panel, text=self._t("folder_label"), style="Section.TLabel")
        folder_label.grid(row=2, column=0, sticky="w")
        self._register_text("folder_label", folder_label)
        folder_row = ttk.Frame(panel, style="Panel.TFrame")
        folder_row.grid(row=3, column=0, sticky="ew", pady=(9, 19))
        folder_row.columnconfigure(0, weight=1)
        self.folder_entry = ttk.Entry(folder_row, textvariable=self.destination)
        self.folder_entry.grid(row=0, column=0, sticky="ew", ipady=5)
        self.browse_button = ttk.Button(
            folder_row,
            text=self._t("choose_folder"),
            style="Secondary.TButton",
            command=self.choose_folder,
        )
        self.browse_button.grid(row=0, column=1, padx=(9, 0))
        self._register_text("choose_folder", self.browse_button)

        settings_row = ttk.Frame(panel, style="Panel.TFrame")
        settings_row.grid(row=4, column=0, sticky="ew", pady=(0, 19))
        quality_label = ttk.Label(
            settings_row, text=self._t("quality_label"), style="PanelText.TLabel"
        )
        quality_label.pack(side="left")
        self._register_text("quality_label", quality_label)
        quality_names = (
            self._t("quality_best"),
            "1080p",
            "720p",
            "480p",
            "360p",
        )
        self.quality_box = ttk.Combobox(
            settings_row,
            textvariable=self.quality,
            values=quality_names,
            state="readonly",
            width=14,
        )
        self.quality_box.pack(side="left", padx=(12, 0))
        self.ffmpeg_label = ttk.Label(settings_row, style="PanelText.TLabel")
        self.ffmpeg_label.pack(side="right")
        self._update_ffmpeg_label()

        actions = ttk.Frame(panel, style="Panel.TFrame")
        actions.grid(row=5, column=0, sticky="ew")
        self.download_button = ttk.Button(
            actions, text=self._t("download"), style="Action.TButton", command=self.start_download
        )
        self.download_button.pack(side="left")
        self.cancel_button = ttk.Button(
            actions, text=self._t("cancel"), style="Secondary.TButton", command=self.cancel_download,
            state="disabled"
        )
        self.cancel_button.pack(side="left", padx=(9, 0))
        self.open_folder_button = ttk.Button(
            actions, text=self._t("open_folder"), style="Secondary.TButton",
            command=self.open_download_folder, state="disabled"
        )
        self.open_folder_button.pack(side="right")
        self._register_text("download", self.download_button)
        self._register_text("cancel", self.cancel_button)
        self._register_text("open_folder", self.open_folder_button)

        progress_area = ttk.Frame(shell, style="App.TFrame", padding=(2, 24, 2, 0))
        progress_area.grid(row=3, column=0, sticky="ew")
        progress_area.columnconfigure(0, weight=1)
        status_row = ttk.Frame(progress_area, style="App.TFrame")
        status_row.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        status_row.columnconfigure(0, weight=1)
        self.status_label = ttk.Label(status_row, textvariable=self.status, style="Body.TLabel")
        self.status_label.grid(row=0, column=0, sticky="w")
        self.percent_label = ttk.Label(status_row, text="", style="Body.TLabel")
        self.percent_label.grid(row=0, column=1, sticky="e")
        self.progress = ttk.Progressbar(
            progress_area, variable=self.progress_value, maximum=100, mode="determinate"
        )
        self.progress.grid(row=1, column=0, sticky="ew")
        disclaimer = ttk.Label(
            shell,
            text=self._t("disclaimer"),
            style="Body.TLabel",
            wraplength=750,
        )
        disclaimer.grid(row=4, column=0, sticky="w", pady=(24, 0))
        self._register_text("disclaimer", disclaimer)
        self.url_entry.focus_set()

    def _update_ffmpeg_label(self) -> None:
        if get_ffmpeg_path():
            self.ffmpeg_label.configure(text=self._t("ffmpeg_ready"))
        else:
            self.ffmpeg_label.configure(text=self._t("ffmpeg_missing"))

    def paste_url(self) -> None:
        try:
            clipboard = self.root.clipboard_get()
        except tk.TclError:
            self.status.set(self._t("clipboard_missing"))
            return
        self.url.set(clipboard.strip())
        self.url_entry.focus_set()

    def choose_folder(self) -> None:
        selected = filedialog.askdirectory(
            title=self._t("choose_folder_title"),
            initialdir=self.destination.get() or str(default_download_dir()),
            mustexist=False,
        )
        if selected:
            self.destination.set(selected)
            self._persist_destination()

    def _persist_destination(self) -> None:
        value = self.destination.get().strip()
        if value:
            try:
                save_download_dir(Path(value).expanduser())
            except OSError as exc:
                messagebox.showerror(
                    self._t("save_settings_error_title"),
                    self._t("save_settings_error", error=exc),
                    parent=self.root,
                )

    def start_download(self) -> None:
        if self.downloading:
            return
        url = self.url.get().strip()
        folder = self.destination.get().strip()
        if not url:
            self.status.set(self._t("url_required"))
            self.url_entry.focus_set()
            return
        if not folder:
            self.status.set(self._t("folder_required"))
            return
        self.downloading = True
        self.cancel_event.clear()
        self.last_download_dir = None
        self.progress_value.set(0)
        self.percent_label.configure(text="")
        self.status.set(self._t("connecting"))
        self._set_busy(True)
        self._persist_destination()
        worker = threading.Thread(
            target=self._download_worker,
            args=(url, Path(folder).expanduser(), self._quality_key(self.quality.get())),
            name="video-downloader",
            daemon=True,
        )
        worker.start()

    def _download_worker(self, url: str, destination: Path, quality: str) -> None:
        def progress_hook(data: dict[str, Any]) -> None:
            if data.get("status") == "downloading":
                self.events.put(("progress", data.copy()))
            elif data.get("status") == "finished":
                self.events.put(("status", self._t("finishing")))

        try:
            result = download_video(
                url, destination, quality, progress_hook, self.cancel_event.is_set
            )
            title = result.get("title", "Video") if result else "Video"
            self.events.put(("success", (destination, title)))
        except DownloadCancelled:
            self.events.put(("cancelled", None))
        except yt_dlp.utils.DownloadError as exc:
            self.events.put(("error", str(exc).strip() or self._t("fallback_download_error")))
        except (OSError, ValueError) as exc:
            self.events.put(("error", str(exc)))
        except Exception as exc:
            self.events.put(("error", self._t("unexpected_error", error=exc)))

    def _process_events(self) -> None:
        try:
            while True:
                kind, payload = self.events.get_nowait()
                if kind == "progress":
                    self._show_progress(payload)
                elif kind == "status":
                    self.status.set(payload)
                elif kind == "success":
                    self._download_succeeded(payload)
                elif kind == "cancelled":
                    self.downloading = False
                    self.status.set(self._t("cancelled"))
                    self._set_busy(False)
                elif kind == "error":
                    self.downloading = False
                    self.status.set(self._t("download_error"))
                    self._set_busy(False)
                    messagebox.showerror(
                        self._t("download_error_title"), payload, parent=self.root
                    )
        except queue.Empty:
            pass
        if self.root.winfo_exists():
            self.root.after(100, self._process_events)

    def _show_progress(self, data: dict[str, Any]) -> None:
        downloaded = data.get("downloaded_bytes") or 0
        total = data.get("total_bytes") or data.get("total_bytes_estimate")
        speed = data.get("speed")
        eta = data.get("eta")
        if total:
            percentage = min(100.0, downloaded * 100 / total)
            self.progress_value.set(percentage)
            self.percent_label.configure(text=f"{percentage:.0f}%")
        else:
            self.percent_label.configure(text=self._format_bytes(downloaded))
        detail = self._format_bytes(downloaded)
        if total:
            detail = self._t(
                "bytes_status",
                downloaded=self._format_bytes(downloaded),
                total=self._format_bytes(total),
            )
        if speed:
            detail += f" · {self._format_bytes(speed)}/s"
        if eta is not None:
            detail += f" · {self._t('remaining', duration=self._format_duration(eta))}"
        self.status.set(self._t("downloading", details=detail))

    def _download_succeeded(self, result: tuple[Path, str]) -> None:
        folder, title = result
        self.last_download_dir = folder
        self.downloading = False
        self.progress_value.set(100)
        self.percent_label.configure(text=self._t("done"))
        self.status.set(self._t("finished", title=title))
        self._set_busy(False)
        self.open_folder_button.configure(state="normal")

    def _set_busy(self, busy: bool) -> None:
        self.download_button.configure(state="disabled" if busy else "normal")
        self.cancel_button.configure(state="normal" if busy else "disabled")
        self.paste_button.configure(state="disabled" if busy else "normal")
        self.browse_button.configure(state="disabled" if busy else "normal")
        self.quality_box.configure(state="disabled" if busy else "readonly")
        self.url_entry.configure(state="disabled" if busy else "normal")
        self.folder_entry.configure(state="disabled" if busy else "normal")

    def cancel_download(self) -> None:
        if self.downloading:
            self.cancel_event.set()
            self.cancel_button.configure(state="disabled")
            self.status.set(self._t("cancel_in_progress"))

    def open_download_folder(self) -> None:
        if self.last_download_dir is None:
            return
        try:
            if os.name == "nt":
                os.startfile(self.last_download_dir)  # type: ignore[attr-defined]
            else:
                subprocess.Popen(["xdg-open", str(self.last_download_dir)])
        except OSError as exc:
            messagebox.showerror(self._t("open_folder_error_title"), str(exc), parent=self.root)

    def _close(self) -> None:
        if self.downloading:
            if not messagebox.askyesno(
                self._t("quit_title"),
                self._t("quit_confirmation"),
                parent=self.root,
            ):
                return
            self.cancel_event.set()
        self.root.destroy()

    @staticmethod
    def _format_bytes(value: float) -> str:
        size = float(value)
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if size < 1024 or unit == "TB":
                return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
            size /= 1024
        return f"{size:.1f} TB"

    @staticmethod
    def _format_duration(seconds: float) -> str:
        remaining = max(0, int(seconds))
        minutes, seconds = divmod(remaining, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:d}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes:d}:{seconds:02d}"


def main() -> None:
    root = tk.Tk()
    VideoDownloaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
