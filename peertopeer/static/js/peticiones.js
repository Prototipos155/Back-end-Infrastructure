const selectTipo = document.getElementById("tipo");
const categoriaTemaDiv = document.getElementById("categoria_tema");

selectTipo.addEventListener("change", () => {
    if (selectTipo.value === "tema") {
        categoriaTemaDiv.hidden = false;
    } else {
        categoriaTemaDiv.hidden = true;
    }
});

