import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app_settings


class LanguageSettingsTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.settings_file = Path(self.temporary_directory.name) / "settings.json"
        self.legacy_settings_file = (
            Path(self.temporary_directory.name) / "legacy" / "settings.json"
        )
        self.config_patch = patch("app_settings.config_file", return_value=self.settings_file)
        self.config_patch.start()
        self.addCleanup(self.config_patch.stop)
        self.legacy_patch = patch(
            "app_settings._legacy_config_file", return_value=self.legacy_settings_file
        )
        self.legacy_patch.start()
        self.addCleanup(self.legacy_patch.stop)
        self.addCleanup(self.temporary_directory.cleanup)

    def test_english_is_the_default_language(self):
        self.assertEqual(app_settings.load_language(), "en")

    def test_saves_language_and_preserves_download_folder(self):
        download_dir = Path(self.temporary_directory.name) / "Videos"
        app_settings.save_download_dir(download_dir)

        app_settings.save_language("vi")

        self.assertEqual(app_settings.load_language(), "vi")
        self.assertEqual(app_settings.load_download_dir(), download_dir)
        self.assertEqual(json.loads(self.settings_file.read_text(encoding="utf-8"))["language"], "vi")

    def test_saving_download_folder_preserves_language(self):
        app_settings.save_language("vi")
        download_dir = Path(self.temporary_directory.name) / "Videos"

        app_settings.save_download_dir(download_dir)

        self.assertEqual(app_settings.load_language(), "vi")

    def test_rejects_unsupported_language(self):
        with self.assertRaises(ValueError):
            app_settings.save_language("fr")

    def test_invalid_saved_language_falls_back_to_english(self):
        self.settings_file.write_text('{"language": "fr"}', encoding="utf-8")

        self.assertEqual(app_settings.load_language(), "en")

    def test_migrates_legacy_language_and_download_folder(self):
        self.legacy_settings_file.parent.mkdir(parents=True)
        old_folder = Path(self.temporary_directory.name) / "Old Videos"
        self.legacy_settings_file.write_text(
            json.dumps({"language": "vi", "download_dir": str(old_folder)}),
            encoding="utf-8",
        )

        self.assertEqual(app_settings.load_language(), "vi")
        self.assertEqual(app_settings.load_download_dir(), old_folder)
        app_settings.save_language("en")
        self.assertEqual(app_settings.load_download_dir(), old_folder)


if __name__ == "__main__":
    unittest.main()
