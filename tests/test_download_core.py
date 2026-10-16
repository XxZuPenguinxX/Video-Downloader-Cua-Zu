import unittest
from pathlib import Path
from unittest.mock import patch

from download_core import (
    DownloadCancelled,
    QUALITY_LIMITS,
    format_selector,
    make_download_options,
    validate_video_url,
)


class ValidateVideoUrlTests(unittest.TestCase):
    def test_trims_valid_http_url(self):
        self.assertEqual(
            validate_video_url("  https://example.com/watch?v=123  "),
            "https://example.com/watch?v=123",
        )

    def test_rejects_non_http_schemes_and_missing_hosts(self):
        for value in ("file:///tmp/video.mp4", "javascript:alert(1)", "https:///video"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_video_url(value)

    def test_rejects_malformed_urls(self):
        with self.assertRaises(ValueError):
            validate_video_url("https://[::1")


class FormatSelectorTests(unittest.TestCase):
    def test_uses_merged_formats_only_when_ffmpeg_is_available(self):
        self.assertEqual(
            format_selector("720p", True),
            "bestvideo[height<=720]+bestaudio/best[height<=720]",
        )
        self.assertEqual(format_selector("720p", False), "best[height<=720]")

    def test_best_quality_selector(self):
        self.assertEqual(format_selector("Tốt nhất", True), "bestvideo+bestaudio/best")
        self.assertEqual(format_selector("Tốt nhất", False), "best")

    def test_rejects_unknown_quality(self):
        with self.assertRaises(ValueError):
            format_selector("4K", True)

    def test_quality_options_include_only_supported_choices(self):
        self.assertEqual(tuple(QUALITY_LIMITS), ("Tốt nhất", "1080p", "720p", "480p", "360p"))

    def test_options_disable_playlist_downloads_and_allow_cancel(self):
        with patch("download_core.shutil.which", return_value=None):
            options = make_download_options(
                Path("downloads"), "720p", lambda _data: None, lambda: True
            )

        self.assertTrue(options["noplaylist"])
        with self.assertRaises(DownloadCancelled):
            options["progress_hooks"][0]({"status": "downloading"})


if __name__ == "__main__":
    unittest.main()
