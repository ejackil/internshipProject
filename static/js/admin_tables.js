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
    const chairs = document.querySelectorAll(".booking-chair-6, .booking-chair-4, .booking-chair-2");
    for (const chair of chairs) {
        chair.style.transform += `rotate(${chair.dataset.angle})`;
    }
});
