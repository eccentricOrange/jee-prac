var section_count = 1;

function get_new_section(section_number) {
    // create section within form
    var host_section = document.createElement("fieldset");
    host_section.id = `section-${section_number}`;

    var section_heading = document.createElement("legend");
    section_heading.innerHTML = `Section ${section_number}`;

    // input for section name
    var name_label = document.createElement("label");
    name_label.innerHTML = "Section Name";
    name_label.setAttribute("for", `section-${section_number}-name`);

    var name_input = document.createElement("input");
    name_input.setAttribute("type", "text");
    name_input.setAttribute("name", `section-${section_number}-name`);
    name_input.setAttribute("id", `section-${section_number}-name`);
    name_input.setAttribute("required", "");

    // input for questions type
    var questions_type_label = document.createElement("label");
    questions_type_label.innerHTML = "Questions Type";
    questions_type_label.setAttribute("for", `section-${section_number}-questions-type`);

    var questions_type_select = document.createElement("select");
    questions_type_select.setAttribute("name", `section-${section_number}-questions-type`);
    questions_type_select.setAttribute("id", `section-${section_number}-questions-type`);
    questions_type_select.setAttribute("required", "");
    questions_type_select.setAttribute("onchange", `change_question_type(${section_number})`);

    var mcq_questions_option = document.createElement("option");
    mcq_questions_option.setAttribute("value", "mcq");
    mcq_questions_option.innerHTML = "Multiple Choice Questions (MCQ)";

    var numeric_questions_option = document.createElement("option");
    numeric_questions_option.setAttribute("value", "numeric");
    numeric_questions_option.innerHTML = "Numeric";

    var text_questions_option = document.createElement("option");
    text_questions_option.setAttribute("value", "text");
    text_questions_option.innerHTML = "Text";

    questions_type_select.appendChild(mcq_questions_option);
    questions_type_select.appendChild(numeric_questions_option);
    questions_type_select.appendChild(text_questions_option);

    // input for MCQ options
    var mcq_options_label = document.createElement("label");
    mcq_options_label.innerHTML = "MCQ Options";
    mcq_options_label.setAttribute("for", `section-${section_number}-options`);
    mcq_options_label.setAttribute("id", `section-${section_number}-options-label`);

    var mcq_options_input = document.createElement("select");
    mcq_options_input.setAttribute("name", `section-${section_number}-options`);
    mcq_options_input.setAttribute("id", `section-${section_number}-options`);
    mcq_options_input.setAttribute("required", "");

    var mcq_options_option_A = document.createElement("option");
    mcq_options_option_A.setAttribute("value", "A");
    mcq_options_option_A.innerHTML = "A";

    var mcq_options_option_a = document.createElement("option");
    mcq_options_option_a.setAttribute("value", "a");
    mcq_options_option_a.innerHTML = "a";

    var mcq_options_option_1 = document.createElement("option");
    mcq_options_option_1.setAttribute("value", "1");
    mcq_options_option_1.innerHTML = "1";

    mcq_options_input.appendChild(mcq_options_option_A);
    mcq_options_input.appendChild(mcq_options_option_a);
    mcq_options_input.appendChild(mcq_options_option_1);

    // input for questions count
    var number_of_questions_label = document.createElement("label");
    number_of_questions_label.innerHTML = "Number of Questions";
    number_of_questions_label.setAttribute("for", `section-${section_number}-number-of-questions`);

    var number_of_questions_input = document.createElement("input");
    number_of_questions_input.setAttribute("type", "number");
    number_of_questions_input.setAttribute("name", `section-${section_number}-number-of-questions`);
    number_of_questions_input.setAttribute("id", `section-${section_number}-number-of-questions`);
    number_of_questions_input.setAttribute("required", "");

    // input for marks if correct
    var marks_if_correct_label = document.createElement("label");
    marks_if_correct_label.innerHTML = "Marks if correct";
    marks_if_correct_label.setAttribute("for", `section-${section_number}-marks-if-correct`);

    var marks_if_correct_input = document.createElement("input");
    marks_if_correct_input.setAttribute("type", "number");
    marks_if_correct_input.setAttribute("name", `section-${section_number}-marks-if-correct`);
    marks_if_correct_input.setAttribute("id", `section-${section_number}-marks-if-correct`);
    marks_if_correct_input.setAttribute("required", "");

    // input for marks if unattempted
    var marks_if_unattempted_label = document.createElement("label");
    marks_if_unattempted_label.innerHTML = "Marks if unattempted";
    marks_if_unattempted_label.setAttribute("for", `section-${section_number}-marks-if-unattempted`);

    var marks_if_unattempted_input = document.createElement("input");
    marks_if_unattempted_input.setAttribute("type", "number");
    marks_if_unattempted_input.setAttribute("name", `section-${section_number}-marks-if-unattempted`);
    marks_if_unattempted_input.setAttribute("id", `section-${section_number}-marks-if-unattempted`);
    marks_if_unattempted_input.setAttribute("required", "");

    // input for marks if wrong
    var marks_if_wrong_label = document.createElement("label");
    marks_if_wrong_label.innerHTML = "Marks if wrong";
    marks_if_wrong_label.setAttribute("for", `section-${section_number}-marks-if-wrong`);

    var marks_if_wrong_input = document.createElement("input");
    marks_if_wrong_input.setAttribute("type", "number");
    marks_if_wrong_input.setAttribute("name", `section-${section_number}-marks-if-wrong`);
    marks_if_wrong_input.setAttribute("id", `section-${section_number}-marks-if-wrong`);
    marks_if_wrong_input.setAttribute("required", "");

    // button to delete section
    var delete_section_button = document.createElement("input");
    delete_section_button.setAttribute("type", "button");
    delete_section_button.setAttribute("id", `delete-section-${section_number}`);
    delete_section_button.setAttribute("onclick", `delete_section(${section_number})`);
    delete_section_button.setAttribute("value", "Delete Section");

    // append all inputs to section
    host_section.appendChild(section_heading);
    host_section.appendChild(name_label);
    host_section.appendChild(name_input);
    host_section.appendChild(questions_type_label);
    host_section.appendChild(questions_type_select);
    host_section.appendChild(mcq_options_label);
    host_section.appendChild(mcq_options_input);
    host_section.appendChild(number_of_questions_label);
    host_section.appendChild(number_of_questions_input);
    host_section.appendChild(marks_if_correct_label);
    host_section.appendChild(marks_if_correct_input);
    host_section.appendChild(marks_if_unattempted_label);
    host_section.appendChild(marks_if_unattempted_input);
    host_section.appendChild(marks_if_wrong_label);
    host_section.appendChild(marks_if_wrong_input);
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

function change_question_type(section_number) {
    if (document.getElementById(`section-${section_number}-questions-type`).value == "mcq") {
        document.getElementById(`section-${section_number}-options`).style.display = "block";
        document.getElementById(`section-${section_number}-options-label`).style.display = "block";
    } else {
        document.getElementById(`section-${section_number}-options`).style.display = "none";
        document.getElementById(`section-${section_number}-options-label`).style.display = "none";
    }
}