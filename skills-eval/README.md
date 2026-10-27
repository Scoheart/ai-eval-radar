# Skills 评测

Skill（SKILL.md）评测的相关来源，一行一个，链接都核对过能打开。每条的要点和摘要在本仓库 `topics/eval/`、`related/skills/` 的同日期文件里。

## 一、Skill 有没有用
- **SkillsBench 1.1**：带与不带 Skill 配对实跑，平均通过率 33.9% → 50.5%，13 个任务负提升 [博客：https://www.skillsbench.ai/blogs/skillsbench-1-1]
- **TestJack**：重审 SkillsBench 等基准的通过轨迹，推翻 34.4% 假阳性 [arXiv：https://arxiv.org/abs/2610.10619] [X：https://x.com/eliotleu/status/2110345815046967572]
- **HPCAgent-Bench**：Agent、Harness、Skill 单变量受控对比，注入 Skill 仅 2/40 组显著改变加速比 [arXiv：https://arxiv.org/abs/2610.20673] [GitHub：https://github.com/spcl/HPCAgent-Bench]
- **Dialpad 客服 Skill 评测**：规则检查与 LLM 裁判结果差距大，裁判间 κ 仅 0.524 [arXiv：https://arxiv.org/abs/2610.14346]
- **legal-ai-errata**：法律基准、Skill 与模板的公开勘误登记 [GitHub：https://github.com/1331labs/legal-ai-errata]

## 二、Skill 会不会被触发、检索和用对
- **Skill-Use**：触发、遵循流程、不越界分开评 [arXiv：https://arxiv.org/abs/2608.04828]
- **Skill 路由/使用评测（2603.22455）**：路由与使用类基准 [arXiv：https://arxiv.org/abs/2603.22455]
- **Skill 路由/使用评测（2610.01506）**：路由与使用类基准 [arXiv：https://arxiv.org/abs/2610.01506]
- **Skill 路由/使用评测（2603.00718）**：路由与使用类基准 [arXiv：https://arxiv.org/abs/2603.00718]
- **SkillRet**：16,129 个 Skill 的检索评测 [arXiv：https://arxiv.org/abs/2605.05726]
- **Graph-of-Skills**：依赖感知的 Skill 检索，EMNLP 2026 [ACL Anthology：https://aclanthology.org/2026.emnlp-main.2614/]
- **Skill 评测综述**：把基准分六类并列出缺口 [arXiv：https://arxiv.org/abs/2606.11435]

## 三、Skill 安不安全
- **MaliciousSkillBench**：9,740 个 Skill 的恶意检测基准 [arXiv：https://arxiv.org/abs/2608.19901]

## 四、评测工具
- **skillgrade**：确定性检查加 LLM rubric，可卡 CI [GitHub：https://github.com/mgechev/skillgrade]
- **skill-up**：YAML 定义环境与用例，让 Skill 失败可复现 [GitHub：https://github.com/alibaba/skill-up] [X：https://x.com/DanKornas/status/2113860880592966054]
- **waza**：行为与工具序列打分器 [GitHub：https://github.com/microsoft/waza]
- **agent-skill-evals**：基于 Promptfoo 验证路由 [GitHub：https://github.com/akshay5995/agent-skill-evals]
- **skillet**：在 PR 里评论评测报告 [GitHub：https://github.com/render-lab/skillet]
- **skillvitals**：触发 F1 与有无 Skill 胜率 [GitHub：https://github.com/ContextJet-ai/skillvitals]
- **agent-skills-eval**：有无 Skill 双轨基线，含邻近负例 [GitHub：https://github.com/darkrishabh/agent-skills-eval]
- **SkillEvaluator**：静态与安全检查、沙箱有无对比 [GitHub：https://github.com/NVIDIA/SkillEvaluator]
- **agent-skill-eval**：跑真实 Claude Code、Codex、OpenCode，支持 pass@k [GitHub：https://github.com/tardigrde/agent-skill-eval]
- **Skillmark**：公开排行榜 [网站：https://skillmark.sh]

## 五、官方文章与实践指南
- **OpenAI：用 evals 系统化测试 Agent Skills**：显式、隐式、带噪触发与负例测试集 [博客：https://developers.openai.com/blog/eval-skills]
- **LangChain：Evaluating Skills**：多 Skill 共存下的触发与误调 [博客：https://www.langchain.com/blog/evaluating-skills]
- **Phil Schmid：测试 Agent Skills 实战**：Skill 测试流程与指标 [博客：https://www.philschmid.de/testing-skills]
- **Anthropic：skill-creator 的测试、度量与改进**：用测试迭代 Skill [文章：https://claude.com/resources/articles/improving-skill-creator-test-measure-and-refine-agent-skills] [X：https://x.com/ClaudeDevs/status/2113328526413996100]
- **Anthropic：子 Agent 折叠进单 Agent 加 Skills**：用同一套 eval 前后对比再决定去留 [文章：https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop] [GitHub：https://github.com/anthropics/single-agent-loop-kit]
- **UiPath/skills**：把触发当二分类评测 [GitHub：https://github.com/UiPath/skills]

## 六、仓库内的原型与图表（演示数据，不是真实评测结果）
- **SWE-Together 排行榜复刻**：Skill 榜与单任务页 [仓库：projects/swe-together-leaderboard-replica/]
- **Harness × 模型 Skill 榜**：演示图 [仓库：projects/harness-model-demo/]
- **Skill Effectiveness 图**：脚本、数据与成品图 [仓库：projects/skill-effectiveness-charts/]

## 待补
- **SkillLearnBench、SRA-Bench、AgentSkillOS、SkillTester**：只在搜索结果里见过，没核对，未收
