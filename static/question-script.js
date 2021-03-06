let time_remaining = new Date(time_remaining_string);

// Used internally
function post(url, data = null) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify(data));
}

function go_to_question(question_number) {
    window.location.href = `/jee/question?question-number=${question_number}`;
}

function go_to_next_question(question_number) {
    go_to_question(parseInt(question_number) + 1);
}

function go_to_previous_question(question_number) {
    go_to_question(parseInt(question_number) - 1);
}

function mark_question(question_number) {

    const question_button = document.getElementById(`question-${question_number}`);
    const mark_button = document.getElementById('mark');
    const mark_count = document.getElementById('marked-count');

    if (question_button.classList.contains('unmarked')) {
        question_button.classList.remove('unmarked');
        question_button.classList.add('marked');

        post('/jee/mark', { 'question-number': question_number });

        mark_count.innerText = parseInt(mark_count.innerText) + 1;
        mark_button.setAttribute('value', 'Unmark');
    }

    else if (question_button.classList.contains('marked')) {
        question_button.classList.remove('marked');
        question_button.classList.add('unmarked');

        post('/jee/unmark', { 'question-number': question_number });

        mark_count.innerText = parseInt(mark_count.innerText) - 1;
        mark_button.setAttribute('value', 'Mark');
    }

    else {
        window.alert('Something went wrong! Please refresh the page.');
        location.reload();
    }

}

function update_answered_count_and_button_state(question_number, new_answered) {
    const question_button = document.getElementById(`question-${question_number}`);
    const answered_count = document.getElementById('answered-count');
    const unanswered_count = document.getElementById('unanswered-count');

    if (question_button.classList.contains('unanswered') && new_answered) {
        question_button.classList.remove('unanswered');
        question_button.classList.add('answered');

        answered_count.innerText = parseInt(answered_count.innerText) + 1;
        unanswered_count.innerText = parseInt(unanswered_count.innerText) - 1;
    }

    else if (question_button.classList.contains('answered') && !new_answered) {
        question_button.classList.remove('answered');
        question_button.classList.add('unanswered');

        answered_count.innerText = parseInt(answered_count.innerText) - 1;
        unanswered_count.innerText = parseInt(unanswered_count.innerText) + 1;
    }

    else {
        return;
    }
}

function mcq_store_value(question_number) {
    const control_value = document.querySelector('input[name="question"]:checked')?.value;
    const answered = !((control_value == null) || (control_value == 'null') || (control_value == undefined));
    const value = answered ? control_value : '';
    post('/jee/receive-value', { 'question-number': question_number, 'value': value });
    update_answered_count_and_button_state(question_number, answered);
}

function clear_mcq(question_number) {
    const control_value = document.querySelector('input[name="question"]:checked');
    if (control_value) {
        control_value.checked = false;
    }
    mcq_store_value(question_number);
}

function field_store_value(question_number) {
    const control_value = document.getElementById('question').value;
    const answered = !((control_value == null) || (control_value == '') || (control_value == undefined));
    const value = answered ? control_value : "";
    post('/jee/receive-value', { 'question-number': question_number, 'value': value });
    update_answered_count_and_button_state(question_number, answered);
}

function clear_field(question_number) {
    const control_value = document.getElementById('question');
    if (control_value) {
        control_value.value = '';
    }
    field_store_value(question_number);
}

function init() {
    if (timer_type != "Untimed Test") {
        time_remaining = new Date(time_remaining_string);
        clock();
        setInterval(clock, 1000);
    }
}

function clock() {
    time_remaining = new Date(time_remaining - 1000);
    const time_remaining_string = `${time_remaining.getUTCHours().toString().padStart(2, '0')}:${time_remaining.getUTCMinutes().toString().padStart(2, '0')}:${time_remaining.getUTCSeconds().toString().padStart(2, '0')}`;
    document.getElementById('timer').innerText = time_remaining_string;

    // if (time_remaining <= 0) {
    //     window.location.href = '/jee/submit';
    // }
}

function finish_test(method) {
    if (window.confirm(`Are you sure you want to ${method} the test?`)){
        window.location.href=`/jee/${method}`;
    }
}