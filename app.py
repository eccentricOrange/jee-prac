from pathlib import Path
from flask import Flask, render_template, request, redirect, send_file
from http import HTTPStatus
from json import load, loads, dumps
from re import match

app = Flask(__name__)

TEMPLATE_TESTS_PATH = Path('preconfigured-exams.json')
chosen_test_data = {}
questions = []
question_section_mapping = []

def make_questions():
    global questions, chosen_test_data
    question_number = 1

    questions = chosen_test_data['sections'].copy()

    for section_number, section in enumerate(questions):
        section['questions'] = [
            {
                'question-number': question_number + counter,
                'answer': "",
                'answered': False,
                'marked': False
            }
            for counter in range(section['number-of-questions'])
        ]

        question_number += section['number-of-questions']

        question_section_mapping.append((section['questions'][0]['question-number'], section['questions'][-1]['question-number'], section_number))


@app.route('/jee/', methods=['GET', 'POST'])
def select_test_type():
    global chosen_test_data

    if not chosen_test_data:
        with open(TEMPLATE_TESTS_PATH, 'r') as template_tests_file:
            template_tests = load(template_tests_file)

        return render_template('select-test-type.html', jsonfile=template_tests), HTTPStatus.OK

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

                        if chosen_test_data['sections'][section_number]['type'] == 'mcq':
                            chosen_test_data['sections'][section_number]['options'] = ['A', 'B', 'C', 'D']

            return redirect('/jee/start-test'), HTTPStatus.TEMPORARY_REDIRECT

        return '', HTTPStatus.BAD_REQUEST

    return '', HTTPStatus.IM_USED


@app.route('/jee/start-test', methods=['GET', 'POST'])
def start_test():
    global chosen_test_data, questions

    if chosen_test_data:
        make_questions()
        return redirect('/jee/question?question-number=1'), HTTPStatus.TEMPORARY_REDIRECT

    return '', HTTPStatus.NOT_IMPLEMENTED


@app.route('/jee/question', methods=['GET', 'POST'])
def get_question():
    global chosen_test_data, questions, question_section_mapping

    if chosen_test_data and questions and question_section_mapping:
        question_number = int(request.args.get('question-number'))  # type: ignore
        for lower, upper, section_number in question_section_mapping:
            if lower <= question_number <= upper:
                section = questions[section_number]

                for question in section['questions']:
                    if question['question-number'] == question_number:
                        return render_template(
                            'question.html',
                            sections=questions,
                            question_number=question_number,
                            question_type=section['name'],
                            test=chosen_test_data['name'],
                        ), HTTPStatus.OK


        return '', HTTPStatus.NOT_IMPLEMENTED

    return '', HTTPStatus.NOT_IMPLEMENTED