//CANCELACION DE EVENTO SUBMIT
document.querySelector("form").addEventListener("submit", (ev) => {
    // Condición para evitar el envío si no es permitido
    if (ev.detail == null || ev.detail.allowed == null) {
        // Prevenir el envío y disparar el evento click
        ev.preventDefault();
        console.log("Formulario no permitido, disparando click en #siguiente");
        document.getElementById("siguiente").dispatchEvent(new Event("click"));
        return;
    }
    // Si pasa la validación, enviar el formulario (esto podría ser un .submit() si deseas hacerlo manualmente)
    console.log("Formulario enviado correctamente");
    ev.target.submit()
});

// Manejo del click en el botón #enviar
document.getElementById("enviar").addEventListener("click", (ev) => {
    console.log("Botón #enviar clickeado");
    // Disparar el evento submit en el formulario manualmente
    const submitEvent = new CustomEvent('submit', {
        bubbles: true, // Permitir propagación
        cancelable: true, // Permitir prevenir el comportamiento predeterminado
        detail: { allowed: true } // Permitir el envío
    });
    document.querySelector("form").dispatchEvent(submitEvent);
});


document.querySelectorAll("input").forEach(input=>{
    input.addEventListener("change",e=>{
        // console.error("change")
        // e.preventDefault()
        // document.getElementById("siguiente").dispatchEvent(new Event("click"))
    })
    input.addEventListener("keyup",ev=>{
        if(ev.key=='Enter'){
            console.error("change-2")
            document.getElementById("siguiente").dispatchEvent(new Event("click"))
        }
    })
})

//ANIMACION DEL REGISTRO E INICIO DE SESION
console.log("uniste diseño")
let c = 1;
let datos = document.querySelector(".datos");
let transDuration = getComputedStyle(datos).getPropertyValue("--TransitionDuration").split("s")[0] * 1000

for (let boton of document.querySelectorAll(".botones .mover")) {
    console.log(c)
    boton.duracion = transDuration;

    boton.addEventListener("click", e => {
        console.log("click")
        cambiarField(e, 2)
        e.preventDefault()
    })
    boton.direccion = c
    c = -1
}
export let fields = document.querySelectorAll(".datos fieldset")
window.iniciaCambio = false


export function cambiarField(e = null, modo = 1, direccion = null, sigFieldSet = null, duracionAnimando = null) {
    direccion = (direccion == null) ? e.target.direccion : direccion
    //modo:
    // forma de mover el fieldset( animacion)
    //direccion:
    //-1=atras       fieldset----->
    //1=siguiente   <-----fieldset 
    console.log("direccion=",(direccion==1)?"atras":"adelante")   
    if (window.iniciaCambio == true) {
        // alert("ya hay un proceso en curso")
        console.log("ya hay otro proceso en curso")
        return
    }
    duracionAnimando = (duracionAnimando == null) ? e.target.duracion : duracionAnimando;
    // console.log(duracionAnimando)
    window.iniciaCambio = true
    
    let index = obtenerCampoActivo();
    if(direccion!=1){

        let emptyInput=null;
        for(let input of fields[index].querySelectorAll("input")){
            if(input.value==""){
                emptyInput=input;
                break
            }
        }
        if(emptyInput!=null){
            emptyInput.focus()
            window.iniciaCambio = false
            return        
        }
    }
        
    if(!fields[index].checkValidity()){
        alert("Debes responder bien el campo")
        window.iniciaCambio=false
        return
    }
    if(index-direccion>fields.length -1 ){
        document.getElementById("enviar").dispatchEvent(new Event("click"))
        window.iniciaCambio=false
        return 
    }
    if (index - direccion < 0) {
        alert("NO TE SALGAS DE LOS LIMITES")
        window.iniciaCambio = false
        // if( index-direccion>fields.length-1){
        //     document.quer
        // }
        return
    }
    sigFieldSet = (sigFieldSet == null) ? index - direccion : sigFieldSet;

    console.log("index=", index)
    if (direccion == 1 && modo == 1) {
        fields[index].style.translate = "-100%"
        fields[index].offsetHeight;
    }

    fields[sigFieldSet].classList.add("fieldactive")
    if (modo == 2) {
        fields[sigFieldSet].style.translate = `${direccion * -100}%`
        fields[index].offsetHeight;
        fields[index].classList.remove("fieldactive")
    }

    fields[sigFieldSet].classList.add("animacion")
    if (modo == 1) {
        fields[index].classList.add("animacion")
        fields[index].style.translate = (direccion != 1) ? `${direccion * 100}%` : "0";
    }

    setTimeout(e => {
        fields[sigFieldSet].style.translate = (direccion == 1 || modo == 2) ? "0%" : `${direccion * 100}%`;
    }, parseInt(duracionAnimando / 100))
    setTimeout((e) => {
        window.iniciaCambio = false
        if (modo == 1) {
            fields[index].classList.remove("fieldactive")
            fields[index].classList.remove("animacion")
        }
        fields[sigFieldSet].classList.remove("animacion")
        if (direccion == 1 && modo == 1) {
            fields[index].style.translate = ""
        } else {
            fields[sigFieldSet].style.translate = ""
        }
        console.log("sig=",fields[sigFieldSet])
        fields[sigFieldSet].querySelector("input[value=''],input").focus()
    }, parseInt(duracionAnimando))

}
export function obtenerCampoActivo() {
    for (let index = 0; index < fields.length; index++) {
        if (fields[index].classList.contains("fieldactive")) {
            //encontro el fieldset en visualizacion
            return index
        }
    }
    // return -1
}
// let lastInputs=document.querySelectorAll(".derecha .alminp:last-of-type input")
// lastInputs.forEach(element => {
//     element.duerme=transDuration
//     element.onchange=e=>{
//         // e.preventDefault()
//         console.log("change")
//         e.preventDefault()
//         document.getElementById("siguiente").dispatchEvent(new Event("click"))

//         setTimeout(e=>{
//             console.log("vuelto a la vida")
//         },parseInt(e.target.duerme))
//     }
// });
//FIN DE ANIMACION


//MOSTRAR CONTENIDO DE CAMPO CONTRASEÑA
document.querySelectorAll('.mostrar').forEach(button => {
    button.addEventListener('click', function (e) {
        e.preventDefault();

        const input = this.parentNode.querySelector('input');
        const icon = e.target.parentNode.querySelector('img');

        if (input.type === "password") {
            input.type = "text";
            console.log("ver")
            this.style.backgroundImage = `url(/static/fotos/iconos/ver.png)`;
            this.title = "Ocultar";
            if (icon) {
                icon.src = "/static/fotos/iconos/ver.png";
            }
        } else {
            input.type = "password";
            console.log("Ocultar")
            this.style.backgroundImage = `url(/static/fotos/iconos/esconder.png)`;
            this.title = "Mostrar";
            if (icon) {
                icon.src = "/static/fotos/iconos/esconder.png";
            }
        }
    });
});


//FIN DE MOSTRAR CAMPO