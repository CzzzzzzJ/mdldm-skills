# 麦当写作 / 商单脚本

把我写观点口播、商单脚本和发布素材的那套口径，收成一个 Agent Skill。

你丢原始口播、brief、选题或旧稿过来，它按麦当 mdldm 的说话方式落本地 Markdown：观点型正文、商单脚本大纲、封面标题、多平台发布文案——能接着改、录、发。

---

## 适合谁

- 做 **AI 工具评测 / 观点口播 / 商单合作** 的人
- 要的是「像本人会说的话」，不是通篇 GPT 味教程
- 已经有本地内容仓，或想把成稿落成可继续编辑的 Markdown

观点型 / 非教程型商单会先读内置的写作参考；教程型商单走「结果前置 → 演示 → 步骤 → CTA」。

---

## 先装

```bash
npx skills add CzzzzzzJ/mdldm-skills --skill content-script-local-draft
```

或把本目录整份拷进 Agent 的 skills 目录。

---

## 怎么用

跟 Agent 说清楚要什么阶段就行，别让它擅自扩成整包：

```text
按麦当写作风格，把这段口播整理成观点型正文。
重写这条商单脚本，产品当证据，不要写成功能教程。
只要封面标题和多平台发布文案，先别动正文。
落一份大纲到本地，后面再扩。
```

---

## 它会守住什么

| 点 | 做法 |
|----|------|
| 原始判断 | 先吃透你当次真要下的判断，不拿通用模板盖掉 |
| 开头 | 观点型直接说命题；商单从已经发生的结果钩进去 |
| 产品位置 | 产品是证据，不是菜名；功能演示别盖过观点 |
| 口语 | 保留真实呼吸，砍掉「不是…而是…」「本质上…」这类模型套话 |
| 封面 | 负责点击，不负责总结课程目录 |
| 发布包 | 封面 / 各平台文案按平台改，不写成同一份复制粘贴 |

---

## 目录

```text
content-script-local-draft/
├── SKILL.md
├── README.md
└── references/
    └── mdldm-viewpoint-writing.md   # 观点型 / 非教程型商单写作口径
```

---

## 接下来你可以

1. **装 Skill**（上面那条 `npx skills add`），顺手 **Star** [mdldm-skills](https://github.com/CzzzzzzJ/mdldm-skills) 跟更新
2. 教程 / 合作：[麦当的知识站](https://www.mdldm.club)
3. 微信：`gaozhizhaji778` · X：[@czzzzzzJ_](https://x.com/czzzzzzJ_)
