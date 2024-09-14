alumno = document.getElementById("alumno");
tutor = document.getElementById("tutor");
numTarjBien = document.getElementById("tarjetabien");
inpTarjetaBien = document.getElementById("numTarjetaBien");

alumno.addEventListener("change", (e) => {
    e.preventDefault();
    if (!alumno.checked) {
        alumno.checked = true;
    }

    tutor.checked = false;
    inpTarjetaBien.required = false;
    numTarjBien.hidden = true;
    tutor.required = false;
});

tutor.addEventListener("change", (e) => {
    e.preventDefault();
    if (!tutor.checked) {
        tutor.checked = true;
    }

    alumno.checked = false;
    alumno.required = false;
    inpTarjetaBien.required = true;
    numTarjBien.hidden = false;
});