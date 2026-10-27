# Skills 评测

收集 Skill（SKILL.md）评测的所有相关来源。只收我们真实看过、链接核对过能打开的内容，不编造。每条后面标了它在本仓库里的原始归档位置，想看要点和摘要去那里翻。

Skill 评测大致回答三个问题，下面按这个顺序分类：Skill 到底有没有用，Skill 会不会被正确触发和使用，Skill 安不安全。再加上工具和工程实践、自建评测的参考实现。

## 一、Skill 有没有用（有无 Skill 对比）
- **SkillsBench / 1.1**：[博客](https://www.skillsbench.ai/blogs/skillsbench-1-1)。带与不带 Skill 的配对实跑：87 个任务，平均通过率 33.9% → 50.5%，13 个任务出现负提升（归档：`topics/eval/2026-10-28.md`）
- **TestJack**：[arXiv 2610.10619](https://arxiv.org/abs/2610.10619)。重审 SkillsBench 等基准的通过轨迹，推翻 34.4% 假阳性，说明评测器本身要审计（归档：`topics/eval/2026-10-24.md`）
- **HPCAgent-Bench**：[arXiv 2610.20673](https://arxiv.org/abs/2610.20673)、[代码](https://github.com/spcl/HPCAgent-Bench)。Agent、Harness、Skill 的单变量受控对比，40 组实验里注入 Skill 仅 2 组显著改变加速比（归档：`topics/eval/2026-10-24.md`）
- **Dialpad 客服 Skill 评测**：[arXiv 2610.14346](https://arxiv.org/abs/2610.14346)。80 个 Skill、500 场景，规则检查与 LLM 裁判结果差距大，裁判间 κ 仅 0.524（归档：`topics/eval/2026-10-24.md`）
- **法律基准勘误登记**：[1331labs/legal-ai-errata](https://github.com/1331labs/legal-ai-errata)。对公开的法律基准、Skill 与模板提交 16 条更正，演示如何维护评测资产（归档：`topics/eval/2026-10-27.md`）

## 二、Skill 会不会被触发、检索和用对
- **Skill-Use、SkillRouter、MCRI-Eval、SkillCraft**：[arXiv 2608.04828](https://arxiv.org/abs/2608.04828)、[2603.22455](https://arxiv.org/abs/2603.22455)、[2610.01506](https://arxiv.org/abs/2610.01506)、[2603.00718](https://arxiv.org/abs/2603.00718)。触发、路由、使用、沉淀复用各测一块；SkillRouter 去掉正文后路由准确率掉 31–44 个百分点（归档：`topics/eval/2026-10-28.md`）
- **SkillRet**：[arXiv 2605.05726](https://arxiv.org/abs/2605.05726)。16,129 个 Skill 的检索评测（归档：`topics/eval/2026-10-28.md`）
- **Graph-of-Skills**：[ACL Anthology](https://aclanthology.org/2026.emnlp-main.2614/)。EMNLP 2026，依赖感知的 Skill 检索（归档：`topics/eval/2026-10-28.md`）
- **Skill 评测综述**：[arXiv 2606.11435](https://arxiv.org/abs/2606.11435)。把基准分六类，列出现有评测的缺口（归档：`topics/eval/2026-10-28.md`）

## 三、Skill 安不安全
- **MaliciousSkillBench**：[arXiv 2608.19901](https://arxiv.org/abs/2608.19901)。9,740 个 Skill 的恶意检测基准，现有检测器没有「高召回加低误报」的方案（归档：`related/skills/2026-10-25.md`）

## 四、评测工具（可接 CI）
- **skillgrade**：[mgechev/skillgrade](https://github.com/mgechev/skillgrade)。确定性检查加 LLM rubric，可设阈值卡 CI
- **skill-up**：[alibaba/skill-up](https://github.com/alibaba/skill-up)。YAML 定义环境与用例，兼容 evals.json
- **waza**：[microsoft/waza](https://github.com/microsoft/waza)。行为与工具序列打分器
- **agent-skill-evals**：[akshay5995/agent-skill-evals](https://github.com/akshay5995/agent-skill-evals)。基于 Promptfoo 验证路由
- **skillet**：[render-lab/skillet](https://github.com/render-lab/skillet)。在 PR 里评论评测报告
- **skillvitals**：[ContextJet-ai/skillvitals](https://github.com/ContextJet-ai/skillvitals)。触发 F1 与有无 Skill 胜率
- **agent-skills-eval**：[darkrishabh/agent-skills-eval](https://github.com/darkrishabh/agent-skills-eval)。with_skill 对 without_skill 双轨基线，含邻近负例
- **SkillEvaluator**：[NVIDIA/SkillEvaluator](https://github.com/NVIDIA/SkillEvaluator)。静态与安全检查、重复检测、沙箱有无对比
- **agent-skill-eval**：[tardigrde/agent-skill-eval](https://github.com/tardigrde/agent-skill-eval)。跑真实 Claude Code、Codex、OpenCode，支持 pass@k 与不应触发的负例
- **Skillmark**：[skillmark.sh](https://skillmark.sh)。公开排行榜

以上工具的归档位置：`topics/eval/2026-10-28.md`，agent-skills-eval 在 `related/skills/2026-10-24.md`。

## 五、官方文章与实践指南
- **OpenAI：用 evals 系统化测试 Agent Skills**：[文章](https://developers.openai.com/blog/eval-skills)（归档：`related/skills/2026-10-24.md`）
- **LangChain：Evaluating Skills**：[文章](https://www.langchain.com/blog/evaluating-skills)（归档：`related/skills/2026-10-24.md`）
- **Phil Schmid：测试 Agent Skills 实战**：[文章](https://www.philschmid.de/testing-skills)（归档：`related/skills/2026-10-24.md`）
- **Anthropic：skill-creator 的测试、度量与改进**：[文章](https://claude.com/resources/articles/improving-skill-creator-test-measure-and-refine-agent-skills)（归档：`topics/eval/2026-10-28.md`）
- **Anthropic：把子 Agent 折叠进单 Agent 加 Skills，并用 eval 对比**：[文章](https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop)、[single-agent-loop-kit](https://github.com/anthropics/single-agent-loop-kit)（归档：`related/skills/2026-10-25.md`）
- **UiPath skills 的触发评测说明**：[UiPath/skills](https://github.com/UiPath/skills)（归档：`topics/eval/2026-10-28.md`）

## 六、据 X 上的报道
- [Dan Kornas 介绍 skill-up](https://x.com/DanKornas/status/2113860880592966054)，用 YAML 让 Skill 失败可复现。
- [ClaudeDevs 关于 Agent Skills 标准捐给 Agentic AI Foundation](https://x.com/ClaudeDevs/status/2113328526413996100)。

## 七、本仓库里的相关原型与图表（演示数据，不是真实评测结果）
- `projects/swe-together-leaderboard-replica/`：SWE-Together 的 Skill 榜与单任务页复刻。
- `projects/harness-model-demo/`：Harness × 模型的 Skill 榜演示图。
- `projects/skill-effectiveness-charts/`：Skill Effectiveness 图的脚本、数据和成品图。
- `references/swe-together/`：SWE-Together 论文，里面有 Skill 维度的评测设计。

## 待补
- 还有几个名字只在搜索结果里见过，没打开核对，所以没收：SkillLearnBench、SRA-Bench、AgentSkillOS、SkillTester。
- 还没有用这些工具实际评测过我们自己的 Skill。
