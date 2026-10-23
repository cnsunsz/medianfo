"""桌面窗默认走嵌入式 UI，可用环境变量退回系统浏览器。"""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from medianfo import desktop_window, distribution, settings_file


class DesktopWindowTests(unittest.TestCase):
    def test_prefer_browser_reads_new_and_legacy_env(self):
        self.assertTrue(desktop_window._prefer_browser({"MEDIANFO_UI": "browser"}))
        self.assertTrue(desktop_window._prefer_browser({"PEACH_UI": "webbrowser"}))
        self.assertFalse(desktop_window._prefer_browser({}))

    def test_open_url_honours_browser_mode(self):
        with patch.dict(os.environ, {"MEDIANFO_UI": "browser"}, clear=False), patch(
            "medianfo.desktop_window.webbrowser.open", return_value=True,
        ) as opened:
            self.assertTrue(desktop_window.open_url("http://127.0.0.1:8900/"))
            opened.assert_called_once_with("http://127.0.0.1:8900/")

    def test_open_in_browser_always_uses_system_browser(self):
        with patch("medianfo.desktop_window.webbrowser.open", return_value=True) as opened:
            self.assertTrue(desktop_window.open_in_browser("http://127.0.0.1:8900/configuration"))
            opened.assert_called_once()


class DataRootBrandTests(unittest.TestCase):
    def test_windows_default_uses_medianfo_brand(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(distribution.sys, "platform", "win32"):
            root = distribution.user_data_root({"LOCALAPPDATA": tmp})
            self.assertEqual(root, Path(tmp) / "MediaNfo" / "medianfo-data")

    def test_legacy_peach_dir_still_discovered(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(distribution.sys, "platform", "win32"):
            legacy = Path(tmp) / "Peach" / "peach-data"
            legacy.mkdir(parents=True)
            root = distribution.user_data_root({"LOCALAPPDATA": tmp})
            self.assertEqual(root, legacy)

    def test_peach_data_root_env_still_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "data"
            path.mkdir()
            root, found = settings_file._bootstrap_data_root(Path(tmp) / "proj",
                                                            {"PEACH_DATA_ROOT": str(path)})
            self.assertTrue(found)
            self.assertEqual(root, path)


if __name__ == "__main__":
    unittest.main()
