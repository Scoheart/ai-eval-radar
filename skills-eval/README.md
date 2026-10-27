# Skills 评测

Skill（SKILL.md）评测的相关来源，一行一个，链接都核对过能打开。每条的要点和摘要在本仓库 `topics/eval/`、`related/skills/` 的同日期文件里。

## 一、Skill 有没有用
- [SkillsBench 1.1](https://www.skillsbench.ai/blogs/skillsbench-1-1)，带与不带 Skill 配对实跑，平均通过率 33.9% → 50.5%，13 个任务负提升
- [TestJack](https://arxiv.org/abs/2610.10619)，重审 SkillsBench 等基准的通过轨迹，推翻 34.4% 假阳性
- [HPCAgent-Bench 论文](https://arxiv.org/abs/2610.20673)，Agent、Harness、Skill 单变量受控对比
- [HPCAgent-Bench 代码](https://github.com/spcl/HPCAgent-Bench)
- [Dialpad 客服 Skill 评测](https://arxiv.org/abs/2610.14346)，规则检查与 LLM 裁判结果差距大
- [legal-ai-errata](https://github.com/1331labs/legal-ai-errata)，法律基准、Skill 与模板的公开勘误登记

## 二、Skill 会不会被触发、检索和用对
- [Skill-Use 等 Skill 评测基准](https://arxiv.org/abs/2608.04828)，触发、遵循流程、不越界分开评
- [Skill 路由/使用评测论文 2603.22455](https://arxiv.org/abs/2603.22455)
- [Skill 路由/使用评测论文 2610.01506](https://arxiv.org/abs/2610.01506)
- [Skill 路由/使用评测论文 2603.00718](https://arxiv.org/abs/2603.00718)
- [SkillRet](https://arxiv.org/abs/2605.05726)，16,129 个 Skill 的检索评测
- [Graph-of-Skills](https://aclanthology.org/2026.emnlp-main.2614/)，EMNLP 2026，依赖感知的 Skill 检索
- [Skill 评测综述](https://arxiv.org/abs/2606.11435)，把基准分六类并列出缺口

## 三、Skill 安不安全
- [MaliciousSkillBench](https://arxiv.org/abs/2608.19901)，9,740 个 Skill 的恶意检测基准

## 四、评测工具
- [skillgrade](https://github.com/mgechev/skillgrade)，确定性检查加 LLM rubric，可卡 CI
- [skill-up](https://github.com/alibaba/skill-up)，YAML 定义环境与用例
- [waza](https://github.com/microsoft/waza)，行为与工具序列打分器
- [agent-skill-evals](https://github.com/akshay5995/agent-skill-evals)，基于 Promptfoo 验证路由
- [skillet](https://github.com/render-lab/skillet)，在 PR 里评论评测报告
- [skillvitals](https://github.com/ContextJet-ai/skillvitals)，触发 F1 与有无 Skill 胜率
- [agent-skills-eval](https://github.com/darkrishabh/agent-skills-eval)，有无 Skill 双轨基线
- [SkillEvaluator](https://github.com/NVIDIA/SkillEvaluator)，静态与安全检查、沙箱有无对比
- [agent-skill-eval](https://github.com/tardigrde/agent-skill-eval)，跑真实 Claude Code、Codex、OpenCode
- [Skillmark](https://skillmark.sh)，公开排行榜

## 五、官方文章与实践指南
- [OpenAI：用 evals 系统化测试 Agent Skills](https://developers.openai.com/blog/eval-skills)
- [LangChain：Evaluating Skills](https://www.langchain.com/blog/evaluating-skills)
- [Phil Schmid：测试 Agent Skills 实战](https://www.philschmid.de/testing-skills)
- [Anthropic：skill-creator 的测试、度量与改进](https://claude.com/resources/articles/improving-skill-creator-test-measure-and-refine-agent-skills)
- [Anthropic：把子 Agent 折叠进单 Agent 加 Skills](https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop)
- [anthropics/single-agent-loop-kit](https://github.com/anthropics/single-agent-loop-kit)
- [UiPath/skills](https://github.com/UiPath/skills)，把触发当二分类评测

## 六、据 X 上的报道
- [Dan Kornas 介绍 skill-up](https://x.com/DanKornas/status/2113860880592966054)
- [ClaudeDevs：Agent Skills 标准捐给 Agentic AI Foundation](https://x.com/ClaudeDevs/status/2113328526413996100)

## 七、仓库内的原型与图表（演示数据，不是真实评测结果）
- `projects/swe-together-leaderboard-replica/`
- `projects/harness-model-demo/`
- `projects/skill-effectiveness-charts/`
- `references/swe-together/`

## 待补
- SkillLearnBench、SRA-Bench、AgentSkillOS、SkillTester 只在搜索结果里见过，没核对，未收
