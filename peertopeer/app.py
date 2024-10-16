from flask import Flask, render_template,redirect, request, session, url_for
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from email.message import EmailMessage

from db.DB import CC

import pymysql
import jwt
import os
import ssl
import smtplib
import random


cbd = CC()
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("PASSWORD1")

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

        nivel = request.form.get('nivel')
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        apodo = request.form.get('apodo')
        telefono = request.form.get('telefono')
        correo = request.form.get('correo')
        contraseña = request.form.get('contraseña')
        confirmcontra = request.form.get('confirmcontra')


        try:
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
                        if correo_exist:
                            return render_template("registro.html", mensaje1 = "este correo ya esta en uso" )

                        else:
                            if contraseña == confirmcontra:

                                contraseña_encript = generate_password_hash(confirmcontra)

                                try:
                                    payload = {
                                    'nivel' : nivel,
                                    'nombres' : nombres,
                                    'apellidos' : apellidos,
                                    'apodo' : apodo,
                                    'telefono' : telefono,
                                    'correo' : correo,
                                    'contraseña_encript' : contraseña_encript,
                                    'exp' : datetime.now(timezone.utc) + timedelta(hours=1)
                                        }

                                    token = jwt.encode(payload, os.getenv("PASSWORD2"), algorithm='HS256')

                                    try:
                                        remitente = "peertopeerverificacion@gmail.com"
                                        password = os.getenv("PASSWORD")
                                        destinatario = (f"{correo}")
                                        codigoveri = random.randint(100000, 999999)

                                        asunto = "Correo de Verificación"
                                        body = (f"Hola {apodo} el código para verificar que ingresaste un correo que esta en tu propiedad es: {codigoveri}")
                                                                            
                                        em = EmailMessage()
                                        em["From"] = remitente
                                        em["To"] = destinatario
                                        em["Subject"] = asunto

                                        em.set_content(body)

                                        context = ssl.create_default_context()

                                        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = context) as smtp:
                                            smtp.login(remitente, password)
                                            smtp.sendmail(remitente, destinatario, em.as_string())

                                    except pymysql.Error as err:
                                        return render_template ("registro.html", mensaje1 = f"el correo no ha podido ser enviado: {err}")

                                    session['token'] = token
                                    session['codigoveri'] = codigoveri
                                    return render_template("vericorreo_acceso.html")


                                except pymysql.Error as err:
                                    return render_template("registro.html", mensaje1 = "este pedo ya no jalo") 
                                        
                            else:
                                return render_template("registro.html", mensaje1 = "las contraseñas que ingresas no coinciden")
                
            except pymysql.Error as err:
 
                return render_template("registro.html", mensaje = "las comprobaciones no jalaron")
                    
        except pymysql.Error as err:
            return render_template("home.html", mensaje = "este pedo ya no jalo")
        
    return render_template ("registro.html")

@app.route ('/vericorreo_registro', methods=['GET', 'POST'])
def vericorreo_registro():

    codigoveri = session.get('codigoveri')
    token = session.get('token')
    
    if request.method in "POST":

        codigo = request.form.get('codigo')
        print(codigo)
        print(codigoveri)

        if str(codigo) == str(codigoveri):

            try:
                payload = jwt.decode(token, os.getenv("PASSWORD2"), algorithms=['HS256'])
                
                nivel = payload['nivel'],
                nombres = payload['nombres'],
                apellidos = payload['apellidos'],
                apodo = payload['apodo'],
                telefono = payload['telefono'],
                correo = payload['correo'],
                contraseña_encript = payload['contraseña_encript']
                
                try:
                    cbd.cursor.execute("INSERT INTO perfil (nivel, nombres, apellidos, apodo, telefono, correo, contraseña_encript) VALUES (%s, %s, %s, %s, %s, %s, %s)", (nivel, nombres, apellidos, apodo, telefono, correo, contraseña_encript ))
                    cbd.connection.commit()

                    return render_template("home.html", mensaje1 = "registro exitoso")
                
                except:
                    return render_template("vericorreo_registro.html", mensaje1 = "no se pudieron insertar los valores del registro")

            except:
                return render_template("vericorreo_registro.html", mensaje1 = "no se pudo separar el token")
            
        else:
            return render_template("vericorreo_registro.html", mensaje1= "no se porque no jala este pedo")


    return render_template("vericorreo_registro.html")

@app.route ('/acceso', methods=['GET', 'POST'])
def acceso():

    print(f"metodo en uso: {request.method}")

    if request.method == "POST" and 'correo' in request.form  and 'apodo':

        correo = request.form.get('correo')
        apodo = request.form.get('apodo')
        contraseña = request.form.get('contraseña')

        try:
            cbd.cursor.execute("SELECT  id_perfil, nivel, apodo, correo, telefono, contraseña_encript FROM perfil WHERE apodo = %s AND correo = %s", (apodo, correo))
            perfil_exist = cbd.cursor.fetchone()

            if perfil_exist:

                id_perfil = perfil_exist[0]
                nivel = perfil_exist[1]
                apodo_exist = perfil_exist[2]
                correo_exist = perfil_exist[3]
                telefono_exist = perfil_exist[4]
                contraseña_encript = perfil_exist[5]     

            try:
                if apodo == apodo_exist and correo == correo_exist:

                    print(f"metodo: {request.method} ")
                    print(contraseña_encript)

                    if contraseña_encript is not None:

                        if check_password_hash(contraseña_encript, contraseña):

                            try:
                                payload = {
                                'id_perfil' : id_perfil,
                                'nivel' : nivel,
                                'apodo' : apodo,
                                'exp' : datetime.now(timezone.utc) + timedelta(hours=1)
                                    }

                                token = jwt.encode(payload, os.getenv("PASSWORD2"), algorithm='HS256')

                                try:
                                    remitente = "peertopeerverificacion@gmail.com"
                                    password = os.getenv("PASSWORD")
                                    destinatario = (f"{correo}")
                                    codigoveri = random.randint(100000, 999999)

                                    asunto = "Correo de Verificación"
                                    body = (f"Hola {apodo} tu código para verificar que ingresaste un correo de tu propiedad es: {codigoveri}")
                                                                                
                                    em = EmailMessage()
                                    em["From"] = remitente
                                    em["To"] = destinatario
                                    em["Subject"] = asunto

                                    em.set_content(body)

                                    context = ssl.create_default_context()

                                    with smtplib.SMTP_SSL("smtp.gmail.com",465,context = context) as smtp:
                                        smtp.login(remitente,password)
                                        smtp.sendmail(remitente,destinatario,asunto,em.as_string())

                                except pymysql.Error as err:
                                    return render_template ("acceso.html", mensaje1 = f"el correo no ha podido ser enviado: {err}")
                            
                                session['token'] = token
                                session['codigoveri'] = codigoveri
                                return redirect(url_for('vericorreo_acceso'))

                            except pymysql.Error as err:
                                    return render_template ("acceso.html", mensaje1 = f"el token no ha podido ser generado: {err}")


                        else:
                            return render_template("acceso.html", mensaje1="Contraseña incorrecta") 
                    
                    else:
                        return render_template("acceso.html", mensaje1="Contraseña no definida en la base de datos.")

                else:
                    return render_template("acceso.html", mensaje1="El apodo y/o correo no coinciden")
            
            except pymysql.Error as err:
                return render_template("acceso.html", mensaje1=" no se puede iniciar sesion")


        except pymysql.Error as err:
            print(f"no jala:{err}")
            return render_template("acceso.html", mensaje1="esta madre no jalo: ")


    return render_template ("acceso.html" )

@app.route ('/vericorreo_acceso', methods=['GET', 'POST'])
def vericorreo_acceso():

    codigoveri = session.get('codigoveri')
    token = session.get('token')
    
    if request.method in "POST":

        codigo = request.form.get('codigo')

        if str(codigo) == str(codigoveri):

            try:
                payload = jwt.decode(token, os.getenv("PASSWORD2"), algorithms=['HS256'])
                
                id_perfil = payload['id_perfil'],
                nivel = payload['nivel'],
                apodo = payload['apodo']
                
                return render_template("home.html", mensaje1 =f"id: {id_perfil}   nivel: {nivel}  apodo{apodo}")

            except:
                return render_template("vericorreo_acceso.html", mensaje1 = "no se pudo separar el token")
            
        else:
            return render_template("vericorreo_acceso.html", mensaje1= "Tu código de verificación no coincide")



    return render_template("vericorreo_acceso.html")


@app.route('/crudAdmin')
def crudAdmin():
    try:
        cbd.cursor.execute("SELECT id_perfil, apodo, nivel, nombres, apellidos, correo, telefono, cuenta_activa FROM perfil")
        perfiles = cbd.cursor.fetchall()

    except pymysql.Error as err:
        print(f"Error al obtener los datos de los perfiles: {err}")

    return render_template("admin/crud-admin.html", perfiles = perfiles)


@app.route('/changeStatusAccount/<int:idPerfil>/<int:statusAcc>')
def changeStatusAccount(idPerfil, statusAcc):
    try: 
        if statusAcc == 1:
            cbd.cursor.execute("UPDATE perfil SET cuenta_activa = 0 WHERE id_perfil = %s", (idPerfil))
            cbd.connection.commit()
        
        elif statusAcc == 0:
            cbd.cursor.execute("UPDATE perfil SET cuenta_activa = 1 WHERE id_perfil = %s", (idPerfil))
            cbd.connection.commit()
        
    except pymysql.Error as err:
        print(f"No se pudo actualizar el estado de la cuenta: {err}")

    return redirect(url_for('crudAdmin'))


@app.route ('/archivo', methods=['GET', 'POST'])
def archivo():

    return render_template ("archivo.html")

if __name__ == "__main__":
    app.run(debug=True)