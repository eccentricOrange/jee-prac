from dataclasses import dataclass


@dataclass(init=False)
class Question:
    question_number: int
    value = ""
    visited = "unvisited"
    marked = "unmarked"
    answered = "unanswered"

    def to_dict(self):
        return {
            "question_number": self.question_number,
            "value": self.value,
            "visited": self.visited,
            "marked": self.marked,
            "answered": self.answered
        }

    def from_dict(self, data):
        self.question_number = data["question_number"]
        self.value = data["value"]
        self.visited = data["visited"]
        self.marked = data["marked"]
        self.answered = data["answered"]

        return self


@dataclass(init=False)
class Section:
    number_of_questions: int
    first_question_number: int
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
            "number_of_questions": self.number_of_questions,
            "correct_marks": self.correct_marks,
            "unattempted_marks": self.unattempted_marks,
            "name": self.name,
            "test_type": self.type,
            "section_number": self.section_number,
            "questions": [question.to_dict() for question in self.questions]
        }

    def from_dict(self, data: dict):
        self.number_of_questions = data["number-of-questions"]
        self.correct_marks = data["correct-marks"]
        self.unattempted_marks = data["unattempted-marks"]
        self.name = data["name"]
        self.type = data["type"]
        self.section_number = data["section-number"]

        return self


@dataclass(init=False)
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
            "exam_code": self.exam_code,
            "duration": self.duration,
            "timing_type": self.timing_type,
            "sections": [section.to_dict() for section in self.sections]
        }

    def from_dict(self, data: dict):
        self.name = data["name"]
        self.exam_code = data["exam-code"]
        self.duration = data["duration"]
        self.sections = [Section().from_dict(section)
                         for section in data["sections"]]

        return self


@dataclass(init=False)
class Session:
    exam: Exam
    answered_count: int
    unanswered_count: int
    marked_count: int
    unvisited_count: int
    start_time: str
    end_time: str
    outage_time: str
    last_known_time: str

    def to_dict(self):
        return {
            "exam": self.exam.to_dict() if self.exam else None,
            "answered_count": self.answered_count,
            "unanswered_count": self.unanswered_count,
            "marked_count": self.marked_count,
            "unvisited_count": self.unvisited_count,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "outage_time": self.outage_time,
            "last_known_time": self.last_known_time
        }

    def from_dict(self, data: dict):
        self.exam = Exam().from_dict(data["exam"]) if data["exam"] else Exam()
        self.answered_count = data["answered_count"]
        self.unanswered_count = data["unanswered_count"]
        self.marked_count = data["marked_count"]
        self.unvisited_count = data["unvisited_count"]
        self.start_time = data["start_time"]
        self.end_time = data["end_time"]
        self.outage_time = data["outage_time"]
        self.last_known_time = data["last_known_time"]

        return self
