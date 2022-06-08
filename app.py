from csv import DictWriter
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from json import dump, load
from os import environ
from pathlib import Path
from re import match
from sqlite3 import Row, connect

from flask import Flask, redirect, render_template, request, send_file

from classes import Exam, Question, Section, Session

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

def back_up_recovery_data():
    global session

    with open(BACKUP_FILE_PATH, 'w') as backup_file:
        session.last_known_time = datetime.now(timezone.utc).isoformat()
        dump(session.to_dict(), backup_file)

def restore_recovery_data():
    global session

    if BACKUP_FILE_PATH.exists():
        with open(BACKUP_FILE_PATH, 'r') as backup_file:
            session.from_dict(load(backup_file))

            session.outage_time = (datetime.fromisoformat(session.outage_time) + (datetime.now(timezone.utc) - datetime.fromisoformat(session.last_known_time))).isoformat()
            print(session.outage_time)

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

def create_csv_from_db(table_name: str) -> Path:
    csv_filepath = ACTIVE_DIRECTORY / f'{table_name}.csv'
    csv_filepath.touch(exist_ok=True)

    with connect(MAIN_DATABASE_PATH) as connection, open(csv_filepath, 'w') as csv_file:
        connection.row_factory = Row
        db_data = connection.execute(f'SELECT * FROM {table_name}').fetchall()
        csv_writer = DictWriter(csv_file, fieldnames=db_data[0].keys())
        csv_writer.writeheader()
        csv_writer.writerows(map(dict, db_data))

    return csv_filepath


@app.route('/jee/', methods=['GET', 'POST'])
def select_test_type():
    if not session.exam:

        with open(TEMPLATE_TESTS_PATH, 'r') as template_tests_file:
            template_tests = load(template_tests_file)

        return render_template(
            'select-test-type.html',
            template_tests=template_tests,
        ), HTTPStatus.OK

    return "You are already in a test session.", HTTPStatus.IM_USED


@app.route('/jee/configure-test/', methods=['GET', 'POST'])
def configure_test():
    if not session.start_time:
        return render_template('configure-test.html'), HTTPStatus.OK

    return "You are already in a test session.", HTTPStatus.IM_USED


@app.route('/jee/receive-test-type', methods=['POST'])
def receive_test_type():
    global session
    
    if not session.exam:
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
            session.exam = exam
            return redirect('/jee/configure-test'), HTTPStatus.TEMPORARY_REDIRECT

        return "", HTTPStatus.BAD_REQUEST

    return "You are already in a test session.", HTTPStatus.IM_USED
    

@app.route('/jee/receive-test-config', methods=['POST'])
def receive_test_config():
    global session

    if not session.exam:
        return "", HTTPStatus.NOT_IMPLEMENTED

    exam: Exam = session.exam  # type: ignore

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

    if not session.start_time:

        session.start_time = datetime.now(timezone.utc).isoformat()
        session.outage_time = '1970-01-01T00:00:00+00:00'
        
        make_questions()

        return redirect('/jee/question?question-number=1'), HTTPStatus.TEMPORARY_REDIRECT

    return "You are already in a test session.", HTTPStatus.IM_USED


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
                    duration = datetime.fromtimestamp(session.exam.duration * 60).replace(tzinfo=timezone.utc)
                    now = datetime.now(timezone.utc)
                    start_time = datetime.fromisoformat(session.start_time)
                    outage_time = datetime.fromisoformat(session.outage_time)
                    time_remaining = duration - (now - start_time) + timedelta(seconds=outage_time.timestamp())
                    time_remaining_string = time_remaining.replace(tzinfo=timezone.utc).isoformat()
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

                back_up_recovery_data()
                return render_template(f'{section.type}.html', data=data), HTTPStatus.OK

        return "", HTTPStatus.BAD_REQUEST

    return "", HTTPStatus.NOT_IMPLEMENTED

@app.route('/jee/mark', methods=['POST'])
def mark():
    global session

    if session.exam:

        form_data = dict(request.get_json(force=True))  # type: ignore
        question_number = int(form_data['question-number'])

        for section in session.exam.sections:
            if section.first_question_number <= question_number <= section.last_question_number:
                question = section.questions[question_number - section.first_question_number]

                if question.marked == 'unmarked':
                    session.marked_count += 1
                question.marked = 'marked'

                back_up_recovery_data()
                return "", HTTPStatus.OK

        return "", HTTPStatus.BAD_REQUEST

    return "", HTTPStatus.NOT_IMPLEMENTED


@app.route('/jee/unmark', methods=['POST'])
def unmark():
    global session

    if session.exam:

        form_data = dict(request.get_json(force=True))  # type: ignore
        question_number = int(form_data['question-number'])

        for section in session.exam.sections:
            if section.first_question_number <= question_number <= section.last_question_number:
                question = section.questions[question_number - section.first_question_number]

                if question.marked == 'marked':
                    session.marked_count -= 1
                question.marked = 'unmarked'

                back_up_recovery_data()
                return "", HTTPStatus.OK

        return "", HTTPStatus.BAD_REQUEST

    return "", HTTPStatus.NOT_IMPLEMENTED

@app.route('/jee/receive-value', methods=['POST'])
def receive_value():
    global session

    if session.exam:

        form_data = dict(request.get_json(force=True))  # type: ignore
        question_number = int(form_data['question-number'])
        value = form_data['value']

        for section in session.exam.sections:
            if section.first_question_number <= question_number <= section.last_question_number:
                question = section.questions[question_number - section.first_question_number]
                old_value = question.value
                question.value = value

                if (not old_value) and value:
                    session.answered_count += 1
                    session.unanswered_count -= 1
                    question.answered = 'answered'

                if old_value and (not value):
                    session.answered_count -= 1
                    session.unanswered_count += 1
                    question.answered = 'unanswered'

                back_up_recovery_data()
                return "", HTTPStatus.OK

        return "", HTTPStatus.BAD_REQUEST

    return "", HTTPStatus.NOT_IMPLEMENTED

@app.route('/jee/quit', methods=['GET'])
def quit():
    global session

    if session.exam:

        session.exam = None
        session.start_time = ""
        session.outage_time = ""
        session.answered_count = 0
        session.unanswered_count = 0
        session.unvisited_count = 0
        session.marked_count = 0

        BACKUP_FILE_PATH.unlink(missing_ok=True)

        return redirect('/jee/'), HTTPStatus.TEMPORARY_REDIRECT

    return "You are not in a test session.", HTTPStatus.NOT_IMPLEMENTED

@app.route('/jee/submit', methods=['GET'])
def submit():
    global session

    if session.exam:
        session.end_time = datetime.now(timezone.utc).isoformat()

        with connect(MAIN_DATABASE_PATH) as connection:
            exam_data = (
                session.exam.name,
                session.exam.duration,
                session.start_time,
                session.end_time,
                session.outage_time
            )

            exam_id: int = connection.execute("""
                INSERT INTO exams
                (exam_name, duration, start_time, end_time, outage_delay)
                VALUES (?, ?, ?, ?, ?)
                RETURNING exam_id;
            """, exam_data).fetchone()[0]

            for section in session.exam.sections:
                section_id: int = connection.execute("""
                    INSERT INTO sections
                    (exam_id, section_name, section_type, correct_marks, unattempted_marks, wrong_marks)
                    VALUES (?, ?, ?, ?, ?, ?)
                    RETURNING section_id;
                """, (exam_id, section.name, section.type, section.correct_marks, section.unattempted_marks, section.wrong_marks)).fetchone()[0]

                for question in section.questions:
                    connection.execute("""
                        INSERT INTO questions
                        (section_id, question_number, attempt, marked)
                        VALUES (?, ?, ?, ?);
                    """, (section_id, question.question_number, question.value, question.marked))

        connection.close()

        
        session.exam = None
        session.start_time = ""
        session.outage_time = ""
        session.answered_count = 0
        session.unanswered_count = 0
        session.unvisited_count = 0
        session.marked_count = 0

        BACKUP_FILE_PATH.unlink(missing_ok=True)

        return redirect('/jee/submitted'), HTTPStatus.TEMPORARY_REDIRECT

    return "You are not in a test session.", HTTPStatus.NOT_IMPLEMENTED

@app.route('/jee/submitted', methods=['GET'])
def submitted():
    return render_template('submitted.html'), HTTPStatus.OK

@app.route('/jee/download', methods=['GET'])
def download():
    return render_template('download.html'), HTTPStatus.OK

@app.route('/jee/download/exams', methods=['GET'])
def download_exams():
    csv_path = create_csv_from_db('exams')
    file = send_file(csv_path)
    csv_path.unlink(missing_ok=True)
    return file, HTTPStatus.OK


@app.route('/jee/download/sections', methods=['GET'])
def download_sections():
    csv_path = create_csv_from_db('sections')
    file = send_file(csv_path)
    csv_path.unlink(missing_ok=True)
    return file, HTTPStatus.OK


@app.route('/jee/download/questions', methods=['GET'])
def download_questions():
    csv_path = create_csv_from_db('questions')
    file = send_file(csv_path)
    csv_path.unlink(missing_ok=True)
    return file, HTTPStatus.OK
        
def main():
    global SERVER_MODE

    create_file_system()
    restore_recovery_data()

    app.run()

if __name__ == '__main__':
    main()
