console.log("uniste diseño")
let c=1;
for(let boton of document.querySelectorAll(".botones .mover")){
    console.log(c)
    boton.addEventListener("click",e=>{
        e.preventDefault()
        console.log("click")
        cambiarField(e,2)
    })
    // boton.addEventListener("dblclick",e=>{
    //     e.preventDefault()
        // let terminar=false;
        // while (!terminar){
        //     let skip=prompt("Cuantas paginas desea saltar?")
        //     mover=(direccion==0)?-1:1;
        //     mover=fields.length+(skip*mover)
        //     if(accion<0 || accion > fields.length-1){
        //         alert("se sale de los limites")
        //     }else{
        //         terminar=true
        //     }
        // }
    // })
    boton.direccion=c
    c=-1
}
let fields=document.querySelectorAll(".datos fieldset")
window.iniciaCambio=false


function cambiarField(e,modo=1){
    direccion=e.target.direccion
    //0=atras       fieldset----->
    //1=siguiente   <-----fieldset    
    if(window.iniciaCambio==true){
        // alert("ya hay un proceso en curso")
        
        return
    }
    window.iniciaCambio=true
    
    let index=obtenerCampoActivo();
    

    if(index-direccion <0 || index-direccion>fields.length-1){
        alert("NO TE SALGAS DE LOS LIMITES")
        window.iniciaCambio=false
        // if( index-direccion>fields.length-1){
        //     document.quer
        // }
        return
    }

    console.log("index=",index)
    if(direccion==1 && modo==1){
        fields[index].style.translate="-100%"
        fields[index].offsetHeight;
    }
    
    fields[index-direccion].classList.add("fieldactive")
    if(modo==2){
        fields[index-direccion].style.translate=`${direccion*-100}%`
        fields[index].offsetHeight;
        fields[index].classList.remove("fieldactive")
    }
    
    fields[index-direccion].classList.add("animacion")
    if(modo==1){
        fields[index].classList.add("animacion")
        fields[index].style.translate=(direccion!=1)?`${direccion*100}%`:"0";
    }

    setTimeout(e=>{
        fields[index-direccion].style.translate=(direccion==1 || modo==2)?"0%":`${direccion*100}%`;
    },50)
    setTimeout((e)=>{
        window.iniciaCambio=false
        if(modo==1){
            fields[index].classList.remove("fieldactive")
            fields[index].classList.remove("animacion")
        }
        fields[index-direccion].classList.remove("animacion")
        if(direccion==1 && modo==1){
            fields[index].style.translate=""
        }else{
            fields[index-direccion].style.translate=""
        }
    },2100)

}
function obtenerCampoActivo(){
    for (let index=0;index<fields.length;index++){
        if(fields[index].classList.contains("fieldactive")){
            //encontro el fieldset en visualizacion
            return index
        }
    }
    // return -1
}