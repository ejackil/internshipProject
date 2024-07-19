const sub_time = (time, diff_minutes) => {
    time = time.split(":");
    let hour = parseInt(time[0]);
    let minutes = parseInt(time[1]);

    let tmp = minutes
    minutes = (minutes - diff_minutes + 60) % 60
    hour += Math.floor((tmp - diff_minutes) / 60)

    return String(hour).padStart(2, "0") + ":" + String(minutes).padStart(2, "0")
}

document.addEventListener("DOMContentLoaded", () => {
    const date_input = document.getElementById("date");
    const time_input = document.getElementById("time");
    const date_group = document.getElementById("date-group");
    const time_group = document.getElementById("time-group");
    const personal_info_group = document.getElementById("personal-info-group");
    const submit_button = document.getElementById("submit");
    const first_name_input = document.getElementById("first-name");
    const last_name_input = document.getElementById("last-name");
    const phone_number_input = document.getElementById("phone-number");
    const inputs = document.querySelectorAll("#create_form input:not([id='submit']), #create_form select");

    const chairs = document.querySelectorAll(".booking-chair-6, .booking-chair-4, .booking-chair-2");
    for (const chair of chairs) {
        chair.style.transform += `rotate(${chair.dataset.angle})`;
    }

    const table_id_input = document.getElementById("table-id");
    const table_display = document.getElementById("booking-info");
    const tables = document.getElementsByClassName("table-container");
    const form = document.getElementById("create_form")

    Array.from(tables).forEach((table, i) => {
        table.addEventListener("click", (e) => {
            e.stopPropagation();

            if (table.classList.contains("table-selected")) {
                return;
            }

            const display_text = table.dataset.interactive ? `Booking for table ${table.dataset.id} (Interactive: +€15.00)` : `Booking for table ${table.dataset.id}`
            table_display.innerHTML = display_text;
            table_id_input.value = table.dataset.id;

            for (other_table of tables) {
                other_table.classList.remove("table-selected");
            }
            table.classList.add("table-selected");

            date_group.hidden = false;
            time_group.hidden = true;
            personal_info_group.hidden = true;
            submit_button.hidden = true;

            date_input.value = "";
            time_input.value = "";
        });
    });

    const table_background = document.getElementById("content");
    table_background.addEventListener("click", () => {
        table_display.innerHTML = "Select a table to begin booking";
        table_id_input.value = "";

        for (other_table of tables) {
            other_table.classList.remove("table-selected");
        }

        date_group.hidden = true;
        time_group.hidden = true;
        personal_info_group.hidden = true;
        submit_button.hidden = true;

        date_input.value = "";
        time_input.value = "";
    });

    date_input.addEventListener("input", async () => {
        time_input.value = "";
        personal_info_group.hidden = true;

         const res = await fetch(
             `/api/bookings/${table_id_input.value}/${date_input.value}`
         );

         const bookings = await res.json();

        for (const time of time_input.children) {
            time.disabled = false;
            time.innerHTML = time.value;

            for (const booking of bookings) {
                if (time.value >= sub_time(booking.start_time, 30) && time.value < booking.end_time) {
                    time.disabled = true;
                    time.innerHTML = `${time.value} (Reserved)`;
                }
            }
        }

        time_group.hidden = false;
    });

    time_input.addEventListener("change", () => {
        personal_info_group.hidden = false;
        submit_button.hidden = false;
    });

    form.addEventListener("click", (e) => {
        e.stopPropagation();
    });

    if (window.sessionStorage.getItem("saved_info") && !window.sessionStorage.getItem("ignore_saved_info")) {
        info = JSON.parse(window.sessionStorage.getItem("saved_info"));

        for (const [id, value] of Object.entries(info)) {
            if (id === "table-id" && value) {
                table = document.querySelector(`.table-container:nth-child(${value})`);
                table.classList.add("table-selected");
            }

            document.getElementById(id).value = value;
        }

        if (info["table-id"]) {
            date_group.hidden = false;
        }
        if (info["date"]) {
            time_group.hidden = false;
        }
        if (info["time"]) {
            personal_info_group.hidden = false;
            submit_button.hidden = false;
        }

        window.sessionStorage.removeItem("saved_info");
    } else if (window.sessionStorage.getItem("ignore_saved_info")) {
        window.sessionStorage.removeItem("saved_info");
        window.sessionStorage.removeItem("ignore_saved_info");
    }

    form.addEventListener("submit", () => {
        window.sessionStorage.setItem("ignore_saved_info", true)
    });

    window.addEventListener("pagehide", (e) => {
        saved_info = {};
        for (const input of inputs) {
            saved_info[input.id] = input.value;
        }

        window.sessionStorage.setItem("saved_info", JSON.stringify(saved_info));
    });
});