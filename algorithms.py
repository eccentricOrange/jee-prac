from pathlib import Path
from sqlite3 import connect, Row
from classes import Session, Question, MCQ, ASSOCIATIONS
from json import load


def create_file_system(active_directory: Path, main_database_path: Path, template_tests_path: Path, schema_path: Path) -> None:
    """
    setup the filesystem and the database
    - create the active directory if it doesn't exist
    - create the database if it doesn't exist, from the schema
    - copy the template tests to the active directory, if it doesn't exist there
    """

    active_directory.mkdir(parents=True, exist_ok=True)
    main_database_path.touch(exist_ok=True)

    with open(schema_path, 'r') as schema_file, connect(main_database_path) as connection:
        connection.executescript(schema_file.read())

    connection.close()

    if not (template_tests_path.exists()):
        template_tests_path.touch(exist_ok=True)
        template_tests_path.write_text((Path('data') / 'preconfigured-exams.json').read_text())


def make_questions(session: Session):
    """generate all the questions for a given exam from section data"""

    # start at the first question, human-readable index 1
    question_number = 1


    for section in session.exam.sections:
        section.first_question_number = question_number
        section.questions = []

        # check that the section has a question type which is valid. raise an error if not
        if section.questions_type in ASSOCIATIONS.keys():
            if section.questions_type == 'mcq' or section.questions_type == 'generic':
                raise ValueError(f"Questions type {section.questions_type} is not allowed.")

            # record the name of the class which questions will be instantiated from
            QuestionClass = ASSOCIATIONS[section.questions_type]

        else:
            raise ValueError(f"Unknown questions type: {section.questions_type}")

        for counter in range(section.number_of_questions):
            question: Question = QuestionClass()

            # assign a question number that is aware of questions in the previous sections
            question.question_number = question_number + counter

            # if the question is a MCQ, also record the choices
            if isinstance(question, MCQ):
                question.choices = section.choices
            
            section.questions.append(question)

        question_number += section.number_of_questions
        section.last_question_number = question_number - 1

    # initialise counters for the rest of the application
    session.exam.total_number_of_questions = question_number - 1
    session.unanswered_count = session.exam.total_number_of_questions
    session.unvisited_count = session.exam.total_number_of_questions


def get_pre_configured_tests(template_tests_path: Path) -> list:
    """
    get the pre-configured tests from the template tests file
    """

    with open(template_tests_path, 'r') as template_tests_file:
        return load(template_tests_file)