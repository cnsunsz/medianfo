"""本机主界面：独立 UI 进程里的嵌入式 WebView，默认绝不打开系统浏览器。

托盘主线程跑 pystray，不能在子线程里 webview.start()（Windows WebView2/COM
需要合适的消息循环）。因此 open_url() 用子进程拉起 `medianfo ui` /
`MediaNfo.exe ui`，由该进程主线程调用 webview.start(gui='edgechromium')。

本地 FastAPI/静态前端仍由托盘拉起的 serve 提供；本模块只负责桌面窗。
系统浏览器仅在显式设置 MEDIANFO_ALLOW_BROWSER=1 时，经 open_in_browser() 可用。
"""
from __future__ import annotations

import logging
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse

LOGGER = logging.getLogger(__name__)

_lock = threading.Lock()
#: 最近一次拉起的 UI 子进程；仍存活则尽量复用，不重复 spawn。
_ui_process: subprocess.Popen | None = None
_ui_url: str | None = None


def browser_allowed(environ: dict[str, str] | None = None) -> bool:
    """系统浏览器入口是否放开（调试 / 局域网）。默认关闭。"""
    env = environ if environ is not None else os.environ
    return (env.get("MEDIANFO_ALLOW_BROWSER") or "").strip() == "1"


def ui_launch_command(url: str, *, title: str = "MediaNfo") -> list[str]:
    """构造打开桌面窗的命令行（供 open_url / 测试断言）。"""
    if getattr(sys, "frozen", False):
        return [sys.executable, "ui", "--url", url, "--title", title]
    script_name = "medianfo.exe" if os.name == "nt" else "medianfo"
    script = Path(sys.executable).with_name(script_name)
    if script.is_file():
        return [str(script), "ui", "--url", url, "--title", title]
    return [sys.executable, "-m", "medianfo", "ui", "--url", url, "--title", title]


def _report_ui_failure(message: str) -> None:
    LOGGER.error("%s", message)
    if os.name != "nt":
        return
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(None, message, "MediaNfo", 0x10)
    except Exception:
        LOGGER.debug("无法弹出错误对话框", exc_info=True)


def run_ui(url: str, *, title: str = "MediaNfo") -> int:
    """在本进程主线程打开嵌入式窗口，阻塞至窗口关闭。供 `ui` 子命令使用。"""
    try:
        import webview
    except Exception as exc:
        _report_ui_failure(f"无法加载嵌入式窗口组件（pywebview）：{exc}")
        return 1
    try:
        webview.create_window(
            title,
            url,
            width=1280,
            height=840,
            min_size=(900, 600),
            text_select=True,
        )
        gui = "edgechromium" if os.name == "nt" else None
        if gui:
            webview.start(gui=gui)
        else:
            webview.start()
        return 0
    except Exception as exc:
        LOGGER.exception("桌面窗启动失败")
        _report_ui_failure(f"桌面窗未能打开：{exc}")
        return 1


def _ui_process_alive() -> bool:
    return _ui_process is not None and _ui_process.poll() is None


def _ui_log_dir() -> Path | None:
    """数据目录下的 logs；拿不到就返回 None（仍可拉起 UI，只是不落盘）。"""
    try:
        from .config import LOG_DIR
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        return LOG_DIR
    except Exception:
        LOGGER.debug("无法解析桌面窗日志目录", exc_info=True)
        return None


def _wait_for_local_ready(url: str, *, timeout: float = 5.0) -> None:
    """加载前短暂确认本机 TCP /healthz 可通，减少服务尚未就绪时的白屏。失败不阻断打开。"""
    parsed = urlparse(url)
    host = parsed.hostname or "127.0.0.1"
    if host not in {"127.0.0.1", "localhost", "::1"}:
        return
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    health = f"{parsed.scheme or 'http'}://{host}:{port}/healthz"
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.3):
                pass
            try:
                with urllib.request.urlopen(health, timeout=0.5) as resp:
                    if getattr(resp, "status", 200) < 500:
                        return
            except urllib.error.HTTPError as exc:
                # 本机已在听端口；4xx 也说明 HTTP 栈起来了。
                if exc.code < 500:
                    return
        except OSError:
            pass
        time.sleep(0.15)


def _spawn_ui_process(url: str, *, title: str) -> subprocess.Popen:
    command = ui_launch_command(url, title=title)
    LOGGER.info("拉起桌面窗进程：%s", command)
    kwargs: dict = {
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "shell": False,
    }
    if os.name == "nt":
        # 不要 CREATE_NO_WINDOW：需要可见的 WebView2 窗口。
        # DETACHED + NEW_PROCESS_GROUP：托盘退出时尽量不连带拖死 UI。
        flags = 0
        if hasattr(subprocess, "DETACHED_PROCESS"):
            flags |= subprocess.DETACHED_PROCESS
        if hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):
            flags |= subprocess.CREATE_NEW_PROCESS_GROUP
        if flags:
            kwargs["creationflags"] = flags
        kwargs["close_fds"] = False
    else:
        kwargs["start_new_session"] = True
    # 日志句柄交给子进程后父进程这一份就关掉（与托盘拉起 serve 同口径）。
    log_dir = _ui_log_dir()
    if log_dir is not None:
        with (log_dir / "desktop-ui.out.log").open("ab") as stdout, \
                (log_dir / "desktop-ui.err.log").open("ab") as stderr:
            kwargs["stdout"] = stdout
            kwargs["stderr"] = stderr
            return subprocess.Popen(command, **kwargs)
    return subprocess.Popen(command, **kwargs)


def open_url(url: str, *, title: str = "MediaNfo") -> bool:
    """打开或复用本机主窗口。只走独立 UI 进程，绝不回退系统浏览器。"""
    global _ui_process, _ui_url
    with _lock:
        if _ui_process_alive() and _ui_url == url:
            LOGGER.debug("桌面窗进程仍在，复用：%s", url)
            return True
        if _ui_process_alive() and _ui_url != url:
            # 已有窗口但 URL 不同（例如配置页）：再开一个窗口进程。
            LOGGER.info("已有桌面窗，为不同 URL 再开一窗：%s", url)
        _wait_for_local_ready(url)
        try:
            process = _spawn_ui_process(url, title=title)
        except Exception:
            LOGGER.exception("拉起桌面窗进程失败")
            _report_ui_failure(
                "无法打开桌面主窗口。请确认本机已安装 WebView2 运行时，"
                "或查看日志后重试。"
            )
            return False
        # 子进程若因缺依赖立刻退出，尽快反馈，不要静默当成功。
        time.sleep(0.4)
        if process.poll() is not None:
            LOGGER.error("桌面窗进程立即退出，code=%s", process.returncode)
            _report_ui_failure(
                "桌面主窗口进程启动后立即退出。"
                "请确认 WebView2 可用，或设置 MEDIANFO_ALLOW_BROWSER=1 仅作调试。"
            )
            return False
        _ui_process = process
        _ui_url = url
        return True


def open_in_browser(url: str) -> bool:
    """显式用系统浏览器打开；默认拒绝，仅 MEDIANFO_ALLOW_BROWSER=1 时可用。"""
    if not browser_allowed():
        LOGGER.warning(
            "拒绝打开系统浏览器（需要 MEDIANFO_ALLOW_BROWSER=1）：%s", url,
        )
        return False
    return bool(webbrowser.open(url))


def bind_open(open_fn: Callable[[str], object] | None = None) -> Callable[[str], object]:
    """供 SetupGate 注入：默认桌面窗，可测时可替换。"""
    return open_fn or open_url
