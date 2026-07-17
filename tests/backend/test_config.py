from backend.react_resume.config import Settings


def test_settings_defaults_are_safe_for_local_dev():
    settings = Settings(_env_file=None, deepseek_api_key="test-key")

    assert settings.deepseek_api_key == "test-key"
    assert settings.deepseek_base_url == "https://api.deepseek.com"
    assert settings.deepseek_model == "deepseek-chat"
    assert settings.max_resume_bytes == 5 * 1024 * 1024
    assert settings.allowed_origins == ["http://localhost:5173"]


def test_settings_accepts_comma_separated_origins():
    settings = Settings(
        _env_file=None,
        deepseek_api_key="test-key",
        allowed_origins="http://localhost:5173,http://127.0.0.1:5173",
    )

    assert settings.allowed_origins == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
