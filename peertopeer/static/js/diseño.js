console.log("uniste diseño")
let c=1;
    for(let boton of document.querySelectorAll(".botones .mover")){
        console.log(c)
        boton.onclick=(e)=>{
            e.preventDefault()
            console.log("click")
            cambiarField(e,2)
        }
        boton.direccion=c
        c=-1
    }
    let fields=document.querySelectorAll(".datos fieldset")
    window.iniciaCambio=false
    
    function cambiarField(e,modo=1){
        if(window.iniciaCambio==true){
            alert("ya hay un proceso en curso")
            return
        }
        window.iniciaCambio=true
        direccion=e.target.direccion
        //0=atras       fieldset----->
        //1=siguiente   <-----fieldset        
        
        let index=0;
        for (index;index<fields.length;index++){
            if(fields[index].classList.contains("fieldactive")){
                //encontro el fieldset en visualizacion
                break
            }
        }

        if(index-direccion <0 || index-direccion>fields.length-1){
            alert("NO TE SALGAS DE LOS LIMITES")
            window.iniciaCambio=false
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