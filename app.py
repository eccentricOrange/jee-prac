from pathlib import Path
from flask import Flask, render_template, request, redirect, send_file
from http import HTTPStatus
from json import load, loads, dumps
from re import match

app = Flask(__name__)

TEMPLATE_TESTS_PATH = Path('preconfigured-exams.json')
chosen_test_data = {}
questions = []

def make_questions_generator(chosen_test_data: dict[str, dict[str, dict]]):
    question_number = 0
    
    for section_name, section_data in chosen_test_data['sections'].items():
        for _ in range(section_data['number-of-questions']):
            question_number += 1
            yield question_number, {
                'question-number': question_number,
                'section-name': section_name,
                'type': section_data['type'],
                'attempt': "",
                'marked': False
            }
        

@app.route('/jee/', methods=['GET', 'POST'])
def select_test_type():
    if not chosen_test_data:
        with open(TEMPLATE_TESTS_PATH, 'r') as template_tests_file:
            template_tests = load(template_tests_file)

        return render_template('select-test-type.html', jsonfile=template_tests), HTTPStatus.OK

    return "", HTTPStatus.IM_USED

@app.route('/jee/configure-test/', methods=['GET', 'POST'])
def configure_test():
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

                        if form_data['timing-type'] != 'set-time':

                            if form_data['timing-type'] == 'custom-time':
                                chosen_test_data['duration'] = int(form_data['duration'])

                            else:
                                chosen_test_data['duration'] = 0

                
                    return redirect('/jee/start-test'), HTTPStatus.OK
            
            return render_template('configure-test.html'), HTTPStatus.OK

        return '', HTTPStatus.BAD_REQUEST

    return '', HTTPStatus.IM_USED

@app.route('/jee/receive-test-config', methods=['POST'])
def receive_test_config():
    global chosen_test_data

    if not chosen_test_data:
        if request.method == 'POST':
            form_data = request.form
            chosen_test_data['subjects'] = {}

            if 'exam-name' in form_data:
                chosen_test_data['name'] = form_data['exam-name']

            for field in form_data:
                if match(r'^section-\d+-name$', field):
                    section_name = form_data[field]
                    section_number = int(field.split('-')[1])
                    section_id = section_name.replace(' ', '-').lower()

                    if section_id not in chosen_test_data['subjects']:
                        chosen_test_data['subjects'][section_id] = {
                            'name': section_name,
                            'type': form_data[f'section-{section_number}-questions-type'],
                            'number-of-questions': int(form_data[f'section-{section_number}-number-of-questions']),
                            'correct-marks': float(form_data[f'section-{section_number}-marks-if-correct']),
                            'unattempted-marks': float(form_data[f'section-{section_number}-marks-if-unattempted']),
                            'wrong-marks': float(form_data[f'section-{section_number}-marks-if-wrong'])
                        }

                        if chosen_test_data['subjects'][section_id]['type'] == 'mcq':
                            chosen_test_data['subjects'][section_id]['options'] = ['A', 'B', 'C', 'D']
                            
            return redirect('/jee/start-test'), HTTPStatus.OK

        return '', HTTPStatus.BAD_REQUEST

    return '', HTTPStatus.IM_USED