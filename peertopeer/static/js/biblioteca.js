let desplegables = document.querySelectorAll(".desplegar")
let targ;
for (let desplegable of desplegables){
    desplegable.addEventListener("click",e=>{
        targ=e;
        menuActual=e.target.parentNode.parentNode.lastElementChild
        console.log(menuActual)
        if(menuActual.checkVisibility()){
            menuActual.style.display="none"
            return
        }
        menuActual.style.display="block"
        if(menuActual.children[0]==undefined){
            alert("no tiene contenido")
        }
        let c=0
        if(e.target.parentNode.classList.contains("categoria")){

            for (let menu of document.querySelectorAll(".menu")){
                if(menu!=menuActual && menu.style.display=="block"){
                    // console.log("menu numero ",c)
                    menu.style.display="none";
                    break
                }
                c+=1
            }
        }
    })
}
let puntosActualmenteSeleccionado=null;

for(let puntos of document.querySelectorAll(".puntos")){
    let salir= new Option()
    salir.addEventListener("click",e=>{
        if(e.stopPropagation){
            e.stopPropagation()
        }
        
        e.target.parentNode.style.display="none"
        if(puntosActualmenteSeleccionado==e.target.parentNode){
            //estamos cerrando el menu actual
            puntosActualmenteSeleccionado=null;
        }
    })
    salir.innerHTML+="Salir"

    puntos.addEventListener("click",e=>{
        if(puntosActualmenteSeleccionado!=null){
            puntosActualmenteSeleccionado.style.display="none"
        }
        
        
        if(e.target.parentNode.lastElementChild.checkVisibility()){
            e.target.parentNode.lastElementChild.style.display="none"
        }else{
            e.target.parentNode.lastElementChild.style.display="block"
        }
        puntosActualmenteSeleccionado=e.target.parentNode.lastElementChild;
    })
    puntos.parentNode.lastElementChild.appendChild(salir)

}