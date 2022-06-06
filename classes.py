from dataclasses import dataclass


@dataclass
class Question:
    question_number: int
    value = ""
    visited = "unvisited"
    marked = "unmarked"
    answered = "unanswered"

    def dict(self):
        return {
            "question_number": self.question_number,
            "value": self.value,
            "visited": self.visited,
            "marked": self.marked,
            "answered": self.answered
        }


@dataclass
class Section:
    number_of_questions: int

    correct_marks: int
    unattempted_marks: int
    wrong_marks: int

    name: str
    test_type: str
    section_number: int

    questions: list[Question]

    def dict(self):
        return {
            "number_of_questions": self.number_of_questions,
            "correct_marks": self.correct_marks,
            "unattempted_marks": self.unattempted_marks,
            "name": self.name,
            "test_type": self.test_type,
            "section_number": self.section_number,
            "questions": [question.dict() for question in self.questions]
        }


@dataclass
class Exam:
    name: str
    exam_code: str
    duration: int
    sections: list[Section]

    def dict(self):
        return {
            "name": self.name,
            "exam_code": self.exam_code,
            "duration": self.duration,
            "sections": [section.dict() for section in self.sections]
        }


@dataclass(init=False)
class Session:
    exam: Exam | None
    answered_count: int | None
    unanswered_count: int | None
    marked_count: int | None
    unvisited_count: int | None
    start_time: str | None
    end_time: str | None
    outage_time: str | None
    last_known_time: str | None

    def dict(self):
        return {
            "exam": self.exam.dict() if self.exam else None,
            "answered_count": self.answered_count,
            "unanswered_count": self.unanswered_count,
            "marked_count": self.marked_count,
            "unvisited_count": self.unvisited_count,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "outage_time": self.outage_time,
            "last_known_time": self.last_known_time
        }