from os import environ
from pathlib import Path
import algorithms

from classes import Session

DIRECTORY_ENV = environ.get("JEE_PRAC_DIRECTORY")
HOST = environ.get("JEE_PRAC_HOST")
PORT = int(str(environ.get("JEE_PRAC_PORT")))

ACTIVE_DIRECTORY = Path(str(DIRECTORY_ENV if DIRECTORY_ENV else "data"))
BACKUP_FILE_PATH = ACTIVE_DIRECTORY / 'jee-prac-session-bkp.json'
MAIN_DATABASE_PATH = ACTIVE_DIRECTORY / 'jee-prac-database.db'
TEMPLATE_TESTS_PATH = ACTIVE_DIRECTORY / 'preconfigured-exams.json'
SCHEMA_PATH = Path('data') / 'schema.sql'

from flask import Flask, redirect, render_template, request, send_file
app = Flask(__name__)
session = Session()



def main():
    algorithms.create_file_system(ACTIVE_DIRECTORY, MAIN_DATABASE_PATH, TEMPLATE_TESTS_PATH, SCHEMA_PATH)
    print(f'Visit http://{HOST}:{PORT}/jee to begin.\n')
    app.run(host=HOST, port=PORT)

if __name__ == '__main__':
    main()
