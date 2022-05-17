function init() {
    const form = document.getElementById("select-test-type-form");
    const default_test = "jee-mains";
    
    const test_type = form.querySelector("#test-type");
    test_type.value = default_test;

    form.querySelector("#timing-type").value = "set-time";

    const time = jsonfile[default_test]["duration"];
    form.querySelector("#duration").value = time;
    form.querySelector("#duration").setAttribute("disabled", "disabled");
}

function update_duration_on_test_change() {
    const form = document.getElementById("select-test-type-form");

    if (form.querySelector("#test-type").value == "custom") {
        form.querySelector("#set-time").setAttribute("disabled", "disabled");

        if (form.querySelector("#timing-type").value == "set-time") {
            form.querySelector("#timing-type").value = "custom-time"
            form.querySelector("#duration").removeAttribute("disabled");
            form.querySelector("#duration").focus();
        }
    } else {
        form.querySelector("#set-time").removeAttribute("disabled");
    }
    
    if (form.querySelector("#timing-type").value == "set-time") {
        const test_type = form.querySelector("#test-type");
        const time = jsonfile[test_type.value]["duration"];
        form.querySelector("#duration").value = time;
    }

    return form
}

function update_duration_on_timing_type_change() {
    const form = update_duration_on_test_change()
    form.querySelector("#duration").setAttribute("disabled", "disabled");

    if (form.querySelector("#timing-type").value == "custom-time") {
        form.querySelector("#duration").removeAttribute("disabled");
        form.querySelector("#duration").focus();
    }

    if (form.querySelector("#timing-type").value == "untimed") {
        form.querySelector("#duration").value = 0;
    }
}