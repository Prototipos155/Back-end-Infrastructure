let desplegables = document.querySelectorAll(".desplegar")
let targ;
for (let desplegable of desplegables){
    desplegable.addEventListener("click",e=>{
        targ=e;
        menuActual=e.target.parentNode.lastElementChild
        console.log(menuActual)
        if(menuActual.checkVisibility()){
            menuActual.style.display="none"
            return
        }
        menuActual.style.display="block"
        if(menuActual.children[0]==undefined){
            alert("no tiene temas")
        }
        let c=0
        for (let menu of document.querySelectorAll(".menu")){
            if(menu!=menuActual && menu.style.display=="block"){
                console.log("menu numero ",c)
                menu.style.display="none";
                break
            }
            c+=1
        }
    })
}

for(let puntos of document.querySelectorAll(".puntos")){
    puntos.addEventListener("click",e=>{
        e.parentNode.lastElementChild.style.display="block"
    })
}