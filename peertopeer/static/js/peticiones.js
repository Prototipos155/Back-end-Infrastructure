const selectTipo = document.getElementById("tipo");
const categoriaTemaDiv = document.getElementById("categoria_tema");

selectTipo.addEventListener("change", () => {
    if (selectTipo.value === "tema") {
        categoriaTemaDiv.hidden = false;
    } else {
        categoriaTemaDiv.hidden = true;
    }
});

const buscador = document.getElementById('buscador');
const lista = document.querySelectorAll('#lista li');

buscador.addEventListener('input', function () {
    const filter = buscador.ariaValueMax.toLowerCase();
    lista.forEach(item => {
        const texto = item.textContent.toLowerCase();
        if (texto.includes(filter)) {
            item.classList.remove('hidden');
        } else {
            item.classList.add('hidden');
        }
    })
})

const selectTipo1 = document.getElementById("tipo");
const categoria_subtema = document.getElementById("categoria_subtema");

selectTipo1.addEventListener("change", () => {
    if (selectTipo1.value === "subtema") {
        categoria_subtema.hidden = false;
    } else {
        categoria_subtema.hidden = true;
    }
});