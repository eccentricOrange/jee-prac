from os import environ
from pathlib import Path

DIRECTORY_ENV = environ.get("JEE_PRAC_DIRECTORY")
HOST = environ.get("JEE_PRAC_HOST")
PORT = environ.get("JEE_PRAC_PORT")

ACTIVE_DIRECTORY = Path(str(DIRECTORY_ENV if DIRECTORY_ENV else "data"))
BACKUP_FILE_PATH = ACTIVE_DIRECTORY / 'jee-prac-session-bkp.json'
MAIN_DATABASE_PATH = ACTIVE_DIRECTORY / 'jee-prac-database.db'
TEMPLATE_TESTS_PATH = ACTIVE_DIRECTORY / 'preconfigured-exams.json'