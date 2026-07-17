from backend.react_resume.safety import find_tech_terms, sanitize_unsupported_skill_claims


def test_find_tech_terms_does_not_confuse_java_and_javascript():
    assert find_tech_terms("熟悉 Java 后端开发") == {"Java"}
    assert find_tech_terms("熟悉 JavaScript 和 React") == {"JavaScript", "React"}


def test_sanitize_replaces_unsupported_skill_claims():
    sanitized, warnings = sanitize_unsupported_skill_claims(
        source_resume="熟悉 Java，参与过订单系统开发。",
        optimized_resume="## 定制简历\n熟悉 Rust，参与 Rust 高性能服务开发。",
    )

    assert "熟悉 Rust" not in sanitized
    assert "原简历未体现 Rust" in sanitized
    assert warnings
    assert "Rust" in warnings[0]


def test_sanitize_keeps_gap_or_suggestion_lines():
    sanitized, warnings = sanitize_unsupported_skill_claims(
        source_resume="熟悉 Java，参与过订单系统开发。",
        optimized_resume="当前简历未体现 Rust 经验，建议补充真实项目后再写入。",
    )

    assert "未体现 Rust 经验" in sanitized
    assert warnings == []
