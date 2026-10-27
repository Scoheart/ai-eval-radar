# Skills 评测

Skill（SKILL.md）评测的相关来源，一行一条，格式是「标题 描述 【平台：链接；平台：链接】」，同一条有多个平台就在同一个【】里用分号分隔，链接都核对过能打开。每条的要点和摘要在本仓库 `topics/eval/`、`related/skills/` 的同日期文件里。

## 一、Skill 有没有用
- **SkillsBench 1.1** 带与不带 Skill 配对实跑，平均通过率 33.9% → 50.5%，13 个任务负提升 【官网：https://www.skillsbench.ai/blogs/skillsbench-1-1；arXiv：https://arxiv.org/abs/2602.12670；Hugging Face 数据集：https://huggingface.co/datasets/benchflow/skillsbench；Hugging Face 榜单：https://huggingface.co/datasets/benchflow/skillsbench-leaderboard】
- **TestJack** 重审 SkillsBench 等基准的通过轨迹，推翻 34.4% 假阳性 【arXiv：https://arxiv.org/abs/2610.10619】
- **HPCAgent-Bench** Agent、Harness、Skill 单变量受控对比 【arXiv：https://arxiv.org/abs/2610.20673；GitHub：https://github.com/spcl/HPCAgent-Bench】
- **Dialpad 客服 Skill 评测** 规则检查与 LLM 裁判结果差距大 【arXiv：https://arxiv.org/abs/2610.14346】
- **legal-ai-errata** 法律基准、Skill 与模板的公开勘误登记 【GitHub：https://github.com/1331labs/legal-ai-errata】
- **Tessl Skills Evaluation Dataset** 1,110 个任务、608 个 Skill、148 个 GitHub 仓库，单 Skill 与多 Skill 组合两类，带两份 LLM 裁判评分表 【Hugging Face 数据集：https://huggingface.co/datasets/tesslio/task-evals-for-skills】

## 二、Skill 会不会被触发、检索和用对
- **Skill-Use** 触发、遵循流程、不越界分开评，79 个 Skill、177 个任务 【arXiv：https://arxiv.org/abs/2608.04828】
- **SkillRouter** 约 8 万 Skill 的路由基准，去掉正文后准确率掉 31–44 个百分点 【arXiv：https://arxiv.org/abs/2603.22455】
- **MCRI** 四维度框架分析与评测 Agent Skills，对 63,812 个 Skill 做执行前打分 【arXiv：https://arxiv.org/abs/2610.01506】
- **SkillCraft** 测 LLM Agent 能否沉淀并复用 Skill 【arXiv：https://arxiv.org/abs/2603.00718】
- **SkillRet** 16,129 个 Skill 的检索评测 【arXiv：https://arxiv.org/abs/2605.05726】
- **Graph-of-Skills** EMNLP 2026，依赖感知的 Skill 检索 【ACL Anthology：https://aclanthology.org/2026.emnlp-main.2614/】
- **Skill 评测综述** 把基准分六类并列出缺口 【arXiv：https://arxiv.org/abs/2606.11435】

## 三、Skill 安不安全
- **MaliciousSkillBench** 9,740 个 Skill 的恶意检测基准 【arXiv：https://arxiv.org/abs/2608.19901】

## 四、评测工具
- **skillgrade** 确定性检查加 LLM rubric，可卡 CI 【GitHub：https://github.com/mgechev/skillgrade】
- **skill-up** YAML 定义环境与用例 【GitHub：https://github.com/alibaba/skill-up；X：https://x.com/DanKornas/status/2113860880592966054】
- **waza** 行为与工具序列打分器 【GitHub：https://github.com/microsoft/waza】
- **agent-skill-evals** 基于 Promptfoo 验证路由 【GitHub：https://github.com/akshay5995/agent-skill-evals】
- **skillet** 在 PR 里评论评测报告 【GitHub：https://github.com/render-lab/skillet】
- **skillvitals** 触发 F1 与有无 Skill 胜率 【GitHub：https://github.com/ContextJet-ai/skillvitals】
- **agent-skills-eval** 有无 Skill 双轨基线 【GitHub：https://github.com/darkrishabh/agent-skills-eval】
- **SkillEvaluator** 静态与安全检查、沙箱有无对比 【GitHub：https://github.com/NVIDIA/SkillEvaluator】
- **agent-skill-eval** 跑真实 Claude Code、Codex、OpenCode 【GitHub：https://github.com/tardigrde/agent-skill-eval】
- **Skillmark** 公开排行榜 【官网：https://skillmark.sh】
- **skillbench（boheling）** 有无 Skill 对抗基准，同一份确定性脚本评分，另含安全静态扫描 【GitHub：https://github.com/boheling/skillbench】
- **skilljack-evals** SkillsBench 风格任务包，真实 agent 跑，带 pass@k、Skill Lift、调用率，可按阈值卡 CI 【GitHub：https://github.com/olaservo/skilljack-evals】
- **skill-eval-harness** 度量 Skill 的因果提升，含防答案泄漏检查与 holdout 切分 【GitHub：https://github.com/adewale/skill-eval-harness】
- **sample-agent-skill-eval（AWS）** 安全、质量、触发可靠性、成本效率四个维度，带回归基线 【GitHub：https://github.com/aws-samples/sample-agent-skill-eval】
- **agent-skills evals（Addy Osmani）** 结构校验、触发与路由、行为三层评测 【GitHub：https://github.com/addyosmani/agent-skills/blob/main/evals/README.md】
- **agent-harness 的 skill-evals** 触发评测与质量评测的格式和评分方法 【GitHub：https://github.com/Phoenixrr2113/agent-harness/blob/main/docs/skill-evals.md】
- **skill-evaluator（materials-simulation-skills）** 脚本检查、触发、质量三层方法论 【GitHub：https://github.com/heshamfs/materials-simulation-skills】

## 五、官方文章与实践指南
- **OpenAI：用 evals 系统化测试 Agent Skills** 【官网：https://developers.openai.com/blog/eval-skills】
- **LangChain：Evaluating Skills** 【官网：https://www.langchain.com/blog/evaluating-skills】
- **Phil Schmid：测试 Agent Skills 实战** 【博客：https://www.philschmid.de/testing-skills】
- **Anthropic：skill-creator 的测试、度量与改进** 【官网：https://claude.com/resources/articles/improving-skill-creator-test-measure-and-refine-agent-skills】
- **Anthropic：把子 Agent 折叠进单 Agent 加 Skills** 【官网：https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop；GitHub：https://github.com/anthropics/single-agent-loop-kit】
- **UiPath/skills** 把触发当二分类评测 【GitHub：https://github.com/UiPath/skills】
- **Agent Skills 标准捐给 Agentic AI Foundation** 据 X 上的 ClaudeDevs 【X：https://x.com/ClaudeDevs/status/2113328526413996100】
- **OpenHands：How to Evaluate Agent Skills** 有无 Skill 基线加确定性验证，再用 trace 解释失败 【官网：https://www.openhands.dev/blog/evaluating-agent-skills】
- **Agent Skills 规范：优化技能描述** 官方给的触发评测方法，约 20 条查询各跑 3 次，触发率阈值 0.5 【官网：https://agentskills.io/skill-creation/optimizing-descriptions】
- **掘金：Agent Skill Eval，从触发信号到 A/B 基准** 把 Skill 做成可回归的工程单元 【掘金：https://juejin.cn/post/7654922935040229391】
- **Richard's Page：Agent Skill 的评测工程实践** 用例区分度、验证条件拆细、结果与过程两类断言 【博客：https://richardwang.me/docs/ai/applications/building-skill-evaluation-framework】

## 六、X 上的讨论
- **Sergii Makarevych：How to write and test agent skills with evals** 长文，讲如何自写 Skill 并验证外部 Skill 是否真有帮助（据 X 上的报道） 【X：https://x.com/sermakarevich/status/2112198653469241856】
- **SEOAgent：SEO Skill 基准更新** 给 seo-skills 打 63.4 综合分，扣分主要在陷阱规避 73%（据 X 上的报道） 【X：https://x.com/SEOAgent_/status/2110737153785258249】
- **windy_brook：kfp-generator 的 with-skill 对 without-skill A/B 测试** 用评测验证 Skill 写 pipeline 的可靠性（据 X 上的报道） 【X：https://x.com/windy_brook2001/status/2110412312901554273】
- **Skill Gate 作者：用决策模型做 Skill 评测** 提到客服 Skill 声称已退款却没执行的案例（据 X 上的报道） 【X：https://x.com/VigneshM865791/status/2114101491719893084】

## 七、仓库内的原型与图表（演示数据，不是真实评测结果）
- **SWE-Together 排行榜复刻** 【仓库：projects/swe-together-leaderboard-replica/】
- **Harness × 模型演示** 【仓库：projects/harness-model-demo/】
- **Skill 有效性图表** 【仓库：projects/skill-effectiveness-charts/】
- **SWE-Together 参考资料** 【仓库：references/swe-together/】

## 待补
- SkillLearnBench、SRA-Bench、AgentSkillOS、SkillTester 只在搜索结果里见过，没核对，未收
