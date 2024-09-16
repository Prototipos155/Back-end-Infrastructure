from flask import Flask, render_template, request, redirect, url_for, flash
from local_library.hash import generate_password_hash, check_password_hash
from db.admin import Admin
from db.conexion import Conexion

import os
import sqlite3
import pymysql

cbd = Admin()

app = Flask(__name__)

@app.route('/')
def home():

    return render_template("home.html")

@app.route ('/iniciarSesion', methods=['GET', 'POST'])
def iniciarSesion():

    print(f"metodo en uso: {request.method}")

    if request.method == "POST":
        return render_template("iniciosesi.html")

    else:
        return render_template("home.html", mensaje = "este pedo ya no jalo")        

@app.route ('/registro', methods=['GET','POST'])
def registro():

    print(f"metodo en uso: {request.method}")

    if request.method =="POST":

            nombres = request.form.get('nombres')
            apellidos = request.form.get('apellidos')
            apodo = request.form.get('apodo')
            telefono = request.form.get('telefono')
            numcontrol = request.form.get('numcontrol')
            correo = request.form.get('correo')
            grado = request.form.get('grado')
            grupo = request.form.get('grupo')
            contraseña = request.form.get('contraseña')
            confirmContra = request.form.get('confirmContra')

            try:
                cbd.execute("SELECT correo FROM perfil WHERE correo = %s", (correo,))
                ces = cbd.cursor.fetchone()
                
                if ces:
                  return render_template("registro.html", mensaje = "este correo ya esta en uso" )

                else:
                  return render_template("registro.html", mensaje = "El correo está disponible")
                
            except:
                return render_template("home.html", mensaje = "este pedo ya no jalo")
            

    return render_template("home.html", mensaje = "YA NO JALA OTRA VEZ")

if __name__ == "__main__":
    app.run(debug=True)