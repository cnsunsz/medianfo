"""桌面窗走独立 UI 进程；默认绝不回退系统浏览器。"""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from medianfo import desktop_window, distribution, settings_file


class DesktopWindowTests(unittest.TestCase):
    def setUp(self):
        desktop_window._ui_process = None
        desktop_window._ui_url = None

    def test_browser_allowed_requires_explicit_env(self):
        self.assertFalse(desktop_window.browser_allowed({}))
        self.assertFalse(desktop_window.browser_allowed({"MEDIANFO_ALLOW_BROWSER": "0"}))
        self.assertTrue(desktop_window.browser_allowed({"MEDIANFO_ALLOW_BROWSER": "1"}))

    def test_open_url_never_calls_webbrowser(self):
        fake = MagicMock()
        fake.poll.return_value = None
        with patch("medianfo.desktop_window.webbrowser.open") as opened, patch(
            "medianfo.desktop_window._spawn_ui_process", return_value=fake,
        ) as spawn, patch("medianfo.desktop_window.time.sleep"):
            self.assertTrue(desktop_window.open_url("http://127.0.0.1:8900/"))
            spawn.assert_called_once()
            opened.assert_not_called()

    def test_open_url_failure_does_not_fallback_to_browser(self):
        with patch("medianfo.desktop_window.webbrowser.open") as opened, patch(
            "medianfo.desktop_window._spawn_ui_process", side_effect=OSError("boom"),
        ), patch("medianfo.desktop_window._report_ui_failure") as report:
            self.assertFalse(desktop_window.open_url("http://127.0.0.1:8900/"))
            opened.assert_not_called()
            report.assert_called_once()

    def test_open_url_rejects_immediate_exit_without_browser(self):
        fake = MagicMock()
        fake.poll.return_value = 1
        fake.returncode = 1
        with patch("medianfo.desktop_window.webbrowser.open") as opened, patch(
            "medianfo.desktop_window._spawn_ui_process", return_value=fake,
        ), patch("medianfo.desktop_window.time.sleep"), patch(
            "medianfo.desktop_window._report_ui_failure",
        ):
            self.assertFalse(desktop_window.open_url("http://127.0.0.1:8900/"))
            opened.assert_not_called()

    def test_open_url_reuses_alive_process_for_same_url(self):
        alive = MagicMock()
        alive.poll.return_value = None
        desktop_window._ui_process = alive
        desktop_window._ui_url = "http://127.0.0.1:8900/"
        with patch("medianfo.desktop_window._spawn_ui_process") as spawn:
            self.assertTrue(desktop_window.open_url("http://127.0.0.1:8900/"))
            spawn.assert_not_called()

    def test_ui_launch_command_frozen_uses_exe_subcommand(self):
        with patch.object(desktop_window.sys, "frozen", True, create=True), patch.object(
            desktop_window.sys, "executable", r"C:\App\MediaNfo.exe",
        ):
            cmd = desktop_window.ui_launch_command(
                "http://127.0.0.1:8900/", title="MediaNfo")
        self.assertEqual(
            cmd,
            [r"C:\App\MediaNfo.exe", "ui", "--url", "http://127.0.0.1:8900/",
             "--title", "MediaNfo"],
        )

    def test_ui_launch_command_module_fallback(self):
        with patch.object(desktop_window.sys, "frozen", False, create=True), patch.object(
            desktop_window.sys, "executable", "/opt/python/bin/python",
        ), patch.object(desktop_window.Path, "is_file", return_value=False):
            cmd = desktop_window.ui_launch_command("http://127.0.0.1:8900/")
        self.assertEqual(
            cmd[:4],
            ["/opt/python/bin/python", "-m", "medianfo", "ui"],
        )
        self.assertIn("--url", cmd)
        self.assertIn("http://127.0.0.1:8900/", cmd)

    def test_open_in_browser_blocked_by_default(self):
        with patch.dict(os.environ, {"MEDIANFO_ALLOW_BROWSER": ""}, clear=False), patch(
            "medianfo.desktop_window.webbrowser.open", return_value=True,
        ) as opened:
            self.assertFalse(
                desktop_window.open_in_browser("http://127.0.0.1:8900/configuration"))
            opened.assert_not_called()

    def test_open_in_browser_when_explicitly_allowed(self):
        with patch.dict(os.environ, {"MEDIANFO_ALLOW_BROWSER": "1"}, clear=False), patch(
            "medianfo.desktop_window.webbrowser.open", return_value=True,
        ) as opened:
            self.assertTrue(
                desktop_window.open_in_browser("http://127.0.0.1:8900/configuration"))
            opened.assert_called_once_with("http://127.0.0.1:8900/configuration")

    def test_medianfo_ui_browser_env_does_not_open_system_browser(self):
        """MEDIANFO_UI=browser 不再作为产品默认路径。"""
        fake = MagicMock()
        fake.poll.return_value = None
        with patch.dict(os.environ, {"MEDIANFO_UI": "browser"}, clear=False), patch(
            "medianfo.desktop_window.webbrowser.open",
        ) as opened, patch(
            "medianfo.desktop_window._spawn_ui_process", return_value=fake,
        ), patch("medianfo.desktop_window.time.sleep"):
            self.assertTrue(desktop_window.open_url("http://127.0.0.1:8900/"))
            opened.assert_not_called()


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
