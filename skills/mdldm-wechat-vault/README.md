# 麦当微信本地 Vault

本机读、解密、查微信聊天记录的 Agent Skill。按会话 / 时间导出素材，也提供可复用 Python 接口。

**0.2.0 · macOS 微信 4.x 实验版** · 离线快照查询；真实微信端到端兼容仍在验。

不做图片解码、语音转写、模型调用或浏览器界面——那些在应用仓 [wechat-vault](https://github.com/CzzzzzzJ/wechat-vault)。

---

## 先装

```bash
npx skills add CzzzzzzJ/mdldm-skills --skill mdldm-wechat-vault
```

或把本目录整份拷进 Agent 的 skills 目录。需要：macOS、Python 3.10+、已登录并落过本地记录的微信。

```bash
cd ~/.codex/skills/mdldm-wechat-vault
python3 scripts/bootstrap.py
```

装到别的路径就改 `cd`。首次装依赖要联网。

想要带界面的工作台 → 直接用 [wechat-vault](https://github.com/CzzzzzzJ/wechat-vault)。

---

## 能做什么

- 发现本地账号，按账号独立存配置和快照
- 取并验证数据库密钥，解密消息库 + 已提交 WAL
- 查会话、跨分库读聊天，支持时间筛选和分页
- 导出 JSON 素材（保留时间与来源）

查询范围 = 本机已有数据。

---

## 用法

### 丢给 Agent

```text
使用 mdldm-wechat-vault，检查环境并引导我完成账号初始化。
读取指定会话今天的消息，整理待办，附上消息来源和快照时间。
```

### 命令行（在 Skill 目录执行）

**1. 发现并选账号**

```bash
VAULT_PY="$HOME/Library/Application Support/mdldm-wechat-vault/runtime/bin/python"
"$VAULT_PY" scripts/vault.py discover
"$VAULT_PY" scripts/vault.py --account personal init \
  --db-dir '/账号目录/db_storage' --scope messages
```

路径换成 discover 返回的目录。`personal` 是你起的代号；`messages` = 联系人 / 会话 / 消息，`all` = 全部库。

**2. 拿密钥**

微信保持登录，`pgrep -x WeChat` 看主进程 PID，把下面的 `12345` 换成真实值：

```bash
"$VAULT_PY" scripts/vault.py --account personal capture-keys \
  --pid 12345 --seconds 120
"$VAULT_PY" scripts/vault.py --account personal doctor
```

要 macOS 允许访问微信进程。权限和副本初始化见 [安装指南](./references/setup.md)。

**3. 出快照**

正常退出微信后：

```bash
"$VAULT_PY" scripts/vault.py --account personal refresh
```

校验通过才发布；失败保留上一份有效快照。

**4. 查聊天**

```bash
"$VAULT_PY" scripts/vault.py --account personal sessions --limit 20
"$VAULT_PY" scripts/vault.py --account personal history \
  --chat '会话列表中的chat_id' \
  --start 2026-01-01 --end 2026-01-02 --limit 200 --offset 0
```

默认北京时间，含开始、不含结束。`has_more` 表示还要不要翻页。

**5. 导出素材**

```bash
mkdir -p "$HOME/Library/Application Support/mdldm-wechat-vault/exports"
"$VAULT_PY" scripts/vault.py --account personal material \
  --chat 'chat_id' --start 2026-01-01 --end 2026-01-02 \
  --limit 200 --offset 0 \
  --output "$HOME/Library/Application Support/mdldm-wechat-vault/exports/material.json"
```

每次导当前页，不覆盖已有文件。把素材丢给模型时，处理范围取决于你用的模型服务。

---

## 本地存哪

默认：`~/Library/Application Support/mdldm-wechat-vault/`

```text
runtime/                  Python 运行环境
accounts/<账号代号>/
  config.json             账号配置
  keys.json               数据库密钥
  staging/                快照暂存
  snapshots/              明文数据库快照
  current.json            当前有效快照
```

`--root` 可换目录。密钥和明文快照放私有位置，别提交仓库。

---

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

`scripts` 进 PYTHONPATH 后：

```python
from wechat_vault.service import execute

result = execute({
    "operation": "sessions",
    "account": "personal",
    "limit": 20,
})
```

浏览器版可在这层上加 HTTP / 任务队列。附件和 AI 分析当独立模块扩；前端走服务接口，别直接碰密钥或库。

- [架构与职责](./references/architecture.md)
- [请求参数与接口约束](./references/api-contract.md)
- [数据处理流程](./references/data-pipeline.md)
- [附件与 AI 分析扩展](./references/attachments-analysis.md)

## 测试

```bash
"$VAULT_PY" -m unittest discover -s tests -v
```

覆盖解密查询、WAL 边界、损坏拒绝、快照保留、分页、账号绑定。详见 [测试指南](./references/validation.md)。

---

## 接下来你可以

1. **装 Skill**（上面那条 `npx skills add`）
2. **跑带界面的应用**：[wechat-vault](https://github.com/CzzzzzzJ/wechat-vault)
3. 教程 / 合作：[麦当的知识站](https://www.mdldm.club)
4. 微信：`gaozhizhaji778` · X：[@czzzzzzJ_](https://x.com/czzzzzzJ_)
