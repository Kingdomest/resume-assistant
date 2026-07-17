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
