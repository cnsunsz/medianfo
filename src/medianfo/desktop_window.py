"""本机主界面：嵌入式 WebView，默认不再调用系统浏览器。

Windows 上 pywebview 走 Edge WebView2（edgechromium）；不可用时回退到 webbrowser。
可用环境变量 MEDIANFO_UI=browser（或兼容别名 PEACH_UI=browser）强制系统浏览器。
局域网远程访问仍由本地 HTTP 服务提供，本模块只负责本机桌面窗。
"""
from __future__ import annotations

import logging
import os
import threading
import webbrowser
from typing import Callable

LOGGER = logging.getLogger(__name__)

_lock = threading.Lock()
_window = None
_started = False


def _prefer_browser(environ: dict[str, str] | None = None) -> bool:
    env = environ if environ is not None else os.environ
    choice = (env.get("MEDIANFO_UI") or env.get("PEACH_UI") or "").strip().lower()
    return choice in {"browser", "system", "webbrowser"}


def open_url(url: str, *, title: str = "MediaNfo") -> bool:
    """打开或聚焦本机主窗口。成功走嵌入式窗返回 True；回退浏览器也返回 True。"""
    if _prefer_browser():
        return bool(webbrowser.open(url))
    try:
        return _open_webview(url, title=title)
    except Exception:
        LOGGER.warning("嵌入式窗口未能打开，回退系统浏览器", exc_info=True)
        return bool(webbrowser.open(url))


def open_in_browser(url: str) -> bool:
    """显式用系统浏览器打开（托盘「在浏览器中打开」/局域网调试）。"""
    return bool(webbrowser.open(url))


def _open_webview(url: str, *, title: str) -> bool:
    global _window, _started
    import webview

    with _lock:
        if _window is not None:
            try:
                _window.load_url(url)
                _window.show()
                _window.restore()
                return True
            except Exception:
                LOGGER.debug("复用已有窗口失败，将重建", exc_info=True)
                _window = None
                _started = False

        _window = webview.create_window(
            title,
            url,
            width=1280,
            height=840,
            min_size=(900, 600),
            text_select=True,
        )
        if not _started:
            _started = True
            thread = threading.Thread(
                target=_start_webview,
                name="MediaNfoDesktop",
                daemon=True,
            )
            thread.start()
        return True


def _start_webview() -> None:
    import webview

    # Windows：Edge Chromium / WebView2；其它平台由 pywebview 自选后端。
    gui = "edgechromium" if os.name == "nt" else None
    try:
        if gui:
            webview.start(gui=gui)
        else:
            webview.start()
    except Exception:
        LOGGER.exception("WebView 事件循环退出异常")
    finally:
        global _window, _started
        with _lock:
            _window = None
            _started = False


def bind_open(open_fn: Callable[[str], object] | None = None) -> Callable[[str], object]:
    """供 SetupGate 注入：默认桌面窗，可测时可替换。"""
    return open_fn or open_url
