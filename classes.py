from dataclasses import dataclass


class Question:
    question_number: int
    value = ""
    visited = "unvisited"
    marked = "unmarked"
    answered = "unanswered"

    def to_dict(self):
        return {
            "question-number": self.question_number,
            "value": self.value,
            "visited": self.visited,
            "marked": self.marked,
            "answered": self.answered
        }

    def from_dict(self, data):
        self.question_number = data["question-number"]
        self.value = data["value"]
        self.visited = data["visited"]
        self.marked = data["marked"]
        self.answered = data["answered"]

        return self


class Section:
    number_of_questions: int
    first_question_number: int = 1
    last_question_number: int

    correct_marks: float
    unattempted_marks: float
    wrong_marks: float

    name: str
    type: str
    options: list[str]
    section_number: int

    questions: list[Question]

    def to_dict(self):
        return {
            "number-of-questions": self.number_of_questions,
            "correct-marks": self.correct_marks,
            "unattempted-marks": self.unattempted_marks,
            "name": self.name,
            "test-type": self.type,
            "section-number": self.section_number,
            "questions": [question.to_dict() for question in self.questions]
        }

    def from_dict(self, data: dict):
        self.number_of_questions = data["number-of-questions"]
        self.correct_marks = data["correct-marks"]
        self.unattempted_marks = data["unattempted-marks"]
        self.wrong_marks = data["wrong-marks"]
        self.name = data["name"]
        self.type = data["type"]
        self.section_number = data["section-number"]

        if "options" in data:
            self.options = data["options"]

        return self


class Exam:
    name: str
    exam_code: str
    duration: int
    sections: list[Section]
    timing_type: str
    total_number_of_questions: int

    def to_dict(self):
        return {
            "name": self.name,
            "exam-code": self.exam_code,
            "duration": self.duration,
            "timing-type": self.timing_type,
            "sections": [section.to_dict() for section in self.sections]
        }

    def from_dict(self, data: dict):
        self.name = data["name"]
        self.exam_code = data["exam-code"]
        self.duration = data["duration"]
        self.sections = [Section().from_dict(section)
                         for section in data["sections"]]

        return self


class Session:
    exam: Exam
    answered_count: int = 0
    unanswered_count: int
    marked_count: int = 0
    unvisited_count: int
    start_time: str
    end_time: str
    outage_time: str
    last_known_time: str

    def to_dict(self):
        return {
            "exam": self.exam.to_dict() if self.exam else None,
            "answered-count": self.answered_count,
            "unanswered-count": self.unanswered_count,
            "marked-count": self.marked_count,
            "unvisited-count": self.unvisited_count,
            "start-time": self.start_time,
            "end-time": self.end_time,
            "outage-time": self.outage_time,
            "last-known-time": self.last_known_time
        }

    def from_dict(self, data: dict):
        self.exam = Exam().from_dict(data["exam"]) if data["exam"] else Exam()
        self.answered_count = data["answered-count"]
        self.unanswered_count = data["unanswered-count"]
        self.marked_count = data["marked-count"]
        self.unvisited_count = data["unvisited-count"]
        self.start_time = data["start-time"]
        self.end_time = data["end-time"]
        self.outage_time = data["outage-time"]
        self.last_known_time = data["last-known-time"]

        return self
