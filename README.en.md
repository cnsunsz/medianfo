<p align="center">
  <img src="resources/medianfo-logo.png" alt="MediaNfo" width="96">
</p>

<h1 align="center">MediaNfo</h1>

<p align="center">A private media library for your own disks, cloud mounts, and followed creators.<br>
<strong>Desktop-first</strong>: the main UI opens in an embedded window, not the system browser by default.</p>

<p align="center">
  <a href="https://github.com/cnsunsz/medianfo/releases">Releases</a> ·
  <a href="https://github.com/cnsunsz/medianfo/issues">Issues</a> ·
  <a href="README.md">中文</a>
</p>

Fork of [peach-mitao/peach](https://github.com/peach-mitao/peach), rebranded to **MediaNfo**, still AGPL-3.0-or-later.

### Windows

Download `MediaNfo-<version>-windows-x64-setup.exe` or the portable ZIP from [Releases](https://github.com/cnsunsz/medianfo/releases), run `MediaNfo.exe`. After the tray starts, the embedded desktop window opens for first-run setup. Optional: tray item “在浏览器中打开”, or `MEDIANFO_UI=browser`.

Default data dir: `%LOCALAPPDATA%\\MediaNfo\\medianfo-data`. Install dir: `%LOCALAPPDATA%\\Programs\\MediaNfo`.

### From source

```bash
uv sync
uv run medianfo-tray
```

See [docs/DESKTOP_WINDOW.md](docs/DESKTOP_WINDOW.md) and [docs/OPERATIONS.md](docs/OPERATIONS.md).
