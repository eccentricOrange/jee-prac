from flask import Flask, render_template, request, redirect
from json import dumps

app = Flask(__name__)

questions_status = {}

test_data = {}

NEW_QUESTION = {
    'number': 0,
    'status': "unvisited",
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


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start')
def start():
    global test_data, questions_status
    test_data = request.args.to_dict()
    questions_status = produce_list_of_questions(test_data)
    return redirect('/question?number=1')

@app.route('/get_questions_status')
def get_questions_status():
    return dumps(questions_status)

@app.route('/get_question_status')
def get_question_status():
    return dumps(questions_status[request.args.get('number')])

@app.route('/question')
def question():
    global questions_status
    number = str(request.args.get('number'))
    question = questions_status[number]
    return render_template(f'{question["type"]}.html', q_no=question['number'], q_type=question["type"])

@app.route('/store_value')
def store_value():
    global questions_status
    number = str(request.args.get('number'))
    value = request.args.get('value')
    questions_status[number]['value'] = value
    return dumps({'status': 'success'}), 200

def test():
    pass

if __name__ == '__main__':
    test()