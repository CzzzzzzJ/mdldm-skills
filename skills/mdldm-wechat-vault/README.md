# 麦当微信本地 Vault

读取、解密和查询本机微信聊天记录的 Agent Skill，支持按会话与时间范围导出素材，并提供可复用的 Python 接口。

**0.2.0 · macOS 微信 4.x 实验版**。目前提供离线快照查询；真实微信环境的端到端兼容性仍待验证。

## 功能

- 发现本地账号数据，按账号独立保存配置与快照。
- 获取并验证数据库密钥，解密消息库及已提交的 WAL 数据。
- 查询会话、跨分库读取聊天记录，支持时间筛选和分页。
- 导出 JSON 素材，保留消息时间和来源。

当前不提供图片解码、语音转写、模型调用或浏览器界面。查询范围限于本机已有数据。

## 安装

```bash
npx skills add CzzzzzzJ/mdldm-skills --skill mdldm-wechat-vault
```

也可将本目录完整复制到 Agent 的 skills 目录。运行需要 macOS、Python 3.10+，以及已登录并保存本地记录的微信。

进入安装目录并创建运行环境：

```bash
cd ~/.codex/skills/mdldm-wechat-vault
python3 scripts/bootstrap.py
```

安装到其他位置时，请替换上述目录。首次安装依赖需要联网。

## 使用

### 通过 Agent

```text
使用 mdldm-wechat-vault，检查环境并引导我完成账号初始化。
读取指定会话今天的消息，整理待办，附上消息来源和快照时间。
```

### 通过命令行

以下命令在 Skill 目录执行。

**1. 发现并选择账号**

```bash
VAULT_PY="$HOME/Library/Application Support/mdldm-wechat-vault/runtime/bin/python"
"$VAULT_PY" scripts/vault.py discover
"$VAULT_PY" scripts/vault.py --account personal init \
  --db-dir '/账号目录/db_storage' --scope messages
```

将路径替换为 discover 返回的目标目录。`personal` 是自定义账号代号；`messages` 包含联系人、会话与消息分库，`all` 表示所有数据库。

**2. 获取密钥**

微信保持登录，使用 `pgrep -x WeChat` 查看主进程 PID，将下方 `12345` 替换为实际值：

```bash
"$VAULT_PY" scripts/vault.py --account personal capture-keys \
  --pid 12345 --seconds 120
"$VAULT_PY" scripts/vault.py --account personal doctor
```

获取密钥需要 macOS 允许访问微信进程。权限问题和副本初始化方法见[安装指南](./references/setup.md)。

**3. 生成快照**

正常退出微信后执行：

```bash
"$VAULT_PY" scripts/vault.py --account personal refresh
```

快照通过校验后发布；失败时保留上一份有效快照。

**4. 查询聊天**

```bash
"$VAULT_PY" scripts/vault.py --account personal sessions --limit 20
"$VAULT_PY" scripts/vault.py --account personal history \
  --chat '会话列表中的chat_id' \
  --start 2026-01-01 --end 2026-01-02 --limit 200 --offset 0
```

日期按需要替换。默认北京时间，包含开始时间，不包含结束时间。结果中的 `has_more` 表示是否需要继续翻页。

**5. 导出素材**

```bash
mkdir -p "$HOME/Library/Application Support/mdldm-wechat-vault/exports"
"$VAULT_PY" scripts/vault.py --account personal material \
  --chat 'chat_id' --start 2026-01-01 --end 2026-01-02 \
  --limit 200 --offset 0 \
  --output "$HOME/Library/Application Support/mdldm-wechat-vault/exports/material.json"
```

每次导出当前页，已有文件不会覆盖。将素材交给模型分析时，数据处理范围取决于所使用的模型服务。

## 本地存储

默认运行目录：`~/Library/Application Support/mdldm-wechat-vault/`。

```text
runtime/                  Python 运行环境
accounts/<账号代号>/
  config.json             账号配置
  keys.json               数据库密钥
  staging/                快照暂存
  snapshots/              明文数据库快照
  current.json            当前有效快照
```

可通过全局参数 `--root` 指定其他目录。密钥和明文快照应保存在私有位置，不提交到代码仓库。

## 二次开发

```text
scripts/
  bootstrap.py            环境安装
  vault.py                命令行入口
  wechat_vault/
    service.py            统一业务接口
    discovery.py          数据源发现
    keys.py + capture.js  密钥获取
    crypto.py             页面认证与解密
    wal.py                WAL 处理
    snapshot.py           快照管理
    query.py              SQLite 查询
    store.py              配置与存储
    errors.py             错误定义
```

将 `scripts` 加入 Python 模块路径后，可直接调用业务接口：

```python
from wechat_vault.service import execute

result = execute({
    "operation": "sessions",
    "account": "personal",
    "limit": 20,
})
```

本地浏览器版可在此接口上增加 HTTP 服务与任务队列。附件处理和 AI 分析作为独立模块扩展；前端通过服务接口访问数据，不直接操作密钥或数据库。

- [架构与职责](./references/architecture.md)
- [请求参数与接口约束](./references/api-contract.md)
- [数据处理流程](./references/data-pipeline.md)
- [附件与 AI 分析扩展](./references/attachments-analysis.md)

## 测试

```bash
"$VAULT_PY" -m unittest discover -s tests -v
```

测试覆盖解密查询、WAL 提交边界、损坏数据拒绝、快照保留、分页及账号绑定。更多说明见[测试指南](./references/validation.md)。

## 联系麦当

想了解更多 AI 实战教程、交流使用体验或项目合作，欢迎联系：

- **知识站：** [麦当的知识站](https://www.mdldm.club)
- **微信：** `gaozhizhaji`
