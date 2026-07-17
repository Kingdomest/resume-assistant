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


class FakeProvider:
    def __init__(self, outputs: list[str]) -> None:
        self.outputs = outputs
        self.calls: list[list[dict[str, str]]] = []

    def generate(self, messages: list[dict[str, str]], temperature: float = 0.3) -> str:
        self.calls.append(messages)
        return self.outputs.pop(0)


def test_decision_agent_creates_diagnosis_trace():
    from backend.react_resume.agents import DecisionAgent

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
    assert provider.calls


def test_decision_agent_selects_expected_action_order():
    from backend.react_resume.agents import DecisionAgent

    agent = DecisionAgent(FakeProvider([]))

    assert agent.choose_action(1) == "rewrite_skills"
    assert agent.choose_action(2) == "rewrite_projects_with_star"
    assert agent.choose_action(3) == "generate_targeted_resume"


def test_action_agent_rewrites_by_action_name():
    from backend.react_resume.agents import ActionAgent

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
