"""独立测试包的资源标记与用户数据目录。"""
from __future__ import annotations

import sys
from pathlib import Path


def standalone() -> bool:
    return bool(getattr(sys, "frozen", False) and
                (Path(getattr(sys, "_MEIPASS", "")) / "standalone.txt").is_file())


def user_data_root(environ: dict[str, str]) -> Path:
    """本机默认数据目录：`%LOCALAPPDATA%\\MediaNfo\\medianfo-data`（Windows）
    或 `~/Library/Application Support/MediaNfo/medianfo-data`（macOS）。

    若新目录尚不存在而旧版 Peach 目录存在，短期沿用旧路径，便于 fork 迁移。
    """
    if sys.platform == "win32":
        base = Path(environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    else:
        base = Path.home() / "Library" / "Application Support"
    modern = base / "MediaNfo" / "medianfo-data"
    if modern.is_dir():
        return modern
    legacy = base / "Peach" / "peach-data"
    if legacy.is_dir():
        return legacy
    return modern
