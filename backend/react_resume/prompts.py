SAFETY_RULES = (
    "你可以优化表达，但不能虚构学历、公司、项目、奖项、技能、编程语言、框架或工具。"
    "禁止把 JD 中出现但原简历没有证据支持的技术栈写成候选人已经掌握。"
    "如果 JD 要求某技能但原简历未体现，只能写成“存在差距”或“建议补充真实经历”，"
    "不能写成“熟悉/掌握/使用/负责/参与过”。"
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
                "诊断时请明确区分“简历已证明的能力”和“JD 要求但简历未体现的差距”。"
            ),
        },
    ]


def build_action_prompt(
    action_name: str,
    resume_text: str,
    jd_text: str,
    previous_feedback: str,
) -> list[dict[str, str]]:
    output_instruction = "请输出本轮优化后的简历正文。"
    if action_name == "generate_resume_and_interview_questions":
        output_instruction = (
            "请一次性完成技能重构、项目 STAR 化、JD 关键词匹配和面试题预测。"
            "必须按以下结构输出：\n"
            "## 定制简历\n"
            "输出完整简历 Markdown。\n\n"
            "## 面试预测问题\n"
            "每行一个问题，建议 6-10 个。\n"
            "如果 JD 技能在原简历中未体现，请在简历中写为“建议补充真实经历”，"
            "不要写成候选人已经熟悉或使用过。"
        )
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
                f"\n输出要求：{output_instruction}"
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
