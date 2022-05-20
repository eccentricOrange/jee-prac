from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, render_template, request, redirect, send_file
from http import HTTPStatus
from json import dump, load, loads, dumps
from re import match
from os import environ
from sqlite3 import connect, Row
from csv import DictWriter

app = Flask(__name__)

DEVELOPMENT_MODE = bool(environ.get("JEE_PRAC_DEVELOPMENT"))

SCHEMA_PATH = Path('data') / 'schema.sql'
ACTIVE_DIRECTORY = Path('data') if DEVELOPMENT_MODE else Path().home() / '.jee-prac'
BACKUP_FILE_PATH = ACTIVE_DIRECTORY / 'jee-prac-session-bkp.json'
MAIN_DATABASE_PATH = ACTIVE_DIRECTORY / 'jee-prac-database.db'
TEMPLATE_TESTS_PATH = ACTIVE_DIRECTORY / 'preconfigured-exams.json'

chosen_test_data = {}
backup_data = {}
question_section_mapping = []
counts = {
    'answered': 0,
    'unanswered': 0,
    'marked': 0,
    'unvisited': 0
}

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
    global chosen_test_data, question_section_mapping, counts, outage_time

    with open(BACKUP_FILE_PATH, 'w') as backup_file:
        backup_data = {
            'chosen-test-data': chosen_test_data,
            'question-section-mapping': question_section_mapping,
            'counts': counts,
            'last-known-time': datetime.now().isoformat(),
            'outage-time': outage_time.isoformat()
        }

        dump(backup_data, backup_file)

def restore_recovery_data():
    global chosen_test_data, question_section_mapping, counts, outage_time, start_time

    if BACKUP_FILE_PATH.exists():
        with open(BACKUP_FILE_PATH, 'r') as backup_file:
            backup_data = load(backup_file)

            chosen_test_data = backup_data['chosen-test-data']
            question_section_mapping = backup_data['question-section-mapping']
            counts = backup_data['counts']
            outage_time = datetime.fromisoformat(backup_data['outage-time']) + (datetime.now() - datetime.fromisoformat(backup_data['last-known-time']))
            start_time = datetime.fromisoformat(backup_data['last-known-time'])

        return True

    return False

def make_questions():
    global chosen_test_data, start_time, question_section_mapping, counts, outage_time
    question_number = 1

    for section_number, section in enumerate(chosen_test_data['sections']):
        section['questions'] = [
            {
                'question-number': question_number + counter,
                'value': "",
                'visited': "unvisited",
                'marked': "unmarked",
                'answered': "unanswered"
            }
            for counter in range(section['number-of-questions'])
        ]

        question_number += section['number-of-questions']

        question_section_mapping.append((section['questions'][0]['question-number'], section['questions'][-1]['question-number'], section_number))

    question_number -= 1

    counts['unanswered'] = question_number
    counts['unvisited'] = question_number
    chosen_test_data['total-number-of-questions'] = question_number
    start_time = datetime.now()
    outage_time = datetime.fromtimestamp(0)

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
    global chosen_test_data

    if not chosen_test_data:
        with open(TEMPLATE_TESTS_PATH, 'r') as template_tests_file:
            template_tests = load(template_tests_file)

        return render_template('select-test-type.html', template_tests=template_tests), HTTPStatus.OK

    return "", HTTPStatus.IM_USED

@app.route('/jee/configure-test/', methods=['GET', 'POST'])
def configure_test():
    global chosen_test_data

    if not chosen_test_data:
        return render_template('configure-test.html'), HTTPStatus.OK

    return "", HTTPStatus.IM_USED

@app.route('/jee/receive-test-type', methods=['POST'])
def receive_test_type():
    global chosen_test_data
    
    if not chosen_test_data:
        if request.method == 'POST':
            form_data = request.form

            if form_data['test-type'] != 'custom':
                with open(TEMPLATE_TESTS_PATH, 'r') as template_tests_file:
                    template_tests = load(template_tests_file)

                    if form_data['test-type'] in template_tests:
                        chosen_test_data = template_tests[form_data['test-type']]
                        chosen_test_data['timing-type'] = form_data['timing-type']

                        if form_data['timing-type'] != 'set-time':

                            if form_data['timing-type'] == 'custom-time':
                                chosen_test_data['duration'] = int(form_data['duration'])

                            else:
                                chosen_test_data['duration'] = 0

                        return redirect('/jee/start-test'), HTTPStatus.TEMPORARY_REDIRECT

                    return "", HTTPStatus.BAD_REQUEST
            
            return render_template('configure-test.html'), HTTPStatus.OK

        return '', HTTPStatus.BAD_REQUEST

    return '', HTTPStatus.IM_USED

@app.route('/jee/receive-test-config', methods=['POST'])
def receive_test_config():
    global chosen_test_data

    if not chosen_test_data:
        if request.method == 'POST':
            form_data = request.form
            chosen_test_data['sections'] = []

            if 'exam-name' in form_data:
                chosen_test_data['name'] = form_data['exam-name']

            section_index = 0

            for field in form_data:
                if match(r'^section-\d+-name$', field):
                    name = form_data[field]
                    section_number = int(field.split('-')[1])
                    section_name = name.replace(' ', '-').lower()

                    if section_name not in chosen_test_data['sections']:
                        chosen_test_data['sections'].append({
                            'section-name': section_name,
                            'section-number': section_number,
                            'name': name,
                            'type': form_data[f'section-{section_number}-questions-type'],
                            'number-of-questions': int(form_data[f'section-{section_number}-number-of-questions']),
                            'correct-marks': float(form_data[f'section-{section_number}-marks-if-correct']),
                            'unattempted-marks': float(form_data[f'section-{section_number}-marks-if-unattempted']),
                            'wrong-marks': float(form_data[f'section-{section_number}-marks-if-wrong'])
                        })

                        if chosen_test_data['sections'][section_index]['type'] == 'mcq':
                            chosen_test_data['sections'][section_index]['options'] = ['A', 'B', 'C', 'D']
                    
                    section_index += 1

            return redirect('/jee/start-test'), HTTPStatus.TEMPORARY_REDIRECT

        return '', HTTPStatus.BAD_REQUEST

    return '', HTTPStatus.IM_USED


@app.route('/jee/start-test', methods=['GET', 'POST'])
def start_test():
    global chosen_test_data

    if chosen_test_data:
        make_questions()
        return redirect('/jee/question?question-number=1'), HTTPStatus.TEMPORARY_REDIRECT

    return '', HTTPStatus.NOT_IMPLEMENTED


@app.route('/jee/question', methods=['GET', 'POST'])
def get_question():
    global chosen_test_data, question_section_mapping, counts, start_time, outage_time

    if chosen_test_data and chosen_test_data['sections'] and question_section_mapping:

        question_number = int(request.args.get('question-number'))  # type: ignore

        for lower, upper, section_number in question_section_mapping:

            if lower <= question_number <= upper:
                section = chosen_test_data['sections'][section_number]

                for question in section['questions']:
                    if question['question-number'] == question_number:
                        value = question['value']

                        next_question_disabled = "disabled" if chosen_test_data['total-number-of-questions'] == question_number else ""
                        previous_question_disabled = "disabled" if question_number == 1 else ""
                        mark_button_text = "Mark" if question['marked'] == "unmarked" else "Unmark"

                        if question['visited'] == 'unvisited':
                            question['visited'] = 'visited'
                            counts['unvisited'] -= 1

                        if chosen_test_data['timing-type'] != 'untimed':
                            time_remaining = datetime.fromtimestamp(chosen_test_data['duration'] * 60) - ((datetime.now() - start_time) + outage_time)
                            time_remaining_string = datetime.fromtimestamp(time_remaining.total_seconds()).isoformat()
                            timer_type = "Time Remaining"
                        
                        else:
                            timer_type = "Untimed Test"
                            time_remaining_string = ""

                        if section['type'] == 'mcq':
                            choices = [
                                {
                                    'option': option,
                                    'value': "checked" if option == value else ""
                                }
                                for option in section['options']
                            ]

                            back_up_recovery_data()
                            return render_template(
                                'mcq.html',
                                sections=chosen_test_data['sections'],
                                question_number=question_number,
                                question_type=section['name'],
                                test=chosen_test_data['name'],
                                choices=choices,
                                counts=counts,
                                next_question_disabled=next_question_disabled,
                                previous_question_disabled=previous_question_disabled,
                                mark_button_text=mark_button_text,
                                timer_type=timer_type,
                                time_remaining_string=time_remaining_string
                            ), HTTPStatus.OK
                        
                        elif section['type'] == 'numeric':
                            back_up_recovery_data()
                            return render_template(
                                'numeric.html',
                                sections=chosen_test_data['sections'],
                                question_number=question_number,
                                question_type=section['name'],
                                test=chosen_test_data['name'],
                                value=question['value'],
                                counts=counts,
                                next_question_disabled=next_question_disabled,
                                previous_question_disabled=previous_question_disabled,
                                mark_button_text=mark_button_text,
                                timer_type=timer_type,
                                time_remaining_string=time_remaining_string
                            ), HTTPStatus.OK

                        else:
                            return '', HTTPStatus.NOT_IMPLEMENTED

        return '', HTTPStatus.NOT_IMPLEMENTED

    return '', HTTPStatus.NOT_IMPLEMENTED

@app.route('/jee/mark', methods=['POST'])
def mark():
    global chosen_test_data, question_section_mapping, counts

    if chosen_test_data and chosen_test_data['sections'] and question_section_mapping:
        form_data = dict(request.get_json(force=True))
        question_number = int(form_data['question-number'])

        for lower, upper, section_number in question_section_mapping:
            if lower <= question_number <= upper:
                section = chosen_test_data['sections'][section_number]

                for question in section['questions']:
                    print(dumps(question, indent=4))
                    if int(question['question-number']) == int(question_number):
                        question['marked'] = 'marked'
                        counts['marked'] += 1
                        print('marked')
                        back_up_recovery_data()
                        return "", HTTPStatus.OK

            
        return '', HTTPStatus.INTERNAL_SERVER_ERROR

    return '', HTTPStatus.NOT_IMPLEMENTED


@app.route('/jee/unmark', methods=['POST'])
def unmark():
    global chosen_test_data, question_section_mapping, counts

    if chosen_test_data and chosen_test_data['sections'] and question_section_mapping:
        form_data = dict(request.get_json(force=True))
        question_number = int(form_data['question-number'])

        for lower, upper, section_number in question_section_mapping:
            if lower <= question_number <= upper:
                section = chosen_test_data['sections'][section_number]

                for question in section['questions']:
                    if question['question-number'] == question_number:
                        question['marked'] = 'unmarked'
                        counts['marked'] -= 1

                        back_up_recovery_data()
                        return "", HTTPStatus.OK

            
        return '', HTTPStatus.INTERNAL_SERVER_ERROR

    return '', HTTPStatus.NOT_IMPLEMENTED


@app.route('/jee/receive-value', methods=['POST'])
def receive_value():
    global chosen_test_data, question_section_mapping, counts

    if chosen_test_data and chosen_test_data['sections'] and question_section_mapping:
        form_data = dict(request.get_json(force=True))
        question_number = int(form_data['question-number'])
        value = form_data['value']

        for lower, upper, section_number in question_section_mapping:
            if lower <= question_number <= upper:
                section = chosen_test_data['sections'][section_number]

                for question in section['questions']:
                    if question['question-number'] == question_number:
                        old_value = question['value']

                        if (not old_value) and value:
                            counts['unanswered'] -= 1
                            counts['answered'] += 1
                            question['answered'] = 'answered'

                        if old_value and not value:
                            counts['answered'] -= 1
                            counts['unanswered'] += 1
                            question['answered'] = 'unanswered'

                        question['value'] = value

                        back_up_recovery_data()
                        return "", HTTPStatus.OK

            
        return '', HTTPStatus.INTERNAL_SERVER_ERROR

    return '', HTTPStatus.NOT_IMPLEMENTED


@app.route('/jee/quit', methods=['GET'])
def quit():
    global chosen_test_data, question_section_mapping, counts, backup_data

    chosen_test_data = {}
    backup_data = {}
    question_section_mapping = []
    counts = {
        'answered': 0,
        'unanswered': 0,
        'marked': 0,
        'unvisited': 0
    }

    BACKUP_FILE_PATH.unlink(missing_ok=True)

    return redirect('/jee/'), HTTPStatus.TEMPORARY_REDIRECT


@app.route('/jee/submit', methods=['GET'])
def submit():
    global chosen_test_data, question_section_mapping, counts, backup_data, start_time, outage_time
    END_TIME = datetime.now()

    if chosen_test_data and chosen_test_data['sections'] and question_section_mapping:
        
        with connect(MAIN_DATABASE_PATH) as connection:

            exam_data = (
                chosen_test_data['name'],
                chosen_test_data['duration'],
                start_time.isoformat(),
                END_TIME.isoformat(),
                outage_time.isoformat()
            )

            exam_id: int = connection.execute("""
                INSERT INTO exams
                (exam_name, duration, start_time, end_time, outage_delay)
                VALUES (?, ?, ?, ?, ?)
                RETURNING exam_id;
            """, exam_data).fetchone()[0]

            for section in chosen_test_data['sections']:
                section_id: int = connection.execute("""
                    INSERT INTO sections
                    (exam_id, section_name, section_type, correct_marks, unattempted_marks, wrong_marks)
                    VALUES (?, ?, ?, ?, ?, ?)
                    RETURNING section_id;
                """, (exam_id, section['name'], section['type'], section['correct-marks'], section['unattempted-marks'], section['wrong-marks'])).fetchone()[0]

                for question in section['questions']:
                    connection.execute("""
                        INSERT INTO questions
                        (section_id, question_number, attempt, marked)
                        VALUES (?, ?, ?, ?);
                    """, (section_id, question['question-number'], question['value'], question['marked']))

        connection.close()

        chosen_test_data = {}
        backup_data = {}
        question_section_mapping = []
        counts = {
            'answered': 0,
            'unanswered': 0,
            'marked': 0,
            'unvisited': 0
        }

        BACKUP_FILE_PATH.unlink(missing_ok=True)
        return redirect('/jee/submitted'), HTTPStatus.TEMPORARY_REDIRECT

    return '', HTTPStatus.NOT_IMPLEMENTED

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
    create_file_system()
    restore_recovery_data()
    app.run()

if __name__ == '__main__':
    main()