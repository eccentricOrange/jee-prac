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

// Called by UI element
function update_values() {
    form = document.getElementById("config_test");

    const test_type = form.elements["test_type"].value;
    if (test_type in PAPER_RULES) {
        for (question in PAPER_RULES[test_type]) {
            form.elements[question].value = PAPER_RULES[test_type][question];
        }
    }
}