from backend.react_resume.agents import ActionAgent, DecisionAgent
from backend.react_resume.llm import LLMProvider
from backend.react_resume.models import AgentTrace, OptimizeResumeResponse, ParsedResume
from backend.react_resume.output import build_optimize_response, split_resume_and_questions
from backend.react_resume.prompts import build_action_prompt, build_decision_prompt
from backend.react_resume.safety import sanitize_unsupported_skill_claims


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

        trace.append(
            AgentTrace(
                round=1,
                agent="DecisionAgent",
                thought="根据诊断结果压缩执行路径，减少模型调用等待时间。",
                action="choose_balanced_actions",
                observation="将技能重构、项目 STAR 化、JD 关键词匹配合并为一次综合改写。",
            )
        )
        trace.append(
            AgentTrace(
                round=1,
                agent="DecisionAgent",
                thought="把面试题预测合并到综合输出中，保留 ReAct 解释摘要。",
                action="merge_interview_prediction",
                observation="下一步由 ActionAgent 一次性生成定制简历和面试预测问题。",
            )
        )

        action_trace, generated_text = self.action_agent.execute(
            round_number=1,
            action_name="generate_resume_and_interview_questions",
            resume_text=parsed_resume.raw_text,
            jd_text=jd_text,
            feedback=diagnosis,
        )
        action_trace.observation = "已生成定制简历和面试预测问题。"
        trace.append(action_trace)

        optimized_resume, questions_text = split_resume_and_questions(generated_text)
        optimized_resume, safety_warnings = sanitize_unsupported_skill_claims(
            source_resume=parsed_resume.raw_text,
            optimized_resume=optimized_resume,
        )
        warnings.extend(safety_warnings)
        return build_optimize_response(
            diagnosis=diagnosis,
            trace=trace,
            optimized_resume=optimized_resume,
            questions_text=questions_text,
            warnings=warnings,
        )

    def stream(
        self,
        parsed_resume: ParsedResume,
        jd_text: str,
        target_company: str,
        target_role: str,
    ):
        trace: list[AgentTrace] = []
        warnings = list(parsed_resume.warnings)

        yield {"type": "status", "message": "已读取简历，正在诊断与 JD 的匹配差距。"}
        diagnosis_parts: list[str] = []
        for chunk in self._stream_generate(
            build_decision_prompt(
                resume_text=parsed_resume.raw_text,
                jd_text=jd_text,
                target_company=target_company,
                target_role=target_role,
            )
        ):
            diagnosis_parts.append(chunk)
            yield {"type": "diagnosis_delta", "content": chunk}

        diagnosis = "".join(diagnosis_parts).strip()
        trace.append(
            AgentTrace(
                round=0,
                agent="DecisionAgent",
                thought="分析简历与 JD 的差距，并制定优化优先级。",
                action="analyze_resume_gap",
                observation=diagnosis,
            )
        )
        trace.append(
            AgentTrace(
                round=1,
                agent="DecisionAgent",
                thought="根据诊断结果压缩执行路径，减少模型调用等待时间。",
                action="choose_balanced_actions",
                observation="将技能重构、项目 STAR 化、JD 关键词匹配合并为一次综合改写。",
            )
        )
        trace.append(
            AgentTrace(
                round=1,
                agent="DecisionAgent",
                thought="把面试题预测合并到综合输出中，保留 ReAct 解释摘要。",
                action="merge_interview_prediction",
                observation="下一步由 ActionAgent 一次性生成定制简历和面试预测问题。",
            )
        )

        yield {"type": "status", "message": "诊断完成，正在生成定制简历与面试预测问题。"}
        generated_parts: list[str] = []
        for chunk in self._stream_generate(
            build_action_prompt(
                action_name="generate_resume_and_interview_questions",
                resume_text=parsed_resume.raw_text,
                jd_text=jd_text,
                previous_feedback=diagnosis,
            )
        ):
            generated_parts.append(chunk)
            yield {"type": "answer_delta", "content": chunk}

        generated_text = "".join(generated_parts)
        trace.append(
            AgentTrace(
                round=1,
                agent="ActionAgent",
                thought="执行第 1 轮优化任务：generate_resume_and_interview_questions。",
                action="generate_resume_and_interview_questions",
                observation="已生成定制简历和面试预测问题。",
            )
        )

        optimized_resume, questions_text = split_resume_and_questions(generated_text)
        optimized_resume, safety_warnings = sanitize_unsupported_skill_claims(
            source_resume=parsed_resume.raw_text,
            optimized_resume=optimized_resume,
        )
        warnings.extend(safety_warnings)
        response = build_optimize_response(
            diagnosis=diagnosis,
            trace=trace,
            optimized_resume=optimized_resume,
            questions_text=questions_text,
            warnings=warnings,
        )
        yield {"type": "result", "data": response.model_dump()}
        yield {"type": "done"}

    def _stream_generate(self, messages: list[dict[str, str]]):
        stream_generate = getattr(self.provider, "stream_generate", None)
        if callable(stream_generate):
            yield from stream_generate(messages)
            return
        yield self.provider.generate(messages)
