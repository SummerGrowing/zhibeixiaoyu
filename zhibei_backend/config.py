import os
from dotenv import load_dotenv

load_dotenv()


def _get_database_path():
    """Get database path - use /tmp on Render for ephemeral filesystem."""
    if os.environ.get('RENDER'):
        return '/tmp/zhibei.db'
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zhibei.db')


class Config:
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    QWEN_API_KEY = os.getenv('QWEN_API_KEY', '')
    DATABASE_PATH = _get_database_path()
    DEFAULT_AI_PROVIDER = os.getenv('DEFAULT_AI_PROVIDER', 'deepseek')
    DEFAULT_AI_MODEL = os.getenv('DEFAULT_AI_MODEL', 'deepseek-chat')

    AI_PROVIDERS = {
        'openai': {
            'name': 'OpenAI',
            'default_url': 'https://api.openai.com/v1',
            'models': ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo'],
            'env_key': 'OPENAI_API_KEY'
        },
        'qwen': {
            'name': '通义千问',
            'default_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
            'models': ['qwen-max', 'qwen-plus', 'qwen-turbo', 'qwen-long'],
            'env_key': 'QWEN_API_KEY'
        },
        'deepseek': {
            'name': 'DeepSeek',
            'default_url': 'https://api.deepseek.com/v1',
            'models': ['deepseek-chat', 'deepseek-reasoner'],
            'env_key': 'DEEPSEEK_API_KEY'
        }
    }
