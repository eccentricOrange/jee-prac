CREATE TABLE IF NOT EXISTS exams (
    exam_id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_name TEXT NOT NULL,
    duration INTEGER NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    outage_delay TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sections (
    section_id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id INTEGER NOT NULL REFERENCES exams(exam_id),
    section_name TEXT NOT NULL,
    section_type TEXT NOT NULL,
    correct_marks REAL NOT NULL,
    unattempted_marks REAL NOT NULL,
    wrong_marks REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS questions (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_id INTEGER NOT NULL REFERENCES sections(section_id),
    question_number INTEGER NOT NULL,
    attempt TEXT NOT NULL,
    marked INTEGER NOT NULL
);