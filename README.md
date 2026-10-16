# mdldm-skills

> 麦当 mdldm 的 Agent Skills 合集（小红书笔记 / 知识变现诊断 / 微信本地记录读取）

本仓库是 **一个仓、多个 Skill** 的 monorepo。推荐从此处安装；旧独立仓 `omi`、`mdldm-monetize` 仍保留约 90 天兼容，但新项目请改用本仓。

**主页：** [mdldm.club](https://www.mdldm.club) · **作者：** 麦当 mdldm

---

## 包含的 Skills

| Skill | 说明 | 路径 |
|-------|------|------|
| `omi` | 小红书图文笔记生产线（分镜 JSON + 封面/内页） | [`skills/omi`](./skills/omi) |
| `mdldm-monetize` | 知识变现诊断：阶段判断、首款产品与 30 天验证计划 | [`skills/mdldm-monetize`](./skills/mdldm-monetize) |
| `mdldm-wechat-vault` | 微信本地记录读取（macOS 实验版）：独立密钥采集、解密快照与查询，不依赖其他微信工具 | [`使用与二次开发`](./skills/mdldm-wechat-vault/README.md) |

---

## 安装（skills.sh）

安装单个 Skill：

```bash
npx skills add CzzzzzzJ/mdldm-skills --skill omi
```

```bash
npx skills add CzzzzzzJ/mdldm-skills --skill mdldm-monetize
```

```bash
npx skills add CzzzzzzJ/mdldm-skills --skill mdldm-wechat-vault
```

微信 Skill 安装后还需初始化独立 Python 环境和本人微信数据，详见[使用教程](./skills/mdldm-wechat-vault/README.md)。安装 Skill 不会自动修改微信。

一次安装全部：

```bash
npx skills add CzzzzzzJ/mdldm-skills --all
```

---

## 目录结构

```text
mdldm-skills/
├── README.md
└── skills/
    ├── omi/
    │   ├── SKILL.md
    │   ├── README.md
    │   └── prompts/
    ├── mdldm-wechat-vault/
    │   ├── SKILL.md
    │   ├── README.md
    │   ├── requirements.txt
    │   ├── scripts/
    │   ├── references/
    │   └── tests/
    └── mdldm-monetize/
        ├── SKILL.md
        ├── README.md
        ├── LICENSE
        ├── agents/
        ├── references/
        ├── templates/
        └── examples/
```

每个子目录是独立 Skill：入口为 `SKILL.md`，细节见各自 README。

---

## 旧仓说明

| 旧仓 | 状态 |
|------|------|
| [CzzzzzzJ/omi](https://github.com/CzzzzzzJ/omi) | 已迁入本仓 `skills/omi`；旧仓保留兼容 |
| [CzzzzzzJ/mdldm-monetize](https://github.com/CzzzzzzJ/mdldm-monetize) | 已迁入本仓 `skills/mdldm-monetize`；旧仓保留兼容 |

---

## License

各 Skill 保留原许可证（多为 MIT）。详见子目录内 `LICENSE` / README。

