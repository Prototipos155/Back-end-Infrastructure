const socket = io('ws://localhost:3500')

const nombreInput = document.querySelector('#nombre')
const mensajeInput = document.querySelector('#mensaje')
const chatForo = document.querySelector('#foro')
const unirse = document.querySelector('.unirse')
const listaUsuarios = document.querySelector('.lista_usuarios')
const listaForo = document.querySelector('.lista_foro')
const actividad = document.querySelector('.actividad')

function enviarMensaje(e){
    e.preventDefault()
    if(nombreInput.value && mensajeInput.value && chatForo.value){
        socket.emit('mensaje',{
            "nombre":nombreInput.value,
            "texto": mensajeInput.value
        } )
        mensajeInput.value = ""
    }
    mensajeInput.focus()
}

function entrarForo(e){
    e.preventDefault()
    if(nombreInput.value && chatForo.value){
        socket.emit('entrarForo', {
           "nombre":nombreInput.value,
            "foro" : chatForo.value
        })
    }
}

document.querySelector('.form-unirse')
.addEventListener('submit', entrarForo)

document.querySelector('.form-mensaje')
.addEventListener('submit', enviarMensaje)

mensajeInput.addEventListener('clicktecla',() => {
    socket.emit('actividad', nombreInput.value)
})

socket.on("message", (data) => {
    actividad.textContent = ""
    const li = document.createElement('li')
    li.textContent = data
    document.querySelector('ul'.appendChild(li))
})