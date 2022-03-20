from pickle import FALSE
from flask import Flask, render_template, request, redirect
from json import dumps
from pathlib import Path
from datetime import datetime
from http import HTTPStatus
from sqlite3 import connect

app = Flask(__name__)
questions_status = {}
test_data = {}

NEW_QUESTION = {
    'number': 0,
    'visit': "unvisited",
    'answer': "unanswered",
    'mark': "unmarked",
    'value': None,
    'type': None,
    'subject': None
}

SUBJECTS = [
    'physics',
    'chemistry',
    'mathematics'
]

TYPES = [
    'mcq',
    'numeric'
]

SCHEMA_PATH = Path(__file__).parent / 'schema.sql'
FOLDER = Path().home() / '.jee-prac'
DB_PATH = FOLDER / 'jee.db'
START_TIME = datetime.now()
SUBMITTED = False


def setup_storage():
    FOLDER.mkdir(exist_ok=True, parents=True)
    with connect(DB_PATH) as connection:
        with open(SCHEMA_PATH, 'r') as f:
            connection.executescript(f.read())
            connection.commit()


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


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html'), HTTPStatus.OK


@app.route('/start', methods=['GET'])
def start():
    if request.args:
        global test_data, questions_status, START_TIME
        test_data = request.args.to_dict()
        questions_status = produce_list_of_questions(test_data)
        START_TIME = datetime.now()
        return redirect('/question?number=1')

    return dumps({}), HTTPStatus.BAD_REQUEST


@app.route('/get_questions_status', methods=['GET'])
def get_questions_status():
    global questions_status
    if questions_status:
        return dumps(questions_status), HTTPStatus.OK

    return dumps({}), HTTPStatus.NOT_FOUND


@app.route('/get_question_status', methods=['GET'])
def get_question_status():
    if request.args and 'number' in request.args:

        if questions_status:
            return dumps(questions_status[request.args.get('number')]), HTTPStatus.OK

        return dumps({}), HTTPStatus.NOT_FOUND
    return dumps({}), HTTPStatus.BAD_REQUEST


@app.route('/question', methods=['GET'])
def question():
    global questions_status

    if request.args and 'number' in request.args:
        if questions_status:
            number = str(request.args.get('number'))

            if questions_status[number]['visit'] == "unvisited":
                questions_status[number]['visit'] = "visited"

            question = questions_status[number]
            return render_template(f'{question["type"]}.html', q_no=question['number'], q_type=question["type"]), HTTPStatus.OK

        return dumps({}), HTTPStatus.NOT_FOUND
    return dumps({}), HTTPStatus.BAD_REQUEST


@app.route('/store_value', methods=['POST'])
def store_value():
    global questions_status

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

            return dumps({'status': 'success'}), HTTPStatus.OK

        return dumps({}), HTTPStatus.NOT_FOUND
    return dumps({}), HTTPStatus.BAD_REQUEST


@app.route('/unmark', methods=['POST'])
def mark():
    global questions_status
    if request.args and 'number' in request.args:
        if questions_status:
            number = str(request.args.get('number'))
            questions_status[number]['mark'] = "unmarked"
            return dumps({'status': 'success'}), HTTPStatus.OK

        return dumps({}), HTTPStatus.NOT_FOUND
    return dumps({}), HTTPStatus.BAD_REQUEST


@app.route('/mark', methods=['POST'])
def unmark():
    global questions_status
    if request.args and 'number' in request.args:
        if questions_status:
            number = str(request.args.get('number'))
            questions_status[number]['mark'] = "marked"
            return dumps({'status': 'success'}), HTTPStatus.OK

        return dumps({}), HTTPStatus.NOT_FOUND
    return dumps({}), HTTPStatus.BAD_REQUEST


@app.route('/submit', methods=['POST', 'GET'])
def submit():
    END_TIME = datetime.now()
    global questions_status, test_data, START_TIME, SUBMITTED

    if questions_status:

        with connect(DB_PATH) as connection:
            cursor = connection.cursor()

            cursor.execute(
                "INSERT INTO exams (start_time, end_time) VALUES (?, ?);",
                (START_TIME, END_TIME)
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

        SUBMITTED = True

        questions_status = {}
        test_data = {}
        START_TIME = datetime.now()

        return redirect('/submitted'), HTTPStatus.TEMPORARY_REDIRECT
    return dumps({}), HTTPStatus.NOT_FOUND


@app.route('/get_remaining_time', methods=['GET'])
def get_remaining_time():
    global START_TIME

    if START_TIME:
        remaining_time = (
            int(test_data['duration']) * 60) - (datetime.now() - START_TIME).total_seconds()

        return dumps({'remaining_time': remaining_time}), HTTPStatus.OK
    return dumps({}), HTTPStatus.NOT_FOUND


@app.route('/get_counts', methods=['GET'])
def get_counts():
    global questions_status

    if questions_status:
        counts = count_questions()

        return dumps(counts), HTTPStatus.OK
    return dumps({}), HTTPStatus.NOT_FOUND


@app.route('/submitted', methods=['GET'])
def submitted():
    global SUBMITTED

    if SUBMITTED:
        return render_template('submitted.html'), HTTPStatus.OK

    SUBMITTED = False

    return dumps({}), HTTPStatus.BAD_REQUEST


@app.route('/quit', methods=['GET'])
def quit():
    global questions_status, test_data, START_TIME

    if questions_status:
        questions_status = {}
        test_data = {}
        START_TIME = datetime.now()

        return redirect('/'), HTTPStatus.TEMPORARY_REDIRECT
    return dumps({}), HTTPStatus.BAD_REQUEST


def main():
    setup_storage()
    app.run()


if __name__ == '__main__':
    main()
