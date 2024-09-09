const roles = document.getElementsByName("rol");
for (const item of roles) {
    item.addEventListener("change", cambiar);
}

function cambiar() {
    if (roles[0].checked) {
        roles[1].checked = false;
    } else if (roles[1].checked) {
        roles[0].checked = false;
    }
}