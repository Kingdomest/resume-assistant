import re


TECH_TERMS: dict[str, tuple[str, ...]] = {
    "Java": ("Java",),
    "Rust": ("Rust",),
    "Go": ("Go", "Golang"),
    "Python": ("Python",),
    "C++": ("C++",),
    "C#": ("C#",),
    "JavaScript": ("JavaScript", "JS"),
    "TypeScript": ("TypeScript", "TS"),
    "PHP": ("PHP",),
    "Ruby": ("Ruby",),
    "Kotlin": ("Kotlin",),
    "Swift": ("Swift",),
    "Scala": ("Scala",),
    "Spring Boot": ("Spring Boot", "SpringBoot"),
    "Spring Cloud": ("Spring Cloud", "SpringCloud"),
    "Django": ("Django",),
    "Flask": ("Flask",),
    "FastAPI": ("FastAPI",),
    "Vue": ("Vue", "Vue.js"),
    "React": ("React", "React.js"),
    "Angular": ("Angular",),
    "Node.js": ("Node.js", "NodeJS", "Node"),
    "Express": ("Express", "Express.js"),
    "Redis": ("Redis",),
    "MySQL": ("MySQL",),
    "PostgreSQL": ("PostgreSQL", "Postgres"),
    "MongoDB": ("MongoDB",),
    "Elasticsearch": ("Elasticsearch", "ElasticSearch", "ES"),
    "Kafka": ("Kafka",),
    "RabbitMQ": ("RabbitMQ",),
    "RocketMQ": ("RocketMQ",),
    "Docker": ("Docker",),
    "Kubernetes": ("Kubernetes", "K8s"),
    "Linux": ("Linux",),
    "Nginx": ("Nginx",),
    "AWS": ("AWS",),
    "Azure": ("Azure",),
    "GCP": ("GCP", "Google Cloud"),
    "Spark": ("Spark",),
    "Hadoop": ("Hadoop",),
    "Flink": ("Flink",),
    "TensorFlow": ("TensorFlow",),
    "PyTorch": ("PyTorch",),
    "微服务": ("微服务",),
    "分布式": ("分布式", "分布式系统"),
    "高并发": ("高并发",),
}

SAFE_GAP_MARKERS = (
    "未体现",
    "待补充",
    "建议补充",
    "如有",
    "若有",
    "如果具备",
    "不建议",
    "请补充真实",
    "存在差距",
    "暂未写入",
    "无法写入",
)


def _contains_alias(text: str, alias: str) -> bool:
    if any("\u4e00" <= char <= "\u9fff" for char in alias):
        return alias in text

    pattern = rf"(?<![A-Za-z0-9+#.]){re.escape(alias)}(?![A-Za-z0-9+#.])"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def find_tech_terms(text: str) -> set[str]:
    return {
        term
        for term, aliases in TECH_TERMS.items()
        if any(_contains_alias(text, alias) for alias in aliases)
    }


def _is_gap_or_suggestion_line(line: str) -> bool:
    return any(marker in line for marker in SAFE_GAP_MARKERS)


def _format_terms(terms: set[str]) -> str:
    return "、".join(sorted(terms))


def sanitize_unsupported_skill_claims(
    source_resume: str,
    optimized_resume: str,
) -> tuple[str, list[str]]:
    source_terms = find_tech_terms(source_resume)
    output_terms = find_tech_terms(optimized_resume)
    unsupported_terms = output_terms - source_terms
    if not unsupported_terms:
        return optimized_resume, []

    lines: list[str] = []
    risky_terms: set[str] = set()

    for line in optimized_resume.splitlines():
        line_terms = find_tech_terms(line) & unsupported_terms
        if not line_terms or _is_gap_or_suggestion_line(line):
            lines.append(line)
            continue

        risky_terms.update(line_terms)
        lines.append(
            f"（真实性校验）原简历未体现 {_format_terms(line_terms)}，"
            "请补充真实经历后再写入。"
        )

    if not risky_terms:
        return "\n".join(lines), []

    warning = (
        f"优化结果中出现原简历未体现的技术栈：{_format_terms(risky_terms)}。"
        "相关表述已替换为补充真实经历提示，避免把 JD 要求写成候选人经历。"
    )
    return "\n".join(lines), [warning]
