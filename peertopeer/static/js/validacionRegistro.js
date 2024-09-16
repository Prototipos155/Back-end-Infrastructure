alumno = document.getElementById("alumno");
tutor = document.getElementById("tutor");

alumno.addEventListener("change", (e) => {
    e.preventDefault();
    if (!alumno.checked) {
        alumno.checked = false;
    }

    tutor.checked = false;
    tutor.required = false;
});

tutor.addEventListener("change", (e) => {
    e.preventDefault();
    if (!tutor.checked) {
        tutor.checked = true;
    }

    alumno.checked = false;
    alumno.required = false;
});