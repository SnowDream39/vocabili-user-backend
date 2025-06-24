import os
from dotenv import load_dotenv

# 判断使用哪个 env 文件
env_file = '.env'
load_dotenv(dotenv_path=env_file)

class Settings:
    APP_ENV: str = os.getenv("APP_ENV", "development")
    API_HOST: str = os.getenv("API_HOST", "http://localhost:8000")
    PORT: str = os.getenv("PORT", "8000")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ROOT: str = os.getenv("ROOT", "")

settings = Settings()

SECRET = 'SECRET'