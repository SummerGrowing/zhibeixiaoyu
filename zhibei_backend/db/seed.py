import json
import re
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import init_db, get_db_connection, execute_db, execute_many_db
from knowledge.curriculum_data import CURRICULUM_DATA
from knowledge.focus_by_type import FOCUS_BY_TYPE
from knowledge.lesson_focus_map import LESSON_FOCUS_MAP
from knowledge.unit_focus_refinement_map import UNIT_FOCUS_REFINEMENT_MAP
from knowledge.kebiao_core import KEBIAO_CORE
from knowledge.kebiao_phase_req import KEBIAO_PHASE_REQ
from knowledge.kebiao_task_groups import KEBIAO_TASK_GROUPS
from knowledge.grade4a_unit_keywords import GRADE4A_UNIT_KEYWORDS
from knowledge.grade4a_lesson_data import GRADE4A_LESSON_DATA

# These files will be created by another agent - use try/except
try:
    from knowledge.focus_keyword_library import FOCUS_KEYWORD_LIBRARY
except ImportError:
    FOCUS_KEYWORD_LIBRARY = {}

try:
    from knowledge.kebiao_content_themes import KEBIAO_CONTENT_THEMES
except ImportError:
    KEBIAO_CONTENT_THEMES = {}

try:
    from knowledge.kebiao_teaching_tips import KEBIAO_TEACHING_TIPS
except ImportError:
    KEBIAO_TEACHING_TIPS = []

try:
    from knowledge.grade4a_global_keywords import GRADE4A_GLOBAL_KEYWORDS
except ImportError:
    GRADE4A_GLOBAL_KEYWORDS = {}

try:
    from knowledge.text_type_maps import TEXT_TYPE_FOCUS_MAP, TEXT_TYPE_METHODS_MAP
except ImportError:
    TEXT_TYPE_FOCUS_MAP = {}
    TEXT_TYPE_METHODS_MAP = {}

try:
    from knowledge.kebiao_full_text import KEBIAO_FULL_TEXT
except ImportError:
    KEBIAO_FULL_TEXT = ""

try:
    from knowledge.grade4a_teaching_focus_full import GRADE4A_TEACHING_FOCUS_FULL
except ImportError:
    GRADE4A_TEACHING_FOCUS_FULL = ""

try:
    from knowledge.grade4a_reading_guide_full import GRADE4A_READING_GUIDE_FULL
except ImportError:
    GRADE4A_READING_GUIDE_FULL = ""


def seed_grades_and_curriculum():
    conn = get_db_connection()
    for grade_name, units in CURRICULUM_DATA.items():
        conn.execute("INSERT OR IGNORE INTO grades (name) VALUES (?)", (grade_name,))
        grade_row = conn.execute("SELECT id FROM grades WHERE name = ?", (grade_name,)).fetchone()
        grade_id = grade_row['id']
        for unit_name, lessons in units.items():
            conn.execute("INSERT OR IGNORE INTO units (grade_id, name) VALUES (?, ?)", (grade_id, unit_name))
            unit_row = conn.execute("SELECT id FROM units WHERE grade_id = ? AND name = ?", (grade_id, unit_name)).fetchone()
            unit_id = unit_row['id']
            for lesson in lessons:
                focus_json = json.dumps(lesson.get('focus', []), ensure_ascii=False)
                conn.execute(
                    "INSERT OR IGNORE INTO lessons (unit_id, name, type, focus) VALUES (?, ?, ?, ?)",
                    (unit_id, lesson['name'], lesson['type'], focus_json)
                )
    conn.commit()
    conn.close()


def seed_focus_by_type():
    conn = get_db_connection()
    for text_type, options in FOCUS_BY_TYPE.items():
        options_json = json.dumps(options, ensure_ascii=False)
        conn.execute(
            "INSERT OR IGNORE INTO focus_by_type (text_type, options) VALUES (?, ?)",
            (text_type, options_json)
        )
    conn.commit()
    conn.close()


def seed_lesson_focus_map():
    conn = get_db_connection()
    for lesson_name, data in LESSON_FOCUS_MAP.items():
        recommended_json = json.dumps(data.get('recommended', []), ensure_ascii=False)
        optional_json = json.dumps(data.get('optional', []), ensure_ascii=False)
        conn.execute(
            "INSERT OR IGNORE INTO lesson_focus_map (lesson_name, recommended, optional) VALUES (?, ?, ?)",
            (lesson_name, recommended_json, optional_json)
        )
    conn.commit()
    conn.close()


def seed_unit_focus_refinement():
    conn = get_db_connection()
    for focus_name, data in UNIT_FOCUS_REFINEMENT_MAP.items():
        refined_json = json.dumps(data.get('refinedOptions', []), ensure_ascii=False)
        related_json = json.dumps(data.get('relatedLessonFocus', []), ensure_ascii=False)
        conn.execute(
            "INSERT OR IGNORE INTO unit_focus_refinement (focus_name, refined_options, related_lesson_focus) VALUES (?, ?, ?)",
            (focus_name, refined_json, related_json)
        )
    conn.commit()
    conn.close()


def seed_kebiao_core():
    conn = get_db_connection()
    dimensions_json = json.dumps(KEBIAO_CORE.get('dimensions', []), ensure_ascii=False)
    details_json = json.dumps(KEBIAO_CORE.get('details', {}), ensure_ascii=False)
    conn.execute(
        "INSERT OR IGNORE INTO kebiao_core (id, name, dimensions, description, details, relation) VALUES (?, ?, ?, ?, ?, ?)",
        (1, KEBIAO_CORE.get('name', ''), dimensions_json,
         KEBIAO_CORE.get('desc', ''), details_json,
         KEBIAO_CORE.get('relation', ''))
    )
    conn.commit()
    conn.close()


def seed_kebiao_phase_req():
    conn = get_db_connection()
    for phase, data in KEBIAO_PHASE_REQ.items():
        conn.execute(
            "INSERT OR IGNORE INTO kebiao_phase_req (phase, range_desc, literacy, reading, expression, organization) VALUES (?, ?, ?, ?, ?, ?)",
            (phase, data.get('range', ''), data.get('识字与写字', ''),
             data.get('阅读与鉴赏', ''), data.get('表达与交流', ''),
             data.get('梳理与探究', ''))
        )
    conn.commit()
    conn.close()


def seed_kebiao_task_groups():
    conn = get_db_connection()
    for name, data in KEBIAO_TASK_GROUPS.items():
        conn.execute(
            "INSERT OR IGNORE INTO kebiao_task_groups (name, level, description, relevance) VALUES (?, ?, ?, ?)",
            (name, data.get('level', ''), data.get('desc', ''), data.get('relevance', ''))
        )
    conn.commit()
    conn.close()


def seed_kebiao_content_themes():
    conn = get_db_connection()
    for theme_name, data in KEBIAO_CONTENT_THEMES.items():
        conn.execute(
            "INSERT OR IGNORE INTO kebiao_content_themes (theme_name, ideas, spirit, virtue, carriers, ratio) VALUES (?, ?, ?, ?, ?, ?)",
            (theme_name, data.get('ideas', ''), data.get('spirit', ''),
             data.get('virtue', ''), data.get('carriers', ''), data.get('ratio', ''))
        )
    conn.commit()
    conn.close()


def seed_kebiao_teaching_tips():
    conn = get_db_connection()
    for tip in KEBIAO_TEACHING_TIPS:
        conn.execute("INSERT OR IGNORE INTO kebiao_teaching_tips (tip_text) VALUES (?)", (tip,))
    conn.commit()
    conn.close()


def seed_kebiao_full_text_segmented():
    """Parse KEBIAO_FULL_TEXT into logical sections for smart retrieval."""
    if not KEBIAO_FULL_TEXT:
        return

    conn = get_db_connection()

    # Define section headers to split on
    section_patterns = [
        # (pattern, category, phase, keywords)
        (r'一、课程性质', '总则', None, ['课程性质', '语文课程']),
        (r'二、课程理念', '总则', None, ['课程理念', '核心素养']),
        (r'三、课程目标', '总则', None, ['课程目标', '总目标']),
        (r'（一）核心素养内涵', '核心素养', None, ['核心素养', '文化自信', '语言运用', '思维能力', '审美创造']),
        (r'（二）总目标', '总目标', None, ['总目标', '课程目标']),
        (r'（三）学段要求', '学段要求', None, ['学段要求']),
        (r'1\.\s*第一学段', '学段要求', '第一学段', ['第一学段', '1~2年级', '低年级']),
        (r'2\.\s*第二学段', '学段要求', '第二学段', ['第二学段', '3~4年级', '中年级']),
        (r'3\.\s*第三学段', '学段要求', '第三学段', ['第三学段', '5~6年级', '高年级']),
        (r'4\.\s*第四学段', '学段要求', '第四学段', ['第四学段', '7~9年级', '初中']),
        (r'四、课程内容', '课程内容', None, ['课程内容']),
        (r'（一）内容组织与呈现方式', '课程内容', None, ['学习任务群', '内容组织']),
        (r'（二）文化自信', '文化主题', None, ['文化自信', '中华优秀传统文化', '革命文化', '社会主义先进文化']),
        (r'1\.语言文字积累与梳理', '学习任务群', None, ['语言文字积累与梳理', '基础型', '识字写字', '朗读背诵']),
        (r'2\.实用性阅读与交流', '学习任务群', None, ['实用性阅读与交流', '发展型', '说明文', '信息提取']),
        (r'3\.文学阅读与创意表达', '学习任务群', None, ['文学阅读与创意表达', '发展型', '散文', '古诗', '小说', '童话', '神话']),
        (r'4\.思辨性阅读与表达', '学习任务群', None, ['思辨性阅读与表达', '发展型', '寓言', '文言文', '批判性思维']),
        (r'5\.整本书阅读', '学习任务群', None, ['整本书阅读', '拓展型', '课外阅读']),
        (r'6\.跨学科学习', '学习任务群', None, ['跨学科学习', '拓展型', '综合性学习']),
        (r'五、学业质量', '学业质量', None, ['学业质量', '评价']),
        (r'六、课程实施', '课程实施', None, ['课程实施', '教学建议', '评价建议']),
    ]

    # Split the full text by section headers
    lines = KEBIAO_FULL_TEXT.split('\n')
    sections = []
    current_section = {'title': '前言', 'content': '', 'category': '总则', 'phase': None, 'keywords': json.dumps(['前言', '义务教育'], ensure_ascii=False)}
    section_started = False

    for line in lines:
        matched = False
        for pattern, category, phase, keywords in section_patterns:
            if re.search(pattern, line):
                if current_section['content'].strip():
                    sections.append(current_section)
                current_section = {
                    'title': line.strip()[:100],
                    'content': line + '\n',
                    'category': category,
                    'phase': phase,
                    'keywords': json.dumps(keywords, ensure_ascii=False)
                }
                matched = True
                section_started = True
                break
        if not matched:
            current_section['content'] += line + '\n'

    if current_section['content'].strip():
        sections.append(current_section)

    # Also add learning task group sub-sections by phase
    # Re-parse sections that contain phase-specific content within task groups
    expanded_sections = []
    for sec in sections:
        if sec['category'] == '学习任务群' and len(sec['content']) > 2000:
            # Try to split this large section into phase sub-sections
            sub_sections = _split_task_group_by_phase(sec)
            expanded_sections.extend(sub_sections)
        else:
            expanded_sections.append(sec)

    for sec in expanded_sections:
        conn.execute(
            "INSERT INTO kebiao_full_text (section_title, content, keywords, phase, category) VALUES (?, ?, ?, ?, ?)",
            (sec['title'], sec['content'].strip(), sec['keywords'], sec['phase'], sec['category'])
        )

    conn.commit()
    conn.close()


def _split_task_group_by_phase(section):
    """Split a large task group section into phase-specific sub-sections."""
    content = section['content']
    phase_patterns = [
        (r'第一学段[（(]', '第一学段', ['第一学段', '1~2年级']),
        (r'第二学段[（(]', '第二学段', ['第二学段', '3~4年级']),
        (r'第三学段[（(]', '第三学段', ['第三学段', '5~6年级']),
        (r'第四学段[（(]', '第四学段', ['第四学段', '7~9年级']),
        (r'教学提示', '教学提示', ['教学提示', '教学建议']),
    ]

    sub_sections = []
    lines = content.split('\n')
    current = {
        'title': section['title'] + ' - 总述',
        'content': '',
        'category': section['category'],
        'phase': section['phase'],
        'keywords': section['keywords']
    }

    for line in lines:
        matched = False
        for pattern, phase_label, kw in phase_patterns:
            if re.search(pattern, line):
                if current['content'].strip():
                    sub_sections.append(current)
                current = {
                    'title': section['title'] + ' - ' + phase_label,
                    'content': line + '\n',
                    'category': section['category'],
                    'phase': phase_label if '学段' in phase_label else section['phase'],
                    'keywords': json.dumps(kw, ensure_ascii=False)
                }
                matched = True
                break
        if not matched:
            current['content'] += line + '\n'

    if current['content'].strip():
        sub_sections.append(current)

    return sub_sections if sub_sections else [section]


def seed_grade4a_unit_keywords():
    conn = get_db_connection()
    for unit_name, data in GRADE4A_UNIT_KEYWORDS.items():
        conn.execute(
            "INSERT OR IGNORE INTO grade4a_unit_keywords (unit_name, theme, reading_element, writing_element, task_group, motto, goals) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (unit_name, data.get('theme', ''), data.get('readingElement', ''),
             data.get('writingElement', ''), data.get('taskGroup', ''),
             data.get('motto', ''), json.dumps(data.get('goals', []), ensure_ascii=False))
        )
    conn.commit()
    conn.close()


def seed_grade4a_lesson_data():
    conn = get_db_connection()
    for lesson_name, data in GRADE4A_LESSON_DATA.items():
        focus_kw_json = json.dumps(data.get('focusKeywords', []), ensure_ascii=False)
        tasks_json = json.dumps(data.get('tasks', []), ensure_ascii=False)
        conn.execute(
            "INSERT OR IGNORE INTO grade4a_lesson_data (lesson_name, focus_keywords, vocabulary, reading_guide, tasks, supplement, is_skimming) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (lesson_name, focus_kw_json, data.get('vocabulary', ''),
             data.get('readingGuide', ''), tasks_json,
             data.get('supplement', ''), 1 if data.get('isSkimming', False) else 0)
        )
    conn.commit()
    conn.close()


def seed_grade4a_global_keywords():
    if not GRADE4A_GLOBAL_KEYWORDS:
        return
    conn = get_db_connection()
    for i, (category, keywords) in enumerate(GRADE4A_GLOBAL_KEYWORDS.items(), 1):
        kw_json = json.dumps(keywords, ensure_ascii=False)
        conn.execute(
            "INSERT OR IGNORE INTO grade4a_global_keywords (id, category, keywords) VALUES (?, ?, ?)",
            (i, category, kw_json)
        )
    conn.commit()
    conn.close()


def seed_grade4a_teaching_focus():
    if not GRADE4A_TEACHING_FOCUS_FULL:
        return
    conn = get_db_connection()
    # Split into paragraphs
    paragraphs = [p.strip() for p in GRADE4A_TEACHING_FOCUS_FULL.split('\n') if p.strip()]
    for para in paragraphs:
        conn.execute("INSERT INTO grade4a_teaching_focus (content) VALUES (?)", (para,))
    conn.commit()
    conn.close()


def seed_grade4a_reading_guide():
    if not GRADE4A_READING_GUIDE_FULL:
        return
    conn = get_db_connection()
    # Split into paragraphs
    paragraphs = [p.strip() for p in GRADE4A_READING_GUIDE_FULL.split('\n') if p.strip()]
    for para in paragraphs:
        conn.execute("INSERT INTO grade4a_reading_guide (content) VALUES (?)", (para,))
    conn.commit()
    conn.close()


def seed_focus_keyword_library():
    if not FOCUS_KEYWORD_LIBRARY:
        return
    conn = get_db_connection()
    for category, keywords in FOCUS_KEYWORD_LIBRARY.items():
        kw_json = json.dumps(keywords, ensure_ascii=False)
        conn.execute(
            "INSERT OR IGNORE INTO focus_keyword_library (category, keywords) VALUES (?, ?)",
            (category, kw_json)
        )
    conn.commit()
    conn.close()


def seed_text_type_maps():
    if not TEXT_TYPE_FOCUS_MAP and not TEXT_TYPE_METHODS_MAP:
        return
    conn = get_db_connection()
    for text_type, desc in TEXT_TYPE_FOCUS_MAP.items():
        conn.execute(
            "INSERT OR IGNORE INTO text_type_focus_map (text_type, focus_description) VALUES (?, ?)",
            (text_type, desc)
        )
    for text_type, desc in TEXT_TYPE_METHODS_MAP.items():
        conn.execute(
            "INSERT OR IGNORE INTO text_type_methods_map (text_type, methods_description) VALUES (?, ?)",
            (text_type, desc)
        )
    conn.commit()
    conn.close()


def seed_all():
    print("Initializing database...")
    init_db()
    print("Seeding grades and curriculum...")
    seed_grades_and_curriculum()
    print("Seeding focus by type...")
    seed_focus_by_type()
    print("Seeding lesson focus map...")
    seed_lesson_focus_map()
    print("Seeding unit focus refinement...")
    seed_unit_focus_refinement()
    print("Seeding kebiao core...")
    seed_kebiao_core()
    print("Seeding kebiao phase requirements...")
    seed_kebiao_phase_req()
    print("Seeding kebiao task groups...")
    seed_kebiao_task_groups()
    print("Seeding kebiao content themes...")
    seed_kebiao_content_themes()
    print("Seeding kebiao teaching tips...")
    seed_kebiao_teaching_tips()
    print("Seeding kebiao full text (segmented)...")
    seed_kebiao_full_text_segmented()
    print("Seeding grade4a unit keywords...")
    seed_grade4a_unit_keywords()
    print("Seeding grade4a lesson data...")
    seed_grade4a_lesson_data()
    print("Seeding grade4a global keywords...")
    seed_grade4a_global_keywords()
    print("Seeding grade4a teaching focus...")
    seed_grade4a_teaching_focus()
    print("Seeding grade4a reading guide...")
    seed_grade4a_reading_guide()
    print("Seeding focus keyword library...")
    seed_focus_keyword_library()
    print("Seeding text type maps...")
    seed_text_type_maps()
    print("Done! Database seeded successfully.")


if __name__ == '__main__':
    seed_all()
