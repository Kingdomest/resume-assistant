# 简历 ReAct 双 Agent 产品设计方案

## 1. 产品定位

本项目是一个面向求职场景的简历定制优化工具。用户上传自己的简历文件，或直接粘贴简历文本，并粘贴目标公司的岗位 JD，系统通过 ReAct 思想驱动两个 Agent 协作：

- 决策 Agent：负责诊断问题、制定优化计划、评估结果、控制迭代。
- 行动 Agent：负责执行具体改写，包括技能重构、项目 STAR 化、JD 定制化、面试问题预测。

第一版重点验证核心链路：打开 Vue 前端页面 -> 上传简历或粘贴简历文本 -> 输入岗位诉求和 JD -> 解析文本 -> 决策分析 -> 行动改写 -> 评估迭代 -> 以对话形式输出思考摘要、定制简历和面试预测问题。

## 2. 用户场景

用户输入示例：

```text
目标：我想投字节跳动的后端开发岗
JD：这里粘贴字节后端开发岗位介绍
简历：上传 PDF/Word 文档，或直接粘贴简历文本
```

前端交互：

```text
用户在一个简洁的对话输入区中输入目标岗位和 JD，通过文件上传按钮上传简历，或在简历文本框中粘贴简历内容，然后点击发送按钮开始优化。
```

系统输出：

```text
1. 简历问题诊断
2. JD 匹配度分析
3. 优化计划和优先级
4. 每一轮 ReAct 思考摘要、行动、观察、评估过程
5. 最终定制版简历
6. 面试预测问题
```

## 3. 第一版范围

### 必须支持

- 支持上传简历文件。
- 支持用户不上传文件，直接粘贴简历文本。
- 支持 PDF 简历解析。
- 支持 Word 简历解析，第一版优先支持 `.docx`。
- 支持用户粘贴目标岗位 JD。
- 支持 DeepSeek 模型调用。
- 支持 Vue 前端页面。
- 支持类似对话助手的输入体验：JD 输入框、简历文本输入框、文件上传按钮、发送按钮。
- 前端去掉“深度思考/深度搜索”和“智能搜索”开关，只保留本产品需要的简历上传和发送。
- 支持以对话消息形式展示用户请求、Agent 思考摘要和最终回答。
- 支持两个 Agent 协作：
  - `DecisionAgent`
  - `ActionAgent`
- 支持折中版 ReAct 优化：一次诊断调用 + 一次综合生成调用。
- 支持输出完整 ReAct 过程日志。
- 支持输出最终简历 Markdown 文本。
- 支持输出面试预测问题。

### 暂不支持

- 暂不做账号系统。
- 暂不做在线支付。
- 暂不自动抓取招聘网站 JD。
- 暂不保证 PDF/Word 的原始排版完全还原。
- 暂不直接导出 Word/PDF 成品文件，第一版先输出 Markdown。
- 暂不支持历史版本管理。
- 暂不做复杂富文本简历编辑器。
- 暂不展示模型原始隐式推理链，只展示系统整理后的 Agent 思考摘要和执行轨迹。

## 4. 文件上传与解析设计

上传与输入模块负责接收用户简历文件或粘贴的简历文本，并统一转换为纯文本，供 Agent 使用。

支持格式：

| 格式 | 第一版策略 | 说明 |
|---|---|---|
| `.pdf` | 支持 | 提取页面文本，适合文本型 PDF |
| `.docx` | 支持 | 提取段落、表格中的文本 |
| `.doc` | 延后 | 老格式解析复杂，后续可用 LibreOffice 转换为 `.docx` |

解析后的统一结果：

```python
ParsedResume:
    file_name: str
    file_type: str
    raw_text: str
    warnings: list[str]
```

当用户没有上传文件但提供 `resume_text` 时，系统直接构造 `ParsedResume(file_type="text")`，不经过文件解析器。

解析失败时，系统不进入 Agent 流程，而是返回明确错误：

- 文件格式不支持。
- 文件为空。
- PDF 无可提取文本，可能是扫描件。
- Word 文档解析失败。

## 5. 前端页面设计

第一版前端使用 Vue 实现一个单页对话界面。页面风格应简洁、大气、美观，参考用户提供的输入框样式，但去掉“深度思考”和“智能搜索”两个功能按钮。

### 5.1 页面结构

页面分为三块：

```text
顶部区域：产品名称和轻量状态提示
中间区域：对话消息流
底部区域：固定输入框，包含文本输入、文件上传、发送按钮
```

首屏不做营销式落地页，用户进入后直接看到可用的对话工作区。

### 5.2 输入区设计

输入区接近用户提供的截图：

- 一个圆角较大的白色输入容器。
- JD 输入框 placeholder 示例：`粘贴目标岗位 JD，或描述你想投递的岗位`。
- 简历文本框 placeholder 示例：`可选：未上传文件时，在这里粘贴简历内容`。
- 左下或右侧放文件上传按钮，使用回形针图标。
- 右侧放圆形发送按钮，使用向上箭头图标。
- 上传文件后，在输入框上方或内部显示文件 chip，例如：`我的简历.pdf`。
- 支持删除已上传文件。
- 不展示“深度思考”和“智能搜索”按钮。

### 5.3 对话输出设计

对话消息分为三类：

| 类型 | 展示方式 |
|---|---|
| 用户消息 | 展示用户输入的岗位诉求、JD 摘要和简历来源（上传文件名或已粘贴简历内容） |
| Agent 思考摘要 | 展示 DecisionAgent / ActionAgent 的可解释思考摘要、行动和观察 |
| 最终回答 | 展示优化后的简历、修改说明和面试预测问题 |

Agent 思考内容不展示模型原始隐藏推理链，而展示产品化整理后的 ReAct 轨迹：

```text
DecisionAgent 正在分析简历与 JD 的差距
Action: analyze_resume_gap
Observation: 技能表达偏泛，项目缺少量化结果，JD 关键词覆盖不足
```

折中版 Agent 过程可以做成可展开的消息块：

```text
DecisionAgent：诊断简历与 JD 差距，并选择综合优化路径
ActionAgent：一次性完成技能重构、项目 STAR 化、JD 定制简历和面试题预测
```

### 5.4 视觉风格

视觉方向：

- 背景使用接近白色或极浅灰色。
- 主内容宽度控制在 760px 到 920px，保证阅读舒适。
- 输入框固定在底部，移动端保持可用。
- 使用轻量边框、柔和阴影和清晰间距。
- 主色使用温和蓝紫作为小面积强调，辅以中性灰和少量绿色状态色，避免整页变成单一蓝紫风格。
- 文本层级清晰，不使用厚重卡片堆叠。
- 所有按钮使用图标加 tooltip 或简短说明。

推荐组件：

```text
ChatPage.vue
MessageList.vue
ChatMessage.vue
Composer.vue
FileUploadButton.vue
ThoughtTimeline.vue
OptimizedResumePanel.vue
InterviewQuestionsPanel.vue
```

### 5.5 前端状态

前端维护以下状态：

```typescript
type ChatState = {
  messages: ChatMessage[]
  inputText: string
  selectedFile: File | null
  isSubmitting: boolean
  errorMessage: string | null
}
```

消息结构：

```typescript
type ChatMessage = {
  id: string
  role: 'user' | 'assistant' | 'system'
  kind: 'request' | 'thought' | 'answer' | 'error'
  content: string
  createdAt: string
}
```

## 6. DeepSeek 接入设计

第一版模型层只支持 DeepSeek，但代码结构保留模型可替换能力。

抽象接口：

```python
class LLMProvider:
    def generate(self, messages: list[dict], temperature: float = 0.3) -> str:
        ...
```

DeepSeek 实现：

```python
class DeepSeekProvider(LLMProvider):
    def generate(self, messages: list[dict], temperature: float = 0.3) -> str:
        ...
```

配置项：

```text
DEEPSEEK_API_KEY=用户自己的 DeepSeek API Key
DEEPSEEK_BASE_URL=DeepSeek API 地址
DEEPSEEK_MODEL=默认模型名
```

设计原则：

- Agent 不直接依赖 DeepSeek SDK 或 HTTP 细节。
- 所有模型调用经过 `LLMProvider`。
- Prompt 单独放在 `prompts.py` 或 `prompts/` 目录。
- 模型调用失败时返回可解释错误，不吞掉异常。

## 7. Agent 分工

### 7.1 DecisionAgent

职责：

- 分析简历与 JD 的差距。
- 判断简历中的主要问题。
- 制定优化计划。
- 决定每一轮交给 ActionAgent 做什么。
- 评估 ActionAgent 的输出质量。
- 判断是否继续迭代。

典型思考：

```text
我需要先判断简历与后端 JD 的匹配度。当前简历的问题可能集中在技能表达、项目量化和 JD 关键词覆盖。
```

典型行动：

```text
Action: analyze_resume_gap
Action: create_optimization_plan
Action: evaluate_optimized_resume
```

### 7.2 ActionAgent

职责：

- 按 DecisionAgent 给出的任务执行具体优化。
- 在折中版流程中一次性完成技能描述重构、项目经历 STAR 化、JD 定制简历和面试预测问题。

典型思考：

```text
当前任务是综合优化简历，我需要把空泛表述变成后端岗位关注的技术能力，同时补充 STAR 结构、JD 关键词和面试预测问题。
```

典型行动：

```text
Action: generate_resume_and_interview_questions
```

## 8. ReAct 工作流

整体流程：

```text
Vue 前端收集用户输入 + 用户上传简历
        ↓
DocumentParser 解析简历文本
        ↓
DecisionAgent 思考并诊断问题
        ↓
DecisionAgent 制定折中版综合优化计划
        ↓
ActionAgent 一次性生成定制简历 + 面试预测问题
        ↓
输出最终简历 + 面试预测问题
```

每轮格式：

```text
[DecisionAgent Thought] 分析当前问题和下一步优先级。
[DecisionAgent Action] choose_next_action
[DecisionAgent Observation] 下一步应优化项目经历。

[ActionAgent Thought] 需要将项目经历改写成 STAR 结构。
[ActionAgent Action] rewrite_projects_with_star
[ActionAgent Observation] 已生成新版项目经历。

[DecisionAgent Thought] 检查新版项目经历是否量化、是否覆盖 JD 关键词。
[DecisionAgent Action] evaluate_result
[DecisionAgent Observation] 仍缺少性能指标，进入下一轮。
```

停止条件：

- 已完成所有计划步骤。
- ActionAgent 已生成定制简历和面试预测问题。
- 模型调用失败且无法恢复。

## 9. 质量评估规则

DecisionAgent 每轮评估时检查：

| 维度 | 说明 |
|---|---|
| JD 关键词覆盖 | 是否覆盖岗位要求中的核心技术栈 |
| 技能表达质量 | 是否从空泛描述变成具体能力 |
| 项目量化程度 | 是否有指标、规模、性能、结果 |
| STAR 完整度 | 是否体现 Situation、Task、Action、Result |
| 岗位匹配度 | 是否像是为该岗位定制，而不是通用简历 |
| 真实性风险 | 是否编造过强、过假的经历 |

评估结果结构：

```python
EvaluationResult:
    score: int
    covered_issues: list[str]
    remaining_issues: list[str]
    should_continue: bool
    feedback: str
```

## 10. 输出设计

最终输出以对话形式呈现，包含四部分。

### 10.1 简历诊断报告

```text
发现的问题：
1. 技能描述偏空泛，缺少 Java、MySQL、Redis、消息队列等后端岗位关键词的具体使用场景。
2. 项目经历没有量化结果，无法体现性能优化或业务价值。
3. 与字节后端 JD 的匹配点没有被突出展示。
```

### 10.2 优化过程日志

展示每一轮的可解释 Thought 摘要、Action、Observation 和 Evaluation。

### 10.3 定制版简历

输出 Markdown 格式：

```markdown
## 个人优势
## 技术栈
## 项目经历
## 教育经历
## 其他
```

### 10.4 面试预测问题

按类型输出：

- Java / Go / Python 后端基础。
- 数据库与索引。
- Redis 与缓存一致性。
- 消息队列。
- 分布式系统。
- 项目深挖。
- 行为面试问题。

## 11. 推荐技术结构

第一版采用 Vue 前端 + Python FastAPI 后端。前端负责上传、输入和对话展示，后端负责文件解析、Agent 工作流和 DeepSeek 调用。

推荐结构：

```text
frontend/
    package.json
    vite.config.ts
    src/
        main.ts
        App.vue
        api/
            resumeOptimizer.ts
        components/
            ChatPage.vue
            MessageList.vue
            ChatMessage.vue
            Composer.vue
            FileUploadButton.vue
            ThoughtTimeline.vue
            OptimizedResumePanel.vue
            InterviewQuestionsPanel.vue
        styles/
            main.css
backend/
    react_resume/
        __init__.py
        app.py
        config.py
        models.py
        parsers.py
        llm.py
        prompts.py
        agents.py
        workflow.py
        output.py
tests/
    test_parsers.py
    test_workflow.py
    test_agents.py
docs/
    design/
        resume-react-agent-design.md
    plan/
```

模块职责：

| 模块 | 职责 |
|---|---|
| `frontend/src/components/ChatPage.vue` | 对话页主容器 |
| `frontend/src/components/Composer.vue` | 输入框、文件上传、发送按钮 |
| `frontend/src/components/MessageList.vue` | 消息流展示 |
| `frontend/src/components/ThoughtTimeline.vue` | Agent 思考摘要和执行轨迹 |
| `frontend/src/api/resumeOptimizer.ts` | 调用后端优化接口 |
| `backend/react_resume/app.py` | Web API 入口，处理上传和请求 |
| `backend/react_resume/config.py` | 读取 DeepSeek 配置 |
| `backend/react_resume/models.py` | 定义数据结构 |
| `backend/react_resume/parsers.py` | PDF / DOCX 简历解析 |
| `backend/react_resume/llm.py` | DeepSeek 模型调用封装 |
| `backend/react_resume/prompts.py` | Agent 提示词模板 |
| `backend/react_resume/agents.py` | DecisionAgent 和 ActionAgent |
| `backend/react_resume/workflow.py` | 控制 ReAct 多轮迭代 |
| `backend/react_resume/output.py` | 整理最终输出 |

## 12. API 草案

第一版接口：

```text
POST /api/optimize-resume
```

请求：

```text
multipart/form-data

resume_file: PDF 或 DOCX 文件，可选
resume_text: 粘贴的简历文本，可选
target_company: 目标公司，例如字节跳动
target_role: 目标岗位，例如后端开发
jd_text: 岗位 JD
```

`resume_file` 与 `resume_text` 至少提供一个；两者都存在时优先使用 `resume_file`。

响应：

第一版可以返回完整 JSON，前端收到后按消息类型渲染成对话。

```json
{
  "diagnosis": "...",
  "react_trace": [
    {
      "round": 1,
      "agent": "DecisionAgent",
      "thought": "分析简历与 JD 的差距",
      "action": "analyze_resume_gap",
      "observation": "发现技能表达偏泛，项目缺少量化结果"
    }
  ],
  "optimized_resume": "...",
  "interview_questions": ["..."],
  "warnings": []
}
```

后续如果要做更强的实时体验，可把接口升级为 NDJSON 或 SSE 流式响应：

```json
{"type":"thought","agent":"DecisionAgent","content":"正在分析简历与 JD 的差距"}
{"type":"thought","agent":"ActionAgent","content":"正在重写技能模块"}
{"type":"answer","content":"最终优化后的简历 Markdown"}
```

## 13. 安全与真实性边界

简历优化不能无边界编造经历。系统应遵守以下原则：

- 可以优化表达，但不能主动虚构学历、公司、项目、奖项。
- 可以把已有经历改写得更具体，但缺失数据时要用占位提示用户补充。
- 对模型生成的量化指标，需要标记为“建议补充真实数据”。
- 面试预测问题基于 JD 和简历生成，不承诺覆盖真实面试全部内容。
- 前端展示的“思考”是 Agent 执行摘要，不展示模型原始隐藏推理链。

## 14. 第一版验收标准

第一版完成后应满足：

- 用户可以打开 Vue 前端页面。
- 页面包含一个简洁大气的对话输入框、文件上传按钮和发送按钮。
- 页面不展示“深度思考/深度搜索”和“智能搜索”功能。
- 用户可以在对话框中输入目标公司、目标岗位和 JD。
- 用户可以上传 PDF/DOCX 简历，或直接粘贴简历文本。
- 系统可以解析或接收简历文本。
- 系统通过 DeepSeek 生成诊断、优化计划、定制简历和面试题。
- 前端以对话形式展示用户请求、Agent 思考摘要、行动过程和最终回答。
- 折中版一次请求使用 2 次模型调用，减少等待时间。
- 模型失败、文件格式错误、解析失败时有明确错误信息。

## 15. 后续扩展

- 支持拖拽上传。
- 支持流式输出 Agent 执行过程。
- 支持导出 `.docx` 和 `.pdf`。
- 支持多版本对比。
- 支持 JD 自动抓取。
- 支持更多模型提供商。
- 支持扫描版 PDF 的 OCR。
- 支持简历真实性检查和风险提示。
