const form = document.getElementById('form-registro')
const confirmacion = document.getElementById('confirmacion')

confirmacion.hidden = true;

form.addEventListener('submit', function(event) {
    event.preventDefault();
    console.log('Formulario enviado');
    confirmacion.hidden = false;
});