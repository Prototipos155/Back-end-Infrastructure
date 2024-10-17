const filas = document.getElementsByName("fila");
const botonX = document.querySelector(".cleanBar");

botonX.addEventListener("click", () => {
    document.getElementById("buscador").value = "";
    filas.forEach (fila => {
        fila.classList.remove("filtro");
    })
    botonX.classList.add("cleanBar");
})

document.addEventListener("keyup", (e) => {
    if (e.target.matches('#buscador')) {

        filas.forEach( fila => {
        let data = `${fila.children[0].innerText} ${fila.children[2].innerText} ${fila.children[3].innerText}`; 

        data.toLowerCase().includes(e.target.value.toLowerCase()) 
        ? fila.classList.remove("filtro") 
        : fila.classList.add("filtro");

        botonX.style.display = e.target.value ? botonX.classList.remove("cleanBar") : botonX.classList.add("cleanBar");
        })
    }
})