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


def main():
    global SERVER_MODE

    create_file_system()

    app.run()

if __name__ == '__main__':
    main()