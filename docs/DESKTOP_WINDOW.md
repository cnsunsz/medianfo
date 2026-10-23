# 桌面窗（嵌入式 UI）

MediaNfo 在本机默认以**桌面应用**方式使用：本地 Python 服务提供 HTTP API 与静态前端，主界面在嵌入式 WebView 中打开，而不是调用系统浏览器。

## 启动路径

1. 入口：`medianfo-tray`（`src/medianfo/error_reporting.py:tray_main` → `src/medianfo/tray.py:main`）
2. 拉起本地 `medianfo serve`（或独立包内同名服务）
3. 服务 `healthz` 就绪后，`SetupGate.open()` → `desktop_window.open_url()` 打开嵌入式窗
4. 托盘可保留；菜单「打开主窗口」走 WebView，「在浏览器中打开」走系统浏览器（局域网/调试）

关键文件：

| 角色 | 文件 |
|------|------|
| 托盘与启动编排 | `src/medianfo/tray.py` |
| 嵌入式窗口 | `src/medianfo/desktop_window.py`（pywebview；Windows 优先 Edge WebView2） |
| 设置/数据目录 | `src/medianfo/settings_file.py`、`src/medianfo/distribution.py` |
| Windows 安装约定 | `src/medianfo/desktop_installer.py`、`scripts/installer/medianfo.iss` |
| 打包 | `scripts/build_windows.ps1`、`scripts/package_windows_release.py` |

## 行为开关

| 方式 | 效果 |
|------|------|
| 默认 | 启动后打开嵌入式主窗口 |
| `--silent` | 仅托盘，不弹窗 |
| `--show` | 与 `--silent` 合用时仍强制打开主窗口 |
| `MEDIANFO_UI=browser`（兼容 `PEACH_UI=browser`） | 全部改走系统浏览器 |
| 托盘「在浏览器中打开」 | 单次用系统浏览器 |

## Windows 包名称

- 可执行文件：`MediaNfo.exe`
- 安装包：`MediaNfo-<版本>-windows-x64-setup.exe`（及 lite 变体）
- 免安装 ZIP：内含 `MediaNfo.exe`
- 默认安装目录：`%LOCALAPPDATA%\\Programs\\MediaNfo`
- 数据目录：`%LOCALAPPDATA%\\MediaNfo\\medianfo-data`

本仓库 CI/脚本负责产出上述名称；在非 Windows 环境无法本地验证 WebView2 与 Inno Setup，需 Windows runner 或真机安装验证。
