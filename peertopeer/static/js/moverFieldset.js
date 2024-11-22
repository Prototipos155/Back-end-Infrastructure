import {obtenerCampoActivo,cambiarField,fields} from './diseño.js'

console.log(cambiarField)
console.log(fields)
const casillaError = document.querySelector('meta[name="casilla-de-error"]').getAttribute('content');
// (e=null, modo = 1,direccion=null, sigFieldSet=null
let cmpActivo=obtenerCampoActivo()

let fieldConError=fields[casillaError].querySelector(".error")
if(fieldConError){
    let mensaje = document.querySelector('meta[id="mensajeFieldset"]');
    if (mensaje){
        fieldConError.innerText = mensaje.getAttribute("content");
        alert(fieldConError.innerText);
        // console.log(fieldConError.innerText)
    }
}


if(casillaError!=cmpActivo){

    let dir=(casillaError<cmpActivo)?1:-1;
    console.log("actual=",cmpActivo)
    console.error("avanza hacia ",dir)
    console.error("error en fieldset ",casillaError)
    cambiarField(null,2,dir, casillaError,1000)
}