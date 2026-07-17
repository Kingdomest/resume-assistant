# Resume ReAct Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Vue + FastAPI MVP that lets users upload a PDF/DOCX resume or paste resume text, paste a target JD, and receive a chat-style ReAct optimization result powered by DeepSeek.

**Architecture:** The frontend is a Vue single-page chat workspace with a bottom composer, file upload, message stream, and structured assistant result panels. The backend is a FastAPI service that parses uploaded resumes, calls a DeepSeek-backed LLM provider, runs `DecisionAgent` and `ActionAgent` through a three-round ReAct workflow, and returns structured JSON for the frontend to render. File parsing, LLM access, prompts, agents, workflow orchestration, and output formatting stay in separate modules.

**Tech Stack:** Vue 3, Vite, TypeScript, lucide-vue-next, FastAPI, Pydantic, httpx, pypdf, python-docx, pytest, Vitest.

---

## Source Design

Use the product design document as the contract for this plan:

```text
docs/design/resume-react-agent-design.md
```

## Module Map

```text
frontend/
    package.json                         # frontend scripts and dependencies
    vite.config.ts                       # Vite config and dev proxy
    tsconfig.json                        # TypeScript config
    index.html                           # Vite entry HTML
    src/
        main.ts                          # Vue app bootstrap
        App.vue                          # root component
        api/
            resumeOptimizer.ts           # POST /api/optimize-resume client
        components/
            ChatPage.vue                 # page-level chat orchestration
            MessageList.vue              # message stream
            ChatMessage.vue              # one message bubble / result block
            Composer.vue                 # text input, upload button, send button
            FileUploadButton.vue         # hidden file input and file chip behavior
            ThoughtTimeline.vue          # ReAct trace display
            OptimizedResumePanel.vue     # Markdown-style resume output
            InterviewQuestionsPanel.vue  # categorized question display
        styles/
            main.css                     # global layout, tokens, responsive rules
backend/
    requirements.txt                     # backend dependencies
    react_resume/
        __init__.py
        app.py                           # FastAPI app and route
        config.py                        # environment settings
        models.py                        # Pydantic request/response/domain models
        parsers.py                       # PDF/DOCX parser
        llm.py                           # LLMProvider and DeepSeekProvider
        prompts.py                       # prompt builders
        agents.py                        # DecisionAgent and ActionAgent
        workflow.py                      # three-round ReAct coordinator
        output.py                        # final response shaping
tests/
    backend/
        test_config.py
        test_models.py
        test_parsers.py
        test_llm.py
        test_agents.py
        test_workflow.py
        test_app.py
    frontend/
        Composer.test.ts
        MessageList.test.ts
        resumeOptimizer.test.ts
```

## Development Rules

- Keep the first version synchronous JSON-based; do not implement SSE until the JSON flow works.
- Do not expose raw model chain-of-thought. Return only productized `thought` summaries, `action`, and `observation`.
- Do not fabricate resume facts. When details are missing, instruct the user to provide real numbers or mark suggested metrics as requiring verification.
- Support `.pdf` and `.docx` in the first release. Treat legacy `.doc` as unsupported with a clear message.
- Use frequent commits if the project is under git. If there is no git repository, skip commit steps and record that in the task notes.

## 功能完成跟踪 Task Plan

说明：每完成并验证一个模块后，把对应条目的 `【 】` 改成 `【√】`。这里记录功能级完成情况，详细开发步骤见后续 `Task 1` 到 `Task 16`。

【√】后端服务骨架：创建 FastAPI 项目结构、依赖文件和 `/api/health` 健康检查接口。

【√】后端配置模块：读取 DeepSeek、文件大小限制和前端 CORS 来源等环境配置。

【√】领域数据模型：定义简历解析、Agent 轨迹、评估结果和优化响应的数据结构。

【√】简历文件解析：支持上传并解析 `.pdf` 和 `.docx`，对 `.doc` 和未知格式返回清晰错误。

【√】DeepSeek 模型接入：封装 `LLMProvider` 和 `DeepSeekProvider`，统一处理模型请求和异常。

【√】Prompt 模板模块：沉淀决策、行动和评估所需的提示词构造逻辑。

【√】双 Agent 核心：实现 `DecisionAgent` 和 `ActionAgent` 的分析、动作选择和执行能力。

【√】ReAct 工作流：串联诊断、折中版综合优化、面试题生成和最终响应组装，一次请求降为 2 次模型调用。

【√】简历优化 API：实现 `/api/optimize-resume`，接收文件或粘贴简历文本以及岗位信息，并返回结构化结果。

【√】粘贴简历文本：支持用户不上传 PDF/DOCX，直接复制简历内容发送给 AI。

【√】停止生成按钮：用户提交优化后，发送按钮切换为浅红色停止按钮，点击可中断当前前端请求并恢复输入状态。

【√】Vue 前端骨架：创建 Vite + Vue + TypeScript 项目入口和基础构建配置。

【√】前端 API 客户端：实现上传简历或粘贴简历文本和 JD 的 `multipart/form-data` 请求封装。

【√】输入与上传组件：实现简洁对话输入框、简历文本框、文件上传按钮、文件 chip 和发送按钮。

【√】消息展示组件：实现用户消息、助手消息、ReAct 轨迹、定制简历和面试题展示组件。

【√】对话页面集成：把输入、接口调用、消息流和结果面板串成完整 Vue 页面。

【√】前端视觉打磨：完成简洁、大气、美观的聊天式界面样式和移动端适配。

【√】端到端联调验收：补充 README，完成后端测试、前端测试、构建和本地手工烟测。

---

### Task 1: Backend Project Skeleton

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/react_resume/__init__.py`
- Create: `backend/react_resume/app.py`
- Create: `tests/backend/test_app.py`

- [ ] **Step 1: Create backend dependencies**

Add this exact content to `backend/requirements.txt`:

```text
fastapi==0.116.0
uvicorn[standard]==0.35.0
python-multipart==0.0.20
pydantic==2.11.7
pydantic-settings==2.10.1
httpx==0.28.1
pypdf==5.7.0
python-docx==1.2.0
pytest==8.4.1
pytest-asyncio==1.0.0
```

- [ ] **Step 2: Write a failing health-check test**

Create `tests/backend/test_app.py`:

```python
from fastapi.testclient import TestClient

from backend.react_resume.app import app


def test_health_check_returns_ok():
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 3: Run the failing test**

Run:

```powershell
python -m pytest tests/backend/test_app.py -v
```

Expected before implementation:

```text
ModuleNotFoundError or route not found
```

- [ ] **Step 4: Implement the minimal FastAPI app**

Create `backend/react_resume/__init__.py` as an empty package marker.

Create `backend/react_resume/app.py`:

```python
from fastapi import FastAPI

app = FastAPI(title="Resume ReAct Agent API")


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
```

- [ ] **Step 5: Run the backend health-check test**

Run:

```powershell
python -m pytest tests/backend/test_app.py -v
```

Expected:

```text
1 passed
```

- [ ] **Step 6: Commit this task**

If git is initialized:

```powershell
git add backend/requirements.txt backend/react_resume/__init__.py backend/react_resume/app.py tests/backend/test_app.py
git commit -m "chore: scaffold backend api"
```

If git is not initialized, skip the commit and continue.

---

### Task 2: Backend Configuration Module

**Files:**
- Create: `backend/react_resume/config.py`
- Create: `tests/backend/test_config.py`

- [ ] **Step 1: Write configuration tests**

Create `tests/backend/test_config.py`:

```python
from backend.react_resume.config import Settings


def test_settings_defaults_are_safe_for_local_dev():
    settings = Settings(deepseek_api_key="test-key")

    assert settings.deepseek_api_key == "test-key"
    assert settings.deepseek_base_url == "https://api.deepseek.com"
    assert settings.deepseek_model == "deepseek-chat"
    assert settings.max_resume_bytes == 5 * 1024 * 1024
    assert settings.allowed_origins == ["http://localhost:5173"]


def test_settings_accepts_comma_separated_origins():
    settings = Settings(
        deepseek_api_key="test-key",
        allowed_origins="http://localhost:5173,http://127.0.0.1:5173",
    )

    assert settings.allowed_origins == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
```

- [ ] **Step 2: Run the failing configuration tests**

Run:

```powershell
python -m pytest tests/backend/test_config.py -v
```

Expected before implementation:

```text
ModuleNotFoundError: No module named 'backend.react_resume.config'
```

- [ ] **Step 3: Implement settings**

Create `backend/react_resume/config.py`:

```python
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    deepseek_api_key: str = Field(default="", alias="DEEPSEEK_API_KEY")
    deepseek_base_url: str = Field(
        default="https://api.deepseek.com",
        alias="DEEPSEEK_BASE_URL",
    )
    deepseek_model: str = Field(default="deepseek-chat", alias="DEEPSEEK_MODEL")
    max_resume_bytes: int = Field(default=5 * 1024 * 1024, alias="MAX_RESUME_BYTES")
    allowed_origins: list[str] | str = Field(
        default_factory=lambda: ["http://localhost:5173"],
        alias="ALLOWED_ORIGINS",
    )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def split_allowed_origins(cls, value: list[str] | str) -> list[str]:
        if isinstance(value, list):
            return value
        return [origin.strip() for origin in value.split(",") if origin.strip()]
```

- [ ] **Step 4: Run configuration tests**

Run:

```powershell
python -m pytest tests/backend/test_config.py -v
```

Expected:

```text
2 passed
```

- [ ] **Step 5: Commit this task**

If git is initialized:

```powershell
git add backend/react_resume/config.py tests/backend/test_config.py
git commit -m "feat: add backend settings"
```

---

### Task 3: Domain Models And Response Contracts

**Files:**
- Create: `backend/react_resume/models.py`
- Create: `tests/backend/test_models.py`

- [ ] **Step 1: Write model serialization tests**

Create `tests/backend/test_models.py`:

```python
from backend.react_resume.models import (
    AgentTrace,
    EvaluationResult,
    OptimizeResumeResponse,
    ParsedResume,
)


def test_parsed_resume_model_stores_parser_warnings():
    parsed = ParsedResume(
        file_name="resume.pdf",
        file_type="pdf",
        raw_text="Java backend project",
        warnings=["PDF contains sparse text"],
    )

    assert parsed.file_name == "resume.pdf"
    assert parsed.file_type == "pdf"
    assert parsed.warnings == ["PDF contains sparse text"]


def test_optimize_response_serializes_nested_trace():
    response = OptimizeResumeResponse(
        diagnosis="技能表达偏泛",
        react_trace=[
            AgentTrace(
                round=1,
                agent="DecisionAgent",
                thought="分析简历和 JD 差距",
                action="analyze_resume_gap",
                observation="项目缺少量化指标",
            )
        ],
        optimized_resume="## 技术栈",
        interview_questions=["讲一下 Redis 缓存一致性"],
        warnings=[],
    )

    data = response.model_dump()

    assert data["react_trace"][0]["agent"] == "DecisionAgent"
    assert data["interview_questions"] == ["讲一下 Redis 缓存一致性"]


def test_evaluation_result_controls_iteration():
    result = EvaluationResult(
        score=82,
        covered_issues=["技能描述已具体化"],
        remaining_issues=["项目结果仍需真实指标"],
        should_continue=True,
        feedback="继续优化项目经历",
    )

    assert result.should_continue is True
    assert result.remaining_issues == ["项目结果仍需真实指标"]
```

- [ ] **Step 2: Run the failing model tests**

Run:

```powershell
python -m pytest tests/backend/test_models.py -v
```

Expected before implementation:

```text
ModuleNotFoundError: No module named 'backend.react_resume.models'
```

- [ ] **Step 3: Implement Pydantic models**

Create `backend/react_resume/models.py`:

```python
from pydantic import BaseModel, Field


class ParsedResume(BaseModel):
    file_name: str
    file_type: str
    raw_text: str
    warnings: list[str] = Field(default_factory=list)


class ResumeIssue(BaseModel):
    category: str
    description: str
    severity: int = Field(ge=1, le=5)
    evidence: str


class OptimizationStep(BaseModel):
    round_number: int = Field(ge=1, le=3)
    goal: str
    action_name: str
    result: str


class EvaluationResult(BaseModel):
    score: int = Field(ge=0, le=100)
    covered_issues: list[str]
    remaining_issues: list[str]
    should_continue: bool
    feedback: str


class AgentTrace(BaseModel):
    round: int
    agent: str
    thought: str
    action: str
    observation: str


class OptimizeResumeRequest(BaseModel):
    target_company: str
    target_role: str
    jd_text: str


class OptimizeResumeResponse(BaseModel):
    diagnosis: str
    react_trace: list[AgentTrace]
    optimized_resume: str
    interview_questions: list[str]
    warnings: list[str] = Field(default_factory=list)
```

- [ ] **Step 4: Run model tests**

Run:

```powershell
python -m pytest tests/backend/test_models.py -v
```

Expected:

```text
3 passed
```

- [ ] **Step 5: Commit this task**

If git is initialized:

```powershell
git add backend/react_resume/models.py tests/backend/test_models.py
git commit -m "feat: define resume optimization models"
```

---

### Task 4: Resume File Parser

**Files:**
- Create: `backend/react_resume/parsers.py`
- Create: `tests/backend/test_parsers.py`

- [ ] **Step 1: Write parser tests**

Create `tests/backend/test_parsers.py`:

```python
from io import BytesIO

import pytest
from docx import Document

from backend.react_resume.parsers import UnsupportedFileTypeError, parse_resume_file


def build_docx_bytes(text: str) -> bytes:
    document = Document()
    document.add_paragraph(text)
    stream = BytesIO()
    document.save(stream)
    return stream.getvalue()


def test_parse_docx_extracts_paragraph_text():
    content = build_docx_bytes("负责 Java 后端系统，使用 Redis 和 MySQL。")

    parsed = parse_resume_file("resume.docx", content)

    assert parsed.file_name == "resume.docx"
    assert parsed.file_type == "docx"
    assert "Java 后端系统" in parsed.raw_text


def test_parse_file_rejects_legacy_doc():
    with pytest.raises(UnsupportedFileTypeError) as error:
        parse_resume_file("resume.doc", b"legacy")

    assert "暂不支持 .doc" in str(error.value)


def test_parse_file_rejects_unknown_extension():
    with pytest.raises(UnsupportedFileTypeError) as error:
        parse_resume_file("resume.txt", b"text")

    assert "仅支持 PDF 和 DOCX" in str(error.value)


def test_parse_file_rejects_empty_text_docx():
    content = build_docx_bytes("")

    with pytest.raises(ValueError) as error:
        parse_resume_file("resume.docx", content)

    assert "没有提取到有效文本" in str(error.value)
```

- [ ] **Step 2: Run failing parser tests**

Run:

```powershell
python -m pytest tests/backend/test_parsers.py -v
```

Expected before implementation:

```text
ModuleNotFoundError: No module named 'backend.react_resume.parsers'
```

- [ ] **Step 3: Implement parser module**

Create `backend/react_resume/parsers.py`:

```python
from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader

from backend.react_resume.models import ParsedResume


class UnsupportedFileTypeError(ValueError):
    pass


def parse_resume_file(file_name: str, content: bytes) -> ParsedResume:
    suffix = Path(file_name).suffix.lower()
    if suffix == ".pdf":
        return _parse_pdf(file_name, content)
    if suffix == ".docx":
        return _parse_docx(file_name, content)
    if suffix == ".doc":
        raise UnsupportedFileTypeError("暂不支持 .doc，请先转换为 .docx 后上传。")
    raise UnsupportedFileTypeError("仅支持 PDF 和 DOCX 简历文件。")


def _parse_docx(file_name: str, content: bytes) -> ParsedResume:
    document = Document(BytesIO(content))
    paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs]
    table_cells: list[str] = []
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                table_cells.append(cell.text.strip())
    text = "\n".join(item for item in [*paragraphs, *table_cells] if item)
    if not text.strip():
        raise ValueError("没有提取到有效文本，请检查简历内容。")
    return ParsedResume(file_name=file_name, file_type="docx", raw_text=text, warnings=[])


def _parse_pdf(file_name: str, content: bytes) -> ParsedResume:
    reader = PdfReader(BytesIO(content))
    pages = [(page.extract_text() or "").strip() for page in reader.pages]
    text = "\n".join(page for page in pages if page)
    warnings: list[str] = []
    if len(text) < 80:
        warnings.append("PDF 可提取文本较少，可能是扫描件或排版复杂。")
    if not text.strip():
        raise ValueError("PDF 没有提取到有效文本，可能是扫描件。")
    return ParsedResume(file_name=file_name, file_type="pdf", raw_text=text, warnings=warnings)
```

- [ ] **Step 4: Run parser tests**

Run:

```powershell
python -m pytest tests/backend/test_parsers.py -v
```

Expected:

```text
4 passed
```

- [ ] **Step 5: Commit this task**

If git is initialized:

```powershell
git add backend/react_resume/parsers.py tests/backend/test_parsers.py
git commit -m "feat: parse uploaded resume files"
```

---

### Task 5: DeepSeek LLM Provider

**Files:**
- Create: `backend/react_resume/llm.py`
- Create: `tests/backend/test_llm.py`

- [ ] **Step 1: Write LLM provider tests with a fake HTTP transport**

Create `tests/backend/test_llm.py`:

```python
import httpx
import pytest

from backend.react_resume.llm import DeepSeekProvider, LLMProviderError


def test_deepseek_provider_returns_message_content():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/chat/completions"
        assert request.headers["Authorization"] == "Bearer test-key"
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"content": "优化建议"}}
                ]
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = DeepSeekProvider(
        api_key="test-key",
        base_url="https://api.deepseek.com",
        model="deepseek-chat",
        client=client,
    )

    result = provider.generate([{"role": "user", "content": "分析简历"}])

    assert result == "优化建议"


def test_deepseek_provider_requires_api_key():
    with pytest.raises(LLMProviderError) as error:
        DeepSeekProvider(api_key="", base_url="https://api.deepseek.com", model="deepseek-chat")

    assert "DEEPSEEK_API_KEY" in str(error.value)
```

- [ ] **Step 2: Run failing LLM tests**

Run:

```powershell
python -m pytest tests/backend/test_llm.py -v
```

Expected before implementation:

```text
ModuleNotFoundError: No module named 'backend.react_resume.llm'
```

- [ ] **Step 3: Implement LLM provider**

Create `backend/react_resume/llm.py`:

```python
from typing import Protocol

import httpx


class LLMProviderError(RuntimeError):
    pass


class LLMProvider(Protocol):
    def generate(self, messages: list[dict[str, str]], temperature: float = 0.3) -> str:
        ...


class DeepSeekProvider:
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        client: httpx.Client | None = None,
    ) -> None:
        if not api_key:
            raise LLMProviderError("缺少 DEEPSEEK_API_KEY，无法调用 DeepSeek。")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.client = client or httpx.Client(timeout=60)

    def generate(self, messages: list[dict[str, str]], temperature: float = 0.3) -> str:
        response = self.client.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
            },
        )
        if response.status_code >= 400:
            raise LLMProviderError(f"DeepSeek 调用失败：HTTP {response.status_code}")
        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMProviderError("DeepSeek 响应格式异常。") from exc
```

- [ ] **Step 4: Run LLM tests**

Run:

```powershell
python -m pytest tests/backend/test_llm.py -v
```

Expected:

```text
2 passed
```

- [ ] **Step 5: Commit this task**

If git is initialized:

```powershell
git add backend/react_resume/llm.py tests/backend/test_llm.py
git commit -m "feat: add deepseek llm provider"
```

---

### Task 6: Prompt Builders

**Files:**
- Create: `backend/react_resume/prompts.py`
- Modify: `tests/backend/test_agents.py`

- [ ] **Step 1: Write prompt tests**

Create `tests/backend/test_agents.py` with prompt-focused tests first:

```python
from backend.react_resume.prompts import (
    build_action_prompt,
    build_decision_prompt,
    build_evaluation_prompt,
)


def test_decision_prompt_contains_resume_jd_and_safety_rule():
    messages = build_decision_prompt(
        resume_text="负责订单系统",
        jd_text="要求 Redis、MySQL、分布式系统",
        target_company="字节跳动",
        target_role="后端开发",
    )

    joined = "\n".join(message["content"] for message in messages)

    assert "字节跳动" in joined
    assert "后端开发" in joined
    assert "负责订单系统" in joined
    assert "不能虚构学历、公司、项目、奖项" in joined


def test_action_prompt_names_requested_action():
    messages = build_action_prompt(
        action_name="rewrite_skills",
        resume_text="熟悉 Java",
        jd_text="要求 Java、Redis",
        previous_feedback="技能描述偏泛",
    )

    joined = "\n".join(message["content"] for message in messages)

    assert "rewrite_skills" in joined
    assert "技能描述偏泛" in joined


def test_evaluation_prompt_requires_json_like_fields():
    messages = build_evaluation_prompt(
        optimized_resume="## 技术栈",
        jd_text="要求 MySQL",
        known_issues=["项目缺少量化结果"],
    )

    joined = "\n".join(message["content"] for message in messages)

    assert "score" in joined
    assert "remaining_issues" in joined
    assert "should_continue" in joined
```

- [ ] **Step 2: Run failing prompt tests**

Run:

```powershell
python -m pytest tests/backend/test_agents.py -v
```

Expected before implementation:

```text
ModuleNotFoundError: No module named 'backend.react_resume.prompts'
```

- [ ] **Step 3: Implement prompt builders**

Create `backend/react_resume/prompts.py`:

```python
SAFETY_RULES = (
    "你可以优化表达，但不能虚构学历、公司、项目、奖项。"
    "缺少真实数据时，用“建议补充真实数据”提示用户。"
)


def build_decision_prompt(
    resume_text: str,
    jd_text: str,
    target_company: str,
    target_role: str,
) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "你是 DecisionAgent，负责诊断简历与 JD 的差距、制定优化计划、"
                "输出可展示给用户的思考摘要。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"目标公司：{target_company}\n"
                f"目标岗位：{target_role}\n"
                f"JD：\n{jd_text}\n\n"
                f"简历文本：\n{resume_text}\n\n"
                f"安全规则：{SAFETY_RULES}\n"
                "请输出诊断、优先级计划和下一步 action。"
            ),
        },
    ]


def build_action_prompt(
    action_name: str,
    resume_text: str,
    jd_text: str,
    previous_feedback: str,
) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "你是 ActionAgent，负责根据指定 action 改写简历。"
                "输出应专业、真实、贴合 JD。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"action_name：{action_name}\n"
                f"上一轮反馈：{previous_feedback}\n"
                f"JD：\n{jd_text}\n\n"
                f"简历文本：\n{resume_text}\n\n"
                f"安全规则：{SAFETY_RULES}"
            ),
        },
    ]


def build_evaluation_prompt(
    optimized_resume: str,
    jd_text: str,
    known_issues: list[str],
) -> list[dict[str, str]]:
    issues = "\n".join(f"- {issue}" for issue in known_issues)
    return [
        {
            "role": "system",
            "content": (
                "你是 DecisionAgent，负责评估 ActionAgent 的简历优化结果。"
                "只输出 JSON 字段：score, covered_issues, remaining_issues, "
                "should_continue, feedback。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"JD：\n{jd_text}\n\n"
                f"已知问题：\n{issues}\n\n"
                f"优化后简历：\n{optimized_resume}"
            ),
        },
    ]
```

- [ ] **Step 4: Run prompt tests**

Run:

```powershell
python -m pytest tests/backend/test_agents.py -v
```

Expected:

```text
3 passed
```

- [ ] **Step 5: Commit this task**

If git is initialized:

```powershell
git add backend/react_resume/prompts.py tests/backend/test_agents.py
git commit -m "feat: add resume optimization prompts"
```

---

### Task 7: DecisionAgent And ActionAgent

**Files:**
- Create: `backend/react_resume/agents.py`
- Modify: `tests/backend/test_agents.py`

- [ ] **Step 1: Extend agent tests with fake provider behavior**

Append to `tests/backend/test_agents.py`:

```python
from backend.react_resume.agents import ActionAgent, DecisionAgent


class FakeProvider:
    def __init__(self, outputs: list[str]) -> None:
        self.outputs = outputs
        self.calls: list[list[dict[str, str]]] = []

    def generate(self, messages: list[dict[str, str]], temperature: float = 0.3) -> str:
        self.calls.append(messages)
        return self.outputs.pop(0)


def test_decision_agent_creates_diagnosis_trace():
    provider = FakeProvider(["技能描述偏泛；下一步 rewrite_skills"])
    agent = DecisionAgent(provider)

    trace, diagnosis = agent.analyze(
        resume_text="熟悉 Java",
        jd_text="要求 Redis 和 MySQL",
        target_company="字节跳动",
        target_role="后端开发",
    )

    assert trace.agent == "DecisionAgent"
    assert trace.action == "analyze_resume_gap"
    assert "技能描述偏泛" in diagnosis


def test_action_agent_rewrites_by_action_name():
    provider = FakeProvider(["## 技术栈\n- Java 后端开发"])
    agent = ActionAgent(provider)

    trace, result = agent.execute(
        round_number=1,
        action_name="rewrite_skills",
        resume_text="熟悉 Java",
        jd_text="要求 Java 后端",
        feedback="技能描述偏泛",
    )

    assert trace.agent == "ActionAgent"
    assert trace.action == "rewrite_skills"
    assert "Java 后端开发" in result
```

- [ ] **Step 2: Run failing agent tests**

Run:

```powershell
python -m pytest tests/backend/test_agents.py -v
```

Expected before implementation:

```text
ModuleNotFoundError: No module named 'backend.react_resume.agents'
```

- [ ] **Step 3: Implement agents**

Create `backend/react_resume/agents.py`:

```python
from backend.react_resume.llm import LLMProvider
from backend.react_resume.models import AgentTrace
from backend.react_resume.prompts import build_action_prompt, build_decision_prompt


class DecisionAgent:
    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    def analyze(
        self,
        resume_text: str,
        jd_text: str,
        target_company: str,
        target_role: str,
    ) -> tuple[AgentTrace, str]:
        result = self.provider.generate(
            build_decision_prompt(
                resume_text=resume_text,
                jd_text=jd_text,
                target_company=target_company,
                target_role=target_role,
            )
        )
        trace = AgentTrace(
            round=0,
            agent="DecisionAgent",
            thought="分析简历与 JD 的差距，并制定优化优先级。",
            action="analyze_resume_gap",
            observation=result,
        )
        return trace, result

    def choose_action(self, round_number: int) -> str:
        actions = {
            1: "rewrite_skills",
            2: "rewrite_projects_with_star",
            3: "generate_targeted_resume",
        }
        return actions[round_number]


class ActionAgent:
    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    def execute(
        self,
        round_number: int,
        action_name: str,
        resume_text: str,
        jd_text: str,
        feedback: str,
    ) -> tuple[AgentTrace, str]:
        result = self.provider.generate(
            build_action_prompt(
                action_name=action_name,
                resume_text=resume_text,
                jd_text=jd_text,
                previous_feedback=feedback,
            )
        )
        trace = AgentTrace(
            round=round_number,
            agent="ActionAgent",
            thought=f"执行第 {round_number} 轮优化任务：{action_name}。",
            action=action_name,
            observation="已生成本轮优化结果。",
        )
        return trace, result
```

- [ ] **Step 4: Run agent tests**

Run:

```powershell
python -m pytest tests/backend/test_agents.py -v
```

Expected:

```text
5 passed
```

- [ ] **Step 5: Commit this task**

If git is initialized:

```powershell
git add backend/react_resume/agents.py tests/backend/test_agents.py
git commit -m "feat: add decision and action agents"
```

---

### Task 8: ReAct Workflow Orchestration And Output Formatting

**Files:**
- Create: `backend/react_resume/output.py`
- Create: `backend/react_resume/workflow.py`
- Create: `tests/backend/test_workflow.py`

- [ ] **Step 1: Write workflow tests**

Create `tests/backend/test_workflow.py`:

```python
from backend.react_resume.models import OptimizeResumeResponse, ParsedResume
from backend.react_resume.workflow import ResumeOptimizationWorkflow


class FakeProvider:
    def __init__(self) -> None:
        self.outputs = [
            "诊断：技能描述偏泛，项目缺少量化，JD 关键词不足。",
            "## 技术栈\n- Java / Spring Boot / Redis / MySQL",
            "## 项目经历\n- Situation: 订单系统性能不足\n- Action: 优化缓存\n- Result: 建议补充真实数据",
            "## 定制简历\n面向字节后端开发岗位",
            "1. Redis 缓存一致性怎么保证？\n2. MySQL 索引失效场景有哪些？",
        ]

    def generate(self, messages: list[dict[str, str]], temperature: float = 0.3) -> str:
        return self.outputs.pop(0)


def test_workflow_runs_three_rounds_and_returns_response():
    workflow = ResumeOptimizationWorkflow(FakeProvider())
    parsed = ParsedResume(
        file_name="resume.docx",
        file_type="docx",
        raw_text="熟悉 Java，做过订单系统。",
        warnings=[],
    )

    response = workflow.run(
        parsed_resume=parsed,
        jd_text="要求 Java、Redis、MySQL、分布式系统",
        target_company="字节跳动",
        target_role="后端开发",
    )

    assert isinstance(response, OptimizeResumeResponse)
    assert "技能描述偏泛" in response.diagnosis
    assert "面向字节后端开发岗位" in response.optimized_resume
    assert len(response.react_trace) == 7
    assert response.react_trace[-1].action == "generate_interview_questions"
    assert response.interview_questions[0] == "Redis 缓存一致性怎么保证？"
```

- [ ] **Step 2: Run failing workflow tests**

Run:

```powershell
python -m pytest tests/backend/test_workflow.py -v
```

Expected before implementation:

```text
ModuleNotFoundError: No module named 'backend.react_resume.workflow'
```

- [ ] **Step 3: Implement output formatter**

Create `backend/react_resume/output.py`:

```python
from backend.react_resume.models import AgentTrace, OptimizeResumeResponse


def parse_interview_questions(questions_text: str) -> list[str]:
    return [
        line.strip().lstrip("0123456789.、 ")
        for line in questions_text.splitlines()
        if line.strip()
    ]


def build_optimize_response(
    diagnosis: str,
    trace: list[AgentTrace],
    optimized_resume: str,
    questions_text: str,
    warnings: list[str],
) -> OptimizeResumeResponse:
    return OptimizeResumeResponse(
        diagnosis=diagnosis,
        react_trace=trace,
        optimized_resume=optimized_resume,
        interview_questions=parse_interview_questions(questions_text),
        warnings=warnings,
    )
```

- [ ] **Step 4: Implement workflow**

Create `backend/react_resume/workflow.py`:

```python
from backend.react_resume.agents import ActionAgent, DecisionAgent
from backend.react_resume.llm import LLMProvider
from backend.react_resume.models import AgentTrace, OptimizeResumeResponse, ParsedResume
from backend.react_resume.output import build_optimize_response


class ResumeOptimizationWorkflow:
    def __init__(self, provider: LLMProvider) -> None:
        self.decision_agent = DecisionAgent(provider)
        self.action_agent = ActionAgent(provider)
        self.provider = provider

    def run(
        self,
        parsed_resume: ParsedResume,
        jd_text: str,
        target_company: str,
        target_role: str,
    ) -> OptimizeResumeResponse:
        trace: list[AgentTrace] = []
        warnings = list(parsed_resume.warnings)
        decision_trace, diagnosis = self.decision_agent.analyze(
            resume_text=parsed_resume.raw_text,
            jd_text=jd_text,
            target_company=target_company,
            target_role=target_role,
        )
        trace.append(decision_trace)

        current_resume = parsed_resume.raw_text
        feedback = diagnosis
        for round_number in range(1, 4):
            action_name = self.decision_agent.choose_action(round_number)
            choice_trace = AgentTrace(
                round=round_number,
                agent="DecisionAgent",
                thought=f"根据诊断结果选择第 {round_number} 轮优化动作。",
                action="choose_next_action",
                observation=f"下一步执行 {action_name}。",
            )
            trace.append(choice_trace)
            action_trace, current_resume = self.action_agent.execute(
                round_number=round_number,
                action_name=action_name,
                resume_text=current_resume,
                jd_text=jd_text,
                feedback=feedback,
            )
            trace.append(action_trace)
            feedback = current_resume

        questions_text = self.provider.generate(
            [
                {
                    "role": "system",
                    "content": "你是面试准备助手，请基于简历和 JD 生成面试预测问题，每行一个问题。",
                },
                {
                    "role": "user",
                    "content": f"JD：\n{jd_text}\n\n优化后简历：\n{current_resume}",
                },
            ]
        )
        trace.append(
            AgentTrace(
                round=3,
                agent="ActionAgent",
                thought="根据最终简历和 JD 生成面试预测问题。",
                action="generate_interview_questions",
                observation="已生成面试预测问题。",
            )
        )
        return build_optimize_response(
            diagnosis=diagnosis,
            trace=trace,
            optimized_resume=current_resume,
            questions_text=questions_text,
            warnings=warnings,
        )
```

- [ ] **Step 5: Run workflow tests**

Run:

```powershell
python -m pytest tests/backend/test_workflow.py -v
```

Expected:

```text
1 passed
```

- [ ] **Step 6: Commit this task**

If git is initialized:

```powershell
git add backend/react_resume/output.py backend/react_resume/workflow.py tests/backend/test_workflow.py
git commit -m "feat: orchestrate react resume workflow"
```

---

### Task 9: FastAPI Optimize Endpoint

**Files:**
- Modify: `backend/react_resume/app.py`
- Create: `tests/backend/test_app.py` if Task 1 did not create it

- [ ] **Step 1: Extend API tests for validation**

Append to `tests/backend/test_app.py`:

```python
from unittest.mock import Mock

from backend.react_resume.models import AgentTrace, OptimizeResumeResponse


def test_optimize_resume_requires_supported_file():
    client = TestClient(app)

    response = client.post(
        "/api/optimize-resume",
        data={
            "target_company": "字节跳动",
            "target_role": "后端开发",
            "jd_text": "要求 Java 和 Redis",
        },
        files={"resume_file": ("resume.txt", b"text", "text/plain")},
    )

    assert response.status_code == 400
    assert "仅支持 PDF 和 DOCX" in response.json()["detail"]


def test_optimize_resume_returns_workflow_response(monkeypatch):
    fake_workflow = Mock()
    fake_workflow.run.return_value = OptimizeResumeResponse(
        diagnosis="技能描述偏泛",
        react_trace=[
            AgentTrace(
                round=1,
                agent="DecisionAgent",
                thought="分析差距",
                action="analyze_resume_gap",
                observation="缺少量化指标",
            )
        ],
        optimized_resume="## 定制简历",
        interview_questions=["Redis 缓存一致性怎么保证？"],
        warnings=[],
    )
    monkeypatch.setattr("backend.react_resume.app.build_workflow", lambda: fake_workflow)

    from docx import Document
    from io import BytesIO

    document = Document()
    document.add_paragraph("熟悉 Java 后端开发，使用 Redis 和 MySQL。")
    stream = BytesIO()
    document.save(stream)

    client = TestClient(app)
    response = client.post(
        "/api/optimize-resume",
        data={
            "target_company": "字节跳动",
            "target_role": "后端开发",
            "jd_text": "要求 Java 和 Redis",
        },
        files={
            "resume_file": (
                "resume.docx",
                stream.getvalue(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["diagnosis"] == "技能描述偏泛"
    assert response.json()["optimized_resume"] == "## 定制简历"
```

- [ ] **Step 2: Run failing endpoint tests**

Run:

```powershell
python -m pytest tests/backend/test_app.py -v
```

Expected before endpoint implementation:

```text
404 Not Found for /api/optimize-resume
```

- [ ] **Step 3: Implement CORS, workflow builder, and endpoint**

Modify `backend/react_resume/app.py`:

```python
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.react_resume.config import Settings
from backend.react_resume.llm import DeepSeekProvider, LLMProviderError
from backend.react_resume.parsers import UnsupportedFileTypeError, parse_resume_file
from backend.react_resume.workflow import ResumeOptimizationWorkflow

settings = Settings()

app = FastAPI(title="Resume ReAct Agent API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


def build_workflow() -> ResumeOptimizationWorkflow:
    provider = DeepSeekProvider(
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        model=settings.deepseek_model,
    )
    return ResumeOptimizationWorkflow(provider)


@app.post("/api/optimize-resume")
async def optimize_resume(
    target_company: str = Form(...),
    target_role: str = Form(...),
    jd_text: str = Form(...),
    resume_file: UploadFile = File(...),
):
    content = await resume_file.read()
    if len(content) > settings.max_resume_bytes:
        raise HTTPException(status_code=400, detail="简历文件过大，请上传 5MB 以内的文件。")
    try:
        parsed = parse_resume_file(resume_file.filename or "resume", content)
        workflow = build_workflow()
        return workflow.run(
            parsed_resume=parsed,
            jd_text=jd_text,
            target_company=target_company,
            target_role=target_role,
        )
    except (UnsupportedFileTypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except LLMProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
```

- [ ] **Step 4: Run API tests**

Run:

```powershell
python -m pytest tests/backend/test_app.py -v
```

Expected:

```text
3 passed
```

- [ ] **Step 5: Commit this task**

If git is initialized:

```powershell
git add backend/react_resume/app.py tests/backend/test_app.py
git commit -m "feat: expose resume optimization api"
```

---

### Task 10: Frontend Project Skeleton

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/index.html`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/styles/main.css`

- [ ] **Step 1: Create frontend dependency file**

Create `frontend/package.json`:

```json
{
  "name": "resume-react-agent-frontend",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc --noEmit && vite build",
    "test": "vitest run",
    "preview": "vite preview"
  },
  "dependencies": {
    "lucide-vue-next": "latest",
    "vue": "latest"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "latest",
    "@types/node": "latest",
    "@vue/test-utils": "latest",
    "jsdom": "latest",
    "typescript": "latest",
    "vite": "latest",
    "vitest": "latest",
    "vue-tsc": "latest"
  }
}
```

- [ ] **Step 2: Create Vite and TypeScript config**

Create `frontend/vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
  test: {
    environment: 'jsdom',
  },
})
```

Create `frontend/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "jsx": "preserve",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "skipLibCheck": true
  },
  "include": ["src/**/*.ts", "src/**/*.vue", "vite.config.ts"],
  "references": []
}
```

- [ ] **Step 3: Create app entry files**

Create `frontend/index.html`:

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>简历优化助手</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

Create `frontend/src/main.ts`:

```typescript
import { createApp } from 'vue'
import App from './App.vue'
import './styles/main.css'

createApp(App).mount('#app')
```

Create `frontend/src/App.vue`:

```vue
<template>
  <main class="app-shell">
    <h1>简历优化助手</h1>
  </main>
</template>
```

Create `frontend/src/styles/main.css`:

```css
:root {
  color: #172033;
  background: #f7f8fb;
  font-family:
    Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
    "Segoe UI", sans-serif;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-width: 320px;
  min-height: 100vh;
}

button,
textarea {
  font: inherit;
}

.app-shell {
  min-height: 100vh;
}
```

- [ ] **Step 4: Install dependencies**

Run:

```powershell
cd frontend
npm install
```

Expected:

```text
added packages
```

- [ ] **Step 5: Build frontend skeleton**

Run:

```powershell
cd frontend
npm run build
```

Expected:

```text
vite build
✓ built
```

- [ ] **Step 6: Commit this task**

If git is initialized:

```powershell
git add frontend/package.json frontend/package-lock.json frontend/vite.config.ts frontend/tsconfig.json frontend/index.html frontend/src/main.ts frontend/src/App.vue frontend/src/styles/main.css
git commit -m "chore: scaffold vue frontend"
```

---

### Task 11: Frontend API Client And Types

**Files:**
- Create: `frontend/src/api/resumeOptimizer.ts`
- Create: `tests/frontend/resumeOptimizer.test.ts`

- [ ] **Step 1: Write API client tests**

Create `tests/frontend/resumeOptimizer.test.ts`:

```typescript
import { describe, expect, it, vi } from 'vitest'
import { optimizeResume } from '../../frontend/src/api/resumeOptimizer'

describe('optimizeResume', () => {
  it('posts multipart form data to the backend', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        diagnosis: '技能描述偏泛',
        react_trace: [],
        optimized_resume: '## 定制简历',
        interview_questions: ['Redis 缓存一致性怎么保证？'],
        warnings: [],
      }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const result = await optimizeResume({
      targetCompany: '字节跳动',
      targetRole: '后端开发',
      jdText: '要求 Java 和 Redis',
      resumeFile: new File(['resume'], 'resume.pdf', { type: 'application/pdf' }),
    })

    expect(fetchMock).toHaveBeenCalledWith('/api/optimize-resume', {
      method: 'POST',
      body: expect.any(FormData),
    })
    expect(result.diagnosis).toBe('技能描述偏泛')
  })
})
```

- [ ] **Step 2: Run failing frontend API test**

Run:

```powershell
cd frontend
npm run test -- ..\tests\frontend\resumeOptimizer.test.ts
```

Expected before implementation:

```text
Failed to resolve import
```

- [ ] **Step 3: Implement API client**

Create `frontend/src/api/resumeOptimizer.ts`:

```typescript
export type AgentTrace = {
  round: number
  agent: string
  thought: string
  action: string
  observation: string
}

export type OptimizeResumeResponse = {
  diagnosis: string
  react_trace: AgentTrace[]
  optimized_resume: string
  interview_questions: string[]
  warnings: string[]
}

export type OptimizeResumeInput = {
  targetCompany: string
  targetRole: string
  jdText: string
  resumeFile: File
}

export async function optimizeResume(input: OptimizeResumeInput): Promise<OptimizeResumeResponse> {
  const formData = new FormData()
  formData.append('target_company', input.targetCompany)
  formData.append('target_role', input.targetRole)
  formData.append('jd_text', input.jdText)
  formData.append('resume_file', input.resumeFile)

  const response = await fetch('/api/optimize-resume', {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({ detail: '请求失败' }))
    throw new Error(errorBody.detail || '简历优化请求失败')
  }

  return response.json()
}
```

- [ ] **Step 4: Run frontend API tests**

Run:

```powershell
cd frontend
npm run test -- ..\tests\frontend\resumeOptimizer.test.ts
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Commit this task**

If git is initialized:

```powershell
git add frontend/src/api/resumeOptimizer.ts tests/frontend/resumeOptimizer.test.ts
git commit -m "feat: add frontend resume optimizer client"
```

---

### Task 12: Composer And File Upload Components

**Files:**
- Create: `frontend/src/components/FileUploadButton.vue`
- Create: `frontend/src/components/Composer.vue`
- Create: `tests/frontend/Composer.test.ts`

- [ ] **Step 1: Write composer tests**

Create `tests/frontend/Composer.test.ts`:

```typescript
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import Composer from '../../frontend/src/components/Composer.vue'
import FileUploadButton from '../../frontend/src/components/FileUploadButton.vue'

describe('Composer', () => {
  it('emits submit with text and selected file', async () => {
    const wrapper = mount(Composer)
    const file = new File(['resume'], 'resume.pdf', { type: 'application/pdf' })

    await wrapper.find('textarea').setValue('我想投字节跳动后端岗，JD 要求 Java 和 Redis')
    await wrapper.findComponent(FileUploadButton).vm.$emit('file-selected', file)
    await wrapper.find('[data-test="send-button"]').trigger('click')

    const emitted = wrapper.emitted('submit')
    expect(emitted).toBeTruthy()
  })

  it('disables send when text or file is missing', () => {
    const wrapper = mount(Composer)

    expect(wrapper.find('[data-test="send-button"]').attributes('disabled')).toBeDefined()
  })
})
```

- [ ] **Step 2: Run failing composer tests**

Run:

```powershell
cd frontend
npm run test -- ..\tests\frontend\Composer.test.ts
```

Expected before implementation:

```text
Failed to resolve import
```

- [ ] **Step 3: Implement FileUploadButton**

Create `frontend/src/components/FileUploadButton.vue`:

```vue
<script setup lang="ts">
import { Paperclip, X } from 'lucide-vue-next'

const props = defineProps<{
  file: File | null
  disabled?: boolean
}>()

const emit = defineEmits<{
  'file-selected': [file: File]
  'file-cleared': []
}>()

function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) {
    emit('file-selected', file)
  }
  input.value = ''
}
</script>

<template>
  <div class="file-upload">
    <label class="icon-button" title="上传简历">
      <Paperclip :size="19" />
      <input
        type="file"
        accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        :disabled="props.disabled"
        @change="onFileChange"
      />
    </label>
    <button
      v-if="props.file"
      class="file-chip"
      type="button"
      title="移除文件"
      @click="emit('file-cleared')"
    >
      <span>{{ props.file.name }}</span>
      <X :size="14" />
    </button>
  </div>
</template>
```

- [ ] **Step 4: Implement Composer**

Create `frontend/src/components/Composer.vue`:

```vue
<script setup lang="ts">
import { computed, ref } from 'vue'
import { ArrowUp } from 'lucide-vue-next'
import FileUploadButton from './FileUploadButton.vue'

defineProps<{
  disabled?: boolean
}>()

const emit = defineEmits<{
  submit: [payload: { text: string; file: File }]
}>()

const text = ref('')
const file = ref<File | null>(null)
const canSubmit = computed(() => Boolean(text.value.trim() && file.value))

function submit() {
  if (!canSubmit.value || !file.value) {
    return
  }
  emit('submit', { text: text.value.trim(), file: file.value })
}
</script>

<template>
  <section class="composer" aria-label="简历优化输入区">
    <FileUploadButton
      :file="file"
      :disabled="disabled"
      @file-selected="file = $event"
      @file-cleared="file = null"
    />
    <textarea
      v-model="text"
      rows="3"
      placeholder="粘贴目标岗位 JD，或描述你想投递的岗位"
      :disabled="disabled"
      @keydown.ctrl.enter.prevent="submit"
    />
    <button
      class="send-button"
      data-test="send-button"
      type="button"
      title="发送"
      :disabled="disabled || !canSubmit"
      @click="submit"
    >
      <ArrowUp :size="20" />
    </button>
  </section>
</template>
```

- [ ] **Step 5: Run composer tests**

Run:

```powershell
cd frontend
npm run test -- ..\tests\frontend\Composer.test.ts
```

Expected:

```text
2 passed
```

- [ ] **Step 6: Commit this task**

If git is initialized:

```powershell
git add frontend/src/components/FileUploadButton.vue frontend/src/components/Composer.vue tests/frontend/Composer.test.ts
git commit -m "feat: add chat composer and file upload"
```

---

### Task 13: Message Rendering Components

**Files:**
- Create: `frontend/src/components/MessageList.vue`
- Create: `frontend/src/components/ChatMessage.vue`
- Create: `frontend/src/components/ThoughtTimeline.vue`
- Create: `frontend/src/components/OptimizedResumePanel.vue`
- Create: `frontend/src/components/InterviewQuestionsPanel.vue`
- Create: `tests/frontend/MessageList.test.ts`

- [ ] **Step 1: Write message list tests**

Create `tests/frontend/MessageList.test.ts`:

```typescript
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import MessageList from '../../frontend/src/components/MessageList.vue'

describe('MessageList', () => {
  it('renders user and assistant messages', () => {
    const wrapper = mount(MessageList, {
      props: {
        messages: [
          {
            id: '1',
            role: 'user',
            kind: 'request',
            content: '我想投字节后端岗',
            createdAt: '2026-07-07T00:00:00.000Z',
          },
          {
            id: '2',
            role: 'assistant',
            kind: 'answer',
            content: '## 定制简历',
            createdAt: '2026-07-07T00:00:01.000Z',
          },
        ],
      },
    })

    expect(wrapper.text()).toContain('我想投字节后端岗')
    expect(wrapper.text()).toContain('## 定制简历')
  })
})
```

- [ ] **Step 2: Run failing message tests**

Run:

```powershell
cd frontend
npm run test -- ..\tests\frontend\MessageList.test.ts
```

Expected before implementation:

```text
Failed to resolve import
```

- [ ] **Step 3: Implement display components**

Create `frontend/src/components/ThoughtTimeline.vue`:

```vue
<script setup lang="ts">
import type { AgentTrace } from '../api/resumeOptimizer'

defineProps<{
  traces: AgentTrace[]
}>()
</script>

<template>
  <ol class="thought-timeline">
    <li v-for="trace in traces" :key="`${trace.round}-${trace.agent}-${trace.action}`">
      <strong>{{ trace.agent }}</strong>
      <span>{{ trace.thought }}</span>
      <code>{{ trace.action }}</code>
      <p>{{ trace.observation }}</p>
    </li>
  </ol>
</template>
```

Create `frontend/src/components/OptimizedResumePanel.vue`:

```vue
<script setup lang="ts">
defineProps<{
  content: string
}>()
</script>

<template>
  <section class="result-panel">
    <h2>定制版简历</h2>
    <pre>{{ content }}</pre>
  </section>
</template>
```

Create `frontend/src/components/InterviewQuestionsPanel.vue`:

```vue
<script setup lang="ts">
defineProps<{
  questions: string[]
}>()
</script>

<template>
  <section class="result-panel">
    <h2>面试预测问题</h2>
    <ol>
      <li v-for="question in questions" :key="question">{{ question }}</li>
    </ol>
  </section>
</template>
```

Create `frontend/src/components/ChatMessage.vue`:

```vue
<script setup lang="ts">
export type ChatMessageModel = {
  id: string
  role: 'user' | 'assistant' | 'system'
  kind: 'request' | 'thought' | 'answer' | 'error'
  content: string
  createdAt: string
}

defineProps<{
  message: ChatMessageModel
}>()
</script>

<template>
  <article class="chat-message" :class="[`is-${message.role}`, `kind-${message.kind}`]">
    <div class="message-content">{{ message.content }}</div>
  </article>
</template>
```

Create `frontend/src/components/MessageList.vue`:

```vue
<script setup lang="ts">
import ChatMessage, { type ChatMessageModel } from './ChatMessage.vue'

defineProps<{
  messages: ChatMessageModel[]
}>()
</script>

<template>
  <section class="message-list" aria-label="对话内容">
    <ChatMessage v-for="message in messages" :key="message.id" :message="message" />
  </section>
</template>
```

- [ ] **Step 4: Run message tests**

Run:

```powershell
cd frontend
npm run test -- ..\tests\frontend\MessageList.test.ts
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Commit this task**

If git is initialized:

```powershell
git add frontend/src/components/MessageList.vue frontend/src/components/ChatMessage.vue frontend/src/components/ThoughtTimeline.vue frontend/src/components/OptimizedResumePanel.vue frontend/src/components/InterviewQuestionsPanel.vue tests/frontend/MessageList.test.ts
git commit -m "feat: render chat messages and result panels"
```

---

### Task 14: Chat Page Integration

**Files:**
- Create: `frontend/src/components/ChatPage.vue`
- Modify: `frontend/src/App.vue`

- [ ] **Step 1: Implement ChatPage state orchestration**

Create `frontend/src/components/ChatPage.vue`:

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { optimizeResume, type OptimizeResumeResponse } from '../api/resumeOptimizer'
import Composer from './Composer.vue'
import MessageList from './MessageList.vue'
import ThoughtTimeline from './ThoughtTimeline.vue'
import OptimizedResumePanel from './OptimizedResumePanel.vue'
import InterviewQuestionsPanel from './InterviewQuestionsPanel.vue'
import type { ChatMessageModel } from './ChatMessage.vue'

const messages = ref<ChatMessageModel[]>([])
const result = ref<OptimizeResumeResponse | null>(null)
const isSubmitting = ref(false)
const errorMessage = ref<string | null>(null)

function makeMessage(
  role: ChatMessageModel['role'],
  kind: ChatMessageModel['kind'],
  content: string,
): ChatMessageModel {
  return {
    id: crypto.randomUUID(),
    role,
    kind,
    content,
    createdAt: new Date().toISOString(),
  }
}

function parseTarget(text: string) {
  const companyMatch = text.match(/投(.+?)的/)
  const roleMatch = text.match(/(后端开发|前端开发|算法|测试|产品|运营)/)
  return {
    targetCompany: companyMatch?.[1] || '目标公司',
    targetRole: roleMatch?.[1] || '目标岗位',
    jdText: text,
  }
}

async function submit(payload: { text: string; file: File }) {
  isSubmitting.value = true
  errorMessage.value = null
  result.value = null
  messages.value.push(
    makeMessage(
      'user',
      'request',
      `${payload.text}\n\n已上传简历：${payload.file.name}`,
    ),
  )
  try {
    const target = parseTarget(payload.text)
    const response = await optimizeResume({
      ...target,
      resumeFile: payload.file,
    })
    result.value = response
    messages.value.push(makeMessage('assistant', 'thought', response.diagnosis))
    messages.value.push(makeMessage('assistant', 'answer', response.optimized_resume))
  } catch (error) {
    const message = error instanceof Error ? error.message : '请求失败'
    errorMessage.value = message
    messages.value.push(makeMessage('assistant', 'error', message))
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <main class="chat-page">
    <header class="chat-header">
      <div>
        <p class="eyebrow">Resume ReAct Agent</p>
        <h1>简历优化助手</h1>
      </div>
      <span class="status-pill">DeepSeek 已接入</span>
    </header>

    <MessageList :messages="messages" />

    <section v-if="result" class="result-stack">
      <ThoughtTimeline :traces="result.react_trace" />
      <OptimizedResumePanel :content="result.optimized_resume" />
      <InterviewQuestionsPanel :questions="result.interview_questions" />
    </section>

    <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

    <Composer :disabled="isSubmitting" @submit="submit" />
  </main>
</template>
```

- [ ] **Step 2: Wire App.vue to ChatPage**

Modify `frontend/src/App.vue`:

```vue
<script setup lang="ts">
import ChatPage from './components/ChatPage.vue'
</script>

<template>
  <ChatPage />
</template>
```

- [ ] **Step 3: Build frontend**

Run:

```powershell
cd frontend
npm run build
```

Expected:

```text
✓ built
```

- [ ] **Step 4: Commit this task**

If git is initialized:

```powershell
git add frontend/src/components/ChatPage.vue frontend/src/App.vue
git commit -m "feat: integrate chat page workflow"
```

---

### Task 15: Frontend Visual Styling

**Files:**
- Modify: `frontend/src/styles/main.css`

- [ ] **Step 1: Add global UI styles**

Replace `frontend/src/styles/main.css` with:

```css
:root {
  color: #172033;
  background: #f7f8fb;
  font-family:
    Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
    "Segoe UI", sans-serif;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-width: 320px;
  min-height: 100vh;
}

button,
textarea {
  font: inherit;
}

button {
  cursor: pointer;
}

button:disabled,
textarea:disabled {
  cursor: not-allowed;
  opacity: 0.62;
}

.chat-page {
  min-height: 100vh;
  max-width: 920px;
  margin: 0 auto;
  padding: 32px 20px 180px;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 32px;
}

.eyebrow {
  margin: 0 0 8px;
  color: #697386;
  font-size: 13px;
}

.chat-header h1 {
  margin: 0;
  font-size: 28px;
  line-height: 1.2;
  letter-spacing: 0;
}

.status-pill {
  border: 1px solid #dfe4ec;
  border-radius: 999px;
  padding: 8px 12px;
  color: #355c43;
  background: #eef9f2;
  font-size: 13px;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.chat-message {
  max-width: 78%;
  border: 1px solid #e5e8ef;
  border-radius: 8px;
  padding: 14px 16px;
  background: #ffffff;
  box-shadow: 0 8px 28px rgb(23 32 51 / 7%);
  white-space: pre-wrap;
}

.chat-message.is-user {
  align-self: flex-end;
  background: #eef3ff;
  border-color: #d9e3ff;
}

.chat-message.kind-error {
  border-color: #f1b8b8;
  background: #fff4f4;
  color: #8a2626;
}

.composer {
  position: fixed;
  left: 50%;
  bottom: 24px;
  width: min(920px, calc(100vw - 32px));
  transform: translateX(-50%);
  border: 1px solid #e3e7ef;
  border-radius: 24px;
  padding: 14px 16px;
  background: #ffffff;
  box-shadow: 0 18px 50px rgb(23 32 51 / 12%);
}

.composer textarea {
  width: 100%;
  min-height: 74px;
  border: 0;
  resize: none;
  outline: none;
  color: #172033;
  background: transparent;
}

.file-upload {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.icon-button,
.send-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 0;
  border-radius: 999px;
}

.icon-button {
  width: 34px;
  height: 34px;
  color: #2a3447;
  background: #f4f6fa;
}

.icon-button input {
  display: none;
}

.file-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid #dfe4ec;
  border-radius: 999px;
  padding: 6px 9px;
  color: #344055;
  background: #ffffff;
  font-size: 13px;
}

.send-button {
  position: absolute;
  right: 16px;
  bottom: 14px;
  width: 36px;
  height: 36px;
  color: #ffffff;
  background: #91a7ff;
}

.thought-timeline,
.result-panel {
  margin-top: 20px;
  border: 1px solid #e5e8ef;
  border-radius: 8px;
  padding: 18px;
  background: #ffffff;
}

.thought-timeline {
  display: grid;
  gap: 12px;
  padding-left: 38px;
}

.thought-timeline code {
  display: inline-block;
  margin-left: 8px;
  border-radius: 6px;
  padding: 2px 6px;
  background: #f1f4fb;
}

.result-panel h2 {
  margin: 0 0 12px;
  font-size: 18px;
}

.result-panel pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

.error-text {
  color: #8a2626;
}

@media (max-width: 640px) {
  .chat-page {
    padding: 24px 14px 180px;
  }

  .chat-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .chat-message {
    max-width: 100%;
  }
}
```

- [ ] **Step 2: Build frontend after styling**

Run:

```powershell
cd frontend
npm run build
```

Expected:

```text
✓ built
```

- [ ] **Step 3: Commit this task**

If git is initialized:

```powershell
git add frontend/src/styles/main.css
git commit -m "style: polish chat interface"
```

---

### Task 16: Backend And Frontend Integration Smoke Test

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create local development README**

Create `README.md`:

```markdown
# 简历 ReAct 双 Agent

## 本地运行

### 后端

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
uvicorn react_resume.app:app --reload --host 127.0.0.1 --port 8000
```

### 前端

```powershell
cd frontend
npm install
npm run dev
```

打开：

```text
http://localhost:5173
```

## 第一版能力

- 上传 PDF 或 DOCX 简历。
- 输入目标公司、目标岗位和 JD。
- 调用 DeepSeek 运行双 Agent ReAct 优化流程。
- 以对话形式展示诊断、Agent 思考摘要、行动轨迹、优化后简历和面试预测问题。
```

- [ ] **Step 2: Run backend tests**

Run:

```powershell
python -m pytest tests/backend -v
```

Expected:

```text
all backend tests pass
```

- [ ] **Step 3: Run frontend tests**

Run:

```powershell
cd frontend
npm run test
```

Expected:

```text
all frontend tests pass
```

- [ ] **Step 4: Build frontend**

Run:

```powershell
cd frontend
npm run build
```

Expected:

```text
✓ built
```

- [ ] **Step 5: Run backend locally**

Run:

```powershell
cd backend
uvicorn react_resume.app:app --reload --host 127.0.0.1 --port 8000
```

Expected:

```text
Uvicorn running on http://127.0.0.1:8000
```

- [ ] **Step 6: Run frontend locally**

In a second terminal:

```powershell
cd frontend
npm run dev
```

Expected:

```text
Local: http://localhost:5173/
```

- [ ] **Step 7: Manual product smoke**

Open `http://localhost:5173`, upload a `.docx` resume, paste:

```text
我想投字节跳动的后端开发岗。JD：要求 Java、Spring Boot、MySQL、Redis、消息队列、分布式系统经验。
```

Expected visible result:

```text
用户消息显示上传文件名。
Assistant 显示简历诊断。
页面展示 DecisionAgent 和 ActionAgent 的 ReAct 轨迹。
页面展示定制版简历。
页面展示面试预测问题。
```

- [ ] **Step 8: Commit this task**

If git is initialized:

```powershell
git add README.md
git commit -m "docs: add local development guide"
```

---

## Final Verification Checklist

- [ ] `python -m pytest tests/backend -v` passes.
- [ ] `cd frontend && npm run test` passes.
- [ ] `cd frontend && npm run build` passes.
- [ ] `GET /api/health` returns `{"status":"ok"}`.
- [ ] `POST /api/optimize-resume` accepts `.pdf` and `.docx`.
- [ ] `.doc` and unsupported extensions return clear 400 errors.
- [ ] Vue page has text input, file upload, and send button.
- [ ] Vue page does not show “深度思考/深度搜索” or “智能搜索”.
- [ ] Assistant output appears as chat messages.
- [ ] ReAct trace shows only productized summaries, not raw hidden reasoning.
- [ ] Maximum optimization loop is three rounds.
- [ ] DeepSeek API key is read from environment variables.

## Execution Recommendation

Recommended execution mode:

```text
Subagent-Driven
```

Use one focused worker per backend/frontend module, then review and run verification between tasks. If working in one session, use inline execution and complete tasks in order from Task 1 through Task 16.
