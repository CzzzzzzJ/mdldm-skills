# mdldm-skills

麦当 mdldm 的 Agent Skills 合集：小红书笔记 · 知识变现诊断 · 微信本地记录 · 口播剪辑。

**一个仓、多个 Skill。** 新项目请装这里；旧独立仓 `omi`、`mdldm-monetize` 仍保留约 90 天兼容。

**主页：** [mdldm.club](https://www.mdldm.club) · **作者：** 麦当 mdldm

---

## 先装一个

```bash
npx skills add CzzzzzzJ/mdldm-skills --skill omi
npx skills add CzzzzzzJ/mdldm-skills --skill mdldm-monetize
npx skills add CzzzzzzJ/mdldm-skills --skill mdldm-wechat-vault
npx skills add CzzzzzzJ/mdldm-skills --skill maidang-koubo
```

一次全装：

```bash
npx skills add CzzzzzzJ/mdldm-skills --all
```

微信 Skill 装完还要初始化独立 Python 环境和本人微信数据，见 [使用教程](./skills/mdldm-wechat-vault/README.md)。安装不会自动改微信。

带界面的微信工作台：[wechat-vault](https://github.com/CzzzzzzJ/wechat-vault)

---

## 包含的 Skills

| Skill | 说明 | 路径 |
|-------|------|------|
| `omi` | 小红书图文笔记生产线（分镜 JSON + 封面/内页） | [`skills/omi`](./skills/omi) |
| `mdldm-monetize` | 知识变现诊断：阶段判断、首款产品与 30 天验证计划 | [`skills/mdldm-monetize`](./skills/mdldm-monetize) |
| `mdldm-wechat-vault` | 微信本地记录读取（macOS 实验版）：独立密钥采集、解密快照与查询 | [`使用与二次开发`](./skills/mdldm-wechat-vault/README.md) |
| `maidang-koubo` | 麦当剪辑口播：录屏讲解类视频的粗剪、术语校对、单行字幕、成果前置、截图信息卡、BGM 与打码 | [`skills/maidang-koubo`](./skills/maidang-koubo) |

---

## 目录结构

```text
mdldm-skills/
├── README.md
└── skills/
    ├── omi/
    ├── mdldm-wechat-vault/
    ├── mdldm-monetize/
    └── maidang-koubo/
```

每个子目录是独立 Skill：入口 `SKILL.md`，细节看各自 README。

---

## 旧仓说明

| 旧仓 | 状态 |
|------|------|
| [CzzzzzzJ/omi](https://github.com/CzzzzzzJ/omi) | 已迁入 `skills/omi`；旧仓保留兼容 |
| [CzzzzzzJ/mdldm-monetize](https://github.com/CzzzzzzJ/mdldm-monetize) | 已迁入 `skills/mdldm-monetize`；旧仓保留兼容 |

---

## 接下来你可以

1. **装合集**：上面的 `npx skills add`
2. **Star** 本仓跟更新
3. 知识站 / 合作：[mdldm.club](https://www.mdldm.club)
4. 微信：`gaozhizhaji778` · X：[@czzzzzzJ_](https://x.com/czzzzzzJ_)

## License

各 Skill 保留原许可证（多为 MIT）。见子目录 `LICENSE` / README。
