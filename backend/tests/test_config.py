from src.config import settings

def test_config_loads():
    assert settings.PROJECT_NAME == "Lockdev SaaS"
    assert settings.DATABASE_URL is not None
