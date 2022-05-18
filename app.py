from pathlib import Path
import statistics
from flask import Flask, render_template, request, redirect, send_file
from http import HTTPStatus
from json import load, loads, dumps
from re import match

app = Flask(__name__)

TEMPLATE_TESTS_PATH = Path('preconfigured-exams.json')
chosen_test_data = {}
questions = []
question_section_mapping = []
counts = {
    'answered': 0,
    'unanswered': 0,
    'marked': 0,
    'unvisited': 0
}

def make_questions():
    global questions, chosen_test_data
    question_number = 1

    questions = chosen_test_data['sections'].copy()

    for section_number, section in enumerate(questions):
        section['questions'] = [
            {
                'question-number': question_number + counter,
                'value': "",
                'visited': "unvisited",
                'marked': "unmarked"
            }
            for counter in range(section['number-of-questions'])
        ]

        question_number += section['number-of-questions']

        question_section_mapping.append((section['questions'][0]['question-number'], section['questions'][-1]['question-number'], section_number))

    question_number -= 1

    counts['unanswered'] = question_number
    counts['unvisited'] = question_number
    chosen_test_data['total-number-of-questions'] = question_number


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
    global chosen_test_data, questions

    if chosen_test_data:
        make_questions()
        return redirect('/jee/question?question-number=1'), HTTPStatus.TEMPORARY_REDIRECT

    return '', HTTPStatus.NOT_IMPLEMENTED


@app.route('/jee/question', methods=['GET', 'POST'])
def get_question():
    global chosen_test_data, questions, question_section_mapping, counts

    if chosen_test_data and questions and question_section_mapping:
        question_number = int(request.args.get('question-number'))  # type: ignore
        for lower, upper, section_number in question_section_mapping:
            if lower <= question_number <= upper:
                section = questions[section_number]

                for question in section['questions']:
                    if question['question-number'] == question_number:
                        value = question['value']

                        next_question_disabled = "disabled" if chosen_test_data['total-number-of-questions'] == question_number else ""
                        previous_question_disabled = "disabled" if question_number == 1 else ""
                        mark_button_text = "Mark" if question['marked'] == "unmarked" else "Unmark"

                        if question['visited'] == 'unvisited':
                            question['visited'] = 'visited'
                            counts['unvisited'] -= 1

                        if section['type'] == 'mcq':
                            choices = [
                                {
                                    'option': option,
                                    'value': "checked" if option == value else ""
                                }
                                for option in section['options']
                            ]

                            return render_template(
                                'mcq.html',
                                sections=questions,
                                question_number=question_number,
                                question_type=section['name'],
                                test=chosen_test_data['name'],
                                choices=choices,
                                counts=counts,
                                next_question_disabled=next_question_disabled,
                                previous_question_disabled=previous_question_disabled,
                                mark_button_text=mark_button_text
                            ), HTTPStatus.OK
                        
                        elif section['type'] == 'numeric':
                            return render_template(
                                'numeric.html',
                                sections=questions,
                                question_number=question_number,
                                question_type=section['name'],
                                test=chosen_test_data['name'],
                                value=question['value'],
                                counts=counts,
                                next_question_disabled=next_question_disabled,
                                previous_question_disabled=previous_question_disabled,
                                mark_button_text=mark_button_text
                            ), HTTPStatus.OK

                        else:
                            return '', HTTPStatus.NOT_IMPLEMENTED

        return '', HTTPStatus.NOT_IMPLEMENTED

    return '', HTTPStatus.NOT_IMPLEMENTED

@app.route('/jee/mark', methods=['POST'])
def mark():
    global chosen_test_data, questions, question_section_mapping, counts

    if chosen_test_data and questions and question_section_mapping:
        form_data = dict(request.get_json(force=True))
        question_number = int(form_data['question-number'])

        for lower, upper, section_number in question_section_mapping:
            if lower <= question_number <= upper:
                section = questions[section_number]

                for question in section['questions']:
                    if question['question-number'] == question_number:
                        questions[section_number]['questions'][question_number - 1]['marked'] = 'marked'

                        counts['marked'] += 1

                    return "", HTTPStatus.OK

            
        return '', HTTPStatus.INTERNAL_SERVER_ERROR

    return '', HTTPStatus.NOT_IMPLEMENTED


@app.route('/jee/unmark', methods=['POST'])
def unmark():
    global chosen_test_data, questions, question_section_mapping, counts

    if chosen_test_data and questions and question_section_mapping:
        form_data = dict(request.get_json(force=True))
        question_number = int(form_data['question-number'])

        for lower, upper, section_number in question_section_mapping:
            if lower <= question_number <= upper:
                section = questions[section_number]

                for question in section['questions']:
                    if question['question-number'] == question_number:
                        questions[section_number]['questions'][question_number - 1]['marked'] = 'unmarked'

                        counts['marked'] -= 1

                    return "", HTTPStatus.OK

            
        return '', HTTPStatus.INTERNAL_SERVER_ERROR

    return '', HTTPStatus.NOT_IMPLEMENTED


@app.route('/jee/receive-value', methods=['POST'])
def receive_value():
    global chosen_test_data, questions, question_section_mapping, counts

    if chosen_test_data and questions and question_section_mapping:
        form_data = request.form
        question_number = int(form_data['question-number'])
        value = form_data['value']

        for lower, upper, section_number in question_section_mapping:
            if lower <= question_number <= upper:
                section = questions[section_number]

                for question in section['questions']:
                    if question['question-number'] == question_number:
                        old_value = questions[section_number]['questions'][question_number - 1]['value']

                        if (not old_value) and value:
                            counts['unattempted'] -= 1
                            counts['attempted'] += 1

                        if old_value and not value:
                            counts['attempted'] -= 1
                            counts['unattempted'] += 1

                        questions[section_number]['questions'][question_number - 1]['value'] = value

                        return "", HTTPStatus.OK

            
        return '', HTTPStatus.INTERNAL_SERVER_ERROR

    return '', HTTPStatus.NOT_IMPLEMENTED