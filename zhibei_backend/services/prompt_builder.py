import json
import re
from db.database import get_db_connection


def get_phase(grade):
    """Determine the learning phase based on grade name."""
    g = grade.replace('上册', '').replace('下册', '')
    if g in ('一年级', '二年级'):
        return '第一学段'
    elif g in ('三年级', '四年级'):
        return '第二学段'
    elif g in ('五年级', '六年级'):
        return '第三学段'
    return '第四学段'


def get_phase_number(grade):
    """Get the phase number (1-3) for a grade."""
    phase = get_phase(grade)
    return {'第一学段': 1, '第二学段': 2, '第三学段': 3}.get(phase, 2)


def get_unit_number(unit_name):
    """Extract unit number from unit name.
    E.g. '第一单元·自然之美' -> 1, '第五单元' -> 5
    """
    m = re.match(r'第([一二三四五六七八九十]+)单元', unit_name)
    if not m:
        return 1
    cn_map = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
              '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
    return cn_map.get(m.group(1), 1)


def get_lesson_number(grade, unit, lesson_name):
    """Get lesson sequence number within a unit from the database."""
    conn = get_db_connection()
    # Find the unit id
    grade_row = conn.execute("SELECT id FROM grades WHERE name = ?", (grade,)).fetchone()
    if not grade_row:
        conn.close()
        return 1
    unit_row = conn.execute(
        "SELECT id FROM units WHERE grade_id = ? AND name = ?",
        (grade_row['id'], unit)
    ).fetchone()
    if not unit_row:
        conn.close()
        return 1
    # Count lessons before this one in the same unit
    lessons = conn.execute(
        "SELECT id, name FROM lessons WHERE unit_id = ? ORDER BY id",
        (unit_row['id'],)
    ).fetchall()
    conn.close()
    for i, l in enumerate(lessons):
        if l['name'] == lesson_name:
            return i + 1
    return 1


def get_phase_summary(grade):
    """Get a summary of the phase requirements for a grade."""
    phase = get_phase(grade)
    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM kebiao_phase_req WHERE phase = ?",
        (phase,)
    ).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def get_relevant_task_groups(text_type):
    """Get task groups relevant to a text type."""
    literary_types = ['散文', '古诗', '小说', '童话', '神话', '现代诗', '寓言', '文言文']
    practical_types = ['说明文', '记叙文']

    conn = get_db_connection()
    rows = conn.execute("SELECT name, level, description, relevance FROM kebiao_task_groups").fetchall()
    conn.close()

    result = []
    for row in rows:
        r = dict(row)
        if r['level'] == '基础型':
            result.append(r)
        elif text_type in literary_types and '文学阅读与创意表达' in r['name']:
            result.append(r)
        elif text_type in practical_types and '实用性阅读与交流' in r['name']:
            result.append(r)
        elif text_type in ('寓言', '文言文') and '思辨性阅读与表达' in r['name']:
            result.append(r)
        elif '整本书阅读' in r['name'] or '跨学科学习' in r['name']:
            result.append(r)
    return result


def get_text_type_focus(text_type):
    """Get the focus description for a text type."""
    conn = get_db_connection()
    row = conn.execute(
        "SELECT focus_description FROM text_type_focus_map WHERE text_type = ?",
        (text_type,)
    ).fetchone()
    conn.close()
    if row:
        return row['focus_description']
    return '"个性化的语言、作者的情感、读者的想象"，引导学生品味文字背后的画面与情感'


def get_text_type_methods(text_type):
    """Get the methods description for a text type."""
    conn = get_db_connection()
    row = conn.execute(
        "SELECT methods_description FROM text_type_methods_map WHERE text_type = ?",
        (text_type,)
    ).fetchone()
    conn.close()
    if row:
        return row['methods_description']
    return '情境教学、朗读感悟、读写结合'


def get_grade_profile(grade):
    """Get a grade-level profile description from kebiao data."""
    phase = get_phase(grade)
    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM kebiao_phase_req WHERE phase = ?",
        (phase,)
    ).fetchone()
    conn.close()
    if not row:
        return '中高年级'

    g = grade.replace('上册', '').replace('下册', '')
    return (
        f"{g}学生（{phase}，{row['range_desc']}）。"
        f"识字写字方面：{(row['literacy'] or '')[:60]}；"
        f"阅读方面：{(row['reading'] or '')[:60]}；"
        f"表达方面：{(row['expression'] or '')[:60]}。"
    )


def get_grade_level(grade):
    """Get a grade level label."""
    g = grade.replace('上册', '').replace('下册', '')
    phase = get_phase(grade)
    return f"{g}（{phase}）"


def get_unit_keywords(grade, unit):
    """Get unit keywords data (currently only for 四年级上册)."""
    if '四年级上册' not in grade:
        return None
    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM grade4a_unit_keywords WHERE unit_name = ?",
        (unit,)
    ).fetchone()
    conn.close()
    if row:
        return {
            "theme": row['theme'] or '',
            "readingElement": row['reading_element'] or '',
            "writingElement": row['writing_element'] or '',
            "taskGroup": row['task_group'] or '',
            "motto": row['motto'] or '',
            "goals": json.loads(row['goals']) if row['goals'] else []
        }
    return None


def get_lesson_data(grade, lesson_name):
    """Get lesson-level data (currently only for 四年级上册)."""
    if '四年级上册' not in grade:
        return None
    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM grade4a_lesson_data WHERE lesson_name = ?",
        (lesson_name,)
    ).fetchone()
    conn.close()
    if row:
        return {
            "focusKeywords": json.loads(row['focus_keywords']) if row['focus_keywords'] else [],
            "vocabulary": row['vocabulary'] or '',
            "readingGuide": row['reading_guide'] or '',
            "tasks": json.loads(row['tasks']) if row['tasks'] else [],
            "supplement": row['supplement'] or '',
            "isSkimming": bool(row['is_skimming'])
        }
    return None


def build_aux_material_ref(grade, unit, lesson_name):
    """Build auxiliary material reference text (for 四年级上册 only)."""
    parts = []
    uk = get_unit_keywords(grade, unit)
    if uk:
        if uk.get('readingElement'):
            parts.append(f"单元阅读要素：{uk['readingElement']}")
        if uk.get('writingElement'):
            parts.append(f"单元写作要素：{uk['writingElement']}")
        if uk.get('taskGroup'):
            parts.append(f"相关学习任务群：{uk['taskGroup']}")

    ld = get_lesson_data(grade, lesson_name)
    if ld:
        if ld.get('focusKeywords'):
            parts.append(f"课文教学侧重：{', '.join(ld['focusKeywords'])}")
        if ld.get('readingGuide'):
            parts.append(f"课中提示：{ld['readingGuide']}")
        if ld.get('tasks'):
            task_strs = [t.get('desc', str(t)) if isinstance(t, dict) else str(t) for t in ld['tasks']]
            parts.append(f"课后任务：{', '.join(task_strs)}")
        if ld.get('supplement'):
            parts.append(f"资料袋/补充：{ld['supplement']}")

    return '\n'.join(parts)


def _get_recommended_dimensions(text_type):
    """Get recommended teaching target dimensions for a text type.
    Returns list of (dimension, reason) tuples.
    Dimensions: 识字与写字、阅读与鉴赏、表达与交流、梳理与探究
    """
    dimension_map = {
        '拼音': [('识字与写字', '拼音学习是识字基础'), ('阅读与鉴赏', '在语境中巩固拼音')],
        '识字': [('识字与写字', '识字课核心目标'), ('阅读与鉴赏', '在语境中巩固识字')],
        '古诗': [('阅读与鉴赏', '古诗赏析与朗读感悟'), ('表达与交流', '诗歌改写与表达')],
        '现代诗': [('阅读与鉴赏', '诗歌意象品读'), ('表达与交流', '仿写创作')],
        '散文': [('阅读与鉴赏', '品味语言与情感'), ('表达与交流', '读写迁移')],
        '记叙文': [('阅读与鉴赏', '理清叙事脉络与人物形象'), ('表达与交流', '叙事方法迁移')],
        '说明文': [('阅读与鉴赏', '提取信息与说明方法'), ('梳理与探究', '梳理说明逻辑')],
        '寓言': [('阅读与鉴赏', '理解故事与寓意'), ('梳理与探究', '思辨与联系生活')],
        '童话': [('阅读与鉴赏', '感受想象与角色'), ('表达与交流', '创编故事')],
        '神话': [('阅读与鉴赏', '感受神奇想象与人物精神'), ('梳理与探究', '文化价值探究')],
        '文言文': [('阅读与鉴赏', '疏通文意与朗读感悟'), ('梳理与探究', '思辨与寓意理解')],
        '小说': [('阅读与鉴赏', '人物形象与情节分析'), ('表达与交流', '描写方法迁移')],
    }
    return dimension_map.get(text_type, [('阅读与鉴赏', '核心阅读能力'), ('表达与交流', '语言表达训练')])


def build_prompt_template(grade, unit, lesson_name, text_type, focuses, other_focus, idea,
                          unit_number=None, lesson_number=None, phase_number=None):
    """Build a prompt that teachers can copy-paste into any AI chat.
    
    The prompt is a self-contained instruction text (starting with "你是一位..."),
    NOT a lesson plan itself. It tells the AI how to generate a lesson plan.
    """

    # Derive numbers if not provided
    if unit_number is None:
        unit_number = get_unit_number(unit)
    if lesson_number is None:
        lesson_number = get_lesson_number(grade, unit, lesson_name)
    if phase_number is None:
        phase_number = get_phase_number(grade)

    focus_str = '、'.join(focuses)
    if other_focus:
        focus_str += '、' + other_focus

    phase = get_phase(grade)
    grade_level = get_grade_level(grade)
    text_type_focus = get_text_type_focus(text_type)
    text_type_methods = get_text_type_methods(text_type)
    grade_profile = get_grade_profile(grade)

    # Build the prompt text — starts with "你是一位..."
    # This is a prompt for AI, not a lesson plan

    # --- 角色设定 + 任务 ---
    template = f"你是一位有15年教龄的小学语文特级教师，擅长{text_type}教学。请为统编版{grade}第{unit_number}单元第{lesson_number}课《{lesson_name}》设计一份第1课时详细教案。"

    # --- 四维知识框架 ---
    template += f"""

【四维知识框架】
- 文本知识：请根据课文内容，分析其核心写作特点、语言特色及思想情感。
- 文体知识：依据课文文体（如{text_type}），聚焦其教学要点（如{text_type}注重{text_type_focus}）。
- 学情知识：{phase}学生对本类文本的认知特点和学习需求，需结合具体学段特点设计教学。{grade_profile}
- 教学法知识：按需采用{text_type_methods}等方法。"""

    # --- 个性化设计要求 ---
    template += f"""

【个性化设计要求】
- 教学侧重：{focus_str}"""

    if idea:
        template += f"""
- 教师初步设想：{idea}"""

    # --- 教案要求 ---
    template += f"""

【教案要求】
主题（题目，居中，醒目）

一、目标确立依据
1. 课标依据：根据《义务教育语文课程标准（2022年版）》第{phase_number}学段要求，本课应引导学生【概括课标要求】。
2. 教材分析：本课是{grade}【第{unit_number}单元·单元主题】第{lesson_number}课，是{text_type}类型，课文描写/讲述了【主要内容概括】，表达了【情感/道理/主旨】。教学本文，能够引导学生【学习价值】。"""

    # Add auxiliary material reference if available (四年级上册)
    aux_ref = build_aux_material_ref(grade, unit, lesson_name)
    if aux_ref:
        template += f"""
【教材助读系统参考】{aux_ref}
（以上助读系统内容仅为参考依据，教师应结合自身对教材的理解和学生的具体学情灵活运用。）"""

    template += f"""
3. 学情分析：[起点]{grade.replace('上册', '').replace('下册', '')}学生已具备【已有基础】，[困难点]但对【学习难点】还需要进一步引导。教学时应注意【教学策略建议】。

二、教学目标内容
1.本课时为【{text_type}课】，核心任务是【核心任务】，因此选择【选择的维度】维度，侧重【{focus_str}】。
-请从"识字与写字、阅读与鉴赏、表达与交流、梳理与探究"四个维度出发，撰写教学目标，四个维度根据课文类型灵活选择，优先保证核心目标的达成；
-每个目标采用"行为条件+行为表现+表现程度"的ABCD法结构，行为动词依据布鲁姆认知目标六层级(记忆、领会、应用、分析、评价、创造)，必须具体、可观察、可测量；
-每个目标主语统一为"学生"；
-先写一般教学目标(概括性)，再写具体学习结果(可观测)。

三、课型(新授课/复习课)(非必要)
四、课时安排(1课时)
五、教学重点、教学难点
六、教学方法
七、教学过程(教案的主体)
八、作业布置（要提供明确的评价标准）
九、板书设计(根据教学灵活设计，突出重点)"""

    if '小练笔设计' in focuses:
        template += "\n（注：读写迁移环节中的练笔必须提供开头或词语支架）"

    # --- 红线要求 ---
    template += f"""

【红线要求】
- 语言符合{grade_level}学生认知，避免成人化
- 教学设计要体现四维知识框架的深度融合"""

    return template
