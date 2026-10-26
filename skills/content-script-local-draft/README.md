# 麦当口述风格

把我怎么说话、怎么抛观点，收成一个 Agent Skill。  
商单文案只是其中一种用法，不是整个人设。

你丢原始口播、观点、brief 或旧稿过来，它按「直抒胸臆 + 判断推演」落本地 Markdown：口述正文、可选商单咬合、封面和多平台发布文案——能接着改、录、发。

Skill id 仍是 `content-script-local-draft`（安装命令不用改）。

---

## 适合谁

- 要「像麦当会说的话」，不要 GPT 万能开头
- 观点口播、产品实测口述、开源/知识站表达
- 商单也要观点立住，产品当证据，不报菜名

---

## 先装

```bash
npx skills add CzzzzzzJ/mdldm-skills --skill content-script-local-draft
```

---

## 怎么用

```text
按麦当口述风格，把这段口播整理成观点正文。
重写这条商单：产品当证据，开头别「你有没有想过」。
只要封面和发布文案，正文已过。
先落大纲，别扩成整包。
```

---

## 它会守住什么

| 点 | 做法 |
|----|------|
| 开头 | 直判 / 结果画面；禁万能「你有没有想过」 |
| 人称 | 默认「我」 |
| 推进 | 判断 → 为什么 → 会怎样 |
| 产品 | 证据不是菜名；适合谁 / 不适合谁 |
| 质检 | L1 硬禁 + L2 口述清单；对照范例与反例 |
| 经历 | 不编造第一手；缺测留空 |
| 封面 | 负责点击，不负责目录 |

---

## 目录

```text
content-script-local-draft/
├── SKILL.md
├── README.md
└── references/
    ├── mdldm-oral-style.md       # 口述 / 观点主口径
    ├── style_examples.md         # 黄金样本
    ├── ai-anti-examples.md       # AI 味反例
    └── mdldm-viewpoint-writing.md # 兼容跳转（指向 oral-style）
```

---

## 接下来你可以

1. **装 Skill**（上面 `npx skills add`），顺手 **Star** [mdldm-skills](https://github.com/CzzzzzzJ/mdldm-skills)
2. 教程 / 合作：[mdldm.club](https://www.mdldm.club)
3. 微信：`gaozhizhaji778` · X：[@czzzzzzJ_](https://x.com/czzzzzzJ_)
