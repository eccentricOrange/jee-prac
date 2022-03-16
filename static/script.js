function create_palette(number_of_questions) {
    let container = document.getElementById("palette").getElementsByTagName("form")[0];
    let buttons = []

    for (var i = 1; i < number_of_questions + 1; i++) {
        var input = document.createElement("input");
        input.setAttribute("type", "button");
        input.setAttribute("name", i);
        input.setAttribute("value", i);
        input.setAttribute("id", i);

        buttons.push(input);
    }

    return buttons;
}

async function get_url(url) {
    const response = await fetch(url);
    const json = await response.json();

    return json;
}

function main() {
    get_palette();

}

window.onload = main;

function get_palette() {
    const test_data = get_url('/get_test_data');
    test_data.then(
        function (data) {
            console.log(data);
            let total_questions = (data.number_of_numeric_questions + data.number_of_mcq_questions) * 3;
            let buttons = create_palette(total_questions);
            console.log(buttons);
            set_palette(buttons);
        }
    );
}
function set_palette(buttons) {
    const questions_status = get_url('/get_questions_status');
    questions_status.then(
        function (data) {
            for (question in data) {
                const current_button = data[question];
                button = buttons[current_button.number - 1];
                button.setAttribute("class", `question_button ${current_button.status}`);
                document.getElementById(current_button.subject).appendChild(button);
            }
        }
    );
}

