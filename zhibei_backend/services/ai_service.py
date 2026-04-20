from openai import OpenAI
from config import Config


def get_provider_config(provider_name):
    """Get provider URL + API key from Config."""
    provider_info = Config.AI_PROVIDERS.get(provider_name)
    if not provider_info:
        return None, None

    env_key = provider_info.get('env_key', '')
    api_key = getattr(Config, env_key, '')
    base_url = provider_info.get('default_url', '')

    if not api_key:
        return None, None

    return base_url, api_key


def stream_ai_response(provider, model, messages, temperature=0.7):
    """Generator that yields text chunks from the AI API.

    Uses the OpenAI Python SDK which is compatible with all 3 providers.
    Yields text content strings incrementally.
    """
    base_url, api_key = get_provider_config(provider)
    if not base_url or not api_key:
        raise ValueError(f"API key not configured for provider: {provider}")

    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )

    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=4096,
        stream=True
    )

    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def call_ai_sync(provider, model, messages, temperature=0.7):
    """Non-streaming AI call. Returns full response text."""
    base_url, api_key = get_provider_config(provider)
    if not base_url or not api_key:
        raise ValueError(f"API key not configured for provider: {provider}")

    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=4096,
        stream=False
    )

    if response.choices and response.choices[0].message:
        return response.choices[0].message.content
    return ''
