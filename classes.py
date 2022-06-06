from dataclasses import dataclass


@dataclass()
class Question:
    question_number: int
    value = ""
    visited = "unvisited"
    marked = "unmarked"
    answered = "unanswered"

    def __init__(self) -> None:
        pass

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


@dataclass()
class Section:
    number_of_questions: int

    correct_marks: int
    unattempted_marks: int
    wrong_marks: int

    name: str
    test_type: str
    section_number: int

    questions: list[Question]

    def __init__(self) -> None:
        pass

    def to_dict(self):
        return {
            "number_of_questions": self.number_of_questions,
            "correct_marks": self.correct_marks,
            "unattempted_marks": self.unattempted_marks,
            "name": self.name,
            "test_type": self.test_type,
            "section_number": self.section_number,
            "questions": [question.to_dict() for question in self.questions]
        }

    def from_dict(self, data: dict):
        self.number_of_questions = data["number_of_questions"]
        self.correct_marks = data["correct_marks"]
        self.unattempted_marks = data["unattempted_marks"]
        self.name = data["name"]
        self.test_type = data["test_type"]
        self.section_number = data["section_number"]
        self.questions = [Question().from_dict(question) for question in data["questions"]]

        return self


@dataclass()
class Exam:
    name: str
    exam_code: str
    duration: int
    sections: list[Section]
    timing_type: str

    def __init__(self) -> None:
        pass

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
        self.exam_code = data["exam_code"]
        self.duration = data["duration"]
        self.timing_type = data["timing_type"]
        self.sections = [Section().from_dict(section) for section in data["sections"]]

        return self


@dataclass()
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

    def __init__(self) -> None:
        pass

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