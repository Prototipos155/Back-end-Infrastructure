from flask import Flask, render_template, redirect, request, session, url_for, send_file, Response
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

from db.DB import CC

import pymysql
import os
import ssl
import smtplib
import random
import jwt
import filetype
import io

r=load_dotenv("./peertopeer/utiles/.env")
cbd = CC()

app = Flask(__name__)
app.secret_key = os.getenv("PASSWORD1")

contraseña = os.getenv("PASSWORD2")

@app.route('/')
def inicio():

    return render_template("inicio.html")


@app.route('/acceso-registro')
def acceso_registro():

    return render_template("acceso-registro.html")   

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
            mensaje=""
            if apodo_exist:
                mensaje = "este apodo ya esta en uso"

            if telefono_exist and mensaje=="":
                mensaje = "este telefono ya esta en uso"

            if correo_exist and mensaje=="":
                mensaje = "este correo ya esta en uso" 

            if not ( contraseña == confirmcontra) and mensaje=="":
                mensaje = "las contraseñas que ingresas no coinciden"
            
            if(mensaje!=""):
                return render_template("registro.html",mensaje1=mensaje,datos=(nivel,nombres,apellidos,apodo,telefono,correo,contraseña,confirmcontra))
            try:

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

                    # print(f"payload={payload}")
                    print(f'psw={os.getenv("PASSWORD2")}')
                    tokenregistro = jwt.encode(payload, os.getenv("PASSWORD2"), algorithm='HS256')

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

                    session['codigoveri'] = codigoveri
                    session['tokenregistro'] = tokenregistro

                    return render_template ("acceso/vericorreo_registro.html", mensaje1="ingrese el codigo que le enviamos por correo")

                except pymysql.Error as err:
                    print(err)
                    return render_template("acceso/registro.html", mensaje1 = "este pedo ya no jalo") 
                                
            except pymysql.Error as err:
 
                return render_template("acceso/registro.html", mensaje = "las comprobaciones no jalaron")
                    
        except pymysql.Error as err:
            return render_template("inicio.html", mensaje = "este pedo ya no jalo")
        
    return render_template ("acceso/registro.html",datos=("","","","","","",""))

@app.route ('/vericorreo_registro', methods=['GET', 'POST'])
def vericorreo_registro():

    codigoveri = session.get('codigoveri')
    tokenregistro = session.get('tokenregistro')
    
    if request.method in "POST":

        codigo = request.form.get('codigo')
        print(codigo)
        print(codigoveri)

        if not (str(codigo) == str(codigoveri)):
            return render_template("vericorreo_registro.html", mensaje1= "no se porque no jala este pedo")

        try:
            payload = jwt.decode(tokenregistro, os.getenv("PASSWORD2"), algorithms=['HS256'])

            nivel = payload['nivel']
            nombres = payload['nombres']
            apellidos = payload['apellidos']
            apodo = payload['apodo']
            telefono = payload['telefono']
            correo = payload['correo']
            contraseña_encript = payload['contraseña_encript']
            
            try:
                cbd.cursor.execute("INSERT INTO perfil (nivel, nombres, apellidos, apodo, telefono, correo, contraseña_encript, cuenta_activa) VALUES (%s, %s, %s, %s, %s, %s, %s, 1)", (nivel, nombres, apellidos, apodo, telefono, correo, contraseña_encript ))
                cbd.connection.commit()

                return render_template("inicio.html", mensaje1 = "registro exitoso")
                
            except pymysql.Error as er:
                print(er)
                return render_template("acceso/vericorreo_registro.html", mensaje1 = "no se pudieron insertar los valores del registro")

        except jwt.InvalidTokenError:
            print("Token inválido.")
            return render_template("acceso/vericorreo_registro.html")


    return render_template("acceso/vericorreo_registro.html")

@app.route ('/iniciar_sesion', methods=['GET', 'POST'])
def iniciar_sesion():

    print(f"metodo en uso: {request.method}")

    if request.method == "POST" and 'correo' in request.form  and 'apodo':

        correo = request.form.get('correo')
        apodo = request.form.get('apodo')
        contraseña = request.form.get('contraseña')

        try:
            cbd.cursor.execute("SELECT  id_perfil, nivel, apodo, correo, telefono, contraseña_encript FROM perfil WHERE apodo = %s AND correo = %s", (apodo, correo))
            perfil_exist = cbd.cursor.fetchone()

            if not perfil_exist:
                return render_template("acceso/iniciar_sesion.html", mensaje1="NO HAY UN USUARIO ASOCIADO A DICHOS DATOS")
            
            id_perfil = perfil_exist[0]
            nivel = perfil_exist[1]
            apodo_exist = perfil_exist[2]
            correo_exist = perfil_exist[3]
            telefono_exist = perfil_exist[4]
            contraseña_encript = perfil_exist[5]     

            try:
                if not(apodo == apodo_exist and correo == correo_exist):
                    return render_template("acceso/iniciar_sesion.html", mensaje1="El apodo y/o correo no coinciden")
                print(f"metodo: {request.method} ")
                print(contraseña_encript)

                if not( contraseña_encript is not None):
                    return render_template("acceso/iniciar_sesion.html", mensaje1="Contraseña no definida en la base de datos.")
                
                if not( check_password_hash(contraseña_encript, contraseña)):
                    return render_template("acceso/iniciar_sesion.html", mensaje1="Contraseña incorrecta")
                
                try:
                    payload = {
                    'id_perfil' : id_perfil,
                    'nivel' : nivel,
                    'apodo' : apodo,
                    'exp' : datetime.now(timezone.utc) + timedelta(hours=1)
                        }

                    tokenacceso = jwt.encode(payload, os.getenv("PASSWORD2"), algorithm='HS256')

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
                            smtp.sendmail(remitente,destinatario,em.as_string())

                    except pymysql.Error as err:
                        return render_template ("acceso/iniciar_sesion.html", mensaje1 = f"el correo no ha podido ser enviado: {err}")
                
                    session['tokenacceso'] = tokenacceso
                    session['codigoveri'] = codigoveri
                    return redirect(url_for('vericorreo_acceso'))

                except pymysql.Error as err:
                        return render_template ("acceso/iniciar_sesion.html", mensaje1 = f"el token no ha podido ser generado: {err}") 

            
            except pymysql.Error as err:
                return render_template("acceso/iniciar_sesion.html", mensaje1=" no se puede iniciar sesion")


        except pymysql.Error as err:
            print(f"no jala:{err}")
            return render_template("acceso/iniciar_sesion.html", mensaje1="esta madre no jalo: ")


    return render_template ("acceso/iniciar_sesion.html" )

@app.route ('/vericorreo_acceso', methods=['GET', 'POST'])
def vericorreo_acceso():

    codigoveri = session.get('codigoveri')
    tokenacceso = session.get('tokenacceso')
    
    if request.method in "POST":

        codigo = request.form.get('codigo')

        if not(str(codigo) == str(codigoveri)):
            return render_template("acceso/vericorreo_acceso.html", mensaje1= "Tu código de verificación no coincide")

        try:
            payload = jwt.decode(tokenacceso, os.getenv("PASSWORD2"), algorithms=['HS256'])
            
            id_perfil = payload['id_perfil'],
            nivel = payload['nivel'],
            apodo = payload['apodo']
            
            return render_template("inicio.html", mensaje1 =f"id: {id_perfil}   nivel: {nivel}  apodo: {apodo}")

        except:
            return render_template("acceso/vericorreo_acceso.html", mensaje1 = "no se pudo separar el token")

    return render_template("acceso/vericorreo_acceso.html")


@app.route ('/archivo', methods=['GET', 'POST'])
def archivo():

    if request.method in "POST":
        tokenacceso = session.get('tokenacceso')

        try:
            payload = jwt.decode(tokenacceso, os.getenv("PASSWORD2"), algorithms=['HS256'])

            id_tupla = payload['id_perfil'],
            nivel = payload['nivel'],
            apodo = payload['apodo']

            id_perfil = id_tupla[0]

        except jwt.InvalidTokenError:
            return render_template("archivo.html", mensaje1 = "no pudo obtener el token")

        TAMAÑO_MAXIMO_ARCHIVOS = 16*1024*1024
        mime_permitidos = ['application/pdf']
        # 'application/msword', 'application/vnd.ms-excel', 'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        # 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.openxmlformats-officedocument.presentationml.presentation'

        mensaje = request.form.get('mensaje')
        link = request.form.get('link')
        archivoblob = request.files['archivo']
        print("Nombre archivo: ",archivoblob.filename)

        if link.strip() == "" and not archivoblob:
            return render_template ("archivo.html", mensaje1 = "Debe enviar un link o archivo")
        
        if archivoblob:
            if len(archivoblob.read()) <= TAMAÑO_MAXIMO_ARCHIVOS :
                try:
                    tipoarchivo = filetype.guess(archivoblob)
                    print(f"\n{archivoblob, tipoarchivo.mime, tipoarchivo.extension}\n")

                    if tipoarchivo is None or not (tipoarchivo.mime in mime_permitidos or tipoarchivo.mime.startswith('image')
                            or tipoarchivo.mime.startswith('video')):
                        return render_template ("archivo.html", mensaje1 = "Sólo archivos PDF, imágenes y videos")
                
                except Exception as err:
                    return render_template ("archivo.html", mensaje1 = f"Sólo archivos PDF, imágenes y videos")
            
            else:
                return render_template ("archivo.html", mensaje1 = "No se permiten archivos mayores a 16MB")

        try:
            archivoblob.seek(0)
            nombrearchivo = archivoblob.filename
            archivo = archivoblob.read()

            fecha = datetime.now ().date()
            hora = datetime.now ().time()
            print(id_perfil)
            print(fecha)
            print(hora)

            cbd.cursor.execute("INSERT INTO peticiones (id_perfil, mensaje, archivo, nombre_archivo, link, fecha, hora) VALUES (%s, %s, %s, %s, %s, %s, %s)", (id_perfil, mensaje, archivo, nombrearchivo, link.strip(), fecha, hora))
            cbd.connection.commit()

            return render_template ("inicio.html", mensaje1 = "la peticion se envio correctamente")

        except pymysql.Error as err:
            return render_template("archivo.html", mensaje1 = f"no se pudo guardar el archivo: {err}")

    return render_template ("archivo.html")

@app.route('/verarchivo/<int:idpeticion>')
def verarchivo(idpeticion):
    try:
        cbd.cursor.execute("SELECT archivo, nombre_archivo FROM peticiones WHERE id_peticiones = %s", (idpeticion))
        archivo = cbd.cursor.fetchone()

        if archivo:
            archivobinario = io.BytesIO(archivo[0])
            tipomime = filetype.guess(archivo[0])
            nombrearchivo = archivo[1]
            print("\nTipo archivo: ",tipomime.mime, " Nombre: ", nombrearchivo)

            return Response(archivobinario, headers={"Content-Disposition": f"inline; filename=\"{nombrearchivo}\""}, mimetype=tipomime.mime)
        
        else:
            return render_template("inicio.html", mensaje1 = f"No se pudo obtener el archivo")

    except pymysql.Error as err:
        print("Error: ", err)
        return redirect(url_for('crudpeticionesadmin'))


@app.route('/crudusuariosadmin')
def crudusuariosadmin():
    try:
        cbd.cursor.execute("SELECT id_perfil, apodo, nivel, nombres, apellidos, correo, telefono, cuenta_activa FROM perfil")
        perfiles = cbd.cursor.fetchall()

    except pymysql.Error as err:
        print(f"Error al obtener los datos de los perfiles: {err}")

    return render_template("admin/crud-usuarios-admin.html", perfiles = perfiles)


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

    return redirect(url_for('crudusuariosadmin'))

@app.route('/crudpeticionesadmin')
def crudpeticionesadmin():
    try:
        cbd.cursor.execute("SELECT pet.id_peticiones, pet.id_perfil, per.apodo, per.correo, pet.mensaje, pet.archivo, pet.link, pet.fecha, pet.hora FROM perfil per JOIN peticiones pet ON per.id_perfil = pet.id_perfil")
        peticiones = cbd.cursor.fetchall()

    except pymysql.Error as err:
        print(f"Error al obtener los datos de los perfiles: {err}")

    return render_template("admin/crud-peticiones-admin.html", peticiones = peticiones)

@app.route('/rechazarpeticion/<int:idpeticion>')
def rechazarpeticion(idpeticion):
    try:
        cbd.cursor.execute("DELETE FROM peticiones WHERE id_peticiones = %s", (idpeticion))
        cbd.connection.commit()

    except pymysql.Error as err:
        print(f"Error al eliminar la petición de la tabla: {err}")
    
    return redirect(url_for("crudpeticionesadmin"))

@app.route('/aceptarpeticion/<int:idpeticion>')
def aceptarpeticion(idpeticion):
    try:
        cbd.cursor.execute("SELECT archivo, nombre_archivo, link FROM peticiones WHERE id_peticiones = %s", (idpeticion))
        datos = cbd.cursor.fetchone()
        archivo = datos[0]
        nombrearchivo = datos[1]
        link = datos[2]

        if archivo != b'' and archivo != "":
            cbd.cursor.execute("INSERT INTO documentos (documento, nombre_archivo) SELECT archivo, nombre_archivo FROM peticiones WHERE id_peticiones = %s", (idpeticion))
            cbd.connection.commit()

        if link != "":
            cbd.cursor.execute("INSERT INTO links (link) SELECT link FROM peticiones WHERE id_peticiones = %s", (idpeticion))
            cbd.connection.commit()

        cbd.cursor.execute("DELETE FROM peticiones WHERE id_peticiones = %s", (idpeticion))
        cbd.connection.commit()

    except pymysql.Error as err:
        print(f"Error al mover la petición de la tabla: {err}")

    return redirect(url_for("crudpeticionesadmin"))


if __name__ == "__main__":
    app.run(debug=True)