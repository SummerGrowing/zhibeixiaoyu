import json
from flask import Blueprint, jsonify, request
from db.database import get_db_connection

keywords_bp = Blueprint('keywords', __name__)


@keywords_bp.route('/keyword-library', methods=['GET'])
def get_keyword_library():
    """GET /api/keyword-library
    Returns the focus keyword library for "other focus" quick selection.
    """
    conn = get_db_connection()
    rows = conn.execute("SELECT category, keywords FROM focus_keyword_library ORDER BY id").fetchall()
    result = {}
    for row in rows:
        result[row['category']] = json.loads(row['keywords'])
    conn.close()
    return jsonify(result)


@keywords_bp.route('/unit-keywords', methods=['GET'])
def get_unit_keywords():
    """GET /api/unit-keywords?grade=四年级上册&unit=第一单元
    Returns unit-level keywords data (theme, readingElement, etc.).
    """
    grade = request.args.get('grade', '')
    unit = request.args.get('unit', '')

    conn = get_db_connection()
    result = None

    if '四年级上册' in grade:
        row = conn.execute(
            "SELECT * FROM grade4a_unit_keywords WHERE unit_name = ?",
            (unit,)
        ).fetchone()
        if row:
            result = {
                "theme": row['theme'] or '',
                "readingElement": row['reading_element'] or '',
                "writingElement": row['writing_element'] or '',
                "taskGroup": row['task_group'] or '',
                "motto": row['motto'] or '',
                "goals": json.loads(row['goals']) if row['goals'] else []
            }

    conn.close()
    return jsonify(result)
