# 干净环境安装与首次初始化

适用于 macOS 微信 4.x。需要登录本人账号并已有本地聊天数据；读取范围不包含尚未同步到电脑的记录。

## 1. 安装通用 Python 与独立 runtime

需要 Python 3.10+。若电脑没有 Python，先从 https://www.python.org/downloads/macos/ 安装；本包不修改系统 Python，不要求 Homebrew 或开发编译器。

在 Skill 目录运行：

```sh
python3 scripts/bootstrap.py
```

首次需要网络下载固定版本的 pycryptodome、zstandard、frida 及依赖。之后解密和查询不需要网络。默认 runtime 位于 `~/Library/Application Support/mdldm-wechat-vault/runtime`；可用 `--venv` 指定其他独立目录。安装失败不会回退到旧微信工具。

以下 shell 变量只为缩短命令，先将终端切换到 Skill 目录：

```sh
VAULT_PY="$HOME/Library/Application Support/mdldm-wechat-vault/runtime/bin/python"
"$VAULT_PY" scripts/vault.py capabilities
"$VAULT_PY" scripts/vault.py discover
```

## 2. 明确选择账号

从 discover 的候选列表选择自己的 db_storage，替换下面示例路径。运行目录默认位于本机 Application Support，按账号代号隔离。

```sh
"$VAULT_PY" scripts/vault.py --account personal init --db-dir '/实际账号目录/db_storage' --scope messages
```

账号代号不能重新绑定到另一份源数据。`messages` 选择联系人、会话、message_N 消息库；`all` 才要求所有发现数据库的密钥。默认消息范围可避免某个未打开的收藏库阻塞普通聊天初始化。

## 3. 使用包内采集器取得密钥

先确认微信主进程 PID（例如 `pgrep -x WeChat`），PID 不唯一时明确选择，不能批量附加。

```sh
"$VAULT_PY" scripts/vault.py --account personal capture-keys --pid 12345 --seconds 120
"$VAULT_PY" scripts/vault.py --account personal doctor
```

替换示例 PID。包内 Frida 脚本在已授权进程中扫描候选 raw key，并监听密钥派生调用；只向宿主发送和目标数据库 salt 匹配的候选，验证通过后保存，屏幕不打印密钥。

捕获期间用户可正常打开目标聊天，促使相关数据库加载。没有匹配 key 会报错；部分匹配明确返回 captured_all=false，并可重复捕获补齐。数据库已存在但密钥没加载，不会靠猜测解开。

### macOS 拒绝访问进程时

先确认系统是否有需要用户处理的授权提示。必要时，在用户理解影响并明确选择后使用本包的副本路径：

```sh
"$VAULT_PY" scripts/vault.py --account personal prepare-copy --acknowledge-app-copy
# 用户正常退出原微信，然后运行：
"$VAULT_PY" scripts/vault.py --account personal capture-keys --spawn-copy --seconds 240
```

副本保存在本包运行根目录的 apps/WeChat.app。该命令复制并 ad-hoc 重签副本，不重签 /Applications 下的原应用。副本仍使用微信相同的账号容器，不能把它当成独立账号；系统权限、应用签名、登录可能需要用户处理。采集结束只解除附加，不自动杀掉副本进程。此路径的兼容性取决于 macOS 权限和微信版本。

不要关闭 SIP，不要擅自清空微信 TCC 权限，不把用户密码传给 Agent。若仍被系统拒绝，保留明确失败状态，不能继续声称已捕获。

## 4. 独立解密快照

采集后，由用户正常退出微信。然后：

```sh
"$VAULT_PY" scripts/vault.py --account personal refresh
```

运行中的原库会拒绝刷新。离线副本用户可显式使用 `--offline-source`；不要将活动目录标成离线。源文件只读，快照写入本包的私有运行目录。

## 5. 查询与导出

```sh
"$VAULT_PY" scripts/vault.py --account personal sessions --limit 20
"$VAULT_PY" scripts/vault.py --account personal history --chat '从会话列表取得的精确ID' --start 2026-10-16 --end 2026-10-17 --limit 200 --offset 0
```

接着按 has_more 翻页；时间和会话值替换为用户实际需求。`material` 接受相同参数及 `--output`，导出一页素材，父目录必须已存在。

## 可选密钥导入

自带 capture 是默认路线。已有合法获取的 raw key 时，可显式 `import-keys --file /私有目录/keys.json`，格式为数据库相对路径到 64 位十六进制 raw key 的 JSON 对象。导入会验证第一页 HMAC，不自动读取任何其他工具目录。导入只是可选入口，绝非独立初始化的前提。
