<p align="center">
  <img src="resources/medianfo-logo.png" alt="MediaNfo" width="96">
</p>

<h1 align="center">MediaNfo</h1>

<p align="center">给自己用的私人影片馆藏：本地硬盘、网盘和关注的创作者，放在一个地方看。<br>
<strong>桌面优先</strong>：本机嵌入式窗口打开主界面，默认不再用系统浏览器当网页端。</p>

<p align="center">
  <a href="https://github.com/cnsunsz/medianfo/releases">下载安装包</a> ·
  <a href="https://github.com/cnsunsz/medianfo/issues">问题反馈</a> ·
  <a href="#文档">文档</a> ·
  <a href="README.en.md">English</a>
</p>

<p align="center">
  <a href="https://github.com/cnsunsz/medianfo/releases"><img src="https://img.shields.io/github/v/release/cnsunsz/medianfo?include_prereleases&amp;filter=v*&amp;sort=semver&amp;display_name=tag" alt="release"></a>
  <a href="https://github.com/cnsunsz/medianfo/actions/workflows/test.yml"><img src="https://img.shields.io/github/actions/workflow/status/cnsunsz/medianfo/test.yml?branch=master&amp;label=tests&amp;logo=githubactions&amp;logoColor=white" alt="CI 状态"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-AGPL--3.0--or--later-blue?logo=gnu&amp;logoColor=white" alt="license"></a>
  <a href="docs/TESTING_DESKTOP.md"><img src="https://img.shields.io/badge/Windows-x64-0078D4" alt="Windows x64"></a>
  <img src="https://img.shields.io/badge/18%2B-adult%20content-critical" alt="18+ 成人内容">
</p>

> **18+** 仅供成年人管理自己的成人内容馆藏。仓库不含媒体或站点数据；连接外部站点需有相应账号和访问权。
>
> 本仓库由 [peach-mitao/peach](https://github.com/peach-mitao/peach) fork，产品名改为 **MediaNfo**，并改为桌面窗口优先体验。许可证仍为 AGPL-3.0-or-later。

## 能做什么

- **桌面主窗口**：托盘拉起本地服务后，在嵌入式 WebView（Windows 上优先 Edge WebView2）中打开界面；可用托盘菜单「在浏览器中打开」或环境变量 `MEDIANFO_UI=browser` 退回系统浏览器。局域网远程访问仍可作为可选项保留。
- **本地、网盘一起看**：硬盘与已挂载的 115、PikPak、OneDrive 等网盘汇成一个馆藏。
- **播放墙挑片**：拖动全屏封面墙，点开原位播放；同一番号的不同版本与分卷集中切换。
- **接手已有收藏**：直接读取 NFO 和海报，缺少的标题、女优、厂牌与封面可从多个来源补齐，保留手动修改。
- **跨站关注 / 云下载 / 口味**：能力与上游 Peach 同源，见下文文档链接。

观看记录、收藏和设置保存在本机。扫描不动原文件；手动整理先预览，可撤回上一批。

## 下载与使用

### Windows（桌面 exe）

1. 从 [Releases](https://github.com/cnsunsz/medianfo/releases) 下载完整安装包 `MediaNfo-<版本>-windows-x64-setup.exe`，双击安装（默认装到 `%LOCALAPPDATA%\\Programs\\MediaNfo`，无需管理员）；或下载免安装 ZIP，解压后运行 `MediaNfo.exe`。
2. 启动后托盘出现，**本机主窗口**打开首次设置页；选择媒体目录和访问范围。
3. 开始扫描，随后在桌面窗口里浏览和播放。需要时可用托盘「在浏览器中打开」做局域网调试。

完整安装包携带媒体工具，可离线安装；轻量安装包体积更小，安装时按需下载工具。

测试版尚未签名。若 Windows 提示「已保护你的电脑」，确认来自本项目的 Release，再点「更多信息 → 仍要运行」。安装、更新和故障排查见 [Windows 使用说明](docs/TESTING_DESKTOP.md)。

### 从源码运行

需要 Git、uv 和 Python 3.14+：

```bash
git clone https://github.com/cnsunsz/medianfo.git
cd medianfo
uv sync
uv run medianfo-tray          # 托盘 + 本地服务 + 嵌入式主窗口
# 或仅起 HTTP 服务（无桌面窗）：
uv run medianfo serve --host 127.0.0.1 --port 8900
```

仅托盘、不弹窗：`uv run medianfo-tray --silent`。强制系统浏览器：`MEDIANFO_UI=browser uv run medianfo-tray`。

数据目录默认：

- Windows：`%LOCALAPPDATA%\\MediaNfo\\medianfo-data`
- macOS：`~/Library/Application Support/MediaNfo/medianfo-data`
- 开发树旁：`../medianfo-data`（或设置 `MEDIANFO_DATA_ROOT`；短期仍兼容 `PEACH_DATA_ROOT`）

更多步骤见[源码运行](docs/OPERATIONS.md#从源码运行windowsmacos)与 [桌面窗说明](docs/DESKTOP_WINDOW.md)。

### Docker（VPS / NAS）

部署步骤见 [Docker 部署](docs/DOCKER.md)。容器场景仍是网页 UI；桌面窗是本机 Windows/macOS 安装的默认体验。

## 常见问题

- **会改我的文件吗？** 扫描、补资料不碰原文件。手动整理会改名或移动；清空回收站会删除文件，均需确认。
- **手机上怎么看？** 首次设置时允许同一局域网的设备访问，手机连同一网络，打开设置页给出的地址，并设置访问密码。
- **数据存在哪？** 本机的 `medianfo-data` 文件夹；Windows 版默认位于 `%LOCALAPPDATA%\\MediaNfo\\medianfo-data`。
- **和 Peach 什么关系？** 代码 fork 自上游 Peach；品牌、包名、安装器与默认 UI 已改为 MediaNfo 桌面优先。

## 问题反馈

先查看[用户反馈](https://github.com/cnsunsz/medianfo/issues)，或[提交问题](https://github.com/cnsunsz/medianfo/issues/new/choose)。安全问题按[安全政策](SECURITY.md)私下报告。

## 文档

- [桌面窗 / 嵌入式 UI](docs/DESKTOP_WINDOW.md)
- [Windows 桌面测试](docs/TESTING_DESKTOP.md)
- [运维与源码运行](docs/OPERATIONS.md)
- [Docker](docs/DOCKER.md)
- [架构](docs/ARCHITECTURE.md)

## 许可证

AGPL-3.0-or-later。见 [LICENSE](LICENSE)。
