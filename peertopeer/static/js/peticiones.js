const selectTipo = document.getElementById("tipo");
const categoria = document.getElementById("categoria");
const categoriaTemaDiv = document.getElementById("categoria_tema");
const categoria_subtema = document.getElementById("categoria_subtema");

selectTipo.addEventListener("change", () => {
    if (selectTipo.value === "tema") {
        categoria.hidden = false;
        categoriaTemaDiv.hidden = false;
        categoria_subtema.hidden = true;

    } else if (selectTipo.value === "subtema") {
        categoria.hidden = false;
        categoriaTemaDiv.hidden = true;
        categoria_subtema.hidden = false;

    } else {
        categoria.hidden = true;
    }
});

const buscador = document.getElementById('buscador');
const lista = document.querySelectorAll('#lista option');

buscador.addEventListener('input', function () {
    const filter = buscador.value.toLowerCase();
    lista[0].selected = true;
    lista.forEach(item => {
        const texto = item.textContent.toLowerCase();
        if (texto.includes(filter)) {
            item.hidden = false;
        } else {
            item.hidden = true;
        }
    })
})

//const selectTipo1 = document.getElementById("tipo");

/*selectTipo1.addEventListener("change", () => {
    if (selectTipo1.value === "subtema") {
        categoria_subtema.hidden = false;
    } else {
        categoria_subtema.hidden = true;
    }
});*/