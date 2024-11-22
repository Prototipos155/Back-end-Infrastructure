import eventlet.wsgi
from flask import Flask, render_template, current_app, redirect, request, session, url_for,Response, send_file, flash,send_from_directory,send_file
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_socketio import join_room, leave_room, send, SocketIO
from functools import wraps
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from string import ascii_uppercase
from flask import request, jsonify

from db.DB import CC
from utiles.hash import Encrypt

import eventlet
import logging
import pymysql
import os
import subprocess
import ssl
import smtplib
import random
import jwt
import filetype
import io
import re

load_dotenv()
cbd = CC()
encriptado = Encrypt()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("PASSWORD4")
app.secret_key = os.getenv("PASSWORD1")

UPLOAD_FOLDER=os.path.join(os.getcwd(),'uploads')
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

login_manager = LoginManager(app)
login_manager.login_view = 'iniciar_sesion'

socketio = SocketIO(app, async_mode="eventlet")
logging.basicConfig(level=logging.DEBUG) 
socketio = SocketIO(app, logger=True, engineio_logger=True)


rooms = {}

class Usuario(UserMixin):
    def __init__(self, id_usuario, rol, nombre_usuario, correo, cuenta_activa):
        self.id = id_usuario
        self.rol = rol
        self.nombre_usuario = nombre_usuario
        self.correo = correo
        self.cuenta_activa = cuenta_activa 

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
    response.headers['Content-Security-Policy'] = (
    "default-src 'self'; "
    "script-src 'self' 'nonce-unique_nonce_value' https://cdn.socket.io https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js; "
    "connect-src 'self' ws://127.0.0.1:5000 ws://localhost:3500;"
    ) 
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "geolocation=(self), microphone=()"
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, proxy-revalidate"
    
    return response



@app.route('/')
def inicio():

    return render_template("inicio.html")

def validaciones(nombres,apellidos,nomusuario,telefono,correo,contraseña):
    errores = {}
    valido = True
    nombreregex = r"[^a-zA-Z\s]"
    apodoregex = r"[^\w.-]"
    correoregex = r"^[\w.]+@[a-zA-Z0-9]+\.+[a-zA-Z.]{1,}$"
    contraregex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!#.-])([\w!#.-]|[^\s]){8,}$"

    if nombres.strip()=="" or len(nombres.strip())>50 or re.search(nombreregex, nombres):
        valido = False
        errores['mensaje01'] = "Campo requerido, no más de 50 caracteres y sin caracteres especiales"
        errores['num_fieldset']= 0

    if apellidos.strip()=="" or len(apellidos.strip())>50 or re.search(nombreregex, apellidos):
        valido = False
        errores['mensaje02'] = "Campo requerido, no más de 50 caracteres y sin caracteres especiales"
        errores['num_fieldset']= 0

    elif nomusuario.strip()=="" or len(nomusuario.strip())>20 or re.search(apodoregex, nomusuario):
        valido = False
        errores['mensaje1'] = "Campo requerido, no más de 20 caracteres y sin espacios ni caracteres especiales"
        errores['num_fieldset']= 1

    elif telefono.strip()==""  or len(telefono.strip())<10 or len(telefono.strip())>13 or not telefono.isdigit():
        valido = False
        errores['mensaje2'] = "Campo de teléfono requerido, entre 10 y 13 caracteres"
        errores['num_fieldset']= 2

    elif correo.strip()==""  or len(correo.strip())<10 or len(correo.strip())>150 or not re.search(correoregex, correo):
        valido = False
        errores['mensaje3'] = "Campo de correo requerido, entre 10 y 150 caracteres"
        errores['num_fieldset']= 2

    elif contraseña.strip()==""  or len(contraseña.strip())<8 or len(contraseña.strip())>30 or not re.search(contraregex, contraseña):
        valido = False
        errores['mensaje4'] = "Contraseña requerida, entre 8 y 30 caracteres, con una letra mayúscula, una minúscula, un número, un caracter especial y sin espacios"
        errores['num_fieldset']= 3

    return valido, errores


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
    
            valido, errores = validaciones(nombres, apellidos, nombre_usuario, telefono, correo, contraseña)
            if not valido:
                return render_template("acceso/registro.html", **errores,  form_data=form_data)

            try:
                cbd.cursor.execute("SELECT nombre_usuario FROM perfil WHERE nombre_usuario = %s", (nombre_usuario,))
                nombre_usuario_exist = cbd.cursor.fetchone()

                cbd.cursor.execute("SELECT correo FROM perfil WHERE correo = %s", (correo,))
                correo_exist = cbd.cursor.fetchone()

                cbd.cursor.execute("SELECT telefono FROM perfil WHERE telefono = %s", (telefono,))
                telefono_exist = cbd.cursor.fetchone()

                error_en_login=None

                if nombre_usuario_exist:
                    errores['mensaje1'] = "Este nombre de usuario ya está en uso"
                    error_en_login=1

                elif telefono_exist:
                    errores["mensaje2"] = "Este teléfono ya está en uso"
                    error_en_login=2

                elif correo_exist:
                    errores["mensaje3"] = "Este correo ya está en uso" 
                    error_en_login=2
                
                elif contraseña != confirmcontra:
                    errores["mensaje4"] =  "Las contraseñas que ingresaste no coinciden"
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
                    body = f"Hola, {nombre_usuario}. El código para verificar que ingresaste un correo que está en tu propiedad es: {codigoveri}"

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

                    return render_template ("acceso/vericorreo_registro.html", mensaje1="Ingrese el código que le enviamos por correo")
                        
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
            return render_template("acceso/vericorreo_registro.html", mensaje1= "Los códigos de verificación no coinciden")

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

                return render_template("acceso/iniciar_sesion.html", mensaje1 = "Registro exitoso",form_data={})
                
            except pymysql.Error as er:
                print(er)
                return render_template("acceso/vericorreo_registro.html", mensaje1 = "No se pudieron insertar los valores del registro")

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

            if correo.strip()=="" or nombre_usuario.strip()=="" or contraseña.strip()=="":
                errores['mensaje1'] = "Todos los campos son obligatorios"
                errores['num_fieldset']=0
                print("entro aca")
                return render_template("acceso/iniciar_sesion.html", **errores, form_data=form_data)

            try:
                cbd.cursor.execute("SELECT id_usuario, rol, nombre_usuario, correo, telefono, contraseña_encript, cuenta_activa FROM perfil WHERE nombre_usuario = %s AND correo = %s", (nombre_usuario, correo))
                perfil_exist = cbd.cursor.fetchone()

                if perfil_exist is None:
                    errores ["mensaje1"] = "El usuario no existe."
                    errores['num_fieldset']=0
                    return render_template("acceso/iniciar_sesion.html", **errores, form_data=form_data)
                
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
                                body = (f"Hola, {nombre_usuario}. Tu código para verificar que ingresaste un correo de tu propiedad es: {codigoveri}")
                                                                                
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
                                return render_template("acceso/iniciar_sesion.html", mensaje="Error al enviar el correo de verificación.", form_data=form_data)

                            session['tokenacceso'] = tokenacceso
                            session['codigoveri'] = codigoveri
                            return redirect(url_for('vericorreo_acceso'))
                        
                        else:
                            print("Contraseña incorrecta")
                            errores["mensaje3"] = "Contraseña incorrecta"
                            errores['num_fieldset']=2
                            return render_template("acceso/iniciar_sesion.html", **errores, form_data=form_data)
                        
                    except Exception as err:
                        print(f"Error durante la verificación de la contraseña o generación del token: {err}")
                        return render_template("acceso/iniciar_sesion.html", mensaje="Error interno al iniciar sesión", form_data=form_data)

                else:
                    print("El nombre de usuario o correo no coinciden.")
                    return render_template("acceso/iniciar_sesion.html", mensaje="El nombre de usuario o correo no coinciden.", form_data=form_data)
            
            except pymysql.Error as err:
                print(f"Error de base de datos: {err}")
                return render_template("acceso/iniciar_sesion.html", mensaje="Error al conectar con la base de datos.", form_data=form_data)
            
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


@app.route('/redireccionar_peticion', methods=["GET", "POST"])
def redireccionar_peticion():
    
    if request.method == "POST":
        boton = request.form.get("boton")
        
        print("boton: ", boton)  
        
        if boton == "categoria":
            return render_template("biblioteca/categoria_peticion.html")
        
        elif boton == "documentos":
            return render_template("biblioteca/documento_peticion.html")            
        
        else:
            return render_template("inicio.html")
    
    return render_template("biblioteca/redireccionar_peticion.html")


@app.route ('/categoria_peticion', methods=['GET', 'POST'])
#@login_required
def categoria_peticion(): 
    
    tipo = request.form.get('tipo')
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    id_categoria = request.form.get("listaTema")
    id_tema = request.form.get("listaSubtema")
    error=""
        
        
    if not (tipo and nombre and descripcion):
        error="Debe llenar los campos correctamente"
    
    else: 
        try:
        
            if tipo == "categoria":

                try:
                
                    if nombre:
                        
                        cbd.cursor.execute("SELECT nombre FROM categoria WHERE nombre = %s", (nombre,))
                        nombre_exist = cbd.cursor.fetchone() 

                        if nombre_exist and nombre_exist[0] == nombre :  
                            error="La categoria que ingreso ya existe"
                            #return render_template("biblioteca/categoria_peticion.html", error = "La categoria que ingreso ya existe")
                            
                        else:
                            cbd.cursor.execute("SELECT MAX(codigo) FROM categoria")
                            ultimo_codigo = cbd.cursor.fetchone()[0]  

                            if ultimo_codigo is None:
                                ultimo_codigo = 0
                                
                            else:
                                ultimo_codigo = int(ultimo_codigo)

                            codigo = f"{ultimo_codigo + 1}"
                            print(f"Nuevo código generado: {codigo}")
                            
                            cbd.cursor.execute("INSERT INTO categoria (codigo, nombre, descripcion) VALUES (%s, %s, %s)", (codigo, nombre, descripcion))
                            cbd.connection.commit()
                            error="Su categoria fue generada."
                            #return render_template ("biblioteca/categoria_peticion.html", error= "Su categoria fue generada.")
                            
                    else:
                        error="Debe proporcionar un nombre de categoria válido."
                        #return render_template ("biblioteca/categoria_peticion.html", error= "Debe proporcionar un nombre de categoria válido.")
                
                except Exception as err:
                    error=f"Error al procesar la solicitud categoria: {err}"
                    #return render_template("biblioteca/categoria_peticion.html", error=f"Error al procesar la solicitud categoria: {err}")
            
            elif tipo == "tema":

                if nombre:
                    try:
                        cbd.cursor.execute("SELECT nombre FROM tema WHERE nombre = %s", (nombre,))
                        nombre_exist1 = cbd.cursor.fetchone()

                        if nombre_exist1 and nombre_exist1[0] == nombre:
                            error="El tema que ingresó ya existe"
                            #return render_template("biblioteca/categoria_peticion.html", error="La categoría que ingresó ya existe")
                        else:
                            cbd.cursor.execute("SELECT codigo FROM categoria")
                            codigo_padre = cbd.cursor.fetchone()[0]

                            cbd.cursor.execute("SELECT MAX(codigo) FROM tema WHERE codigo LIKE %s", (f"{codigo_padre}-%",))
                            ultimo_codigo1 = cbd.cursor.fetchone()[0]

                            if not id_categoria:
                                error="Seleccione una categoria para crear un tema"
                            else:

                                if ultimo_codigo1 is None:
                                    nuevo_sub = 1
                                else:
                                    nuevo_sub = int(ultimo_codigo1.split('-')[-1]) + 1

                                codigo = f"{codigo_padre}-{nuevo_sub}"

                                cbd.cursor.execute("INSERT INTO tema (codigo, nombre, descripcion, id_categoria) VALUES (%s, %s, %s, %s)",(codigo, nombre, descripcion, id_categoria))
                                cbd.connection.commit()
                                error="Tema generado correctamente"
                            
                    except Exception as err:
                        error=f"Error al procesar la solicitud: {err}"
                        #return render_template("biblioteca/categoria_peticion.html", error=f"Error al procesar la solicitud: {err}")
                else:
                    error="Debe proporcionar un nombre de tema válido."
                    #return render_template("biblioteca/categoria_peticion.html", error="Debe proporcionar un nombre de categoría válido.")

            elif tipo == "subtema":
                if nombre:
                    try:
                        cbd.cursor.execute("SELECT nombre FROM subtema WHERE nombre = %s", (nombre,))
                        nombre_exist1 = cbd.cursor.fetchone()

                        if nombre_exist1 and nombre_exist1[0] == nombre:
                            error="El subtema que ingresó ya existe"
                            #return render_template("biblioteca/categoria_peticion.html", error="La categoría que ingresó ya existe")
                        else:
                            cbd.cursor.execute("SELECT codigo FROM tema ")
                            codigo_padre = cbd.cursor.fetchone()[0]

                            cbd.cursor.execute("SELECT MAX(codigo) FROM subtema WHERE codigo LIKE %s", (f"{codigo_padre}-%",))
                            ultimo_codigo1 = cbd.cursor.fetchone()[0]

                            if ultimo_codigo1 is None:
                                nuevo_sub1 = 1
                            else:
                                nuevo_sub1 = int(ultimo_codigo1.split('-')[-1]) + 1

                            nuevo_codigo = f"{codigo_padre}-{nuevo_sub1}"

                            if not id_tema:
                                error = "Seleccione un tema para crear un subtema"
                            else:

                                cbd.cursor.execute("INSERT INTO subtema (codigo, nombre, descripcion, id_tema) VALUES (%s, %s, %s, %s)",(nuevo_codigo, nombre, descripcion, id_tema))
                                cbd.connection.commit()
                                error="Subtema creado con éxito"
                                #return render_template("biblioteca/categoria_peticion.html", mensaje="Categoría creada con éxito.")
                    except Exception as err:
                        error=f"Error al procesar la solicitud: {err}"
                        #return render_template("biblioteca/categoria_peticion.html", error=f"Error al procesar la solicitud: {err}")
                else:
                    error="Debe proporcionar un nombre de subtema válido."
                    #return render_template("biblioteca/categoria_peticion.html", error="Debe proporcionar un nombre de categoría válido.")

            else:
                print ("no se pudo enviar") 
                error="Opción escogida incorrecta"       

        except Exception as err:
            print("SU PTM NO JALO")
            error=f"Error no sé: {err}"

    cbd.cursor.execute("SELECT id_categoria, nombre FROM categoria")
    resultados = cbd.cursor.fetchall()     

    print("resultados: ",resultados)

    list_items_html_cate = ""
    for resultado in resultados:
        idc = resultado[0]
        nombre = resultado[1]
        list_items_html_cate += f'<option value="{idc}">{nombre}</option>'


    cbd.cursor.execute("SELECT id_tema, nombre FROM tema")
    resultados = cbd.cursor.fetchall()     

    print("resultados: ",resultados)

    list_items_html_tema = ""
    for resultado in resultados:
        idt = resultado[0]
        nombre = resultado[1]
        list_items_html_tema += f'<option value="{idt}">{nombre}</option>'
        
        
    return render_template ("biblioteca/categoria_peticion.html", items_cate = list_items_html_cate, items_tema=list_items_html_tema, error=error)


@app.route('/documento_peticion', methods=['GET', 'POST'])
# @login_required
def documento_peticion():
    if request.method == "POST":
        try:
            id_usuario = current_user.id
        except jwt.InvalidTokenError:
            return render_template("biblioteca/peticiones.html", mensaje1="Al parecer no ha iniciado sesión")

        TAMAÑO_MAXIMO_ARCHIVOS = 16 * 1024 * 1024
        mime_permitidos = ['application/pdf']

        mensaje = request.form.get('mensaje', '').strip()
        link = request.form.get('link', '').strip()
        archivoblob = request.files.get('archivo')

        if not link and not archivoblob:
            return render_template("biblioteca/peticiones.html", mensaje1="Debe enviar un enlace o archivo")

        if archivoblob:
            if archivoblob.content_length > TAMAÑO_MAXIMO_ARCHIVOS:
                return render_template("biblioteca/peticiones.html", mensaje1="No se permiten archivos mayores a 16MB")

            archivoblob.seek(0)
            tipoarchivo = filetype.guess(archivoblob)
            if not tipoarchivo or tipoarchivo.mime not in mime_permitidos:
                return render_template("biblioteca/peticiones.html", mensaje1="Solo se permiten archivos PDF")

        try:
            archivoblob.seek(0)
            nombrearchivo = archivoblob.filename
            archivo = archivoblob.read()

            fecha = datetime.now().date()
            hora = datetime.now().time()

            cbd.cursor.execute(
                "INSERT INTO peticiones (id_usuario, mensaje, archivo, nombre_archivo, link, fecha, hora) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (id_usuario, mensaje, archivo, nombrearchivo, link, fecha, hora)
            )
            cbd.connection.commit()

            return render_template("inicio.html", mensaje1="La petición se envió correctamente")
        except pymysql.Error as err:
            return render_template("biblioteca/peticiones.html", mensaje1=f"No se pudo guardar la petición: {err}")

    return render_template("biblioteca/documento_peticion.html")


@app.route('/inicio_biblioteca')
#@login_required
def inicio_biblioteca():
    cbd.cursor.execute("select id_categoria,nombre,descripcion from categoria order by id_categoria asc;")
    categorias=cbd.cursor.fetchall()
    
    cbd.cursor.execute("select id_tema,id_categoria,nombre,descripcion from tema order by id_categoria asc;")
    temas=separarSubCategorias(cbd.cursor.fetchall())

    cbd.cursor.execute("select id_subtema,id_tema,nombre,descripcion from subtema order by id_tema;")
    subtemas=separarSubCategorias(cbd.cursor.fetchall())
    
    print("temas=",temas)
    print("subtemas=",subtemas)
    return render_template("biblioteca/inicio_biblioteca.html",categorias=categorias,Temas=temas
        ,Subtemas=subtemas,
        limiteTemas=len(temas),
        limiteSubtemas=len(subtemas)
    )

@app.route('/docs')
def documentos():
    cbd.cursor.execute("select id_documento,nombre_archivo from documentos")
    docs=cbd.cursor.fetchall()

    return render_template("biblioteca/documentos.html",docs=docs)
    
@app.route('/uploads/<int:id>')
def view_file(id):
    cbd.cursor.execute("select nombre_archivo,documento from documentos where id=%s"%(id))
    doc=cbd.cursor.fetchone()
    if(doc):
        return send_file(io.BytesIO(doc['documento']),nombre=doc['nombre_archivo'],as_attachment=True)
    return "DOC NO ENCONTRADO"

def separarSubCategorias(tupla):
    nuevoOrden=()
    nivel=()
    longitud_registros=len(tupla)
    for index in range(longitud_registros):
        if(nivel==()):
            nivel+=tupla[index][1],
        #nivel+=tupla[index],
        nivel+=(tupla[index][0],tupla[index][2],tupla[index][3]),
        #print(nivel)
        try:
            if(tupla[index][1]!=tupla[index+1][1]):
                #este es el ultimo elemento del nivel
                nuevoOrden+=nivel, #agregamos al nuevo orden
                #print("f===",nivel)
                nivel=() #refrescamos el nivel
        except Exception as ex:
            nuevoOrden+=nivel,
    #f[0][0]
    #1
    #f[0][1]
    #(id,'martin','desc')
    return nuevoOrden


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
    
    
def generar_codigo_unico(length):
    while True:
        codigo = ""
        for _ in range(length):
            codigo += random.choice(ascii_uppercase)
        
        if codigo not in rooms:
            break
    
    return codigo


@app.route('/foro', methods=["GET", "POST"])
@login_required
def foro():
    print(f"\n\nUsuario autenticado? {current_user.is_authenticated}\n\n")

    if not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()

    id_user = current_user.id
    nombre_usuario = current_user.nombre_usuario
    
    if request.method == "POST":
        #nombre = request.form.get("nombre")
        codigo = request.form.get("codigo")
        unirse = request.form.get("unirse", False)
        crear  = request.form.get("crear", False)
    
        #if not nombre:
            #return render_template("salas/foro.html", error = "Por favor ingrese un nombre", codigo=codigo, nombre = nombre)
    
        if unirse != False and not codigo:
            return render_template("salas/foro.html", error = "Por favor ingrese el codigo de la sala", codigo=codigo)
    
        cbd.cursor.execute("SELECT codigo_sala FROM sala WHERE codigo_sala=%s", (codigo))
        sala = cbd.cursor.fetchone()
        
        room = codigo
        
        if crear != False:
            room = generar_codigo_unico(8)
            #rooms[room] = {"miembros": 0, "mensajes": []}
            cbd.cursor.execute("INSERT INTO sala (codigo_sala) VALUES (%s)", (room))
            cbd.connection.commit()
        
        elif not sala:
            return render_template("salas/foro.html", error = "La sala no existe", codigo=codigo)

        session["room"] = room
        session["id_usuario"] = current_user.id
        session["nombre"] = current_user.nombre_usuario
        #print(f"\n\n'room: ', {room}, 'nombre: ', {current_user.nombre_usuario}\n\n")
        return redirect(url_for('sala'))
                    
    return render_template("salas/foro.html")

@app.route('/sala')
@login_required
def sala():
    room = session.get("room")
    cbd.cursor.execute("SELECT codigo_sala FROM sala WHERE codigo_sala=%s", (room))
    sala = cbd.cursor.fetchone()
    #id_user = session.get("id_usuario")
    nombre = session.get("nombre")
    #print(("sala: ", room), ("nombre: ", nombre))
    
    if room is None or nombre is None or not sala:
        return redirect(url_for("inicio"))
    
    cbd.cursor.execute("SELECT id_sala FROM sala WHERE codigo_sala = %s", (room))
    idsala = cbd.cursor.fetchone()
    cbd.cursor.execute("SELECT m.id_msj,m.id_usuario,p.nombre_usuario,m.id_sala,m.mensaje,DATE_FORMAT(m.fecha,'%%d-%%m-%%Y'),m.hora FROM mensaje m, sala s, perfil p WHERE m.id_sala=s.id_sala AND m.id_usuario=p.id_usuario AND s.id_sala=%s ORDER BY m.id_msj DESC LIMIT 100", (idsala[0]))
    mensajes = cbd.cursor.fetchall()

    session["id_sala"] = idsala
        
    return render_template("salas/sala.html", codigo=room, mensajes=reversed(mensajes),EstamosEnSalas=True)

@socketio.on("message")
def message(data):
    room = session.get("room")
    id_user = session.get("id_usuario")
    nombre = session.get("nombre")
    idsala = session.get("id_sala")
    cbd.cursor.execute("SELECT codigo_sala FROM sala WHERE codigo_sala=%s", (room))
    sala = cbd.cursor.fetchone()
    #print(f"\n{room}")
    if not sala:
        return 
    
    contenido = {
        "nombre": nombre,
        "mensaje": data["mensaje"]
    }
    send(contenido, to=room)
    #print(rooms)
    #rooms[room]["mensajes"].append(contenido)
    print(f"{nombre} dice: {data['mensaje']}")

    cbd.cursor.execute("INSERT INTO mensaje (id_usuario,id_sala,mensaje,fecha,hora) VALUES (%s,%s,%s,%s,%s)", (id_user,idsala,data["mensaje"],datetime.strptime(data["fecha"],'%d-%m-%Y').strftime('%Y-%m-%d'),data["hora"]))
    cbd.connection.commit()

@socketio.on("connect")
def conectar(auth):
    room = session.get("room")
    nombre = session.get("nombre")
    if not room or not nombre:
        return
    #if room not in rooms:
    #    leave_room(room)
    #    return
    
    join_room(room)
    send({"nombre": nombre, "mensaje": "entró a la sala"}, to=room)
    #rooms[room]["miembros"] += 1
    print(f"{nombre} entró a la sala {room}")

@socketio.on("disconnect")
def desconectar():
    room = session.get("room")
    nombre = session.get("nombre")
    leave_room(room)

    #if room in rooms:
    #    rooms[room]["miembros"] -= 1
        #if rooms[room]["miembros"] <= 0:
        #    del rooms[room]
    
    send({"nombre": nombre, "mensaje": "ha salido de la sala"}, to=room)
    print(f"{nombre} ha salido de la sala {room}")




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

#/////////////////////////////////////////////////////////////////////////
#                         A D M I N I S T R A D O R
#///////////////////////////////////////////////////////////////////////////


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

def status_401(error):
    return redirect(url_for('inicio.html'))


def status_404(error):
    return "<h1>Página no encontrada</h1>", 404


current_dir = os.path.dirname(os.path.abspath(__file__))

cert_path = os.path.join(current_dir,'utiles', 'server.crt')
key_path = os.path.join(current_dir,'utiles', 'server.key')

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile=cert_path, keyfile=key_path)


if __name__ == "__main__":    
    
    server = eventlet.wrap_ssl(
    eventlet.listen(('127.0.0.1', 5000)),
    certfile = cert_path,
    keyfile = key_path,
    server_side=True
)

    
    eventlet.wsgi.server(server, app)
    
