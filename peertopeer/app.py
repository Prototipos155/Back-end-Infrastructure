from flask import Flask, render_template, request, redirect, url_for, flash

import os

app = Flask(__name__)

@app.route('/')
def home():

    a=Admin()
    # a.logInAlumn('22301061553360','22301061553360@cetis155.edu.mx','7839123848','contraseñ','pepito',3,'A')
    # a.logInTutor('22301061553361','22301061553361@cetis155.edu.mx','7839120048','contraseñ','oscar','guzaman alvedo','1234123340989301','josefa ortiz de dominguez','bachillerato')
    a.close()

    return render_template("home.html")

@app.route ('/iniciarSesion')
def iniciarSesion():
    return render_template("iniciosesi.html")

@app.route ('/registro')
def registro():
    return render_template("registro.html")

if __name__ == "__main__":
    app.run(debug=True)