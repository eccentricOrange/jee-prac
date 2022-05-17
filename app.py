from pathlib import Path
from flask import Flask, render_template, request, redirect, send_file
from json import loads, dumps

app = Flask(__name__)

template_tests = Path('preconfigured-exams.json')

@app.route('/jee/', methods=['GET', 'POST'])
def select_test_type():
    return render_template('select-test-type.html', jsonfile=loads(template_tests.read_text()))

@app.route('/jee/configure-test/', methods=['GET', 'POST'])
def configure_test():
    return render_template('configure-test.html')