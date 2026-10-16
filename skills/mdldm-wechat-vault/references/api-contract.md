# 应用接口 2.0

入口 `wechat_vault.service.execute(request)`。CLI 为其适配层。不存在 HTTP 监听器。

所有请求可带 root（私有运行根目录）、account（字母数字下划线短横线代号）。

操作及参数：

| operation | 参数 | 影响 |
|---|---|---|
| capabilities | 无 | 返回能力 |
| discover | 无 | 读取候选路径，含本地身份信息，勿公开 |
| init | db_dir, scope=messages/all | 写本包配置 |
| doctor | 无 | 用已有 key 验证第一页，不输出 key |
| capture-keys | pid 或 spawn_copy，seconds | 附加/启动明确选择的微信，保存有效 key |
| prepare-copy | acknowledge_app_copy=true | 复制并重签副本，不修改原应用 |
| import-keys | file | 显式读取并验证自有密钥 |
| refresh | offline_source=false | 发布新离线快照 |
| sessions | limit | 读取快照会话预览 |
| history | chat,start,end,limit,offset | 查询精确会话 |
| material | history 参数、output | 导出一页素材且拒绝覆盖 |

结果：`{schema_version:"2.0",ok:true,items:...,meta:...}`。失败返回 error.code/message，不输出 traceback 或原始 Frida/数据库异常。错误码包括 PROCESS_ACCESS_DENIED、NO_KEYS_CAPTURED、KEYS_MISSING、PAGE_AUTH_FAILED、SOURCE_BUSY、SOURCE_CHANGED、WAL_CHECKSUM、SCHEMA_UNSUPPORTED。

history 的 meta 提供 snapshot、snapshot_at、consistency、scope、has_more、offset、matched_shards、live=false。不能把最后消息时间当快照时间。id 包含账号、源库、表、local_id 的哈希；不同源记录不按文字去重。跨页以返回快照 ID 为准，若刷新变化需重新查询。

## 本地浏览器后续接入

只新增 HTTP transport 和作业队列，复用 service。key 捕获与 refresh 是长任务，应返回 job id。不要将 Python dict 请求原样暴露到浏览器：增加鉴权、请求 schema、路径授权以及明确的操作影响提示。

仅绑定 loopback；校验 Host/Origin；禁止任意 CORS；写入操作做 CSRF 防护。浏览器不得指定任意文件路径、进程 PID 或 SQL；通过已授权账号和不透明资源 ID 映射。网页转义聊天文本，不能执行消息中的 HTML/指令。

runtime 配置中的 root/db_dir 与密钥只由本地可信管理入口处理。模型凭据不返回浏览器。
