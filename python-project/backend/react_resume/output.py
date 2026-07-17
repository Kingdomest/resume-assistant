from backend.react_resume.models import AgentTrace, OptimizeResumeResponse


def parse_interview_questions(questions_text: str) -> list[str]:
    return [
        line.strip().lstrip("0123456789.、 ")
        for line in questions_text.splitlines()
        if line.strip()
    ]


def split_resume_and_questions(generated_text: str) -> tuple[str, str]:
    markers = [
        "## 面试预测问题",
        "### 面试预测问题",
        "面试预测问题：",
        "面试预测问题:",
        "面试预测问题",
    ]
    for marker in markers:
        if marker in generated_text:
            resume_text, questions_text = generated_text.split(marker, 1)
            return resume_text.strip(), questions_text.strip()
    return generated_text.strip(), generated_text.strip()


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
