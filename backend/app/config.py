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


def get_openai_key() -> str:
    # OPEN_AI is the custom variable used in the class activity; pass it explicitly.
    return os.getenv('OPEN_AI', '').strip()


def get_openai_model() -> str:
    return os.getenv('OPENAI_MODEL', 'gpt-5.6-luna').strip() or 'gpt-5.6-luna'
