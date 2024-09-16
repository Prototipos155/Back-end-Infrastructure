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

@app.route ('/registro', methods=['GET','POST'])
def registro():

    if request.method == ["GET","POST"]:

        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        apodo = request.form ['apodo']
        telefono = request.form['telefono']
        numcontrol = request.form['numcontrol']
        correo = request.form['correo']
        grado = request.form['grado']
        grupo = request.form['grupo']
        contraseña = request.form['contraseña']
        confirmContra = request.form['confirmContra']

        try:
           dbc.execute("SELECT correo FROM perfil where correo =  %s", (correo,)) 
           correo_exist = self.cx.getFetch()

           if correo_exist:
               return render_template("home.html")
           else:
               return render_template ("registrar.html")

        except:
            return render_template("registro.html")
        
    else: 
        return render_template("registro.html")

if __name__ == "__main__":
    app.run(debug=True)