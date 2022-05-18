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
    
        post('/jee/mark', {'question-number': question_number});

        mark_count.innerText = parseInt(mark_count.innerText) + 1;
        mark_button.setAttribute('value', 'Unmark');
    }
    
    else if (question_button.classList.contains('marked')) {
        question_button.classList.remove('marked');
        question_button.classList.add('unmarked');

        post('/jee/unmark', {'question-number': question_number});

        mark_count.innerText = parseInt(mark_count.innerText) - 1;
        mark_button.setAttribute('value', 'Mark');
    }

    else {
        window.alert('Something went wrong! Please refresh the page.');
    }
        
}