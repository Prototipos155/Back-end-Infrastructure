from flask import Flask, render_template, request, redirect, url_for, flash
from local_library.hash import generate_password_hash, check_password_hash
from db.admin import Admin
from db.conexion import Conexion

import os
import pymysql

dbc = Admin()

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

    if request.method in ["GET","POST"]:

        nombres = request.form ['nombres']
        apellidos = request.form ['apellidos']
        apodo = request.form ['apodo']
        correo = request.form ['correo']
        telefono = request.form ['telefono']
        grado = request.form ['grado']
        grupo = request.form ['grupo']
        contraseña = request.form ['contraseña']
        contraseña1 = request.form ['contraseña1']
    
        try:
            dbc.cursor.excute("SELECT correo FROM perfil where correo = %s", (correo,))
            ce = dbc.cursor.fetchone()

        except:
            return render_template

    else:
        return render_template("registro.html")

if __name__ == "__main__":
    app.run(debug=True)