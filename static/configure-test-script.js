var section_count = 1;

const field_container = document.createElement("div")
field_container.className = "section-field-config-test"

function get_new_section(section_number) {
    // create section within form
    var host_section = document.createElement("fieldset");
    host_section.id = `section-${section_number}`;

    var section_heading = document.createElement("legend");
    section_heading.innerHTML = `Section ${section_number}`;

    // input for section name
    var name_div = field_container.cloneNode(true);
    name_div.innerHTML = "Section name"

    var name_input = document.createElement("input");
    name_input.setAttribute("type", "text");
    name_input.setAttribute("name", `section-${section_number}-name`);
    name_input.setAttribute("id", `section-${section_number}-name`);
    name_input.setAttribute("required", "");

    name_div.appendChild(name_input);

    // input for questions type
    var questions_type_div = field_container.cloneNode(true);
    questions_type_div.innerHTML = "Questions type"

    var questions_type_select = document.createElement("select");
    questions_type_select.setAttribute("name", `section-${section_number}-questions-type`);
    questions_type_select.setAttribute("id", `section-${section_number}-questions-type`);
    questions_type_select.setAttribute("required", "");

    var mcq_questions_option = document.createElement("option");
    mcq_questions_option.setAttribute("value", "mcq");
    mcq_questions_option.innerHTML = "Multiple Choice Questions (MCQ)";

    var numeric_questions_option = document.createElement("option");
    numeric_questions_option.setAttribute("value", "numeric");
    numeric_questions_option.innerHTML = "Numeric";

    questions_type_select.appendChild(mcq_questions_option);
    questions_type_select.appendChild(numeric_questions_option);

    questions_type_div.appendChild(questions_type_select);

    // input for questions count
    var number_of_questions__div = field_container.cloneNode(true);
    number_of_questions__div.innerHTML = "Number of questions"

    var number_of_questions_input = document.createElement("input");
    number_of_questions_input.setAttribute("type", "number");
    number_of_questions_input.setAttribute("name", `section-${section_number}-number-of-questions`);
    number_of_questions_input.setAttribute("id", `section-${section_number}-number-of-questions`);
    number_of_questions_input.setAttribute("required", "");

    number_of_questions__div.appendChild(number_of_questions_input);

    // input for marks if correct
    var marks_if_correct_div = field_container.cloneNode(true);
    marks_if_correct_div.innerHTML = "Marks if correct"

    var marks_if_correct_input = document.createElement("input");
    marks_if_correct_input.setAttribute("type", "number");
    marks_if_correct_input.setAttribute("name", `section-${section_number}-marks-if-correct`);
    marks_if_correct_input.setAttribute("id", `section-${section_number}-marks-if-correct`);
    marks_if_correct_input.setAttribute("required", "");

    marks_if_correct_div.appendChild(marks_if_correct_input);

    // input for marks if unattempted
    var marks_if_unattempted_div = field_container.cloneNode(true);
    marks_if_unattempted_div.innerHTML = "Marks if unattempted"

    var marks_if_unattempted_input = document.createElement("input");
    marks_if_unattempted_input.setAttribute("type", "number");
    marks_if_unattempted_input.setAttribute("name", `section-${section_number}-marks-if-unattempted`);
    marks_if_unattempted_input.setAttribute("id", `section-${section_number}-marks-if-unattempted`);
    marks_if_unattempted_input.setAttribute("required", "");

    marks_if_unattempted_div.appendChild(marks_if_unattempted_input);

    // input for marks if wrong
    var marks_if_wrong_div = field_container.cloneNode(true);
    marks_if_wrong_div.innerHTML = "Marks if wrong"

    var marks_if_wrong_input = document.createElement("input");
    marks_if_wrong_input.setAttribute("type", "number");
    marks_if_wrong_input.setAttribute("name", `section-${section_number}-marks-if-wrong`);
    marks_if_wrong_input.setAttribute("id", `section-${section_number}-marks-if-wrong`);
    marks_if_wrong_input.setAttribute("required", "");

    marks_if_wrong_div.appendChild(marks_if_wrong_input);

    // button to delete section
    var delete_section_button = document.createElement("button");
    delete_section_button.setAttribute("type", "button");
    delete_section_button.setAttribute("id", `delete-section-${section_number}`);
    delete_section_button.setAttribute("onclick", `delete_section(${section_number})`);
    delete_section_button.innerHTML = "Delete";

    // append all inputs to section
    host_section.appendChild(section_heading);
    host_section.appendChild(name_div);
    host_section.appendChild(questions_type_div);
    host_section.appendChild(number_of_questions__div);
    host_section.appendChild(number_of_questions_div);
    host_section.appendChild(marks_if_correct_div);
    host_section.appendChild(marks_if_unattempted_div);
    host_section.appendChild(marks_if_wrong_div);
    host_section.appendChild(delete_section_button);

    return host_section
}

function add_section() {
    section_count += 1;
    document.getElementById("sections").appendChild(get_new_section(section_count));
}

function delete_section(section_number) {
    document.getElementById(`section-${section_number}`).remove();
}

function reset_form() {
    for (let section_number = section_count; section_number > 1; section_number--) {
        const element_to_remove = document.getElementById(`section-${section_number}`);

        if (element_to_remove) {
            element_to_remove.remove();
        }
    }

    section_count = 1;
}