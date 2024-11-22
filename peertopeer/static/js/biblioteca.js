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
        // console.log(menuActual.children[0])
        if(menuActual.checkVisibility()){
            ocultarMenu(menuActual,false)
            // menuActual.classList.add("esconder")
            // menuActual.classList.remove("mostrar-2")
            return
        }
        ocultarMenu(menuActual,true)
        // menuActual.classList.remove("esconder")
        // menuActual.classList.add("mostrar-2")
        let c=0
        if(e.target.parentNode.classList.contains("categoria")){
            // console.log("tocaste una categoria")
            for (let menu of document.querySelectorAll(".menu.menu-categoria")){
                if(menu!=menuActual && menu.style.display=="block"){
                    // console.log("menu numero ",c)
                    // console.log("toca esconder a ",menu)
                    ocultarMenu(menu,false)
                    // menu.classList.add("esconder");
                    // menu.classList.remove("mostrar-2");
                    
                    if(cerrarTodo){
                        menu.parentNode.querySelectorAll(".menu").forEach(item=>{
                            ocultarMenu(item,false)
                            // item.classList.add("esconder");
                            // item.classList.remove("mostrar-2");
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
    let buscando=key.target.value.toLocaleLowerCase();
    // console.error("esta buscando a '"+buscando+"'")
    // si esta en blanco hay que mostrar todo
    // si es puro texto hay que buscar en todos los option
    // si lleva algunos guinones medios hay que buscar siguiendo el patron:
        // categoria-subcategoria-tema
    // document.querySelectorAll(".menu-categoria").forEach(categoria =>{
    //     let opcionEncontrada=false
    //     let temaEncontrado=[];
    //     categoria.querySelectorAll(".opciones").forEach(opcion=>{
    //         // console.log("opcion=",opcion)
    //         if(buscando=="" || opcion.innerText.trim().toLocaleLowerCase().includes(buscando)){
    //             opcionEncontrada=true
    //             opcion.parentNode.classList.remove("esconder-opcion")
    //             desbloquearPadre(opcion,true)
    //             temaEncontrado.push(opcion.padreCategoria)
    //             // console.log("orgullo:",opcion.padreCategoria)
    //         }else{
    //             opcion.parentNode.classList.add("esconder-opcion")
    //             if(!temaEncontrado.includes(opcion.padreCategoria)){
    //                 desbloquearPadre(opcion,false)
    //                 // console.log("deshonra:",opcion.padreCategoria)
    //             }
    //         }
    //     })
    //     // console.log("_____opcion encontrada?=",opcionEncontrada)
    //     if(buscando==""){
    //         categoria.parentNode.classList.remove("mostrar-opcion")
    //         categoria.parentNode.classList.remove("esconder-opcion")
    //         // console.log("deberia de reiniciar")
    //     }else if(opcionEncontrada==false && !categoria.parentNode.children[0].innerText.trim().toLocaleLowerCase().includes(buscando)){
    //         //ni el ni sus hijos tienen lo que el usuario busca
    //         // console.log("ni la categoria ni sus hijas tienen lo que busco")
    //         categoria.parentNode.classList.add("esconder-opcion")
    //         categoria.parentNode.classList.remove("mostrar-opcion")
    //     }else if(!categoria.parentNode.checkVisibility()){
    //         // console.log("deberia de aparecer la categoria")
    //         categoria.parentNode.classList.add("mostrar-opcion")
    //         categoria.parentNode.classList.remove("esconder-opcion")
    //     }else{
    //         // console.log("Que verga?")
    //         categoria.parentNode.classList.add("mostrar-opcion")
    //     }
    // })
    
    // if(buscando==""){
    // }
    document.querySelector(".materias").querySelectorAll(".ocultar,.mostrar-2").forEach(item=>{
        item.classList.remove("ocultar")
        item.classList.remove("mostrar-2")
    })
    
    document.querySelectorAll(".menu-categoria").forEach(categoria =>{
        let opcionEncontrada=false
        let temaEncontrado=[];
        
        opcionEncontrada=(buscarIncidencia(categoria.parentNode,buscando))
       
        // console.error(opcionEncontrada)
        // categoria.querySelectorAll(".opciones").forEach(opcion=>{
        //     // console.log("opcion=",opcion)
        //     if(buscando=="" || opcion.innerText.trim().toLocaleLowerCase().includes(buscando)){
        //         opcionEncontrada=true
        //         opcion.parentNode.classList.remove("esconder-opcion")
        //         desbloquearPadre(opcion,true)
        //         temaEncontrado.push(opcion.padreCategoria)
        //         // console.log("orgullo:",opcion.padreCategoria)
        //     }else{
        //         opcion.parentNode.classList.add("esconder-opcion")
        //         if(!temaEncontrado.includes(opcion.padreCategoria)){
        //             desbloquearPadre(opcion,false)
        //             // console.log("deshonra:",opcion.padreCategoria)
        //         }
        //     }
        // })
        // console.log("_____opcion encontrada?=",opcionEncontrada)
        if(buscando==""){
            categoria.parentNode.classList.remove("mostrar-opcion")
            categoria.parentNode.classList.remove("esconder-opcion")
            // console.log("deberia de reiniciar")
        }else if(opcionEncontrada==false && !categoria.parentNode.children[0].innerText.trim().toLocaleLowerCase().includes(buscando)){
            //ni el ni sus hijos tienen lo que el usuario busca
            // console.log("ni la categoria ni sus hijas tienen lo que busco")
            categoria.parentNode.classList.add("esconder-opcion")
            categoria.parentNode.classList.remove("mostrar-opcion")
        }else if(!categoria.parentNode.checkVisibility()){
            // console.log("deberia de aparecer la categoria")
            categoria.parentNode.classList.add("mostrar-opcion")
            categoria.parentNode.classList.remove("esconder-opcion")
        }else{
            // console.log("Que verga?")
            categoria.parentNode.classList.add("mostrar-opcion")
        }
    })
})
function buscarIncidencia(ObjetoLi,buscando){
    let opcionEncontrada=false;
    let hijosExitosos=false;

    // console.log("objeto Li antes de .menu=?",ObjetoLi)
    // console.log("h5?=",ObjetoLi.children[0].children[0])
    // ObjetoLi.children[0]=>div .main-menu
    // ObjetoLi.children[1]=>objeto .menu
    // opcion=> objetosLi de un nivel mas abajo
    // console.log("-------TxT=",ObjetoLi.children[0].children[0].innerText.trim() ,"????",buscando)
    if(buscando=="" || ObjetoLi.children[0].children[0].innerText.trim().toLocaleLowerCase().includes(buscando)){
        opcionEncontrada=true 
        // console.log("SI")
        // aqui se analiza el <h5>
        // console.log("exito para",ObjetoLi.children[0])
        
        ocultarMenu(ObjetoLi.children[0],true)
        
        // console.log(opcionEncontrada," en ",ObjetoLi.children[0])
    }
    // else if(ObjetoLi.children[0].checkVisibility()){
    //     // console.log("NO")
    //     //aqui se analiza el <div .main-opciones>
    //     // console.log("fracaso para",ObjetoLi.children[0])
    //     ocultarMenu(ObjetoLi.children[0],false)

    // }
    if(ObjetoLi.children[1]==undefined){
        // console.log("llegaste al fin de los menus en este tema y es (",opcionEncontrada,")")
        if(!opcionEncontrada){
            ocultarMenu(ObjetoLi.children[0],false)
        }

        return opcionEncontrada;
    }
    if(ObjetoLi.children[1].matches(".menu") ){

        for(let opcion of ObjetoLi.children[1].children){
            // console.log(opcion)
            // console.log("menu?=",ObjetoLi.children[1])
            // opcion=> Objetoli
            if(buscarIncidencia(opcion,buscando)){
                // es padre de mas opciones
                hijosExitosos=true
            }
        }
    }
    // console.log("TEXTO =",ObjetoLi.children[0].children[0].innerText.trim().toLocaleLowerCase())

    // console.log("HIJOS EXITOSOS?",hijosExitosos)
    // console.log("Este ObjetoLi contiene al buscado?",opcionEncontrada)
    if(hijosExitosos){
        opcionEncontrada=true;
        ocultarMenu(ObjetoLi,true)
    }

    if (!hijosExitosos && !opcionEncontrada){
        // console.log(ObjetoLi)
        // console.log(ocultarMenu(ObjetoLi,false))
        ObjetoLi.classList.add("esconder-opcion")
        ObjetoLi.classList.remove("mostrar-opcion")
        ObjetoLi.classList.remove("mostrar-2")
        // ocultarMenu(ObjetoLi,false)
    }else if(opcionEncontrada && !hijosExitosos){
        ocultarMenu(ObjetoLi,true)
    }
    return opcionEncontrada
}

function ocultarMenu(menu, visible){
    // console.log(menu)
    if(visible){
        if(!menu.checkVisibility() && !menu.classList.contains("mostrar-2")){
            menu.classList.add("mostrar-2")
        }
        if(menu.classList.contains("esconder-opcion")){
            menu.classList.remove("esconder-opcion")
        }
        menu.classList.remove("ocultar")
        return 1
    }else if(!visible){
        if(menu.checkVisibility() && menu.classList.contains("mostrar-2")){
            menu.classList.remove("mostrar-2")
        }
        if(menu.classList.contains("mostrar-opcion")){
            menu.classList.remove("mostrar-opcion")
        }
        // if(classList)
        menu.classList.add("ocultar")
        return 2
    }
    return 0
}

document.querySelectorAll(".opciones").forEach(opcion=>{
    // if(opcion.parentNode.parentNode.parentNode.matches(".menu-categoria")){
    //     opcion.padreCategoria=opcion.parentNode.parentNode.parentNode
    // }else{
    //     opcion.padreCategoria=opcion.parentNode.parentNode.parentNode.parentNode.parentNode
    // }
    opcion.padreCategoria=opcion.parentNode.parentNode.parentNode
})

function desbloquearPadre(elemento,mostrar){
    if(!elemento.padreCategoria.parentNode.checkVisibility() && mostrar){
        elemento.padreCategoria.parentNode.classList.remove("esconder-opcion")
        elemento.padreCategoria.parentNode.classList.add("mostrar-opcion")
    }else if (elemento.padreCategoria.parentNode.checkVisibility() && !mostrar){
        elemento.padreCategoria.parentNode.classList.add("esconder-opcion")
        elemento.padreCategoria.parentNode.classList.remove("mostrar-opcion")
    }
}