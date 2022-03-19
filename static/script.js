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

async function get_url(url) {
    const response = await fetch(url);
    const json = await response.json();

    return json;
}

function post(url, data = null) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify(data));
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


function clear_mcq() {
    let radios = document.getElementsByName('question');
    for (let i = 0; i < radios.length; i++) {
        radios[i].checked = false;
    }

    store_value();
}

function store_value() {
    question_status.then(
        function (question_status) {
            let value = null;
            if (question_status["type"] == 'mcq') {
                const options = document.querySelector('input[name="question"]:checked');
                if (options != null) {
                    value = options.value
                }

                else {
                    value = null;
                }
            }

            else if (question_status["type"] == 'numeric') {
                value = document.getElementsByName('question')[0].value;
            }

            post(`/store_value?number=${current_number}&value=${value}`);
        }
    );
}

function set_palette() {
    questions_status.then(
        function (data) {
            for (question in data) {
                let new_button = document.createElement('button');
                new_button.className = `question_button ${data[question]['visit']} ${data[question]['answer']} ${data[question]['mark']}`;
                new_button.id = `${question}`;
                new_button.innerHTML = data[question]['number'];
                new_button.onclick = function () {
                    window.location.href = `/question?number=${new_button.id}`;
                }

                document.getElementById(data[question]['subject']).appendChild(new_button);
            }
        }
    );
}

function set_value_from_server() {
    question_status.then(
        function (data) {
            if (data["type"] == 'mcq') {
                clear_mcq();
                if ((data["value"] != 'null') && (data["value"] != null)) {
                    document.querySelector(`input[value=${data["value"]}]`).checked = true;
                }
            }

            else if (data["type"] == 'numeric') {
                document.getElementsByName('question')[0].value = data["value"];
            }
        }
    );
}

function next() {
    const next_number = parseInt(current_number) + 1;
    window.location.href = `/question?number=${next_number}`;
}

function previous() {
    const previous_number = parseInt(current_number) - 1;
    window.location.href = `/question?number=${previous_number}`;
}


function disable_previous() {
    if (current_number == 1) {
        document.getElementById('previous').disabled = true;
    }

    else {
        document.getElementById('previous').disabled = false;
    }
}

function set_mark() {
    question_status.then(
        function (data) {
            if (data["mark"] == 'marked') {
                document.getElementById('mark').innerHTML = 'Unmark';
            }

            else {
                document.getElementById('mark').innerHTML = 'Mark';
            }
        }
    );
}

function mark() {
    question_status.then(
        function (data) {
            if (data["mark"] == 'marked') {
                post(`/unmark?number=${current_number}`);
                document.getElementById('mark').innerHTML = 'Mark';
            }

            else {
                post(`/mark?number=${current_number}`);
                document.getElementById('mark').innerHTML = 'Unmark';
            }
        }
    );
    question_status = get_url(`/get_question_status?number=${current_number}`);
}

function disable_next() {
    questions_status.then(
        function (data) {
            if (current_number == Object.keys(data).length) {
                document.getElementById('next').disabled = true;
            }

            else {
                document.getElementById('next').disabled = false;
            }
        }
    );
}

function submit() {
    window.location.href = '/submit';
}


function clock() {
    time -= 1;
    var time_remaining = new Date(null)
    time_remaining.setUTCSeconds(time);
    document.getElementById('timer').innerHTML = `${time_remaining.getUTCHours()}:${time_remaining.getUTCMinutes()}:${time_remaining.getUTCSeconds()}`;
    delete time_remaining;
    auto_submit();
}

function auto_submit() {
    if (time == 0) {
        submit();
    }
}

function init_question() {
    url_params = new URLSearchParams(window.location.search);
    current_number = parseInt(url_params.get('number'));
    questions_status = get_url('/get_questions_status');
    question_status = get_url(`/get_question_status?number=${current_number}`);
    get_url('/get_remaining_time').then(
        function (data) {
            time = data.remaining_time;
        }
    )
    set_palette()
    set_value_from_server();
    disable_previous();
    disable_next();
    set_mark();
    setInterval(clock, 1000);
}


function new_exam() {
    window.location.href = '/';
}

function quit() {
    window.location.href = '/quit';
}