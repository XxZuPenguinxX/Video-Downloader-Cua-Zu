from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlsplit

import yt_dlp
from yt_dlp.utils import DownloadCancelled


QUALITY_LIMITS = {
    "Tốt nhất": None,
    "1080p": 1080,
    "720p": 720,
    "480p": 480,
    "360p": 360,
}


def validate_video_url(url: str) -> str:
    value = url.strip()
    try:
        parsed = urlsplit(value)
    except ValueError as exc:
        raise ValueError("Đường dẫn không hợp lệ.") from exc
    if parsed.scheme.lower() not in ("http", "https") or not parsed.netloc:
        raise ValueError("Hãy nhập đường dẫn video bắt đầu bằng http:// hoặc https://.")
    return value


def format_selector(quality: str, ffmpeg_available: bool) -> str:
    if quality not in QUALITY_LIMITS:
        raise ValueError(f"Chất lượng không được hỗ trợ: {quality}")
    height = QUALITY_LIMITS[quality]
    if height is None:
        return "bestvideo+bestaudio/best" if ffmpeg_available else "best"
    if ffmpeg_available:
        return f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"
    return f"best[height<={height}]"


def make_download_options(
    destination: Path,
    quality: str,
    progress_hook: Callable[[dict[str, Any]], None],
    cancelled: Callable[[], bool],
) -> dict[str, Any]:
    has_ffmpeg = shutil.which("ffmpeg") is not None

    def observe_progress(data: dict[str, Any]) -> None:
        if cancelled():
            raise DownloadCancelled("Đã hủy tải xuống.")
        progress_hook(data)

    return {
        "format": format_selector(quality, has_ffmpeg),
        "outtmpl": str(destination / "%(title).180B [%(id)s].%(ext)s"),
        "noplaylist": True,
        "windowsfilenames": True,
        "progress_hooks": [observe_progress],
        "quiet": True,
        "no_warnings": True,
    }


def download_video(
    url: str,
    destination: Path,
    quality: str,
    progress_hook: Callable[[dict[str, Any]], None],
    cancelled: Callable[[], bool],
) -> dict[str, Any] | None:
    valid_url = validate_video_url(url)
    if cancelled():
        raise DownloadCancelled("Đã hủy tải xuống.")
    destination.mkdir(parents=True, exist_ok=True)
    options = make_download_options(destination, quality, progress_hook, cancelled)
    with yt_dlp.YoutubeDL(options) as downloader:
        return downloader.extract_info(valid_url, download=True)


def get_ffmpeg_path() -> str | None:
    return shutil.which("ffmpeg")


__all__ = [
    "DownloadCancelled",
    "QUALITY_LIMITS",
    "download_video",
    "get_ffmpeg_path",
    "validate_video_url",
]
