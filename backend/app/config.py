import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def get_geoapify_api_key() -> str:
    return os.getenv("GEOAPIFY_API_KEY", "").strip()


def geoapify_key_status() -> str:
    if get_geoapify_api_key():
        return "key is configured"
    return "key is not configured"
