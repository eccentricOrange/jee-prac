"""
classes for various parts of a session
- `Question` is for one question. Child classes define the type of question
- `Section` is for one section of an exam. It has one or more questions
- `Exam` is for the entire exam. It has one or more sections
- `Session` is for the entire session. It has one exam, and additional state data
"""

from __future__ import annotations

from collections import Counter
from typing import Type


class Question:
    """
    defines a generic question
     - `Question` defines a generic question
     - each class defines one kind of question, inheriting from `Question`
     - each class has a marking function
     - it will accept data about the marking system, the attempt(s), and the correct answer(s)
     - it will return the marks scored
  """

    question_number: int = 0
    attempts: None | str | float | tuple[str] = None
    answers: None | str | float | tuple[str] = None
    score: float = 0.0
    visited = "unvisited"
    marked = "unmarked"
    answered = "unanswered"
    name = "Question"
    code = "question"

    def mark(self, wrong: float, correct: float, unattempted: float = 0) -> float:
        """
        mark a generic question
        - correct if `answer == attempt`
        - if correct, award `correct` marks (usually positive)
        - if wrong, award `wrong` marks (usually negative)
        - if unattempted, award `unattempted` marks (usually zero)
        """

        if self.attempts:
            if self.answers == self.attempts:
                return correct

            else:
                return wrong

        return unattempted

    def to_dict_generic(self) -> dict:
        """
        convert some data about the question to a dictionary
        - these data will always be exported
        - specific data will be exported by each particular question child class
        """

        return_data = {
            "question-number": self.question_number,
            "visited": self.visited,
            "marked": self.marked,
            "answered": self.answered
        }

        if self.score:
            return_data["score"] = self.score

        return return_data

    def to_dict(self) -> dict:
        """
        convert more specific data about the question to a dictionary
        - many question child classes will export this data
        - a question child class may override this method to export different specific data
        """

        return_data = self.to_dict_generic()

        if self.attempts:
            return_data["attempts"] = self.attempts

        if self.answers:
            return_data["answers"] = self.answers

        return return_data

    def from_dict_generic(self, data: dict) -> Question:
        """
        convert some data about the question from a dictionary
        - these data will always be imported
        - specific data will be imported by each particular question child class
        """

        self.question_number = data["question-number"]
        self.visited = data["visited"]
        self.marked = data["marked"]
        self.answered = data["answered"]

        if "score" in data:
            self.score = data["score"]

        return self

    def from_dict(self, data: dict) -> Question:
        """
        convert more specific data about the question from a dictionary
        - many question child classes will import this data
        - a question child class may override this method to import different specific data
        """

        self.from_dict_generic(data)

        if "attempts" in data:
            self.attempts = data["attempts"]

        if "answers" in data:
            self.answers = data["answers"]

        return self


class NumericQuestion(Question):
    """defines a numeric question"""
    answers: float = 0
    attempts: float = 0
    name = "Numeric"
    code = "numeric"


class TextQuestion(Question):
    """defines a text question"""
    answers: str = ""
    attempts: str = ""
    name = "Text"
    code = "text"


class MCQ(Question):
    """
    defines a multiple choice question
    """

    choices = ('A', 'B', 'C', 'D')
    name = "MCQ"
    code = "mcq"

    def to_dict(self) -> dict:
        """
        convert specific data about MCQ-style questions to a dictionary
        - adds the conversion for `choices`
        """

        return_data = self.to_dict_generic()

        if self.attempts:
            return_data["attempts"] = self.attempts

        if self.answers:
            return_data["answers"] = self.answers

        return_data["choices"] = list(self.choices)

        return return_data

    def from_dict(self, data: dict) -> Question:
        """
        convert specific data about MCQ-style questions from a dictionary
        - adds the conversion for `choices`
        """

        self.from_dict_generic(data)

        if "attempts" in data:
            self.attempts = data["attempts"]

        if "answers" in data:
            self.answers = data["answers"]

        if "choices" in data:
            self.choices = data["choices"]

        return self


class MCQSCC(MCQ):
    """
    defines a multiple choice question
    - only one of the possible choices can be correct
    """

    answers: str = ""
    attempts: str = ""
    name = "MCQ (Single Choice Correct)"
    code = "mcq-scc"


class MCQMCC(MCQ):
    """
    defines a multiple choice question
    - multiple correct choices can be correct
    """

    answers: tuple[str] = tuple("")
    attempts: tuple[str] = tuple("")
    name = "MCQ (Multiple Choices Correct)"
    code = "mcq-mcc"

    def mark_mcq_mcc(self, wrong: float, correct: float, unattempted: float = 0) -> float:
        """
        mark a multiple choice question with multiple correct choices
        - correct if all entries in `attempts` are in `answers`, and there are no other entries in `attempts`
        - partial if all entries in `attempts` are in `answers`, and there are no other entries in `attempts`, but there are other entries in `answers`
        - wrong if any entries in `attempts` are not in `answers`
        - unattempted if there are no entries in `attempts`
        - if correct, award `correct` marks (usually positive)
        - if partial, award one mark for each correct attempt (usually positive)
        - if wrong, award `wrong` marks (usually negative)
        - if unattempted, award `unattempted` marks (usually zero)
        """

        # check if attempted
        if self.attempts:
            attempts_counter = Counter(self.attempts)
            answers_counter = Counter(self.answers)

            # check if correct
            if attempts_counter == answers_counter:
                return correct

            # if not correct, begin check for partial or wrong
            correct_count = 0

            for attempt in attempts_counter:

                # check if given attempt is correct
                if attempt in answers_counter:
                    correct_count += 1

                # if given attempt is not correct, it is wrong
                return wrong

            # return partial or correct marks
            return correct_count

        # if unattempted, return unattempted marks
        return unattempted


class Section:
    """
    defines a section of a test
    - a section is a collection of questions
    - all questions in a section must be of the same type
    """

    number_of_questions: int = 0
    first_question_number: int = 1
    last_question_number: int = -1

    correct_marks: float = 0.0
    wrong_marks: float = 0.0
    unattempted_marks: float = 0.0

    name: str = ""
    questions_type: str = ""
    section_number: int = 0

    choices: tuple[str] = tuple("")
    questions: list[Question] = []

    def to_dict(self) -> dict:
        """convert data about the section to a dictionary"""
        return_data = {
            "number-of-questions": self.number_of_questions,
            "first-question-number": self.first_question_number,
            "last-question-number": self.last_question_number,
            "correct-marks": self.correct_marks,
            "wrong-marks": self.wrong_marks,
            "unattempted-marks": self.unattempted_marks,
            "name": self.name,
            "questions-type": self.questions_type,
            "section-number": self.section_number,
            "questions": [question.to_dict() for question in self.questions]
        }

        if self.choices:
            return_data["choices"] = list(self.choices)

        return return_data

    def from_dict(self, data: dict) -> Section:
        """
        convert generic data about the section from a dictionary
        - these data will always be imported
        - specific data will be imported by `from_bkp_dict` only when restoring a session from a backup
        """

        self.number_of_questions = data["number-of-questions"]
        self.correct_marks = data["correct-marks"]
        self.wrong_marks = data["wrong-marks"]
        self.unattempted_marks = data["unattempted-marks"]
        self.name = data["name"]
        self.questions_type = data["questions-type"]
        self.section_number = data["section-number"]

        if "choices" in data:
            self.choices = data["choices"]

        return self

    def from_bkp_dict(self, data: dict) -> Section:
        """convert specific data about the section from a dictionary when restoring a session from a backup"""

        self.from_dict(data)
        self.first_question_number = data["first-question-number"]
        self.last_question_number = data["last-question-number"]
        self.questions = [Question().from_dict(question)
                          for question in data["questions"]]

        if "choices" in data:
            self.choices = data["choices"]

        return self


class Exam:
    """
    defines an exam
    - an exam is a collection of sections
    """

    name: str = ""
    exam_code: str = ""
    duration: int = 0
    timing_type: str = ""
    total_number_of_questions: int = 0
    sections: list[Section] = []

    def to_dict(self) -> dict:
        return_data = {
            "name": self.name,
            "exam-code": self.exam_code,
            "duration": self.duration,
            "timing-type": self.timing_type,
            "total-number-of-questions": self.total_number_of_questions,
            "sections": [section.to_dict() for section in self.sections]
        }

        return return_data

    def from_dict(self, data: dict) -> Exam:
        self.name = data["name"]
        self.exam_code = data["exam-code"]
        self.duration = data["duration"]
        self.timing_type = data["timing-type"]

        return self

    def from_bkp_dict(self, data: dict) -> Exam:
        self.from_dict(data)
        self.total_number_of_questions = data["total-number-of-questions"]
        self.sections = [Section().from_bkp_dict(section)
                         for section in data["sections"]]

        return self


class Session:
    """
    defines a session
    - a session has one exam
    - contains additional state data
    """
    exam: Exam = None  # type: ignore
    answered_count: int = 0
    unanswered_count: int = 0
    marked_count: int = 0
    unvisited_count: int = 0
    start_time: str = ""
    end_time: str = ""
    outage_time: str = ""
    last_known_time: str = ""

    def to_dict(self) -> dict:
        """convert data about the session to a dictionary"""

        return_data = {
            "exam": self.exam.to_dict(),
            "answered-count": self.answered_count,
            "unanswered-count": self.unanswered_count,
            "marked-count": self.marked_count,
            "unvisited-count": self.unvisited_count,
            "start-time": self.start_time,
            "end-time": self.end_time,
            "outage-time": self.outage_time,
            "last-known-time": self.last_known_time
        }

        return return_data

    def from_dict(self, data: dict) -> Session:
        """restore data about the session from a dictionary"""

        self.exam = Exam().from_dict(data["exam"])
        self.answered_count = data["answered-count"]
        self.unanswered_count = data["unanswered-count"]
        self.marked_count = data["marked-count"]
        self.unvisited_count = data["unvisited-count"]
        self.start_time = data["start-time"]
        self.end_time = data["end-time"]
        self.outage_time = data["outage-time"]
        self.last_known_time = data["last-known-time"]

        return self


ASSOCIATIONS: dict[str, Type[Question]] = {
    'generic': Question,
    'numeric': NumericQuestion,
    'text': TextQuestion,
    'mcq': MCQ,
    'mcq-scc': MCQSCC,
    'mcq-mcc': MCQMCC
}
