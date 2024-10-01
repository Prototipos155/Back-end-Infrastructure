<<<<<<< HEAD
<<<<<<< HEAD
from flask import Flask, render_template,uest, redirect, url_for, flash
=======
from flask import Flask, render_template #,uest, redirect, url_for, flash
from db.admin import Admin
>>>>>>> DB/main
=======
from flask import Flask, render_template, request, redirect, url_for, flash

import os
>>>>>>> 7f685ae1798463d8c70a0bc4f83809877f9d2b36

app = Flask(__name__)

@app.route('/')
def home():
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
=======

>>>>>>> Back-end-Infrastructure/main
    a=Admin()
    # a.logInAlumn('22301061553360','22301061553360@cetis155.edu.mx','7839123848','contraseñ','pepito',3,'A')
    # a.logInTutor('22301061553361','22301061553361@cetis155.edu.mx','7839120048','contraseñ','oscar','guzaman alvedo','1234123340989301','josefa ortiz de dominguez','bachillerato')
    a.close()
<<<<<<< HEAD
    
>>>>>>> DB/main
    return render_template("principal.html")
=======
=======

>>>>>>> Back-end-Infrastructure/main
    return render_template("home.html")

@app.route ('/iniciarSesion')
def iniciarSesion():
    return render_template("iniciosesi.html")

@app.route ('/registro')
def registro():
    return render_template("registro.html")
>>>>>>> 7f685ae1798463d8c70a0bc4f83809877f9d2b36

if __name__ == "__main__":
    app.run(debug=True)