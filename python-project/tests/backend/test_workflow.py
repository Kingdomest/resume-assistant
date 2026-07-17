from backend.react_resume.models import OptimizeResumeResponse, ParsedResume
from backend.react_resume.output import parse_interview_questions
from backend.react_resume.workflow import ResumeOptimizationWorkflow


class FakeProvider:
    def __init__(self) -> None:
        self.outputs = [
            "诊断：技能描述偏泛，项目缺少量化，JD 关键词不足。",
            (
                "## 定制简历\n"
                "面向字节后端开发岗位\n\n"
                "## 面试预测问题\n"
                "1. Redis 缓存一致性怎么保证？\n"
                "2. MySQL 索引失效场景有哪些？"
            ),
        ]
        self.calls = 0

    def generate(self, messages: list[dict[str, str]], temperature: float = 0.3) -> str:
        self.calls += 1
        return self.outputs.pop(0)


class RiskyProvider:
    def __init__(self) -> None:
        self.outputs = [
            "诊断：JD 要求 Rust，但原简历只体现 Java。",
            (
                "## 定制简历\n"
                "熟悉 Rust，参与 Rust 高性能服务开发。\n\n"
                "## 面试预测问题\n"
                "1. Rust 所有权机制是什么？"
            ),
        ]

    def generate(self, messages: list[dict[str, str]], temperature: float = 0.3) -> str:
        return self.outputs.pop(0)


def test_parse_interview_questions_removes_number_prefix():
    questions = parse_interview_questions("1. Redis 缓存一致性怎么保证？\n2、MySQL 索引失效场景有哪些？")

    assert questions == [
        "Redis 缓存一致性怎么保证？",
        "MySQL 索引失效场景有哪些？",
    ]


def test_workflow_runs_balanced_two_call_flow_and_returns_response():
    provider = FakeProvider()
    workflow = ResumeOptimizationWorkflow(provider)
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
    assert provider.calls == 2
    assert "技能描述偏泛" in response.diagnosis
    assert "面向字节后端开发岗位" in response.optimized_resume
    assert len(response.react_trace) == 4
    assert response.react_trace[-1].action == "generate_resume_and_interview_questions"
    assert response.interview_questions[0] == "Redis 缓存一致性怎么保证？"


def test_workflow_does_not_turn_missing_jd_skill_into_resume_claim():
    workflow = ResumeOptimizationWorkflow(RiskyProvider())
    parsed = ParsedResume(
        file_name="resume.txt",
        file_type="text",
        raw_text="熟悉 Java，参与过订单系统开发。",
        warnings=[],
    )

    response = workflow.run(
        parsed_resume=parsed,
        jd_text="要求熟悉 Rust，有系统性能优化经验。",
        target_company="目标公司",
        target_role="后端开发",
    )

    assert "熟悉 Rust" not in response.optimized_resume
    assert "原简历未体现 Rust" in response.optimized_resume
    assert response.warnings
    assert "Rust" in response.warnings[0]
