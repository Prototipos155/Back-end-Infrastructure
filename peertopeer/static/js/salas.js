var socketio = io();

  const mensajes = document.getElementById("mensajes");

  const crearMensaje = (nombre, mensaje) => {
    const contenido = `
      <div class="texto">
          <span>
              <strong>${nombre}</strong>: ${mensaje}
          </span>
          <span class="sordear">
              ${new Date().toLocaleString()}
          </span>
      </div>
      `;
    mensajes.innerHTML += contenido;
  };

  socketio.on("mensaje", (datos) => {
    crearMensaje(datos.nombre, datos.mensaje);
  });

  const enviarMensaje = () => {
    const mensaje = document.getElementById("mensaje");
    if (mensaje.value == "") return;
    socketio.emit("mensaje", { data: mensaje.value });
    mensaje.value = "";
  };