"""Read-only OpenAI model-access check; never prints credentials."""
import json

import httpx
from .config import get_openai_key, get_openai_model


def check():
    key, model = get_openai_key(), get_openai_model()
    if not key:
        return {'configured': False, 'model': model,
                'detail': 'Add OPEN_AI privately to the backend .env and restart.'}
    try:
        response = httpx.get(f'https://api.openai.com/v1/models/{model}',
                            headers={'Authorization': f'Bearer {key}'}, timeout=15)
        response.raise_for_status()
        return {'configured': True, 'model': model, 'accessible': response.json().get('id') == model,
                'note': 'No generation request made. Check API credit/spending limits in your OpenAI account; model access does not prove available credit.'}
    except (httpx.HTTPError, ValueError, TypeError):
        return {'configured': True, 'model': model, 'accessible': False,
                'detail': 'Model-access preflight failed; no generation request was made.'}


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
