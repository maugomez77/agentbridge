import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "")
    secret_key: str = os.getenv("AGENTBRIDGE_SECRET_KEY", "dev-key-change-in-prod")
    data_dir: Path = Path.home() / ".agentbridge"
    stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "")
    stripe_pro_price_id: str = os.getenv("STRIPE_PRO_PRICE_ID", "price_pro_monthly")
    stripe_ent_price_id: str = os.getenv("STRIPE_ENT_PRICE_ID", "price_ent_monthly")

    model_config = {"env_prefix": "AGENTBRIDGE_"}


settings = Settings()


def ensure_dirs():
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    for d in ["projects", "artifacts", "servers"]:
        (settings.data_dir / d).mkdir(exist_ok=True)
