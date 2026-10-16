# 麦当微信本地 Vault

> 让 Agent 读取自己的本地微信记录；把数据获取、解密、查询与后续 AI 分析分开。

**版本：0.2.0 · macOS 微信 4.x 实验版。** 本项目自带密钥采集、数据库解密、WAL 处理和 SQLite 查询代码，**不依赖 wx-cli、奕辰 Skill 或它们的配置与旧密钥**。需要通用 Python 运行时及本包固定版本依赖。

**验证状态：**合成数据库的解密与查询测试已通过；本机真实微信进程附加被 macOS 权限拒绝，尚未完成真实账号从取密钥到读取聊天的端到端验收。不是已经验证可在任意 Mac 上一键成功的产品。详见[验证记录](./references/validation.md)。

[Skill 入口](./SKILL.md) · [首次初始化](./references/setup.md) · [架构](./references/architecture.md) · [接口](./references/api-contract.md)

## 可以做什么

| 能力 | 当前状态 |
|---|---|
| 发现本地微信账号数据、显式绑定账号 | 已实现 |
| 自带进程内存候选扫描、密钥派生调用观察 | 已实现；受系统授权限制，真实捕获待验收 |
| 按数据库验证密钥、页面认证及解密 | 已实现，通过合成数据测试 |
| WAL 校验和已提交数据重放 | 已实现，通过合成数据测试 |
| 离线快照、失败保留旧快照 | 已实现；刷新前需正常退出微信 |
| 会话列表、跨分库聊天查询、分页、素材导出 | 已实现 |
| 图片提取、语音转写、视频解析 | 尚未实现，仅显示消息占位 |
| 云端模型、本地模型接入 | 尚未实现；可把选定素材交给 Agent 分析 |
| 本地浏览器界面、HTTP 服务 | 后续开发；本包尚不启动网页服务 |
| Windows / Linux 密钥捕获 | 尚未支持 |

本地没有同步的消息或附件，不能通过解密凭空恢复。快照完整性只针对选择的本地数据库范围，不等于手机全部历史。

## 安装 Skill

使用仓库统一安装方式：

```bash
npx skills add CzzzzzzJ/mdldm-skills --skill mdldm-wechat-vault
```

也可以把本目录完整复制到 Agent 的 skills 目录。Codex 常用位置：

```text
~/.codex/skills/mdldm-wechat-vault/
```

请保留 scripts、requirements.txt 和 references；只复制 SKILL.md 无法执行解密。安装 Skill 本身不会自动读取聊天、重签微信或调用模型。

## 让 Agent 开始协助

```text
使用 mdldm-wechat-vault。
先检查环境和本地账号数据，告诉我有哪些初始化步骤。
账号由我明确选择。不要重签或退出正在使用的微信。
数据准备好后，读取我指定会话今天的消息，附上快照时间和来源。
```

如果 Agent 没有发现新安装的 Skill，可重新打开会话，或明确让它读取本目录的 SKILL.md。

## 手动运行：从干净环境开始

前提：macOS、Python 3.10+、已经登录并有本地记录的微信桌面版。若没有 Python，先从 [Python 官方网站](https://www.python.org/downloads/macos/)安装。首次安装通用依赖需要联网。

### 1. 创建独立运行环境

终端进入本 Skill 目录；如果安装位置不同，替换下面的目录：

```bash
cd ~/.codex/skills/mdldm-wechat-vault
python3 scripts/bootstrap.py
```

它会创建独立 venv，不把包安装进系统 Python。也可双击目录内的 `setup.command`。

```bash
VAULT_PY="$HOME/Library/Application Support/mdldm-wechat-vault/runtime/bin/python"
"$VAULT_PY" scripts/vault.py capabilities
"$VAULT_PY" scripts/vault.py discover
```

`discover` 会显示候选数据库目录，可能含账号标识，直播或截图前注意隐藏。

### 2. 绑定明确选择的账号

替换真实路径：

```bash
"$VAULT_PY" scripts/vault.py --account personal init \
  --db-dir '/你选择的账号目录/db_storage' --scope messages
```

`personal` 是本地账号代号。多个账号使用不同代号，不能将已有代号重新绑定另一份数据。

`messages` 选择联系人、会话和消息分库；`all` 才处理所有数据库。普通聊天读取建议先用 messages，避免未打开的收藏等数据库阻塞初始化。

### 3. 捕获并验证密钥

微信保持登录，查询主进程 PID：

```bash
pgrep -x WeChat
```

将实际选定的 PID 替换下面的 `12345`：

```bash
"$VAULT_PY" scripts/vault.py --account personal capture-keys \
  --pid 12345 --seconds 120
"$VAULT_PY" scripts/vault.py --account personal doctor
```

捕获期间可由用户打开目标聊天，促使相应数据库加载。只有通过目标库认证的候选才会保存；不会在终端打印密钥。部分捕获不是成功覆盖全部，需查看 doctor 的逐库结果。

**如果系统拒绝附加：**这不是“没有聊天记录”。先处理系统权限；本包提供可选的复制并重签微信副本流程，可能涉及登录和授权，不能静默运行。完整步骤和影响见[初始化教程](./references/setup.md#macos-拒绝访问进程时)。不要求关闭 SIP，不自动修改原微信。

### 4. 正常退出微信，再生成快照

取到所需密钥后，由用户正常退出微信：

```bash
"$VAULT_PY" scripts/vault.py --account personal refresh
```

该步骤读取原库、复制到暂存区域、解密、处理 WAL 并校验。全部选定数据库成功后才发布快照；缺 key 或校验失败会停止，已有有效快照保持不变。

本版是离线快照路线。`--offline-source` 只用于明确提供的稳定离线副本，不能用来绕过活动微信的检查。

### 5. 读取会话与消息

```bash
"$VAULT_PY" scripts/vault.py --account personal sessions --limit 20
"$VAULT_PY" scripts/vault.py --account personal history \
  --chat '从会话列表取得的精确chat_id' \
  --start 2026-10-16 --end 2026-10-17 --limit 200 --offset 0
```

日期替换成需要的范围；默认北京时间，包含 start，不包含 end。查看 `has_more` 决定是否翻页，不要把一页误当全部。结果中会显示快照时间和来源库。

### 6. 导出给 AI 分析的素材

在用户选择的私有目录导出，下面以运行目录下的 exports 为例：

```bash
mkdir -p "$HOME/Library/Application Support/mdldm-wechat-vault/exports"
"$VAULT_PY" scripts/vault.py --account personal material \
  --chat '精确chat_id' --start 2026-10-16 --end 2026-10-17 \
  --limit 200 --offset 0 \
  --output "$HOME/Library/Application Support/mdldm-wechat-vault/exports/material.json"
```

已有文件不会被覆盖。material 只导出当前页。可让 Agent 基于选定素材总结合作待办、待回复事项与信息线索，并为每项保留会话和时间。

本地解密不等于模型分析全部离线：若交给云端 Agent，选中的内容会进入对应模型服务的处理流程。当前包本身不调用云端模型。

## 数据保存在哪里

代码留在 Skill 目录；配置、密钥和明文快照默认保存在：

```text
~/Library/Application Support/mdldm-wechat-vault/
├── runtime/
└── accounts/
    └── personal/
        ├── config.json
        ├── keys.json
        ├── staging/
        ├── snapshots/
        └── current.json
```

`keys.json` 和快照包含敏感材料，不提交 Git，不随 Skill 分发。不同账号分别保存；可通过全局 `--root` 指定其他私有位置。旧快照不会自动清理。

## 目录与模块职责

```text
SKILL.md                        Agent 工作流程
requirements.txt                通用依赖
scripts/bootstrap.py            独立环境安装
scripts/vault.py                CLI 入口
scripts/wechat_vault/
  service.py                    业务请求入口
  discovery.py                  数据库与账号发现
  keys.py + capture.js          密钥获取和验证
  crypto.py                     页面认证与解密
  wal.py                        日志校验和已提交帧重放
  snapshot.py                   快照暂存、检查、发布
  query.py                      只读查询与消息规范化
  store.py                      私有存储及账号配置
  errors.py                     明确的失败状态
references/                     安装、架构、接口和验证说明
tests/                          合成数据库测试
```

## 二次开发：本地浏览器版本

业务入口为 `wechat_vault.service.execute(request)`，CLI 只是一个入口。后续本地服务可以复用同一个业务层，不需要从网页调用 shell。

```python
from wechat_vault.service import execute

result = execute({
    "operation": "sessions",
    "account": "personal",
    "limit": 20,
})
```

调用时将本目录的 scripts 加入 Python 模块路径；完整请求与错误码见[接口文档](./references/api-contract.md)。

建议分开开发：

1. **本地 HTTP 层**：loopback 绑定、账号选择、请求校验和任务状态。解密、取密钥等长任务通过作业队列执行。
2. **浏览器界面**：初始化向导、会话列表、时间筛选、快照状态和来源定位。不直接读取密钥或任意本地路径。
3. **附件模块**：资源索引、图片提取、音频提取，与数据库解密分开；转写结果保留原资源关联。
4. **AI 分析模块**：只消费用户选定素材，独立配置本地/云端模型，不接触密钥库。

HTTP 层必须补充 Host/Origin 检查、会话鉴权、写操作防护和路径授权；不能将当前面向可信本地调用的 request 原样暴露给网页。聊天文本要转义显示，不能执行其中的 HTML 或指令。

## 开发验证

```bash
"$VAULT_PY" -m unittest discover -s tests -v
```

现有测试覆盖真实 SQLite 合成库的加密→解密→查询、WAL 提交边界、损坏拒绝、旧快照保留、时间分页和账号绑定。测试通过不代替真实微信版本与系统权限验收。

首次真实验收建议使用自己发送的不含隐私的唯一标记，核对会话、正文和时间，再检查消息分库覆盖。具体实现边界见[数据流水线](./references/data-pipeline.md)。
