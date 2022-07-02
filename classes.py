"""
algorithms for questions
- `Question` defines a generic question
- each class defines one kind of question, inheriting from `Question`
- each class has a marking function
  - it will accept data about the marking system, the attempt(s), and the correct answer(s)
  - it will return the marks scored
"""


from collections import Counter


class Question:
    """defines a generic question"""

    question_number: int = 0
    attempts: None | str | float | tuple[str] = None
    answers: None | str | float | tuple[str] = None
    marks: float = 0.0
    visited = "unvisited"
    marked = "unmarked"
    answered = "unanswered"

    def mark(self, wrong: float, correct: float, unattempted: float = 0):
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

    def to_dict_generic(self):
        return_data = {
            "question-number": self.question_number,
            "visited": self.visited,
            "marked": self.marked,
            "answered": self.answered
        }

        if self.marks:
            return_data["marks"] = self.marks

        return return_data

    def to_dict(self):
        return_data = self.to_dict_generic()

        if self.attempts:
            return_data["attempts"] = self.attempts

        if self.answers:
            return_data["answers"] = self.answers

        return return_data

    def from_dict_generic(self, data: dict):
        self.question_number = data["question-number"]
        self.visited = data["visited"]
        self.marked = data["marked"]
        self.answered = data["answered"]

        if "marks" in data:
            self.marks = data["marks"]

        return self

    def from_dict(self, data: dict):
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


class TextQuestion(Question):
    """defines a text question"""
    answers: str = ""
    attempts: str = ""


class MCQ(Question):
    """
    defines a multiple choice question
    """

    choices = ('A', 'B', 'C', 'D')

    def to_dict(self):
        return_data = self.to_dict_generic()

        if self.attempts:
            return_data["attempts"] = self.attempts

        if self.answers:
            return_data["answers"] = self.answers

        return_data["choices"] = list(self.choices)

        return return_data

    def from_dict(self, data: dict):
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


class MCQMCC(MCQ):
    """
    defines a multiple choice question
    - multiple correct choices can be correct
    """

    answers: tuple[str] = tuple("")
    attempts: tuple[str] = tuple("")

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
    number_of_questions: int = 0
    first_question_number: int = 1
    last_question_number: int = -1

    correct_marks: float = 0.0
    wrong_marks: float = 0.0
    unattempted_marks: float = 0.0

    name: str = ""
    questions_type: str = ""
    section_number: int = 0

    questions: list[Question] = []


    def to_dict(self):
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

        return return_data

    def from_dict(self, data: dict):
        self.number_of_questions = data["number-of-questions"]
        self.correct_marks = data["correct-marks"]
        self.wrong_marks = data["wrong-marks"]
        self.unattempted_marks = data["unattempted-marks"]
        self.name = data["name"]
        self.questions_type = data["questions-type"]
        self.section_number = data["section-number"]

        return self

    
    def from_bkp_dict(self, data: dict):
        self.from_dict(data)
        self.first_question_number = data["first-question-number"]
        self.last_question_number = data["last-question-number"]
        self.questions = [Question().from_dict(question) for question in data["questions"]]

        return self


class Exam:
    name: str = ""
    exam_code: str = ""
    duration: int = 0
    timing_type: str = ""
    total_number_of_questions: int = 0
    sections: list[Section] = []

    def to_dict(self):
        return_data = {
            "name": self.name,
            "exam-code": self.exam_code,
            "duration": self.duration,
            "timing-type": self.timing_type,
            "total-number-of-questions": self.total_number_of_questions,
            "sections": [section.to_dict() for section in self.sections]
        }

        return return_data

    def from_dict(self, data: dict):
        self.name = data["name"]
        self.exam_code = data["exam-code"]
        self.duration = data["duration"]
        self.timing_type = data["timing-type"]

        return self

    def from_bkp_dict(self, data: dict):
        self.from_dict(data)
        self.total_number_of_questions = data["total-number-of-questions"]
        self.sections = [Section().from_bkp_dict(section) for section in data["sections"]]

        return self