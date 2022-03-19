CREATE TABLE IF NOT EXISTS exams (
    exam_id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    CONSTRAINT unique_start_time UNIQUE (start_time)
);
CREATE TABLE IF NOT EXISTS questions (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_number INTEGER NOT NULL,
    exam_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    subject TEXT NOT NULL,
    value NULL,
    FOREIGN KEY(exam_id) REFERENCES exams(exam_id),
    CONSTRAINT unique_question UNIQUE (question_number, exam_id)
);