from os import environ
from pathlib import Path
import algorithms

import classes

DIRECTORY_ENV = environ.get("JEE_PRAC_DIRECTORY")
HOST = environ.get("JEE_PRAC_HOST")
PORT = int(str(environ.get("JEE_PRAC_PORT")))

ACTIVE_DIRECTORY = Path(str(DIRECTORY_ENV if DIRECTORY_ENV else "data"))
BACKUP_FILE_PATH = ACTIVE_DIRECTORY / 'jee-prac-session-bkp.json'
MAIN_DATABASE_PATH = ACTIVE_DIRECTORY / 'jee-prac-database.db'
TEMPLATE_TESTS_PATH = ACTIVE_DIRECTORY / 'preconfigured-exams.json'
SCHEMA_PATH = Path('data') / 'schema.sql'

APP_NAME = "jee"

from flask import Flask, redirect, render_template, request, send_file
app = Flask(__name__)

@app.route(f"/{APP_NAME}")
def index():
    return render_template('index.html')

@app.route(f"/{APP_NAME}/select-test-type")
def select_test_type():
    return render_template('select-test-type.html', template_tests=algorithms.get_pre_configured_tests(TEMPLATE_TESTS_PATH))

@app.before_first_request
def init():
    algorithms.create_file_system(ACTIVE_DIRECTORY, MAIN_DATABASE_PATH, TEMPLATE_TESTS_PATH, SCHEMA_PATH)
    print(f'Visit http://{HOST}:{PORT}/{APP_NAME} to begin.\n')

