from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from db.DB import CC

import pymysql


cbd = CC()

app = Flask(__name__)

@app.route('/')
def home():

    return render_template("home.html")

@app.route ('/iniciarSesion')
def iniciarSesion():
    return render_template("iniciosesi.html")
    

@app.route ('/registro', methods=['GET','POST'])
def registro():

    print(f"metodo en uso: {request.method}")

    if request.method in "POST":

        rol = request.form.get('alumno','tutor')
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        apodo = request.form.get('apodo')
        telefono = request.form.get('telefono')
        numcontrol = request.form.get('numcontrol')
        correo = request.form.get('correo')
        grado = request.form.get('grado')
        grupo = request.form.get('grupo')
        contraseña = request.form.get('contraseña')
        confirmcontra = request.form.get('confirmcontra')


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
                                if contraseña == confirmcontra:

                                    contraseña_encript = generate_password_hash(confirmcontra)

                                    cbd.cursor.execute("INSERT INTO perfil (rol, nombres, apellidos, apodo, telefono, numcontrol, correo, grado, grupo, contraseña_encript) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (rol, nombres, apellidos, apodo, telefono, numcontrol, correo, grado, grupo, contraseña_encript ))
                                    cbd.connection.commit()
                                        
                                else:
                                     return render_template("registro.html", mensaje1 = "las contraseñas que ingresas no coinciden")
                
                    
            except pymysql.Error as err:
 
                return render_template("registro.html", mensaje = "las comprobaciones no jalaron")
                    
        except pymysql.Error as err:
            return render_template("home.html", mensaje = "este pedo ya no jalo")
        
        
    return render_template ("registro.html")

@app.route ('/acceso', methods=['GET', 'POST'])
def acceso():

    print(f"metodo en uso: {request.method}")

    if request.method == "POST" and 'correo' in request.form  and 'apodo':

        correo = request.form.get('correo')
        apodo = request.form.get('apodo')
        contraseña = request.form.get('contraseña')

        try:
            cbd.cursor.execute("SELECT  id_perfil, rol, apodo, correo, contraseña_encript FROM perfil WHERE apodo = %s AND correo = %s", (apodo, correo))
            perfil_exist = cbd.cursor.fetchone()

            if perfil_exist:

                id_perfil = perfil_exist[0]
                rol = perfil_exist[1]
                apodo_exist = perfil_exist[2]
                correo_exist = perfil_exist[3]
                contraseña_encript = perfil_exist[4]     

            try:
                if apodo == apodo_exist and correo == correo_exist:

                    print(f"metodo: {request.method} ")
                    print(contraseña_encript)

                    if contraseña_encript is not None:

                        if check_password_hash(contraseña_encript, contraseña):

                            return render_template("home.html", mensaje1 =f"id: {id_perfil}   rol: {rol}")

                        else:
                            return render_template("acceso.html", mensaje="Contraseña incorrecta") 
                    
                    else:
                        return render_template("acceso.html", mensaje="Contraseña no definida en la base de datos.")

                else:
                    return render_template("acceso.html", mensaje="El apodo y/o correo no coinciden")
            
            except pymysql.Error as err:
                return render_template("acceso.html", mensaje=" no se puede iniciar sesion")


        except pymysql.Error as err:
            return render_template("acceso.html", mensaje="esta madre no jalo")


    return render_template ("acceso.html" )

if __name__ == "__main__":
    app.run(debug=True)