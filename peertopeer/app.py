from flask import Flask, render_template, current_app, redirect, request, session, url_for,Response, send_file, flash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from functools import wraps
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

from db.DB import CC
from utiles.hash import Encrypt

import pymysql
import os
import subprocess
import ssl
import smtplib
import random
import jwt
import filetype
import io

load_dotenv()
cbd = CC()
encriptado = Encrypt()

app = Flask(__name__)
login_manager = LoginManager(app)
login_manager.login_view = 'iniciar_sesion'
app.secret_key = os.getenv("PASSWORD1")

class Usuario(UserMixin):
    def __init__(self, id_usuario, rol, nombre_usuario, correo, cuenta_activa):
        self.id = id_usuario
        self.rol = rol
        self.nombre_usuario = nombre_usuario
        self.correo = correo
        self.cuenta_activa = cuenta_activa  # Asegúrate de que sea un valor booleano (1 o 0 en la BD convertido a True/False)

    def get_id(self):
        return str(self.id)

    def is_active(self):
        return self.cuenta_activa == 1


@login_manager.user_loader
def load_user(id_usuario):
    
    try:
    
        cbd.cursor.execute("SELECT id_usuario, rol, nombre_usuario, correo, cuenta_activa FROM perfil WHERE id_usuario = %s", (id_usuario,))
        current_user_data = cbd.cursor.fetchone()
        print("Datos de usuario: ", current_user_data)

        if current_user_data:
            return Usuario(
                id_usuario=current_user_data[0],
                rol=current_user_data[1],
                nombre_usuario=current_user_data[2],
                correo=current_user_data[3],
                cuenta_activa=current_user_data[4]
            )
        return None
    
    except Exception as err:
        print("Error de load_user: ", err)
        return None

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        errores = {}
        if not current_user.is_authenticated:
            return redirect(url_for('inicio'))

        elif current_user.rol != 'administrador':
            errores ['mensaje'] = "No tienes permiso para acceder a esta página.", "warning"
            return redirect(url_for('inicio'))
        return f(*args, **kwargs)
    return decorated_function


@app.after_request
def apply_csp(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self';"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "geolocation=(self), microphone=()"
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, proxy-revalidate"
    
    return response


@app.route('/')
def inicio():

    return render_template("inicio.html")


@app.route ('/registro',  methods=['GET', 'POST'])
def registro():

    print(f"metodo en uso: {request.method}")
    form_data = request.form.to_dict() if request.method == 'POST' else {}
    if request.method == "POST":

        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        nombre_usuario = request.form.get('nombre_usuario')
        telefono = request.form.get('telefono')
        correo = request.form.get('correo')
        contraseña = request.form.get('contraseña')
        confirmcontra = request.form.get('confirmcontra')

        try:            
            form_data = {
                'nombres': nombres,
                'apellidos': apellidos,
                'nombre_usuario': nombre_usuario,
                'telefono': telefono,
                'correo': correo
            }

            errores = {}
    

            try:
                cbd.cursor.execute("SELECT nombre_usuario FROM perfil WHERE nombre_usuario = %s", (nombre_usuario,))
                nombre_usuario_exist = cbd.cursor.fetchone()

                cbd.cursor.execute("SELECT correo FROM perfil WHERE correo = %s", (correo,))
                correo_exist = cbd.cursor.fetchone()

                cbd.cursor.execute("SELECT telefono FROM perfil WHERE telefono = %s", (telefono,))
                telefono_exist = cbd.cursor.fetchone()

                error_en_login=None

                if nombre_usuario_exist:
                    errores['mensaje1'] = "este nombre_usuario ya esta en uso"
                    error_en_login=1

                elif telefono_exist:
                    errores["mensaje2"] = "este telefono ya esta en uso"
                    error_en_login=2

                elif correo_exist:
                    errores["mensaje3"] = "este correo ya esta en uso" 
                    error_en_login=2
                
                elif contraseña != confirmcontra:
                    errores["mensaje4"] =  "las contraseñas que ingresas no coinciden"
                    error_en_login=3

                else:        
                    confirmcontra1 = str(confirmcontra)
                    
                    cpe = os.getenv("PASSWORD3")

                    contraseña_encript = encriptado.encriptar_gcm(confirmcontra1, cpe)

                    payload = {
                    'nombres' : nombres,
                    'apellidos' : apellidos,
                    'nombre_usuario' : nombre_usuario,
                    'telefono' : telefono,
                    'correo' : correo,
                    'contraseña_encript' : contraseña_encript,
                    'exp' : datetime.now(timezone.utc) + timedelta(hours=1)
                    }
                    
                    tokenregistro = jwt.encode(payload, os.getenv("PASSWORD2"), algorithm='HS256')

                    remitente = "peertopeerverificacion@gmail.com"
                    password = os.getenv("PASSWORD")
                    destinatario = (f"{correo}")
                    codigoveri = random.randint(100000, 999999)

                    asunto = "Correo de Verificación"
                    body = f"Hola {nombre_usuario} el código para verificar que ingresaste un correo que esta en tu propiedad es: {codigoveri}"

                    try:
                                    
                        em = EmailMessage()
                        em["From"] = remitente
                        em["To"] = destinatario
                        em["Subject"] = asunto

                        em.set_content(body)

                        context = ssl.create_default_context()

                        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = context) as smtp:
                            smtp.login(remitente, password)
                            smtp.sendmail(remitente, destinatario, em.as_string())

                    except smtplib.SMTPException as err:
                        errores['mensaje_email'] = f"No se pudo enviar el correo: {err}"

                    session['codigoveri'] = codigoveri
                    session['tokenregistro'] = tokenregistro

                    return render_template ("acceso/vericorreo_registro.html", mensaje1="ingrese el codigo que le enviamos por correo")
                        
            except pymysql.Error as err:
                print(f"Error en la base de datos: {err}")
                errores['mensajes_db'] = "Hubo un problema en el registro, intente nuevamente"     

            if(error_en_login):
                print("NUM_FIELDSET ERROR",error_en_login)
                errores['num_fieldset']=error_en_login

            return render_template("acceso/registro.html", **errores,  form_data=form_data)    
           
        except pymysql.Error as err:
            return render_template("acceso/registro.html", mensaje="Error al procesar el registro",**errores, form_data=form_data)

    return render_template ("acceso/registro.html",form_data={})


@app.route ('/vericorreo_registro', methods=['GET', 'POST'])
def vericorreo_registro():

    codigoveri = session.get('codigoveri')
    tokenregistro = session.get('tokenregistro')
    
    if request.method == "POST":

        codigo = request.form.get('codigo')
        
        if not (str(codigo) == str(codigoveri)):
            return render_template("vericorreo_registro.html", mensaje1= "no se porque no jala este pedo")

        try:
            payload = jwt.decode(tokenregistro, os.getenv("PASSWORD2"), algorithms=['HS256'])

            nombres = payload['nombres']
            apellidos = payload['apellidos']
            nombre_usuario = payload['nombre_usuario']
            telefono = payload['telefono']
            correo = payload['correo']
            contraseña_encript = payload['contraseña_encript']
            
            try:
                cbd.cursor.execute("INSERT INTO perfil (rol,  nombres, apellidos, nombre_usuario, telefono, correo, contraseña_encript, cuenta_activa) VALUES ('usuario', %s, %s, %s, %s, %s, %s, 1)", ( nombres, apellidos, nombre_usuario, telefono, correo, contraseña_encript ))
                cbd.connection.commit()

                return render_template("acceso/iniciar_sesion.html", mensaje1 = "registro exitoso")
                
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

    form_data = request.form.to_dict() if request.method == 'POST' else {}
    if request.method == "POST" and 'correo' in request.form and 'nombre_usuario' in request.form:

        correo = request.form.get('correo')
        nombre_usuario = request.form.get('nombre_usuario')
        contraseña = request.form.get('contraseña')

        print(correo, nombre_usuario, contraseña)
        
        try:            
            form_data = {
                'correo': correo,
                'nombre_usuario': nombre_usuario
            }
            
            errores = {}

            if not correo or not nombre_usuario or not contraseña:
                errores['mensaje1'] = "Todos los campos son obligatorios"
                print("entro aca")
                return render_template("acceso/iniciar_sesion.html")   

            try:
                cbd.cursor.execute("SELECT id_usuario, rol, nombre_usuario, correo, telefono, contraseña_encript, cuenta_activa FROM perfil WHERE nombre_usuario = %s AND correo = %s", (nombre_usuario, correo))
                perfil_exist = cbd.cursor.fetchone()

                if perfil_exist is None:
                    errores ["mensaje2"] = "El usuario no existe."
                    return render_template("acceso/iniciar_sesion.html")
                
                id_usuario = perfil_exist[0]
                rol = perfil_exist[1]
                nombre_usuario_exist = perfil_exist[2]
                correo_exist = perfil_exist[3]
                telefono_exist = perfil_exist[4]
                contraseña_encript = perfil_exist[5]  
                cuenta_activa = perfil_exist[6]

                print(perfil_exist)

                if (nombre_usuario == nombre_usuario_exist and correo == correo_exist):
                    
                    try:
                        cpe = os.getenv("PASSWORD3")
                        comprobacion_contraseña = encriptado.verificar_gcm(contraseña, contraseña_encript, cpe)
                        
                        if comprobacion_contraseña:
                            
                            print("si llego al token")
                            payload = {
                            'id_usuario': id_usuario,
                            'rol': rol,
                            'nombre_usuario': nombre_usuario,
                            'correo' : correo,
                            'cuenta_activa': cuenta_activa,
                            'exp': datetime.now(timezone.utc) + timedelta(minutes=10) 
                            }

                            tokenacceso = jwt.encode(payload, os.getenv("PASSWORD2"), algorithm='HS256')
                            print("token generado: ",tokenacceso)

                            remitente = "peertopeerverificacion@gmail.com"
                            password = os.getenv("PASSWORD")
                            destinatario = correo
                            codigoveri = random.randint(100000, 999999)

                            try:
                                asunto = "Correo de Verificación"
                                body = (f"Hola {nombre_usuario}, tu código para verificar que ingresaste un correo de tu propiedad es: {codigoveri}")
                                                                                
                                em = EmailMessage()
                                em["From"] = remitente
                                em["To"] = destinatario
                                em["Subject"] = asunto
                                em.set_content(body)

                                context = ssl.create_default_context()

                                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                                    smtp.login(remitente, password)
                                    smtp.sendmail(remitente, destinatario, em.as_string())

                            except smtplib.SMTPException as err:
                                print(f"El correo no ha podido ser enviado: {err}")
                                return render_template("acceso/iniciar_sesion.html", mensaje="Error al enviar el correo de verificación.")

                            session['tokenacceso'] = tokenacceso
                            session['codigoveri'] = codigoveri
                            return redirect(url_for('vericorreo_acceso'))
                        
                        else:
                            print("Contraseña incorrecta")
                            errores["mensaje3"] = "Contraseña incorrecta"
                            return render_template("acceso/iniciar_sesion.html", **errores, form_data=form_data)
                        
                    except Exception as err:
                        print(f"Error durante la verificación de la contraseña o generación del token: {err}")
                        return render_template("acceso/iniciar_sesion.html", mensaje="Error interno al iniciar sesión")

                else:
                    print("El nombre de usuario o correo no coinciden.")
                    return render_template("acceso/iniciar_sesion.html", mensaje="El nombre de usuario o correo no coinciden.")
            
            except pymysql.Error as err:
                print(f"Error de base de datos: {err}")
                return render_template("acceso/iniciar_sesion.html", mensaje="Error al conectar con la base de datos.")
            
        except pymysql.Error as err:
            return render_template("acceso/registro.html", mensaje="Error al procesar el registro",**errores, form_data=form_data)

    return render_template("acceso/iniciar_sesion.html", form_data={})


@app.route ('/vericorreo_acceso', methods=['GET', 'POST'])
def vericorreo_acceso():

    codigoveri = session.get('codigoveri')
    tokenacceso = session.get('tokenacceso')
    
    if request.method == "POST":

        codigo = request.form.get('codigo')
        
        print (codigo,codigoveri)

        if str(codigo).strip() == str(codigoveri).strip():
            print("si entro aca", codigo, codigoveri)

            try:
                payload = jwt.decode(tokenacceso, os.getenv("PASSWORD2"), algorithms=['HS256'])
                
                id_usuario = payload['id_usuario']
                rol = payload['rol']
                nombre_usuario = payload['nombre_usuario']
                correo = payload['correo']
                cuenta_activa = payload['cuenta_activa']
                
                if cuenta_activa == 1:
                    usuario = Usuario(id_usuario, rol, nombre_usuario, correo, cuenta_activa)
                    login_user(usuario)

                    return render_template("inicio.html", mensaje1=f"id: {id_usuario} nombre_usuario: {nombre_usuario}")
                
                else:
                    print("La cuenta no está activa.")
                    return render_template("acceso/vericorreo_acceso.html", mensaje1="La cuenta no está activa. Contacta con el administrador.")
                
            except jwt.ExpiredSignatureError:
                return render_template("acceso/vericorreo_acceso.html", mensaje1="El token ha expirado")
            
            except jwt.InvalidTokenError:
                return render_template("acceso/vericorreo_acceso.html", mensaje1="El token es inválido")
            
            except Exception as err:
                print("Error al decodificar el token:", err)
                return render_template("acceso/vericorreo_acceso.html", mensaje1="No se pudo separar el token")
        
        else:
            print("Tu código de verificación no coincide")
            return render_template("acceso/vericorreo_acceso.html", mensaje1="Tu código de verificación no coincide")

    return render_template("acceso/vericorreo_acceso.html")


@app.route ('/cerrarsesion')
@login_required
def cerrarsesion():

    logout_user()

    return render_template("inicio.html", mensaje1 = "has cerrado sesion")


@app.route ('/peticiones', methods=['GET', 'POST'])
@login_required
def archivo():

    if request.method == "POST":
        tokenacceso = session.get('tokenacceso')

        try:
            payload = jwt.decode(tokenacceso, os.getenv("PASSWORD2"), algorithms=['HS256'])

            id_tupla = payload['id_usuario'],
            nombre_usuario = payload['nombre_usuario']

            id_usuario = id_tupla[0]

        except jwt.InvalidTokenError:
            return render_template("biblioteca/peticiones.html", mensaje1 = "Al parece no ha iniciado session")

        TAMAÑO_MAXIMO_ARCHIVOS = 16*1024*1024
        mime_permitidos = ['application/pdf']
        # 'application/msword', 'application/vnd.ms-excel', 'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        # 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.openxmlformats-officedocument.presentationml.presentation'

        mensaje = request.form.get('mensaje')
        link = request.form.get('link')
        archivoblob = request.files['archivo']

        if link.strip() == "" and not archivoblob:
            return render_template ("biblioteca/peticiones.html", mensaje1 = "Debe enviar un link o archivo")
        
        if archivoblob:
            if len(archivoblob.read()) <= TAMAÑO_MAXIMO_ARCHIVOS :
                try:
                    tipoarchivo = filetype.guess(archivoblob)
                    print(f"\n{archivoblob, tipoarchivo.mime, tipoarchivo.extension}\n")

                    if tipoarchivo is None or not (tipoarchivo.mime in mime_permitidos or tipoarchivo.mime.startswith('image')
                            or tipoarchivo.mime.startswith('video')):
                        return render_template ("biblioteca/peticiones.html", mensaje1 = "Sólo archivos PDF, imágenes y videos")
                
                except Exception as err:
                    return render_template ("biblioteca/peticiones.html", mensaje1 = f"Sólo archivos PDF, imágenes y videos")
            
            else:
                return render_template ("biblioteca/peticiones.html", mensaje1 = "No se permiten archivos mayores a 16MB")

        try:
            archivoblob.seek(0)
            nombrearchivo = archivoblob.filename
            archivo = archivoblob.read()

            fecha = datetime.now ().date()
            hora = datetime.now ().time()
            print(id_usuario)
            print(fecha)
            print(hora)

            cbd.cursor.execute("INSERT INTO peticiones (id_usuario, mensaje, archivo, nombre_archivo, link, fecha, hora) VALUES (%s, %s, %s, %s, %s, %s, %s)", (id_usuario, mensaje, archivo, nombrearchivo, link.strip(), fecha, hora))
            cbd.connection.commit()

            return render_template ("inicio.html", mensaje1 = "la peticion se envio correctamente")

        except pymysql.Error as err:
            return render_template("biblioteca/peticiones.html", mensaje1 = f"no se pudo guardar el archivo: {err}")

    return render_template ("biblioteca/peticiones.html")

@app.route('/inicio_biblioteca')
@login_required
def inicio_biblioteca():
    return render_template("biblioteca/inicio_biblioteca.html")


@app.route('/verarchivo/<int:idpeticion>')
@admin_required
def verarchivo(idpeticion):
    try:
        cbd.cursor.execute("SELECT archivo, nombre_archivo FROM peticiones WHERE id_peticiones = %s", (idpeticion))
        archivo = cbd.cursor.fetchone()

        if archivo:
            archivobinario = io.BytesIO(archivo[0])
            tipomime = filetype.guess(archivo[0])
            nombrearchivo = archivo[1]
            archivobinario.name = nombrearchivo
            print("\nTipo archivo: ",tipomime.mime, " Nombre: ", archivobinario.name)

            return Response(archivobinario, headers={"Content-Disposition": f"inline; filename=\"{nombrearchivo}\""}, mimetype=tipomime.mime)
        
        else:
            return render_template("inicio.html", mensaje1 = "No se pudo obtener el archivo")

    except pymysql.Error as err:
        print("Error: ", err)
        return redirect(url_for('crudpeticionesadmin'))


@app.route('/crudusuariosadmin')
@login_required
@admin_required
def crudusuariosadmin():
    try:
        cbd.cursor.execute("SELECT id_usuario, nombre_usuario, nombres, apellidos, correo, telefono, cuenta_activa FROM perfil")
        perfiles = cbd.cursor.fetchall()

    except pymysql.Error as err:
        print(f"Error al obtener los datos de los perfiles: {err}")

    return render_template("admin/crud-usuarios-admin.html", perfiles = perfiles)


@app.route('/changeStatusAccount/<int:statusAcc>')
@login_required
@admin_required
def changeStatusAccount(statusAcc):

    if 'id_usuario' in session:
            id_usuario = session['id_usuario']

    try: 
        if statusAcc == 1:
            cbd.cursor.execute("UPDATE perfil SET cuenta_activa = 0 WHERE id_usuario = %s", (id_usuario))
            cbd.connection.commit()
        
        elif statusAcc == 0:
            cbd.cursor.execute("UPDATE perfil SET cuenta_activa = 1 WHERE id_usuario = %s", (id_usuario))
            cbd.connection.commit()
        
    except pymysql.Error as err:
        print(f"No se pudo actualizar el estado de la cuenta: {err}")

    return redirect(url_for('crudusuariosadmin'))

@app.route('/crudpeticionesadmin')
@login_required
@admin_required
def crudpeticionesadmin():
    try:
        cbd.cursor.execute("SELECT pet.id_peticiones, pet.id_usuario, per.nombre_usuario, per.correo, pet.mensaje, pet.archivo, pet.link, pet.fecha, pet.hora FROM perfil per JOIN peticiones pet ON per.id_usuario = pet.id_usuario")
        peticiones = cbd.cursor.fetchall()
        
        #id_peticiones = peticiones[0]
        #id_usuario_peticion = peticiones[0]

        #session['peticiones'] = id_peticiones
        #session['id_usuario_peticion'] = id_usuario_peticion
        
    except pymysql.Error as err:
        print(f"Error al obtener los datos de los perfiles: {err}")

    return render_template("admin/crud-peticiones-admin.html", peticiones = peticiones)

@app.route('/rechazarpeticion')
@login_required
@admin_required
def rechazarpeticion():

    if  'id_usuario_peticion' in session:
        id_usuario_peticion = session['id_usuario_peticion']

    try:
        cbd.cursor.execute("DELETE FROM peticiones WHERE id_peticiones = %s", (id_usuario_peticion))
        cbd.connection.commit()

    except pymysql.Error as err:
        print(f"Error al eliminar la petición de la tabla: {err}")
    
    return redirect(url_for("crudpeticionesadmin"))

@app.route('/aceptarpeticion/<int:idpeticion>')
@login_required
@admin_required
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

@app.route('/convertirarchivos', methods=['GET', 'POST'])
def convertirarchivos():
    if request.method == "POST":
        mime_permitidos = ['application/msword', 'application/vnd.ms-excel', 'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.openxmlformats-officedocument.presentationml.presentation']
        
        archivo = request.files['file']
        if archivo:
            try:
                mime = filetype.guess(archivo)
                if mime is None or mime not in mime_permitidos:
                    return render_template("biblioteca/convertirarchivos.html", mensaje1 = "Sólo documentos Office")
                
            except Exception as err:
                return render_template ("biblioteca/convertirarchivos.html", mensaje1 = f"Sólo documentos Office")
            
        else:
            return render_template("biblioteca/convertirarchivos.html", mensaje1 = "Suba un archivo para su conversión") 

        rutaarchivo = os.path.join('/tmp/', archivo.filename)
        archivo.save(rutaarchivo)

        rutapdf = rutaarchivo.rsplit('.', 1)[0] + ".pdf"
        subprocess.run(['unoconv', '-f', 'pdf', rutaarchivo])
        #os.remove(rutaarchivo)

        return send_file(rutapdf, as_attachment=True)      

    return render_template("biblioteca/convertirarchivos.html")

def status_401(error):
    return redirect(url_for('inicio.html'))


def status_404(error):
    return "<h1>Página no encontrada</h1>", 404

if __name__ == "__main__":
    app.run (host='127.0.0.1', port=5000, ssl_context=('adhoc'))