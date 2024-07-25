document.addEventListener("DOMContentLoaded", () => {
    const input_password = document.getElementById("signup-password");
    const check_password = document.getElementById("signup-confirm-password");
    const password_submit = document.getElementById("create_form");

    password_submit.addEventListener("submit", (e) => {
        if (input_password.value !== check_password.value) {
            e.preventDefault();
        }
    });

    const length_regex = /.{8,}/;
    const lowercase_regex = /[a-z]/;
    const uppercase_regex = /[A-Z]/;
    const special_character_regex = /[@$!%*?&€£#^-_]/;
    const number_regex = /\d/;

    const length_req = document.getElementById("length-req");
    const lowercase_req = document.getElementById("lowercase-req");
    const uppercase_req = document.getElementById("uppercase-req");
    const number_req = document.getElementById("number-req");
    const special_req = document.getElementById("special-req");

    input_password.addEventListener("input", () => {
        let password = input_password.value;

        if (length_regex.test(password)) {
            length_req.classList.add("req-satisfied");
        } else {
            length_req.classList.remove("req-satisfied");
        }

        if (lowercase_regex.test(password)) {
            lowercase_req.classList.add("req-satisfied");
        } else {
            lowercase_req.classList.remove("req-satisfied");
        }

        if (number_regex.test(password)) {
            number_req.classList.add("req-satisfied");
        } else {
            number_req.classList.remove("req-satisfied");
        }

        if (uppercase_regex.test(password)) {
            uppercase_req.classList.add("req-satisfied");
        } else {
            uppercase_req.classList.remove("req-satisfied");
        }

        if (special_character_regex.test(password)) {
            special_req.classList.add("req-satisfied");
        } else {
            special_req.classList.remove("req-satisfied");
        }
    });

    const match_req = document.getElementById("match-req");
    check_password.addEventListener("input", () => {
        if (check_password.value === input_password.value) {
            match_req.classList.add("req-satisfied");
        } else {
            match_req.classList.remove("req-satisfied");
        }
    });

    const show_password_buttons = document.getElementsByClassName("password-eye");
    for (const show_password_button of show_password_buttons) {
        show_password_button.addEventListener("click", () => {
            const input = show_password_button.previousElementSibling;
            if (input.type === "password") {
                input.type = "text";
            } else {
                input.type = "password";
            }
        });
    }
});
