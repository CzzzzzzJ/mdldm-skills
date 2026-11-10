# video-studio-setup · 做视频的本机环境，一句话装好

想用 Claude（或别的 Agent）写代码做视频，第一道坎是装环境：Node、FFmpeg、Python、Git，再加一个风格库和它的渲染依赖。光看名字就够劝退。

这个 Skill 把这一步交给 Agent：它先给电脑做体检，缺什么告诉你，你点头了才装，装完自己渲染一段 2 秒的测试片。测试片能播，这台电脑就能做视频了。

配套视频和全部样片 prompt：《Claude Fable 5.2 实测：用 Claude 做视频，一口气讲完》。

---

## 适合谁

- 想用 **Claude Code / Codex / Cursor** 这类 Agent 写代码做视频，但电脑上什么都没装的人
- 不想自己敲命令、查报错、换镜像的人
- 已经装过一部分、不确定还缺什么的人（它只补缺的，已有的不动）

它只负责装环境，不负责做片。做片用的是开源风格库 [Lemo-Opuscar](https://github.com/lemomo-ai/lemo-opuscar)（作者 Lemomo，MIT）。

---

## 先装

```bash
npx skills add CzzzzzzJ/mdldm-skills --skill video-studio-setup
```

或把本目录整份拷进 Agent 的 skills 目录。

---

## 怎么用

装好后跟 Agent 说一句：

```text
按 video-studio-setup 这个 skill，帮我把这台电脑做视频要用的环境配好。每一步先告诉我要装什么，我同意了再装。
```

它会按这个顺序走：

1. **体检**：`scripts/doctor.sh` 只检查不改动，列出已有的和缺的
2. **装系统工具**：macOS 用 Homebrew，Windows 用 winget，Linux 用 apt；装之前先问你
3. **装风格库**：Claude Code 走插件，其他 Agent 走 git clone
4. **装渲染依赖**：无头浏览器、Python 包、配音模型，约 1 GB
5. **出测试片**：`scripts/selftest.sh` 渲染 2 秒 mp4，看到 `SELFTEST OK` 才算配好
6. **交代结果**：装了什么、什么版本、测试片在哪、下一步怎么开始做片

国内网络下载失败时，它只对失败的那一步换源（npm、Playwright、PyPI、Hugging Face 各有对应镜像），换之前会告诉你。

---

## 需要什么

| 项目 | 要求 |
|---|---|
| 系统 | macOS / Windows（Git Bash）/ Linux |
| 磁盘 | 约 3 GB 空闲 |
| 网络 | 能访问 GitHub、npm、PyPI |
| Node.js | 20 以上 |
| FFmpeg | 7 以上（6.x 会把音频长度算错） |
| Python | 3.11 以上，或装 uv |

目前只在 macOS 上实测跑通；Windows 和 Linux 的安装命令按官方做法写，还没有真机验证。

---

## 它不会做的事

- 不经你同意安装或升级系统软件
- 不卸载、不覆盖你已有的 Node、Python、FFmpeg
- 不往系统 Python 里装包
- 同一步失败两次就停下，把报错和试过的办法告诉你，不乱试

---

## 接下来你可以

1. 环境配好后，对 Agent 说「用 Lemo-Opuscar 的某某风格，做一支 30 秒的片子，讲……」
2. **Star** 本仓跟更新
3. 完整课程和每周直播：[mdldm.club](https://www.mdldm.club)
4. 微信：`gaozhizhaji778` · X：[@czzzzzzJ_](https://x.com/czzzzzzJ_)

## License

MIT
