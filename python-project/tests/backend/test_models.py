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
