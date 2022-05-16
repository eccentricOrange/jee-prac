from flask import Flask, render_template, request, redirect, send_file
from json import dumps, loads
from pathlib import Path
from datetime import datetime
from http import HTTPStatus
from sqlite3 import connect
from csv import writer

app = Flask(__name__)
questions_status = {}  # store data about each question while a test is live
test_data = {}  # store data about the test in general while it is live
recovery_data = {}  # store data about multiple parameters to use for recovery
start_time = datetime.now()  # time of starting the test
test_submitted = False  # flag to indicate if the test has been submitted
last_known_time = datetime.now()  # time of the last interaction before error

# template to create a new question
NEW_QUESTION = {
    'number': 0,
    'visit': "unvisited",
    'answer': "unanswered",
    'mark': "unmarked",
    'value': None,
    'type': None,
    'subject': None
}

# subjects examined
SUBJECTS = [
    'physics',
    'chemistry',
    'mathematics'
]

# types of questions
TYPES = [
    'mcq',
    'numeric'
]

# main folder for a given user
FOLDER = Path().home() / '.jee-prac'

SCHEMA_PATH = Path(__file__).parent / 'schema.sql'  # path to the schema file
DB_PATH = FOLDER / 'jee.db'  # path to the database
RECOVERY_FILE = FOLDER / 'recovery.json'  # path to the recovery file
EXAMS_CSV_FILE = FOLDER / 'exams.csv'  # path to the (temporary) exams csv file
QUESTIONS_CSV_FILE = FOLDER / 'questions.csv'  # path to the (temporary) questions csv file

# setup the storage (files, folders, DB) for the application
def setup_storage():
    FOLDER.mkdir(exist_ok=True, parents=True)  # create the folder if it doesn't exist

    # create the DB from the schema if it doesn't exist and connect to it
    with connect(DB_PATH) as connection:
        with open(SCHEMA_PATH, 'r') as f:
            connection.executescript(f.read())
            connection.commit()

# generate the list of questions for a given exam
def produce_list_of_questions(exam_data: dict):
    questions = {}
    question_number = 1

    for subject_no, subject in enumerate(SUBJECTS, start=1):
        for type_no, type in enumerate(TYPES, start=1):

            for i in range(1, int(exam_data[f"{subject}_{type}"]) + 1):

                question = NEW_QUESTION.copy()
                question['number'] = question_number
                question['subject'] = subject
                question['type'] = type
                questions[str(question_number)] = question
                question_number += 1

    return questions

# count the number questions answered, unanswered, and marked
def count_questions():
    counts = {
        'unanswered': 0,
        'answered': 0,
        'marked': 0
    }

    for question_number, question in questions_status.items():
        if (not question['value']) and (question['value'] != "null"):
            counts['unanswered'] += 1

        else:
            counts['answered'] += 1

        if question['mark'] == "marked":
            counts['marked'] += 1

    return counts

# save the recovery data to the recovery file
def save_recovery_data():
    global recovery_data, questions_status, last_known_time

    last_known_time = datetime.now()  # update the last known time
    recovery_data['questions_status'] = questions_status  # update the questions status
    recovery_data['last_known_time'] = last_known_time.isoformat()  # update the last known time

    # write the recovery data to the recovery file
    with open(RECOVERY_FILE, 'w') as recovery:
        recovery.write(dumps(recovery_data))

# check if the recovery data exists and if it does, load it
def check_recovery_data():
    global recovery_data, questions_status, test_data, start_time, last_known_time

    if RECOVERY_FILE.exists():
        with open(RECOVERY_FILE, 'r') as recovery:
            recovery_data = recovery.read()

            if recovery_data:
                recovery_data = loads(recovery_data)
                questions_status = recovery_data['questions_status']
                test_data = recovery_data['test_data']
                last_known_time = datetime.fromisoformat(recovery_data['last_known_time'])

                # account for time loss due to crash, so that the candidate does not get penalized
                start_time = datetime.fromisoformat(recovery_data['start_time']) + (datetime.now() - last_known_time)

                return True
    return False

# convert post-exam data to CSV
def convert_to_csv(file_type: str):

    # connect to the DB
    with connect(DB_PATH) as connection:
        cursor = connection.cursor()
    
        # if the user is looking at the file that stores exam metadata
        if file_type == 'exams':
            EXAMS_CSV_FILE.touch(exist_ok=True)  # create the file if it doesn't exist

            with open(EXAMS_CSV_FILE, 'w') as exams_csv:

                exams_headers = ["exam_id", "start_time", "end_time"]

                exams_data = cursor.execute(f"SELECT {', '.join(exams_headers)} FROM exams").fetchall()  # get the data from the DB
                
                # write the data to the CSV file
                exams_writer = writer(exams_csv)
                exams_writer.writerow(exams_headers)
                exams_writer.writerows(exams_data)

        # if the user is looking at the file that stores questions
        elif file_type == 'questions':
                
                QUESTIONS_CSV_FILE.touch(exist_ok=True)  # create the file if it doesn't exist
    
                with open(QUESTIONS_CSV_FILE, 'w') as questions_csv:
    
                    questions_headers = ["question_id", "question_number", "exam_id", "type", "subject", "value"]
    
                    questions_data = cursor.execute(f"SELECT {', '.join(questions_headers)} FROM questions").fetchall()  # get the data from the DB
                    
                    # write the data to the CSV file
                    questions_writer = writer(questions_csv)
                    questions_writer.writerow(questions_headers)
                    questions_writer.writerows(questions_data)

        # if the user is looking at the file that does not exist
        else:
            raise Exception(f"Invalid file type: {file_type}")  # yell at them

# entry point for the application
# this is where the user will configure a test and start it
@app.route('/jee/', methods=['GET', 'POST'])
def index():
    return render_template('index.html'), HTTPStatus.OK

# this is where the user will start the test
# numbers of questions and time are received from a form submitted by the user
@app.route('/jee/start', methods=['GET'])
def start():

    # if there are arguments in the URL
    if request.args:
        global test_data, questions_status, start_time, recovery_data

        # load the data into variables
        test_data = request.args.to_dict()
        questions_status = produce_list_of_questions(test_data)
        start_time = datetime.now()

        # create the recovery file and write the data to it
        RECOVERY_FILE.touch()
        recovery_data = {
            'test_data': test_data,
            'start_time': start_time.isoformat()
        }
        save_recovery_data()

        # redirect the user to the first question
        return redirect('/jee/question?number=1')

    return "", HTTPStatus.BAD_REQUEST

# 
@app.route('/jee/get_questions_status', methods=['GET'])
def get_questions_status():
    global questions_status
    if questions_status:
        return dumps(questions_status), HTTPStatus.OK

    return "", HTTPStatus.NOT_FOUND


@app.route('/jee/get_question_status', methods=['GET'])
def get_question_status():
    if request.args and 'number' in request.args:

        if questions_status:
            return dumps(questions_status[request.args.get('number')]), HTTPStatus.OK

        return "", HTTPStatus.NOT_FOUND
    return "", HTTPStatus.BAD_REQUEST


@app.route('/jee/question', methods=['GET'])
def question():
    global questions_status

    if request.args and 'number' in request.args:
        if questions_status:
            number = str(request.args.get('number'))

            if questions_status[number]['visit'] == "unvisited":
                questions_status[number]['visit'] = "visited"

            question = questions_status[number]

            save_recovery_data()
            return render_template(f'{question["type"]}.html', q_no=question['number'], q_type=question["type"]), HTTPStatus.OK

        return "", HTTPStatus.NOT_FOUND
    return "", HTTPStatus.BAD_REQUEST


@app.route('/jee/store_value', methods=['POST'])
def store_value():
    global questions_status, recovery_data

    if request.args and 'number' in request.args and 'value' in request.args:
        if questions_status:
            number = str(request.args.get('number'))
            value = request.args.get('value')

            if value == "null" or not value:
                questions_status[number]['answer'] = "unanswered"
                questions_status[number]['value'] = None

            else:
                questions_status[number]['answer'] = "answered"
                questions_status[number]['value'] = value

            save_recovery_data()
            return dumps({'status': 'success'}), HTTPStatus.OK

        return "", HTTPStatus.NOT_FOUND
    return "", HTTPStatus.BAD_REQUEST


@app.route('/jee/unmark', methods=['POST'])
def mark():
    global questions_status
    if request.args and 'number' in request.args:
        if questions_status:
            number = str(request.args.get('number'))
            questions_status[number]['mark'] = "unmarked"

            save_recovery_data()
            return dumps({'status': 'success'}), HTTPStatus.OK

        return "", HTTPStatus.NOT_FOUND
    return "", HTTPStatus.BAD_REQUEST


@app.route('/jee/mark', methods=['POST'])
def unmark():
    global questions_status
    if request.args and 'number' in request.args:
        if questions_status:
            number = str(request.args.get('number'))
            questions_status[number]['mark'] = "marked"

            save_recovery_data()
            return dumps({'status': 'success'}), HTTPStatus.OK

        return "", HTTPStatus.NOT_FOUND
    return "", HTTPStatus.BAD_REQUEST


@app.route('/jee/submit', methods=['POST', 'GET'])
def submit():
    END_TIME = datetime.now()
    global questions_status, test_data, start_time, test_submitted

    if questions_status:

        with connect(DB_PATH) as connection:
            cursor = connection.cursor()

            cursor.execute(
                "INSERT INTO exams (start_time, end_time) VALUES (?, ?);",
                (start_time, END_TIME)
            )

            connection.commit()

            exam_id = int(cursor.execute(
                "SELECT exam_id FROM exams ORDER BY exam_id DESC LIMIT 1;"
            ).fetchone()[0])

            insertable = [
                (
                    int(exam_id),
                    int(number),
                    question_data['value'],
                    question_data['type'],
                    question_data['subject']
                ) for number, question_data in questions_status.items()
            ]

            cursor.executemany(
                "INSERT INTO questions (exam_id, question_number, value, type, subject) VALUES (?, ?, ?, ?, ?);",
                (insertable)
            )

            connection.commit()

        test_submitted = True

        questions_status = {}
        test_data = {}
        start_time = datetime.now()

        RECOVERY_FILE.unlink(missing_ok=True)

        return redirect('/jee/submitted'), HTTPStatus.TEMPORARY_REDIRECT
    return "", HTTPStatus.NOT_FOUND


@app.route('/jee/get_remaining_time', methods=['GET'])
def get_remaining_time():
    global start_time, test_data

    if start_time:
        remaining_time = (
            int(test_data['duration']) * 60) - (datetime.now() - start_time).total_seconds()

        return dumps({'remaining_time': remaining_time}), HTTPStatus.OK
    return "", HTTPStatus.NOT_FOUND


@app.route('/jee/get_counts', methods=['GET'])
def get_counts():
    global questions_status

    if questions_status:
        counts = count_questions()

        return dumps(counts), HTTPStatus.OK
    return "", HTTPStatus.NOT_FOUND


@app.route('/jee/submitted', methods=['GET'])
def submitted():
    global test_submitted

    if test_submitted:
        return render_template('submitted.html'), HTTPStatus.OK

    test_submitted = False

    return "", HTTPStatus.BAD_REQUEST


@app.route('/jee/quit', methods=['GET'])
def quit():
    global questions_status, test_data, start_time

    if questions_status:
        questions_status = {}
        test_data = {}
        start_time = datetime.now()

        RECOVERY_FILE.unlink(missing_ok=True)

        return redirect('/jee/'), HTTPStatus.TEMPORARY_REDIRECT
    return "", HTTPStatus.BAD_REQUEST


@app.route('/jee/downloads', methods=['GET'])
def downloads():
    return render_template('downloads_page.html'), HTTPStatus.OK


@app.route('/jee/download_exams_csv', methods=['GET'])
def download_exams_csv():
    convert_to_csv('exams')
    file = send_file(EXAMS_CSV_FILE)
    EXAMS_CSV_FILE.unlink(missing_ok=True)
    return file, HTTPStatus.OK


@app.route('/jee/download_questions_csv', methods=['GET'])
def download_questions_csv():
    convert_to_csv('questions')
    file = send_file(QUESTIONS_CSV_FILE)
    QUESTIONS_CSV_FILE.unlink(missing_ok=True)
    return file, HTTPStatus.OK


def main():
    setup_storage()
    check_recovery_data()
    app.run(port=80, host='0.0.0.0')


if __name__ == '__main__':
    main()
