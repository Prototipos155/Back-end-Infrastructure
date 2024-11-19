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

  socketio.on("mensaje", (data) => {
    console.log("Mensaje recibido: ", data);
    crearMensaje(data.nombre, data.mensaje);
  });

  function enviarMensaje() {
    const mensajeInput = document.getElementById("mensaje");
    const mensaje = mensajeInput.value.trim()

    if (mensaje === "") return;
    socketio.emit("mensaje", { nombre: "Tu", mensaje });
    crearMensaje("Tu", mensaje);
    mensajeInput.value = "";
  }
  const btnEnviar = document.getElementById("btnEnviar");

  if (!btnEnviar){
    console.error("El boton Enviar no se encontro en el DOM")
    return
  }

  btnEnviar.addEventListener("click", enviarMensaje);
});



document.addEventListener("DOMContentLoaded", () => {
  const mensajesData = document.getElementById("mensajes-data");

  if (mensajesData) {
    const mensajes = JSON.parse(mensajesData.dataset.mensajes);

    mensajes.forEach((mensaje) => {
      crearMensaje(mensaje.nombre, mensaje.mensaje);
    });
  }
});
