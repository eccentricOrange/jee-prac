const url_params = new URLSearchParams(window.location.search);
const current_number = parseInt(url_params.get('number'));
const questions_status = get_url('/jee/get_questions_status');
const counts_request = get_url('/jee/get_counts')
const remaining_time_request = get_url('/jee/get_remaining_time');

let remaining_time = 0;

let counts = {
    'answered': 0,
    'marked': 0,
    'unanswered': 0
}

// Called on page load
function init_question() {
    remaining_time_request.then(
        function (data) {
            remaining_time = data['remaining_time'];
            update_timer_UI();
        }
    );
    counts_request.then(
        function (data) {
            counts = data;
            set_counts();
        }
    );
    create_palette();
    disable_next();
    disable_previous();
    initialize_mark_button();
    set_value_from_server();
    setInterval(clock, 1000);
}

// Used internally
async function get_url(url) {
    const response = await fetch(url);
    const json = await response.json();

    return json;
}

// Used internally
function post(url, data = null) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify(data));
}

// Used internally
function end_prompt(data, task) {
    return window.confirm(`You have attempted ${data['answered']} questions, ${data['marked']} questions are marked, and ${data['unanswered']} questions are unanswered. Are you sure you want to ${task}?`);
}

// Used internally
function get_mcq_value() {
    const options_chosen = document.querySelector('input[name="question"]:checked');

    let value = null;

    if (options_chosen == null) {
        value = 'null';
    }

    else {
        value = options_chosen.value;
    }

    return value;
}

// Used internally
function get_numeric_value() {
    return document.getElementsByName('question')[0].value;
}

// Used internally
function set_palette_button_answer(value) {
    const palette_button = document.getElementById(`${current_number}`);

    if (value == 'null' || value == null || value == '') {
        if (palette_button.classList.contains('answered')) {
            palette_button.classList.remove('answered');
            palette_button.classList.add('unanswered');
        }

        counts['answered'] -= 1;
        counts['unanswered'] += 1;
    }

    else {
        if (palette_button.classList.contains('unanswered')) {
            palette_button.classList.remove('unanswered');
            palette_button.classList.add('answered');
        }

        counts['answered'] += 1;
        counts['unanswered'] -= 1;
    }
}

// Used internally
function auto_submit() {
    if (remaining_time <= 0) {
        submit(false);
    }
}

//Used internally
function set_counts() {
    document.getElementById('answered_count').innerHTML = counts['answered'];
    document.getElementById('marked_count').innerHTML = counts['marked'];
    document.getElementById('unanswered_count').innerHTML = counts['unanswered'];
}

// Used internally
function update_timer_UI() {
    var remaining_time_date_object = new Date(null);
    remaining_time_date_object.setUTCSeconds(remaining_time);
    document.getElementById('timer').innerHTML = `${remaining_time_date_object.getUTCHours().toString().padStart(2, '0')}:${remaining_time_date_object.getUTCMinutes().toString().padStart(2, '0')}:${remaining_time_date_object.getUTCSeconds().toString().padStart(2, '0')}`;
}

// Used internally
function clock() {
    remaining_time -= 1;
    update_timer_UI();
    auto_submit();
}

// Used internally
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

// Used internally
function disable_previous() {
    if (current_number == 1) {
        document.getElementById('previous').disabled = true;
    }

    else {
        document.getElementById('previous').disabled = false;
    }
}

function set_value_from_server() {
    questions_status.then(
        function (data) {
            if (data[current_number]['type'] == 'mcq') {
                if (data[current_number]['value'] != 'null' && data[current_number]['value'] != null && data[current_number]['value'] != '') {
                    document.querySelector(`input[value="${data[current_number]['value']}"]`).checked = true;
                }
            }

            else {
                document.getElementsByName('question')[0].value = data[current_number]['value'];
            }
        }
    );
}

// Used internally
function create_palette() {
    questions_status.then(
        function (data) {
            for (let i = 1; i <= Object.keys(data).length; i++) {
            create_button_in_palette(data, i);
            }
        }
    );
}

function create_button_in_palette(data, question) {
    let new_button = document.createElement('button');
    new_button.className = `question_button ${data[question]['visit']} ${data[question]['answer']} ${data[question]['mark']}`;
    new_button.id = `${question}`;
    new_button.innerHTML = data[question]['number'];

    new_button.onclick = function () {
        window.location.href = `/jee/question?number=${new_button.id}`;
    };

    document.getElementById(data[question]['subject']).appendChild(new_button);
}

// Used internally
function initialize_mark_button() {
    questions_status.then(
        function (data) {
            if (data[current_number]['mark'] == 'marked') {
                document.getElementById('mark').innerHTML = 'Unmark';
            }

            else {
                document.getElementById('mark').innerHTML = 'Mark';
            }
        }
    );
}

// Called by UI button
function mark() {
    questions_status.then(
        function (data) {
            let palette_button_classes = document.getElementById(`${current_number}`).classList;

            if (data[current_number]['mark'] == 'marked') {
                post(`/jee/unmark?number=${current_number}`);

                palette_button_classes.remove('marked');
                palette_button_classes.add('unmarked');

                counts['marked'] -= 1;
                data[current_number]['mark'] = 'unmarked';

                document.getElementById('mark').innerHTML = 'Mark';
            }

            else {
                post(`/jee/mark?number=${current_number}`);

                palette_button_classes.remove('unmarked');
                palette_button_classes.add('marked');

                counts['marked'] += 1;
                data[current_number]['mark'] = 'marked';

                document.getElementById('mark').innerHTML = 'Unmark';
            }
            set_counts();
        }
    );

}

// Called by UI button
function next() {
    window.location.href = `/jee/question?number=${current_number + 1}`;
}

// Called by UI button
function previous() {
    window.location.href = `/jee/question?number=${current_number - 1}`;
}

// Called by UI button
function quit() {
    if (end_prompt(counts, 'quit')) {
        window.location.href = '/jee/quit';
    }
}

// Called by UI button, or used internally
function submit(popup_required) {
    if (popup_required) {
        if (end_prompt(counts, 'submit')) {
            store_value();
            window.location.href = '/jee/submit';
        }
    }

    else {
        window.location.href = '/jee/submit';
    }
}

// Called by UI element
function store_value() {
    questions_status.then(
        function (data) {
            const value = data[current_number]['type'] == 'mcq' ? get_mcq_value() : get_numeric_value();

            post(`/jee/store_value?number=${current_number}&value=${value}`);
            set_palette_button_answer(value);
            set_counts();
        }
    );
}

// Called by UI element, or used internally
function clear_mcq() {
    let radios = document.getElementsByName('question');
    for (let i = 0; i < radios.length; i++) {
        radios[i].checked = false;
    }

    store_value();
}