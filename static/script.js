async function get_url(url) {
    const response = await fetch(url);
    const json = await response.json();

    return json;
}

const PAPER_RULES = {
    'mains': {
        'physics_mcq': 20,
        'chemistry_mcq': 20,
        'mathematics_mcq': 20,
        'physics_numeric': 5,
        'chemistry_numeric': 5,
        'mathematics_numeric': 5,
        'duration': 180
    },
    'mains_old': {
        'physics_mcq': 30,
        'chemistry_mcq': 30,
        'mathematics_mcq': 30,
        'physics_numeric': 0,
        'chemistry_numeric': 0,
        'mathematics_numeric': 0,
        'duration': 180
    }
}

function update_values() {

    form = document.getElementById("config_test");

    const test_type = form.elements["test_type"].value;
    if (test_type in PAPER_RULES) {
        for (question in PAPER_RULES[test_type]) {
            form.elements[question].value = PAPER_RULES[test_type][question];
        }
    }
}

function set_palette() {
    const questions_status = get_url('/get_questions_status');
    questions_status.then(
        function (data) {
            for (question in data) {
                // console.log(question);
                let new_button = document.createElement('button');
                new_button.className = `question_button ${data[question]['status']}`;
                new_button.innerHTML = data[question]['number'];

                document.getElementById(data[question]['subject']).appendChild(new_button);
            }
        }
    );
}

function clear_mcq() {
    const radios = document.getElementsByName('question');
    for (let i = 0; i < radios.length; i++) {
        radios[i].checked = false;
    }
}

function store_value() {
    const url_params = new URLSearchParams(window.location.search);
    const question_status = get_url(`/get_question_status?number=${url_params.get('number')}`);
    question_status.then(
        function (question_status) {
            let value = null;
            if (question_status["type"] == 'mcq') {
                value = document.querySelector('input[name="question"]:checked').value
            }

            else if (question_status["type"] == 'numeric') {
                value = document.getElementsByName('question')[0].value;
            }

            fetch(`/store_value?number=${url_params.get('number')}&value=${value}`);
        }
    );
}

function main() {
    const question_status = get_url(`/get_question_status?number=${url_params.get('number')}`);
    question_status.then(
        function (question_status) {
            if (question_status["type"] == 'mcq') {
                clear_mcq();

                if (question_status["value"] != null) {
                    document.querySelector(`input[value=${question_status["value"]}]`).checked = true;
                }
            }

            else if (question_status["type"] == 'numeric') {
                document.getElementsByName('question')[0].value = question_status["value"];
            }
        }
    )
}

window.onload = main;