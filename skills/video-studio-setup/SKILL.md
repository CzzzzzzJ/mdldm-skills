---
name: video-studio-setup
description: 给「用代码做视频」配好本机环境：检查并安装 Node、FFmpeg、Python、Git，装好 Lemo-Opuscar 风格库和它的渲染依赖，最后渲染一段 2 秒测试片确认能出片。当用户说「帮我配置做视频的环境」「装一下视频制作工具」「我想用 Claude / Agent 做视频但什么都没装」「ffmpeg 没装」时使用。只负责装环境，不负责做片。
---

# 代码做视频 · 本机环境配置

目标：让这台电脑上的 agent 能把「一句话」做成 mp4。做完后用户不需要懂任何命令。

用户多半不会编程。全程用大白话说话：每一步先说「我要做什么、为什么」，再做。不要让用户自己敲命令，除非需要输入系统密码。

## 要装的东西

| 工具 | 最低版本 | 它管什么 |
|---|---|---|
| Git | 任意 | 下载风格库 |
| Node.js | 20 | 运行渲染器，驱动无头浏览器逐帧截图 |
| FFmpeg | 7 | 把帧和声音压成 mp4（6.x 会把音频长度算错，不能用） |
| Python | 3.11（或装 uv） | 合成配乐和音效、配音、字幕 |
| Lemo-Opuscar | 最新 | 开源风格库（github.com/lemomo-ai/lemo-opuscar，MIT），含渲染工具和各风格说明 |

另外需要约 3 GB 空闲磁盘，和能访问 GitHub、npm、PyPI 的网络。

## 步骤

### 1. 体检

运行 `sh "<本 skill 目录>/scripts/doctor.sh"`（Windows 在 Git Bash 里运行；没有 Git Bash 就先看第 2 步装 Git）。它只检查，不改动任何东西，最后一行是 `MISSING=` 加缺少的项目。

把结果用一句话告诉用户，例如「你已经有 Node 和 Git，还缺 FFmpeg 和 Python」。

### 2. 装系统工具（先征得同意）

把要装的清单和大概占用告诉用户，得到明确同意后再装。只装缺的，已有且版本够的不要动、不要升级。

**macOS**（用 Homebrew）：

```sh
brew install node ffmpeg python@3.12 git
```

没有 Homebrew 时，先问用户是否同意安装它（需要输入开机密码），同意后按 brew.sh 首页的官方命令安装。

**Windows**（用系统自带的 winget，在 PowerShell 里）：

```powershell
winget install -e --id Git.Git
winget install -e --id OpenJS.NodeJS.LTS
winget install -e --id Gyan.FFmpeg
winget install -e --id Python.Python.3.12
```

装完要重开终端才认得到新命令。之后所有 `sh` 命令都在 Git Bash 里跑。

**Linux**（Debian / Ubuntu）：

```sh
sudo apt update && sudo apt install -y git python3 python3-venv
```

- Node 要 20 以上：发行版自带的不够新时，用 NodeSource 或 nvm 装 LTS 版。
- FFmpeg 要 7 以上：Ubuntu 24.04 自带的是 6.1，不能用，换成 johnvansickle.com/ffmpeg 的静态版，解压后把 `ffmpeg`、`ffprobe` 放进 `~/.local/bin`。

装完再跑一次 `doctor.sh`，确认 `MISSING=` 后面是空的。

### 3. 装风格库

用户用的是 Claude Code 时：

```sh
claude plugin marketplace add lemomo-ai/lemo-opuscar
claude plugin install lemo-opuscar@lemolab
```

装完需要重启 Claude Code 才能用 `/lemo-opuscar`。

其他 agent（Codex、Cursor 等）：

```sh
git clone --depth 1 https://github.com/lemomo-ai/lemo-opuscar.git ~/lemo-opuscar
```

然后把 `~/lemo-opuscar/plugin/skills/lemo-opuscar/` 复制到该 agent 的 skills 目录。

### 4. 装渲染依赖

```sh
sh ~/lemo-opuscar/plugin/skills/lemo-opuscar/scripts/setup.sh deps voice
```

（通过 Claude Code 插件安装的，`setup.sh` 在插件自己的目录里，库会被下载到 `~/lemo-opuscar`；用 `find ~/.claude/plugins -name setup.sh -path '*lemo-opuscar*'` 找到它。）

这一步会下载无头浏览器、Python 包和配音模型，共约 1 GB，要几分钟。开始前告诉用户大概要等多久。`voice` 是配音和旁白校验；用户明确说不需要旁白时可以去掉。

### 5. 出一段测试片

```sh
sh "<本 skill 目录>/scripts/selftest.sh"
```

它用风格库的渲染器把 `selftest/` 里的测试页渲染成 2 秒的 mp4，放在用户主目录的 `video-studio-selftest.mp4`。看到 `SELFTEST OK` 才算配好。

### 6. 交代结果

告诉用户：

- 装了哪些东西、各是什么版本、哪些原来就有
- 测试片在哪，请他点开看一眼（应该是一个从左滑到右的橙色圆点和「环境就绪」四个字）
- 接下来怎么开始：对 agent 说「用 Lemo-Opuscar 的某某风格，做一支 30 秒的片子，讲……」

## 下载失败时

国内网络常见。先确认是哪一步失败，再只对那一步换源，换之前告诉用户：

| 失败的步骤 | 做法 |
|---|---|
| `git clone` GitHub | 让用户打开代理后重试；不要换成来路不明的镜像仓库 |
| `npm install` | `npm config set registry https://registry.npmmirror.com` |
| 无头浏览器下载 | 设 `PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright` 后重跑第 4 步 |
| Python 包 | 设 `PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple`（用 uv 时是 `UV_DEFAULT_INDEX`） |
| 配音模型（Hugging Face） | 设 `HF_ENDPOINT=https://hf-mirror.com` |

## 不要做的事

- 不要在没征得同意时安装或升级系统软件，不要用 `sudo` 改全局配置。
- 不要卸载或覆盖用户已有的 Node、Python、FFmpeg；版本不够时装一个新的并排放，并说明。
- 不要把包装进系统 Python；风格库自己有 `.venv`。
- 某一步失败两次仍不行，停下来把原始报错和已经试过的做法告诉用户，不要换一堆办法硬试。
