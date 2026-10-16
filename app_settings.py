from __future__ import annotations

import json
import os
import sys
from pathlib import Path

SUPPORTED_LANGUAGES = ("en", "vi")
APP_CONFIG_DIR = "VideoDownloaderCuaZu"
LEGACY_CONFIG_DIR = "TaiNhanh"


def config_file() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / APP_CONFIG_DIR / "settings.json"


def _legacy_config_file() -> Path:
    path = config_file()
    return path.parent.parent / LEGACY_CONFIG_DIR / path.name


def _read_settings() -> dict[str, object]:
    for path in (config_file(), _legacy_config_file()):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            continue
        except (json.JSONDecodeError, OSError):
            continue
        if isinstance(data, dict):
            return data
    return {}


def default_download_dir() -> Path:
    videos = Path.home() / "Videos"
    return (videos if videos.is_dir() else Path.home()) / "Video Downloader Cua Zu"


def load_download_dir() -> Path:
    value = _read_settings().get("download_dir")
    if isinstance(value, str) and value.strip():
        return Path(value).expanduser()
    return default_download_dir()


def load_language() -> str:
    language = _read_settings().get("language")
    if language in SUPPORTED_LANGUAGES:
        return language
    return "en"


def _save_settings(update: dict[str, str]) -> None:
    path = config_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    settings: dict[str, str] = {}
    existing = _read_settings()
    settings = {
        key: value
        for key, value in existing.items()
        if key in ("download_dir", "language") and isinstance(value, str)
    }
    settings.update(update)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    temporary.replace(path)


def save_download_dir(directory: Path) -> None:
    _save_settings({"download_dir": str(directory)})


def save_language(language: str) -> None:
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {language}")
    _save_settings({"language": language})
