import json
from db.database import get_db_connection


def get_relevant_kebiao_context(grade, text_type, focuses):
    """Smart retrieval of relevant kebiao paragraphs.

    Instead of sending the entire ~9368-line KEBIAO_FULL_TEXT (~50,000+ tokens),
    this selects only relevant sections based on grade, textType, and selected focuses.

    Strategy:
    1. Always include kebiao_core summary
    2. Include relevant phase requirements based on grade
    3. Include relevant task groups based on textType
    4. Include relevant content themes based on focuses
    5. Include teaching tips
    6. Keyword-match kebiao_full_text sections against focuses
    7. For 四年级上册, include relevant teaching focus + reading guide

    Returns a concise, relevant subset of the kebiao text.
    """
    parts = []

    # 1. Core competency summary (always included - small)
    conn = get_db_connection()
    core_row = conn.execute("SELECT * FROM kebiao_core WHERE id = 1").fetchone()
    if core_row:
        dimensions = json.loads(core_row['dimensions']) if core_row['dimensions'] else []
        parts.append(
            f"【核心素养】{core_row['name']}：{'、'.join(dimensions)}。"
            f"{core_row['description'][:200]}"
        )

    # 2. Phase requirements based on grade
    phase = _get_phase(grade)
    phase_row = conn.execute(
        "SELECT * FROM kebiao_phase_req WHERE phase = ?",
        (phase,)
    ).fetchone()
    if phase_row:
        parts.append(
            f"【{phase}（{phase_row['range_desc']}）】\n"
            f"识字与写字：{phase_row['literacy'][:200]}\n"
            f"阅读与鉴赏：{phase_row['reading'][:200]}\n"
            f"表达与交流：{phase_row['expression'][:200]}"
        )

    # 3. Relevant task groups based on textType
    task_groups = _get_relevant_task_group_names(text_type)
    for tg_name in task_groups:
        tg_row = conn.execute(
            "SELECT name, level, description, relevance FROM kebiao_task_groups WHERE name = ?",
            (tg_name,)
        ).fetchone()
        if tg_row:
            parts.append(
                f"【学习任务群：{tg_row['name']}（{tg_row['level']}）】\n"
                f"{tg_row['description'][:300]}\n"
                f"教学相关性：{tg_row['relevance'][:200]}"
            )

    # 4. Relevant content themes
    theme_rows = conn.execute("SELECT * FROM kebiao_content_themes").fetchall()
    focus_str = '、'.join(focuses)
    for theme_row in theme_rows:
        # Check if any focus keyword relates to this theme
        if any(kw in focus_str for kw in ['传统文化', '革命', '社会主义', '文化自信', '家国情怀']):
            parts.append(
                f"【文化主题：{theme_row['theme_name']}】{theme_row['spirit']}"
            )

    # 5. Teaching tips
    tip_rows = conn.execute("SELECT tip_text FROM kebiao_teaching_tips").fetchall()
    tips_text = '\n'.join(f"· {t['tip_text']}" for t in tip_rows)
    parts.append(f"【教学建议】\n{tips_text}")

    # 6. Keyword-match kebiao_full_text sections
    if focuses:
        kebiao_sections = _keyword_match_kebiao_sections(conn, grade, text_type, focuses)
        if kebiao_sections:
            parts.append("【课标相关段落】\n" + '\n'.join(kebiao_sections))

    # 7. For 四年级上册, add relevant teaching focus + reading guide
    if '四年级上册' in grade:
        grade4a_context = _get_grade4a_context(conn, focuses)
        if grade4a_context:
            parts.append(grade4a_context)

    conn.close()
    return '\n\n'.join(parts)


def _get_phase(grade):
    g = grade.replace('上册', '').replace('下册', '')
    if g in ('一年级', '二年级'):
        return '第一学段'
    elif g in ('三年级', '四年级'):
        return '第二学段'
    elif g in ('五年级', '六年级'):
        return '第三学段'
    return '第四学段'


def _get_relevant_task_group_names(text_type):
    """Map textType to relevant task group names."""
    literary_types = ['散文', '古诗', '小说', '童话', '神话', '现代诗', '寓言', '文言文']
    practical_types = ['说明文', '记叙文']
    result = ['语言文字积累与梳理']  # Always include base type

    if text_type in literary_types:
        result.append('文学阅读与创意表达')
    if text_type in practical_types:
        result.append('实用性阅读与交流')
    if text_type in ('寓言', '文言文'):
        result.append('思辨性阅读与表达')

    return result


def _keyword_match_kebiao_sections(conn, grade, text_type, focuses):
    """Find kebiao_full_text sections that match the given focuses via keyword overlap."""
    phase = _get_phase(grade)

    # Get all sections
    rows = conn.execute(
        "SELECT section_title, content, keywords, phase, category FROM kebiao_full_text"
    ).fetchall()

    scored = []
    for row in rows:
        score = 0
        keywords = json.loads(row['keywords']) if row['keywords'] else []

        # Phase match (high priority)
        if row['phase'] and row['phase'] == phase:
            score += 10

        # Keyword overlap with focuses
        for focus in focuses:
            for kw in keywords:
                if kw in focus or focus in kw:
                    score += 3

        # Category relevance
        if row['category'] == '学习任务群':
            task_group_names = _get_relevant_task_group_names(text_type)
            for tg in task_group_names:
                if tg in row['section_title']:
                    score += 5

        if score > 0:
            scored.append((score, row))

    # Sort by score descending, take top sections (limit total content size)
    scored.sort(key=lambda x: x[0], reverse=True)

    result = []
    total_chars = 0
    max_chars = 3000  # Limit total kebiao section content

    for score, row in scored:
        content = row['content'].strip()
        if total_chars + len(content) > max_chars:
            # Truncate this section if needed
            remaining = max_chars - total_chars
            if remaining > 100:
                content = content[:remaining] + '...'
                result.append(f"【{row['section_title']}】\n{content}")
                total_chars += len(content)
            break
        result.append(f"【{row['section_title']}】\n{content}")
        total_chars += len(content)

    return result


def _get_grade4a_context(conn, focuses):
    """Get 四年级上册 specific context from teaching focus and reading guide."""
    parts = []

    # Teaching focus - find paragraphs matching focuses
    tf_rows = conn.execute("SELECT content FROM grade4a_teaching_focus").fetchall()
    focus_str = '、'.join(focuses)
    matched_tf = []
    for row in tf_rows:
        # Simple keyword matching
        if any(f in row['content'] for f in focuses) or any(kw in row['content'] for kw in focus_str.split('、')):
            matched_tf.append(row['content'])

    if matched_tf:
        parts.append(
            "【四年级上册教学侧重参考】\n" + '\n'.join(matched_tf[:5])  # Limit
        )

    # Reading guide - not matched by keyword (too many), skip unless needed
    return '\n\n'.join(parts) if parts else ''
