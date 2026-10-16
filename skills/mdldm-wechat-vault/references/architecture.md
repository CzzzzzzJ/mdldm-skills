# 独立目录与依赖方向

```text
mdldm-wechat-vault/
  SKILL.md
  requirements.txt                    固定通用依赖
  scripts/
    bootstrap.py                      私有 venv 安装
    vault.py                          CLI 参数与输出
    wechat_vault/
      service.py                      统一请求入口、用例编排
      discovery.py                    发现源库、选择范围、逐库检查
      keys.py                         密钥捕获、显式导入、副本准备
      capture.js                      自带 Frida 扫描与函数观察
      crypto.py                       页面认证及解密
      wal.py                          WAL 校验、提交边界与重放
      snapshot.py                     稳定源检查、暂存、结构验证、原子发布
      query.py                        只读 SQLite 查询与消息规范化
      store.py                        独立账号配置、密钥及当前快照
      errors.py                       稳定错误码
  tests/
    fixtures.py                       合成数据库和日志生成
    test_standalone.py                 端到端及失败行为测试
  references/                         分模块工作说明
```

CLI/未来 HTTP → service。密钥模块只产出逐库 key；crypto 不知道账号或微信进程；wal 只使用 codec；snapshot 编排私有文件生成；query 只读已经发布的快照，不参与采集或解密。

运行依赖为 Python、Frida、PyCryptodome 和 Zstandard。数据获取、解密和查询由本包模块实现。

## 运行数据（不随 Skill 分发）

```text
运行根目录/
  runtime/                          通用 Python 虚拟环境
  apps/WeChat.app                    仅用户选择副本路线时生成
  accounts/账号代号/
    config.json                     显式绑定的源目录和范围
    keys.json                       经验证 raw key，0600
    .lock                           操作互斥
    staging/                        临时加密副本及明文，不发布半成品
    snapshots/快照ID/
      data/                         按原相对路径排列的明文库
      manifest.json                 校验、范围、时间，不含 key
    current.json                    原子指向最新有效快照
```

原库与运行目录不能互相嵌套。旧快照保留，清理需另行明确选择；版本更新不删除数据。客户端账户身份以用户绑定目录为准，不根据目录排序猜账号。

后续附件模块只读取资源索引与媒体文件；分析模块只消费选定素材；前端通过 service 请求和作业状态调用，不直接访问密钥、SQL 或 shell。
