from flask import Blueprint, jsonify, request
from services.kebiao_retriever import get_relevant_kebiao_context

kebiao_bp = Blueprint('kebiao', __name__)


@kebiao_bp.route('/kebiao-context', methods=['GET'])
def get_kebiao_context():
    """GET /api/kebiao-context?grade=四年级上册&textType=散文&focuses=品读语言,朗读感悟
    Returns smart-retrieved relevant kebiao context.
    """
    grade = request.args.get('grade', '')
    text_type = request.args.get('textType', '')
    focuses_str = request.args.get('focuses', '')
    focuses = [f.strip() for f in focuses_str.split(',') if f.strip()]

    context = get_relevant_kebiao_context(grade, text_type, focuses)
    return jsonify({
        "context": context,
        "charCount": len(context)
    })
