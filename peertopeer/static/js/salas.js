document.addEventListener("DOMContentLoaded", () => {

  const socketio = io("https://127.0.0.1:5000", {
    transports: ["websocket", "polling"]
  });

  function crearMensaje(nombre, mensaje) {
    const mensajes = document.getElementById("mensajes");
    const contenido = `
      <div class="text">
          <span><strong>${nombre}</strong>: ${mensaje}</span>
          <span class="muted">${new Date().toLocaleString()}</span>
      </div>
      `;
    mensajes.insertAdjacentHTML("beforeend", contenido);
  };

  socketio.on("message", (data) => {
    console.log("Mensaje recibido: ", data);
    crearMensaje(data.nombre, data.mensaje);
  });

  function enviarMensaje(ev){
    ev.preventDefault();
    if(!ev.target.checkValidity()){
      alert("llena bien el campo de mensaje")
      return
    }

    const mensajeInput = document.getElementById("mensaje");
    const mensaje = mensajeInput.value.trim()

    if (mensaje === "") return;
    socketio.emit("message", { "nombre": "Tú", "mensaje": mensaje });
    //crearMensaje("Tú", mensaje);
    mensajeInput.value = "";
  }
  // const btnEnviar = document.getElementById("btnEnviar");
  const btnEnviar = document.getElementById("form-enviar");

  if (!btnEnviar){
    console.error("El boton Enviar no se encontro en el DOM")
    return
  }

  // btnEnviar.addEventListener("click", enviarMensaje);
  btnEnviar.addEventListener("submit", enviarMensaje);
});



document.addEventListener("DOMContentLoaded", () => {
  const mensajesData = document.getElementById("mensajes-container");

  if (mensajesData) {
    const mensajes = JSON.parse(mensajesData.dataset.mensajes);

    mensajes.forEach((mensaje) => {
      crearMensaje(mensaje.nombre, mensaje.mensaje);
    });
  }
});
