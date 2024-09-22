from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db.DB import CC

import pymysql


cbd = CC()

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

    if request.method in "POST":

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
            cbd.cursor.execute("SELECT numcontrol FROM perfil WHERE numcontrol = %s", (numcontrol,))
            numcontrol_exist = cbd.cursor.fetchone()

            cbd.cursor.execute("SELECT apodo FROM perfil WHERE apodo = %s", (apodo,))
            apodo_exist = cbd.cursor.fetchone()

            cbd.cursor.execute("SELECT correo FROM perfil WHERE correo = %s", (correo,))
            correo_exist = cbd.cursor.fetchone()

            cbd.cursor.execute("SELECT telefono FROM perfil WHERE telefono = %s", (telefono,))
            telefono_exist = cbd.cursor.fetchone()

            try:
                    
                if apodo_exist:
                    return render_template("registro.html", mensaje1 = "este apodo ya esta en uso")
                
                else:
                    if telefono_exist:
                        return render_template("registro.html", mensaje1 = "este telefono ya esta en uso")
                    
                    else:
                        if numcontrol_exist:
                            return render_template("registro.html", mensaje1 = "este numero de control ya esta en uso")
                        else:
                            if correo_exist:
                                return render_template("registro.html", mensaje1 = "este correo ya esta en uso" )

                            else:
                                if contraseña == confirmContra:

                                    contraseña_encript = generate_password_hash(confirmContra)

                                    cbd.cursor.execute("INSERT INTO perfil (nombres, apellidos, apodo, telefono, numcontrol, correo, grado, grupo, contraseña_encript) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (nombres, apellidos, apodo, telefono, numcontrol, correo, grado, grupo, contraseña_encript ))
                                    cbd.connection.commit()
                                
                                else:
                                    return render_template("registro.html", mensaje1 = "las contraseñas que ingresas no coinciden")
                            
            except pymysql.Error as err:

                return render_template("registro.html", mensaje = "las comprobaciones no jalaron")
                    
        except pymysql.Error as err:
            return render_template("home.html", mensaje = "este pedo ya no jalo")
        
        
    return render_template ("registro.html")

if __name__ == "__main__":
    app.run(debug=True)