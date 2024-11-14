let desplegables = document.querySelectorAll(".desplegar")
let targ;
for (let desplegable of desplegables){
    desplegable.addEventListener("click",e=>{
        targ=e;
        console.log(e.target.parentNode.lastElementChild)
        if(e.target.parentNode.lastElementChild.checkVisibility()){
            e.target.parentNode.lastElementChild.style.display="none"
            return
        }
        e.target.parentNode.lastElementChild.style.display="block"
    })
}