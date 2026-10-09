# MDLDM Monetize

> Turn content into a validated knowledge business.

[![skills.sh](https://skills.sh/b/CzzzzzzJ/mdldm-monetize)](https://skills.sh/CzzzzzzJ/mdldm-monetize)

`MDLDM Monetize` 是麦当 mdldm 面向已有内容创作者设计的知识变现诊断与行动 Skill。

它帮助用户完成：

1. 判断当前知识变现阶段；
2. 比较服务、训练营、产品和会员路线；
3. 设计第一款可验证产品；
4. 生成 30 天行动计划；
5. 判断什么时候才值得录课、做会员或搭知识站。

## 直接使用

主文件：[`SKILL.md`](./SKILL.md)

示例输入：

```text
我是一名分享 AI 办公效率的博主，持续更新了半年。
用户经常问我怎么用 AI 自动写周报、整理会议纪要和分析 Excel。
我帮同事做过几个自动化流程，但还没有正式收费。
每周可以投入 8 小时。请帮我判断第一款产品应该做什么。
```

## RED Skill 上传

`SKILL.md` 保留完整的核心判断、证据边界和输出规范，不依赖浏览器、账号登录、外部 API 或本地脚本，可作为 RED Skill 主文件。完整本地版本会根据任务渐进式读取 `references/`、`templates/` 和 `examples/`。

建议上架信息：

- 名称：`MDLDM Monetize`
- 短描述：`帮已有内容的博主找到知识付费路线，设计第一款产品和30天验证计划。`
- 分类：创作 / 商业 / 个人成长
- 权限：无

## 通过 skills.sh 安装

```bash
npx skills add CzzzzzzJ/mdldm-monetize --skill mdldm-monetize
```

Skill 页面：<https://skills.sh/czzzzzzj/mdldm-monetize/mdldm-monetize>

## 手动安装

将整个 `mdldm-monetize` 文件夹复制到 Agent 支持的 skills 目录即可。

Codex 常见个人目录：

```text
~/.codex/skills/mdldm-monetize/
```

项目级目录可以使用：

```text
<project>/.agents/skills/mdldm-monetize/
```

具体目录以当前 Agent 的 Skill 发现规则为准。

## 目录

```text
mdldm-monetize/
├── SKILL.md
├── README.md
├── LICENSE
├── agents/
│   └── openai.yaml
├── references/
│   ├── stage-model.md
│   ├── monetization-routes.md
│   ├── decision-rules.md
│   ├── common-mistakes.md
│   ├── validation-playbook.md
│   └── mdldm-case-study.md
├── templates/
│   ├── diagnosis-report.md
│   ├── offer-onepager.md
│   ├── 30-day-validation-plan.md
│   ├── launch-copy.md
│   ├── delivery-blueprint.md
│   └── weekly-review.md
└── examples/
    ├── ai-coding-creator.md
    ├── workplace-ai-creator.md
    └── aigc-creator.md
```

## 版本

- `v0.2.0`：成熟结构版。增加证据契约、四个 Gate、渐进式文件路由、完整验证与交付手册、发布文案、周复盘和三个端到端行业案例。
- `v0.1.0`：阶段诊断、路线推荐、第一款产品单页、30 天验证计划。

## 作者

麦当 mdldm

## 许可证

[MIT](./LICENSE)
