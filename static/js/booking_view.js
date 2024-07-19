document.addEventListener("DOMContentLoaded", () => {
    const booking_popup = document.getElementById("popup");
    const show_popup = async (event, booking_id) => {
        booking_popup.style.left = `${event.pageX}px`;
        booking_popup.style.top = `${event.pageY}px`;

        const res = await fetch(`/api/booking/${booking_id}`);
        const reservation_info = await res.json();

        document.getElementById("popup-reservation-id").innerHTML = booking_id;
        document.getElementById("popup-time").innerHTML = reservation_info["start_time"] + " - " + reservation_info["end_time"];
        document.getElementById("popup-name").innerHTML = reservation_info["name"] ? reservation_info["name"] : "&lt;Deleted User&gt;";
        document.getElementById("popup-phone-number").innerHTML = reservation_info["phone_number"];

        booking_popup.hidden = false;
    }

    document.getElementById("content").addEventListener("click", () => {
        booking_popup.hidden = true;
    });

    document.getElementById("popup-close-button").addEventListener("click", () => {
        booking_popup.hidden = true;
    });

    // without this, clicking on the popup would make it disappear
    document.getElementById("popup").addEventListener("click", (e) => {
        e.stopPropagation();
    });

    const booking_squares = document.getElementsByClassName("booked")
    Array.from(booking_squares).forEach((booking_square) => {
        booking_square.addEventListener("click", (e) => {
            e.stopPropagation()
            show_popup(e, booking_square.dataset.id)
        });
    });
});
