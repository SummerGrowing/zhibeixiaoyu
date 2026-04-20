import json
from flask import Blueprint, jsonify, request
from db.database import get_db_connection

curriculum_bp = Blueprint('curriculum', __name__)


@curriculum_bp.route('/curriculum', methods=['GET'])
def get_curriculum():
    """GET /api/curriculum
    Returns full curriculum tree with position numbers:
    { "一年级上册": { "第一单元·识字": [{"name":"天地人","type":"识字","focus":[...],"unitNumber":1,"lessonNumber":1}, ...], ...}, ... }
    """
    conn = get_db_connection()
    grades = conn.execute("SELECT id, name FROM grades ORDER BY id").fetchall()
    result = {}
    for grade in grades:
        units = conn.execute(
            "SELECT id, name FROM units WHERE grade_id = ? ORDER BY id",
            (grade['id'],)
        ).fetchall()
        grade_data = {}
        for unit_idx, unit in enumerate(units, 1):
            lessons = conn.execute(
                "SELECT name, type, focus FROM lessons WHERE unit_id = ? ORDER BY id",
                (unit['id'],)
            ).fetchall()
            grade_data[unit['name']] = [
                {
                    "name": l['name'],
                    "type": l['type'],
                    "focus": json.loads(l['focus']) if l['focus'] else [],
                    "unitNumber": unit_idx,
                    "lessonNumber": lesson_idx
                }
                for lesson_idx, l in enumerate(lessons, 1)
            ]
        result[grade['name']] = grade_data
    conn.close()
    return jsonify(result)


@curriculum_bp.route('/focus-options', methods=['GET'])
def get_focus_options():
    """GET /api/focus-options?textType=散文
    Returns supplementary focus options for a text type.
    """
    text_type = request.args.get('textType', '')
    conn = get_db_connection()
    row = conn.execute(
        "SELECT options FROM focus_by_type WHERE text_type = ?",
        (text_type,)
    ).fetchone()
    conn.close()
    if row:
        return jsonify(json.loads(row['options']))
    return jsonify([])


@curriculum_bp.route('/lesson-detail', methods=['GET'])
def get_lesson_detail():
    """GET /api/lesson-detail?grade=四年级上册&unit=第一单元·自然之美&lesson=观潮
    Returns detailed lesson data including focus keywords, vocabulary, etc.
    """
    grade = request.args.get('grade', '')
    unit = request.args.get('unit', '')
    lesson = request.args.get('lesson', '')

    conn = get_db_connection()
    result = {}

    # Try grade4a_lesson_data first (for 四年级上册)
    if '四年级上册' in grade:
        row = conn.execute(
            "SELECT * FROM grade4a_lesson_data WHERE lesson_name = ?",
            (lesson,)
        ).fetchone()
        if row:
            result = {
                "focusKeywords": json.loads(row['focus_keywords']) if row['focus_keywords'] else [],
                "vocabulary": row['vocabulary'] or '',
                "readingGuide": row['reading_guide'] or '',
                "tasks": json.loads(row['tasks']) if row['tasks'] else [],
                "supplement": row['supplement'] or '',
                "isSkimming": bool(row['is_skimming'])
            }

    # Try lesson_focus_map for all grades
    row = conn.execute(
        "SELECT * FROM lesson_focus_map WHERE lesson_name = ?",
        (lesson,)
    ).fetchone()
    if row:
        result["lessonFocusMap"] = {
            "recommended": json.loads(row['recommended']) if row['recommended'] else [],
            "optional": json.loads(row['optional']) if row['optional'] else []
        }

    # Try unit keywords for 四年级上册
    if '四年级上册' in grade:
        uk_row = conn.execute(
            "SELECT * FROM grade4a_unit_keywords WHERE unit_name = ?",
            (unit,)
        ).fetchone()
        if uk_row:
            result["unitKeywords"] = {
                "theme": uk_row['theme'] or '',
                "readingElement": uk_row['reading_element'] or '',
                "writingElement": uk_row['writing_element'] or '',
                "taskGroup": uk_row['task_group'] or '',
                "motto": uk_row['motto'] or '',
                "goals": json.loads(uk_row['goals']) if uk_row['goals'] else []
            }

    # Try unit focus refinement
    ufr_rows = conn.execute("SELECT * FROM unit_focus_refinement").fetchall()
    if ufr_rows:
        result["unitFocusRefinementMap"] = {
            row['focus_name']: {
                "refinedOptions": json.loads(row['refined_options']) if row['refined_options'] else [],
                "relatedLessonFocus": json.loads(row['related_lesson_focus']) if row['related_lesson_focus'] else []
            }
            for row in ufr_rows
        }

    conn.close()
    return jsonify(result)
