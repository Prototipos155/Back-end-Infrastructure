const form = document.getElementById("form-registro");
const niveles = document.getElementsByName("nivel");
const nombres = document.getElementById("nombres");
const apellidos = document.getElementById("apellidos");
const apodo = document.getElementById("apodo");
const telefono = document.getElementById("telefono");
const correo = document.getElementById("correo");
const contraseña = document.getElementById("contraseña");
const confirmcontra = document.getElementById("confirmcontra");

window.onload = () => {form.addEventListener("submit", (e) => {
    e.preventDefault();

    if (validarFormulario()) {
        form.submit();
    }
})};

function validarFormulario() {
    let valido = true;
    const nombresRegex = /[^a-zA-Z\s]/;
    const apodoRegex = /[^\w.-]/;
    const correoRegex = /^[\w.]+@[a-zA-Z0-9]+\.+[a-zA-Z.]{1,}$/;
    const contraseñaRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!#.-])([\w!#.-]|[^\s]){8,}$/;

    if (!niveles[0].checked && !niveles[1].checked && !niveles[2].checked) {
        valido = false;
        if (!document.getElementById("msgNivel")) {
            let msgNivel = document.createElement('span');
            msgNivel.id = "msgNivel";
            msgNivel.className = "msgsValidaciones";
            msgNivel.textContent = "Debe escoger un nivel";
            form.children["role-selection"].parentNode.insertBefore(msgNivel, form.children["role-selection"]);
        }

    } else if (document.getElementById("msgNivel")) {
        document.getElementById("msgNivel").remove();
    }

    if (nombres.value.trim() == '' || nombres.value.trim().length < 3 || nombres.value.trim().length > 50 
        || nombresRegex.test(nombres.value.trim())) {
        valido = false;
        if (!document.getElementById("msgNombres")) {
            let msgNombres = document.createElement('span');
            msgNombres.id = "msgNombres";
            msgNombres.className = "msgsValidaciones";
            msgNombres.textContent = "Campo obligatorio, debe contener entre 3 y 50 caracteres, sin caracteres especiales";
            form.children["nombres"].parentNode.insertBefore(msgNombres, form.children["nombres"]);
        }

    } else if (document.getElementById("msgNombres")) {
        document.getElementById("msgNombres").remove();
    }

    if (apellidos.value.trim() == '' || apellidos.value.trim().length < 3 || apellidos.value.trim().length > 50 
        || nombresRegex.test(apellidos.value.trim())) {
        valido = false;
        if (!document.getElementById("msgApellidos")) {
            let msgApellidos = document.createElement('span');
            msgApellidos.id = "msgApellidos";
            msgApellidos.className = "msgsValidaciones";
            msgApellidos.textContent = "Campo obligatorio, debe contener entre 3 y 50 caracteres, sin caracteres especiales";
            form.children["apellidos"].parentNode.insertBefore(msgApellidos, form.children["apellidos"]);
        }

    } else if (document.getElementById("msgApellidos")) {
        document.getElementById("msgApellidos").remove();
    }

    if (apodo.value.trim() == '' || apodo.value.trim().length < 1 || apodo.value.trim().length > 20
        || apodoRegex.test(apodo.value.trim())) {
        valido = false;
        if (!document.getElementById("msgApodo")) {
            let msgApodo = document.createElement('span');
            msgApodo.id = "msgApodo";
            msgApodo.className = "msgsValidaciones";
            msgApodo.textContent = "Campo obligatorio, debe contener entre 1 y 20 caracteres, sin espacios";
            form.children["apodo"].parentNode.insertBefore(msgApodo, form.children["apodo"]);
        }

    } else if (document.getElementById("msgApodo")) {
        document.getElementById("msgApodo").remove();
    }

    if (telefono.value.trim() === '' || telefono.value.trim().length < 10  || telefono.value.trim().length > 13 || isNaN(telefono.value.trim())) {
        valido = false;
        if (!document.getElementById("msgTelefono")) {
            let msgTelefono = document.createElement('span');
            msgTelefono.id = "msgTelefono";
            msgTelefono.className = "msgsValidaciones";
            msgTelefono.textContent = "Campo obligatorio, debe ser un número de teléfono de entre 10 y 13 dígitos";
            form.children["telefono"].parentNode.insertBefore(msgTelefono, form.children["telefono"]);
        }

    } else if (document.getElementById("msgTelefono")) {
        document.getElementById("msgTelefono").remove();
    }

    if (correo.value.trim() == '' || correo.value.trim().length < 10 || nombres.value.trim().length > 150 
    || !correoRegex.test(correo.value.trim())) {
        valido = false;
        if (!document.getElementById("msgCorreo")) {
            let msgCorreo = document.createElement('span');
            msgCorreo.id = "msgCorreo";
            msgCorreo.className = "msgsValidaciones";
            msgCorreo.textContent = "Campo obligatorio, debe ser un correo de entre 10 y 150 caracteres, sin espacios al inicio y final";
            form.children["correo"].parentNode.insertBefore(msgCorreo, form.children["correo"]);
        }

    } else if (document.getElementById("msgCorreo")) {
        document.getElementById("msgCorreo").remove();
    }

    if (contraseña.value.trim() == '' || contraseña.value.trim().length < 8 || contraseña.value.trim().length > 30
    || !contraseñaRegex.test(contraseña.value)) {
        valido = false;
        if (!document.getElementById("msgContraseña")) {
            let msgContraseña = document.createElement('span');
            msgContraseña.id = "msgContraseña";
            msgContraseña.className = "msgsValidaciones";
            msgContraseña.textContent = "Campo obligatorio, debe tener entre 8 y 30 caracteres, al menos una letra mayúscula, una minúscula, un número, un caracter especial y sin espacios";
            form.children["contraseña"].parentNode.insertBefore(msgContraseña, form.children["contraseña"]);
        }

    } else if (document.getElementById("msgContraseña")) {
        document.getElementById("msgContraseña").remove();
    }

    if (contraseña.value != confirmcontra.value) {
        valido = false;
        if (!document.getElementById("msgConfirmContra")) {
            let msgConfirmContra = document.createElement('span');
            msgConfirmContra.id = "msgConfirmContra";
            msgConfirmContra.className = "msgsValidaciones";
            msgConfirmContra.textContent = "Las contraseñas deben coincidir";
            form.children["confirmcontra"].parentNode.insertBefore(msgConfirmContra, form.children["confirmcontra"]);
        }

    } else if (document.getElementById("msgConfirmContra")) {
        document.getElementById("msgConfirmContra").remove();
    }

    return valido;
}

niveles[0].addEventListener("change", () => {
    niveles[1].checked = false;
    niveles[2].checked = false;
});
niveles[1].addEventListener("change", () => {
    niveles[0].checked = false;
    niveles[2].checked = false;
});
niveles[2].addEventListener("change", () => {
    niveles[0].checked = false;
    niveles[1].checked = false;
});

function insertAfter(newElement, existingElement) {
    existingElement.parentNode.insertBefore(newElement, existingElement);
}
