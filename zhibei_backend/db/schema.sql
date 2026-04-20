-- Curriculum structure
CREATE TABLE IF NOT EXISTS grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grade_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (grade_id) REFERENCES grades(id),
    UNIQUE(grade_id, name)
);

CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    focus TEXT,
    FOREIGN KEY (unit_id) REFERENCES units(id),
    UNIQUE(unit_id, name)
);

-- Focus options by text type
CREATE TABLE IF NOT EXISTS focus_by_type (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text_type TEXT UNIQUE NOT NULL,
    options TEXT NOT NULL
);

-- Lesson-level focus mapping (recommended + optional)
CREATE TABLE IF NOT EXISTS lesson_focus_map (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_name TEXT UNIQUE NOT NULL,
    recommended TEXT NOT NULL,
    optional TEXT NOT NULL
);

-- Unit focus refinement
CREATE TABLE IF NOT EXISTS unit_focus_refinement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    focus_name TEXT UNIQUE NOT NULL,
    refined_options TEXT NOT NULL,
    related_lesson_focus TEXT NOT NULL
);

-- Kebiao (curriculum standard) data
CREATE TABLE IF NOT EXISTS kebiao_core (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    dimensions TEXT NOT NULL,
    description TEXT NOT NULL,
    details TEXT NOT NULL,
    relation TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS kebiao_phase_req (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phase TEXT UNIQUE NOT NULL,
    range_desc TEXT NOT NULL,
    literacy TEXT,
    reading TEXT,
    expression TEXT,
    organization TEXT
);

CREATE TABLE IF NOT EXISTS kebiao_task_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    level TEXT NOT NULL,
    description TEXT NOT NULL,
    relevance TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS kebiao_content_themes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    theme_name TEXT UNIQUE NOT NULL,
    ideas TEXT,
    spirit TEXT,
    virtue TEXT,
    carriers TEXT,
    ratio TEXT
);

CREATE TABLE IF NOT EXISTS kebiao_teaching_tips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tip_text TEXT NOT NULL
);

-- Kebiao full text segmented for smart retrieval
CREATE TABLE IF NOT EXISTS kebiao_full_text (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_title TEXT NOT NULL,
    content TEXT NOT NULL,
    keywords TEXT,
    phase TEXT,
    category TEXT
);

-- Grade 4A specific data
CREATE TABLE IF NOT EXISTS grade4a_unit_keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_name TEXT UNIQUE NOT NULL,
    theme TEXT,
    reading_element TEXT,
    writing_element TEXT,
    task_group TEXT,
    motto TEXT,
    goals TEXT
);

CREATE TABLE IF NOT EXISTS grade4a_lesson_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_name TEXT UNIQUE NOT NULL,
    focus_keywords TEXT,
    vocabulary TEXT,
    reading_guide TEXT,
    tasks TEXT,
    supplement TEXT,
    is_skimming INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS grade4a_global_keywords (
    id INTEGER PRIMARY KEY,
    category TEXT UNIQUE NOT NULL,
    keywords TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS grade4a_teaching_focus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS grade4a_reading_guide (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL
);

-- Focus keyword library
CREATE TABLE IF NOT EXISTS focus_keyword_library (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT UNIQUE NOT NULL,
    keywords TEXT NOT NULL
);

-- Text type methodology maps
CREATE TABLE IF NOT EXISTS text_type_focus_map (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text_type TEXT UNIQUE NOT NULL,
    focus_description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS text_type_methods_map (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text_type TEXT UNIQUE NOT NULL,
    methods_description TEXT NOT NULL
);
