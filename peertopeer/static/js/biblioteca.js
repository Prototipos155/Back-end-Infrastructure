let desplegables = document.querySelectorAll(".desplegar")
let targ;
let cerrarTodo=true;

for (let desplegable of desplegables){
    desplegable.addEventListener("click",e=>{
        targ=e;
        if(e.target.parentNode.parentNode.lastElementChild.children[0]==undefined){
            alert("no tiene contenido")
            return
        }
        menuActual=e.target.parentNode.parentNode.lastElementChild
        console.log(menuActual.children[0])
        if(menuActual.checkVisibility()){
            menuActual.classList.add("esconder")
            menuActual.classList.remove("mostrar-2")
            return
        }
        menuActual.classList.remove("esconder")
        menuActual.classList.add("mostrar-2")
        let c=0
        if(e.target.parentNode.classList.contains("categoria")){
            console.log("tocaste una categoria")
            for (let menu of document.querySelectorAll(".menu.menu-categoria")){
                if(menu!=menuActual && menu.style.display=="block"){
                    // console.log("menu numero ",c)
                    console.log("toca esconder a ",menu)
                    menu.classList.add("esconder");
                    menu.classList.remove("mostrar-2");
                    
                    if(cerrarTodo){
                        menu.parentNode.querySelectorAll(".menu").forEach(item=>{
                            item.classList.add("esconder");
                            item.classList.remove("mostrar-2");
                        })
                    }
                    break
                }
                // c+=1
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
        
        e.target.parentNode.classList.add("esconder")
        e.target.parentNode.classList.remove("mostrar-2")
        if(puntosActualmenteSeleccionado==e.target.parentNode){
            //estamos cerrando el menu actual
            puntosActualmenteSeleccionado=null;
        }
    })
    salir.innerHTML+="Salir"

    puntos.addEventListener("click",e=>{
        if(puntosActualmenteSeleccionado!=null){
            puntosActualmenteSeleccionado.classList.add("esconder")
            puntosActualmenteSeleccionado.classList.remove("mostrar-2")
        }
        
        
        if(e.target.parentNode.lastElementChild.checkVisibility()){
            e.target.parentNode.lastElementChild.classList.add("esconder")
            e.target.parentNode.lastElementChild.classList.remove("mostrar-2")
        }else{
            e.target.parentNode.lastElementChild.classList.remove("esconder")
            e.target.parentNode.lastElementChild.classList.add("mostrar-2")
        }
        puntosActualmenteSeleccionado=e.target.parentNode.lastElementChild;
    })
    puntos.parentNode.lastElementChild.appendChild(salir)
}


document.querySelector(".buscador input").addEventListener("keyup",key=>{
    let buscando=key.target.value;
    console.log("esta buscando a '"+buscando+"'")
    // si esta en blanco hay que mostrar todo
    // si es puro texto hay que buscar en todos los option
    // si lleva algunos guinones medios hay que buscar siguiendo el patron:
        // categoria-subcategoria-tema
    // document.querySelectorAll(".opciones").forEach(opcion=>{
    //     if(key.target.value=="" || (opcion.innerText.trim().includes(buscando))){
    //         if(opcion.parentNode.matches(".esconder-opcion")){
    //             opcion.parentNode.classList.remove("esconder-opcion")
    //         }
    //         if(opcion.checkVisibility()==false){
    //             //esta oculto, por lo que uno de sus padres tiene display none
    //             opcion.padreCategoria.classList.add("esconder")
    //         }
    //     }else{
    //         opcion.parentNode.classList.add("esconder-opcion")
    //     }
    // })

    document.querySelectorAll(".menu-categoria").forEach(categoria =>{
        let opcionEncontrada=false
        categoria.querySelectorAll(".opciones").forEach(opcion=>{
            if(buscando=="" || opcion.innerText.trim().toLocaleLowerCase().includes(buscando)){
                opcionEncontrada=true
                opcion.parentNode.classList.remove("esconder-opcion")
            }else{
                opcion.parentNode.classList.add("esconder-opcion")
            }
        })
        if(buscando==""){
            categoria.parentNode.classList.remove("mostrar-opcion")
            categoria.parentNode.classList.remove("esconder-opcion")
        }else if(opcionEncontrada==false && !categoria.parentNode.children[0].innerText.trim().toLocaleLowerCase().includes(buscando)){
            //ni el ni sus hijos tienen lo que el usuario busca
            categoria.parentNode.classList.add("esconder-opcion")
            categoria.parentNode.classList.remove("mostrar-opcion")
        }else if(!categoria.checkVisibility()){
            categoria.parentNode.classList.add("mostrar-opcion")
            categoria.parentNode.classList.remove("esconder-opcion")
        }
    })
})

document.querySelectorAll(".opciones").forEach(opcion=>{
    if(opcion.parentNode.parentNode.parentNode.matches(".menu-categoria")){
        opcion.padreCategoria=opcion.parentNode.parentNode.parentNode
    }else{
        opcion.padreCategoria=opcion.parentNode.parentNode.parentNode.parentNode.parentNode
    }
})