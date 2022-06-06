from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, redirect, send_file
from http import HTTPStatus
from json import dump, load
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
    exam = session.exam

    if request.method == 'POST':
        form_data = request.form
        exam = Exam()

        if form_data['test_type'] != "custom":
            with open(TEMPLATE_TESTS_PATH, 'r') as template_tests_file:
                template_tests = load(template_tests_file)

                if form_data['test_type'] in template_tests:
                    exam.from_dict(data=template_tests[form_data['test_type']])
                    exam.timing_type = form_data['timing_type']

                    if exam.timing_type != 'set-time':
                        exam.duration = int(form_data['duration']) if exam.timing_type == 'custom-time' else 0

                    return redirect('/jee/start-test'), HTTPStatus.TEMPORARY_REDIRECT

                return "", HTTPStatus.BAD_REQUEST

        exam.timing_type = form_data['timing_type']
        exam.duration = int(form_data['duration']) if exam.timing_type == 'custom-time' else 0
        return redirect('/jee/configure-test'), HTTPStatus.TEMPORARY_REDIRECT

    return "", HTTPStatus.BAD_REQUEST
    

@app.route('/jee/receive-test-config', methods=['POST'])
def receive_test_config():
    global session
    exam = session.exam

    if request.method == 'POST':
        form_data = request.form
        
        if 'exam-name' in form_data:
            exam.name = form_data['exam-name']

        section_index = 0

        for field in form_data:
            if match(r'^section-\d+-name$', field):

                name = form_data[field]
                section_number = int(field.split('-')[1])
                section_name = name.replace(' ', '-').lower()

    return '', HTTPStatus.BAD_REQUEST

        
def main():
    global SERVER_MODE

    create_file_system()

    app.run()

if __name__ == '__main__':
    main()