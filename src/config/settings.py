# src/config/settings.py

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration loaded from environment or defaults.
    """
    dumps_dir: Path = Path("dumps/time")

    sys_glob: str = "sys_mem_*.csv"
    proc_glob: str = "process_mem_*.csv"

    class Config:
        env_file = ".env"
