# 桌面窗（嵌入式 UI）

MediaNfo 在本机默认以**桌面应用**方式使用：本地 Python 服务提供 HTTP API 与静态前端，主界面在**独立 UI 进程**的嵌入式 WebView 中打开，**默认绝不调用系统浏览器**。

## 启动路径

1. 入口：`medianfo-tray` / `MediaNfo.exe`（`src/medianfo/error_reporting.py:tray_main` → `src/medianfo/tray.py:main`）
2. 拉起本地 `medianfo serve`（或独立包内同名服务）
3. 服务 `healthz` 就绪后，`SetupGate.open()` → `desktop_window.open_url()`
4. `open_url()` 用 `subprocess.Popen` 拉起 **`MediaNfo.exe ui --url …`**（或 `medianfo ui`），在**该进程主线程**调用 `webview.start(gui='edgechromium')`（Windows）
5. 托盘可保留；菜单「打开主窗口」走桌面窗。系统浏览器入口默认隐藏

关键：托盘主线程是 `pystray.icon.run()`，不能在 daemon 线程里 `webview.start()`——Windows WebView2/COM 需要合适的消息循环，子线程启动常失败。失败时也**不会**回退 `webbrowser.open`。

关键文件：

| 角色 | 文件 |
|------|------|
| 托盘与启动编排 | `src/medianfo/tray.py` |
| 嵌入式窗口 / UI 进程 | `src/medianfo/desktop_window.py`（pywebview；Windows 优先 Edge WebView2） |
| CLI `ui` 子命令 | `src/medianfo/cli.py`（打包入口经 `scripts/build_app_entry.py` 分发） |
| 设置/数据目录 | `src/medianfo/settings_file.py`、`src/medianfo/distribution.py` |
| Windows 安装约定 | `src/medianfo/desktop_installer.py`、`scripts/installer/medianfo.iss` |
| 打包 | `scripts/build_windows.ps1`（`--collect-all pywebview` 及 pythonnet / clr_loader / bottle / proxy_tools）、`scripts/package_windows_release.py` |

## 行为开关

| 方式 | 效果 |
|------|------|
| 默认 | 启动后 spawn 独立桌面窗进程；无系统浏览器回退 |
| `--silent` | 仅托盘，不弹窗 |
| `--show` | 与 `--silent` 合用时仍强制打开主窗口 |
| `MEDIANFO_ALLOW_BROWSER=1` | 允许托盘「在浏览器中打开」与 `open_in_browser()`（调试/局域网）；未设置则拒绝 |
| `MEDIANFO_UI=browser` | **已不再作为产品路径**；`open_url` 仍只走桌面窗 |

## Windows 包名称

- 可执行文件：`MediaNfo.exe`
- 安装包：`MediaNfo-<版本>-windows-x64-setup.exe`（及 lite 变体）
- 免安装 ZIP：内含 `MediaNfo.exe`
- 默认安装目录：`%LOCALAPPDATA%\\Programs\\MediaNfo`
- 数据目录：`%LOCALAPPDATA%\\MediaNfo\\medianfo-data`

本仓库 CI/脚本负责产出上述名称；在非 Windows 环境无法本地验证 WebView2 与 Inno Setup，需 Windows runner 或真机安装验证。
