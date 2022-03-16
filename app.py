from flask import Flask, render_template, request, redirect
from json import dumps

app = Flask(__name__)

questions_status = {}

test_data = {
    'number_of_numeric_questions': 0,
    'number_of_mcq_questions': 0,
    'duration': 0
}

new_question = {
    'number': 0,
    'status': "unvisited",
    'value': None,
    'type': None,
    'subject': None
}

PAPER_RULES = {
    'mains': {
        'numeric': 5,
        'mcq': 20,
        'duration': 180
    },
    'mains_old': {
        'numeric': 0,
        'mcq': 30,
        'duration': 180
    }
}

SUBJECTS = [
    'physics',
    'chemistry',
    'mathematics'
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start')
def start():
    global PAPER_RULES, test_data, questions_status
    test_type = str(request.args.get('test_type'))
    number_of_numeric_questions = int(str(request.args.get('number_of_numeric_questions')))
    number_of_mcq_questions = int(str(request.args.get('number_of_mcq_questions')))
    duration = int(str(request.args.get('duration')))

    test_data = {
        'number_of_numeric_questions': number_of_numeric_questions,
        'number_of_mcq_questions': number_of_mcq_questions,
        'duration': duration
    }

    questions_status = initialize_paper(test_type, test_data)

    return redirect('/question?number=1')

@app.route('/get_question_by_number')
def get_question_by_number():
    global questions_status
    question_number = int(str(request.args.get('question_number')))
    return dumps(questions_status[question_number])

@app.route('/get_questions_status')
def get_questions_status():
    global questions_status
    return dumps(questions_status)

@app.route('/get_test_data')
def get_test_data():
    global test_data
    return dumps(test_data)

@app.route('/question')
def question():
    number = f"q{request.args.get('number')}"

    if number in questions_status:
        if questions_status[number]['type'] == 'numeric':
            return render_template('numeric.html')
        
        if questions_status[number]['type'] == 'mcq':
            return render_template('mcq.html')

    return render_template('error.html')

def initialize_paper(test_type, test_data):
    questions_status= {}
    
    if test_type in PAPER_RULES:
        test_data['number_of_numeric_questions'] = PAPER_RULES[test_type]['numeric']
        test_data['number_of_mcq_questions'] = PAPER_RULES[test_type]['mcq']
        test_data['duration'] = PAPER_RULES[test_type]['duration']

    for subject_counter, subject in enumerate(SUBJECTS):

        subject_increment = (test_data['number_of_mcq_questions'] + test_data['number_of_numeric_questions']) * subject_counter

        for question_counter in range(1, test_data['number_of_mcq_questions'] + 1):
            current_question_number = question_counter + subject_increment
            current_question_number_index = f"q{current_question_number}"

            questions_status[current_question_number_index] = new_question.copy()
            questions_status[current_question_number_index]['type'] = 'mcq'
            questions_status[current_question_number_index]['subject'] = subject
            questions_status[current_question_number_index]['number'] = current_question_number

        for question_counter in range(1, test_data['number_of_numeric_questions'] + 1):
            current_question_number = question_counter + test_data['number_of_mcq_questions'] + subject_increment
            current_question_number_index = f"q{current_question_number}"
            questions_status[current_question_number_index] = new_question.copy()
            questions_status[current_question_number_index]['type'] = 'numeric'
            questions_status[current_question_number_index]['subject'] = subject
            questions_status[current_question_number_index]['number'] = current_question_number

    return questions_status

def test():
    print(dumps(initialize_paper('mains', test_data), indent=4))

if __name__ == '__main__':
    test()