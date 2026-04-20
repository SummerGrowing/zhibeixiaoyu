from flask import Blueprint, jsonify
from config import Config

providers_bp = Blueprint('providers', __name__)


@providers_bp.route('/providers', methods=['GET'])
def get_providers():
    """GET /api/providers
    Returns available AI providers and their models.
    No API keys are exposed to the frontend - only boolean hasKey.
    """
    result = {}
    for provider_id, provider_info in Config.AI_PROVIDERS.items():
        env_key = provider_info.get('env_key', '')
        has_key = bool(getattr(Config, env_key, ''))
        result[provider_id] = {
            "name": provider_info['name'],
            "models": provider_info['models'],
            "hasKey": has_key
        }
    return jsonify(result)
