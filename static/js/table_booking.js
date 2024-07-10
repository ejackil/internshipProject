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

    const chairs = document.getElementsByClassName("booking-chair");
    for (const chair of chairs) {
        chair.style.transform += `rotate(${chair.dataset.angle})`;
    }

    const table_id_input = document.getElementById("table-id");
    const table_display = document.getElementById("booking-info");
    const tables = document.getElementsByClassName("table-container");

    Array.from(tables).forEach((table, i) => {
        table.addEventListener("click", (e) => {
            e.stopPropagation();

            if (table.classList.contains("table-selected")) {
                return;
            }

            table_display.innerHTML = `Booking for table ${i + 1}`;
            table_id_input.value = i;

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

    const table_background = document.getElementById("tables");
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

    date_input.addEventListener("change", async () => {
        time_input.value = "";
        personal_info_group.hidden = true;

         const res = await fetch(
             `/api/bookings/${table_id_input.value}?`
             + new URLSearchParams({date: date_input.value})
         );

         const bookings = await res.json();

        for (const time of time_input.children) {
            time.disabled = false;
            time.innerHTML = time.value;

            for (const booking of bookings) {
                if (time.value >= booking.start_time && time.value <= booking.end_time) {
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
});