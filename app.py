from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, redirect, send_file
from http import HTTPStatus
from json import dump, dumps, load
from re import match
from os import environ
from sqlite3 import connect, Row
from csv import DictWriter
from classes import Session, Exam, Section, Question

app = Flask(__name__)
session = Session()

DEVELOPMENT_MODE = bool(environ.get("JEE_PRAC_DEVELOPMENT"))
SERVER_MODE = bool(environ.get("JEE_PRAC_SERVER"))

SCHEMA_PATH = Path('data') / 'schema.sql'
ACTIVE_DIRECTORY = Path('data') if DEVELOPMENT_MODE else Path().home() / '.jee-prac'
BACKUP_FILE_PATH = ACTIVE_DIRECTORY / 'jee-prac-session-bkp.json'
MAIN_DATABASE_PATH = ACTIVE_DIRECTORY / 'jee-prac-database.db'
TEMPLATE_TESTS_PATH = ACTIVE_DIRECTORY / 'preconfigured-exams.json'

def create_file_system():
    ACTIVE_DIRECTORY.mkdir(parents=True, exist_ok=True)
    MAIN_DATABASE_PATH.touch(exist_ok=True)

    with open(SCHEMA_PATH, 'r') as schema_file, connect(MAIN_DATABASE_PATH) as connection:
        connection.executescript(schema_file.read())

    connection.close()

    if not (DEVELOPMENT_MODE or TEMPLATE_TESTS_PATH.exists()):
        TEMPLATE_TESTS_PATH.touch(exist_ok=True)
        TEMPLATE_TESTS_PATH.write_text((Path('data') / 'preconfigured-exams.json').read_text())


def get_sections_from_form(form_data):
    exam_section_number = 0

    for field in form_data:
        if match(r'^section-\d+-name$', field):
            section = Section()

            form_section_number = field.split('-')[1]

            section.name = form_data[field]
            section.section_number = exam_section_number
            section.type = form_data[f'section-{form_section_number}-questions-type']
            section.number_of_questions = int(form_data[f'section-{form_section_number}-number-of-questions'])
            section.correct_marks = float(form_data[f'section-{form_section_number}-marks-if-correct'])
            section.unattempted_marks = float(form_data[f'section-{form_section_number}-marks-if-unattempted'])
            section.wrong_marks = float(form_data[f'section-{form_section_number}-marks-if-wrong'])

            if section.type == "mcq":
                section.options = form_data[f'section-{form_section_number}-options'].split(',')

            exam_section_number += 1

            yield section


def make_questions():
    global session
    question_number = 1

    for section in session.exam.sections:
        section.first_question_number = question_number
        section.questions = []

        for counter in range(section.number_of_questions):
            question = Question()
            question.question_number = question_number + counter
            section.questions.append(question)

        question_number += section.number_of_questions
        section.last_question_number = question_number - 1

    session.exam.total_number_of_questions = question_number - 1
    session.unanswered_count = session.exam.total_number_of_questions
    session.unvisited_count = session.exam.total_number_of_questions


@app.route('/jee/', methods=['GET', 'POST'])
def select_test_type():
    with open(TEMPLATE_TESTS_PATH, 'r') as template_tests_file:
        template_tests = load(template_tests_file)

    return render_template(
        'select-test-type.html',
        template_tests=template_tests,
    ), HTTPStatus.OK


@app.route('/jee/configure-test/', methods=['GET', 'POST'])
def configure_test():
    return render_template('configure-test.html'), HTTPStatus.OK


@app.route('/jee/receive-test-type', methods=['POST'])
def receive_test_type():
    global session
    exam = Exam()

    if request.method == 'POST':
        form_data = request.form
        exam = Exam()

        if form_data['test-type'] != "custom":
            with open(TEMPLATE_TESTS_PATH, 'r') as template_tests_file:
                template_tests = load(template_tests_file)

                for test in template_tests:

                    if test['exam-code'] == form_data['test-type']:
                        exam.from_dict(data=test)
                        exam.timing_type = form_data['timing-type']

                        if exam.timing_type != 'set-time':
                            exam.duration = int(form_data['duration']) if exam.timing_type == 'custom-time' else 0

                        session.exam = exam
                        return redirect('/jee/start-test'), HTTPStatus.TEMPORARY_REDIRECT

                return "", HTTPStatus.BAD_REQUEST

        exam.timing_type = form_data['timing-type']
        exam.duration = int(form_data['duration']) if exam.timing_type == 'custom-time' else 0
        return redirect('/jee/configure-test'), HTTPStatus.TEMPORARY_REDIRECT

    return "", HTTPStatus.BAD_REQUEST
    

@app.route('/jee/receive-test-config', methods=['POST'])
def receive_test_config():
    global session
    exam = Exam()

    if request.method == 'POST':
        form_data = request.form
        
        if 'exam-name' in form_data:
            exam.name = form_data['exam-name']

        exam.sections = list(get_sections_from_form(form_data))

        session.exam = exam
        return redirect('/jee/start-test'), HTTPStatus.TEMPORARY_REDIRECT

    return '', HTTPStatus.BAD_REQUEST


@app.route('/jee/start-test', methods=['GET', 'POST'])
def start_test():
    global session

    session.start_time = datetime.now().isoformat()
    session.outage_time = datetime.fromtimestamp(0).isoformat()

    make_questions()
    return redirect('/jee/question?question-number=1'), HTTPStatus.TEMPORARY_REDIRECT


@app.route('/jee/question', methods=['GET', 'POST'])
def get_question():
    global session

    if session.exam:
        
        question_number = int(request.args.get('question-number'))  # type: ignore

        for section in session.exam.sections:
            if section.first_question_number <= question_number <= section.last_question_number:
                question = section.questions[question_number - section.first_question_number]

                next_question_disabled = "disabled" if question_number == session.exam.total_number_of_questions else ""
                previous_question_disabled = "disabled" if question_number == 1 else ""
                mark_button_text = "Unmark" if question.marked == 'marked' else "Mark"

                if question.visited == "unvisited":
                    session.unvisited_count -= 1
                    question.visited = "visited"

                if session.exam.timing_type != "untimed":
                    time_remaining = datetime.fromtimestamp(session.exam.duration * 60) - ((datetime.now() - datetime.fromisoformat(session.start_time)) + datetime.fromisoformat(session.outage_time))
                    time_remaining_string = datetime.fromtimestamp(time_remaining.total_seconds()).isoformat()
                    timer_type = "Time Remaining:"

                else:
                    timer_type = "Untimed Test"
                    time_remaining_string = ""

                data = {
                    'question-number': question_number,
                    'next-question-disabled': next_question_disabled,
                    'previous-question-disabled': previous_question_disabled,
                    'mark-button-text': mark_button_text,
                    'answered-count': session.answered_count,
                    'unanswered-count': session.unanswered_count,
                    'unvisited-count': session.unvisited_count,
                    'marked-count': session.marked_count,
                    'timer-type': timer_type,
                    'time-remaining-string': time_remaining_string,
                    'exam': session.exam.to_dict(),
                    'section-type': section.type,
                }
                
                if section.type == 'mcq':
                    choices = [
                        {
                            'option': option,
                            'value': "checked" if option == question.value else ""
                        }
                        for option in section.options
                    ]

                    data['choices'] = choices

                return render_template(f'{section.type}.html', data=data), HTTPStatus.OK


    return "", HTTPStatus.BAD_REQUEST

                

        
def main():
    global SERVER_MODE

    create_file_system()

    app.run()

if __name__ == '__main__':
    main()