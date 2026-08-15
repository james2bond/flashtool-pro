import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # NVIDIA API
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
    NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
    NVIDIA_MODEL = "meta/llama-3.1-70b-instruct"

    # Database (SQLite for now)
    DATABASE_URL = "sqlite:///flashtool.db"

    # USB Tools
    ADB_PATH = "adb"
    FASTBOOT_PATH = "fastboot"
    HEIMDALL_PATH = "heimdall"

    # Logging
    LOG_FILE = "flashtool.log"

    # Queue (Redis later)
    REDIS_URL = "redis://localhost:6379"
