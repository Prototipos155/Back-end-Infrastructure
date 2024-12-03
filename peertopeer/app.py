import eventlet.wsgi
from flask import Flask, render_template, current_app, redirect, request, session, url_for,Response, send_file, flash,send_from_directory,send_file,make_response
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
from utiles.email.email_validation import verify_email
from utiles.hash import Encrypt
from utiles.myprint import myprint

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
verify_domain = verify_email()
encrypted = Encrypt()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("PASSWORD4")
app.secret_key = os.getenv("PASSWORD1")

UPLOAD_FOLDER=os.path.join(os.getcwd(),'uploads')
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

login_manager = LoginManager(app)
login_manager.login_view = 'login'

socketio = SocketIO(app, async_mode="eventlet")
logging.basicConfig(level=logging.DEBUG) 
socketio = SocketIO(app, logger=True, engineio_logger=True)


rooms = {}

class Usuario(UserMixin):
    def __init__(self, id_usuario, rol, username, email, active_account):
        self.id = id_usuario
        self.rol = rol
        self.username = username
        self.email = email
        self.active_account = active_account 

    def get_id(self):
        return str(self.id)

    def is_active(self):
        return self.active_account == 1


@login_manager.user_loader
def load_user(id_user):
    
    try:
    
        cbd.cursor.execute("SELECT id_user, id_roleeee, username, email, active_account FROM perfil WHERE id_user = %s", (id_user,))
        current_user_data = cbd.cursor.fetchone()
        print("Datos de usuario: ", current_user_data)

        if current_user_data:
            return Usuario(
                id_user=current_user_data[0],
                rol=current_user_data[1],
                username=current_user_data[2],
                email=current_user_data[3],
                active_account=current_user_data[4]
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

        elif current_user.rol != 1:
            errores ['mensaje'] = "No tienes permiso para acceder a esta página.", "warning"
            return redirect(url_for('inicio'))
        return f(*args, **kwargs)
    return decorated_function


@app.after_request
def apply_csp(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    # response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
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

def validaciones(names,surnames,username,phone_number,email,password):
    errors = {}
    valid = True
    nameregex = r"[^a-zA-Z\s]"
    usernameregex = r"[^\w.-]"
    emailregex = r"^(?!.*\.\.)[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    passwordregex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!.-_])([\w!.-_]|[^\s]){8,}$"

    if names.strip()=="" or len(names.strip())>50 or re.search(nameregex, names):
        valid = False
        errors['mensaje01'] = "Campo requerido, no más de 50 caracteres y sin caracteres especiales"
        errors['num_fieldset']= 0

    if surnames.strip()=="" or len(surnames.strip())>50 or re.search(nameregex, surnames):
        valid = False
        errors['mensaje02'] = "Campo requerido, no más de 50 caracteres y sin caracteres especiales"
        errors['num_fieldset']= 0

    elif username.strip()=="" or len(username.strip())>20 or re.search(usernameregex, username):
        valid = False
        errors['mensaje1'] = "Campo requerido, no más de 20 caracteres y sin espacios ni caracteres especiales"
        errors['num_fieldset']= 1

    elif phone_number.strip()==""  or len(phone_number.strip())<10 or len(phone_number.strip())>13 or not phone_number.isdigit():
        valid = False
        errors['mensaje2'] = "Campo de teléfono requerido, entre 10 y 13 caracteres"
        errors['num_fieldset']= 2

    elif email.strip()==""  or len(email.strip())<10 or len(email.strip())>150 or not re.search(emailregex, email):
        valid = False
        errors['mensaje3'] = "Campo de email requerido, entre 10 y 150 caracteres"
        errors['num_fieldset']= 2

    elif password.strip()==""  or len(password.strip())<8 or len(password.strip())>30 or not re.search(passwordregex, password):
        valid = False
        errors['mensaje4'] = "password requerida, entre 8 y 30 caracteres, con una letra mayúscula, una minúscula, un número, un caracter especial (!.-_) y sin espacios"
        errors['num_fieldset']= 3

    return valid, errors


@app.route ('/registration',  methods=['GET', 'POST'])
def registration():

    print(f"metodo en uso: {request.method}")
    form_data = request.form.to_dict() if request.method == 'POST' else {}
    if request.method == "POST":

        names = request.form.get('names')
        surnames = request.form.get('surnames')
        username = request.form.get('username')
        phone_number = request.form.get('phone_number')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        try:            
            form_data = {
                'names': names,
                'surnames': surnames,
                'username': username,
                'phone_number': phone_number,
                'email': email
            }

            errores = {}
    
            valid, errores = validaciones(names, surnames, username, phone_number, email, password)
            if not valid:
                return render_template("acceso/registration.html", **errores,  form_data=form_data)

            try:
                cbd.cursor.execute("SELECT username FROM perfil WHERE username = %s", (username,))
                username_exist = cbd.cursor.fetchone()

                cbd.cursor.execute("SELECT email FROM perfil WHERE email = %s", (email,))
                email_exist = cbd.cursor.fetchone()

                cbd.cursor.execute("SELECT phone_number FROM perfil WHERE phone_number = %s", (phone_number,))
                phone_number_exist = cbd.cursor.fetchone()
                
            except pymysql.Error as err:
                print(f"Error en la base de datos: {err}")
                errores['mensajes_db'] = "Hubo un problema en el registro, intente nuevamente"

                error_en_login=None

            try:            
                if username_exist:
                    errores['mensaje1'] = "Este nombre de usuario ya está en uso"
                    error_en_login=1

                elif phone_number_exist:
                    errores["mensaje2"] = "Este teléfono ya está en uso"
                    error_en_login=2

                elif email_exist:
                    errores["mensaje3"] = "Este email ya está en uso" 
                    error_en_login=2
                
                elif password != confirm_password:
                    errores["mensaje4"] =  "Las passwords que ingresaste no coinciden"
                    error_en_login=3

                else:        
                    confirm_password1 = str(confirm_password)
                    
                    cpe = os.getenv("PASSWORD3")
                    
                    encrypted_password = encrypted.encrypted_gcm(confirm_password1, cpe)

                    payload = {
                    'names' : names,
                    'surnames' : surnames,
                    'username' : username,
                    'phone_number' : phone_number,
                    'email' : email,
                    'encrypted_password' : encrypted_password,
                    'exp' : datetime.now(timezone.utc) + timedelta(hours=1)
                    }
                    
                    tokenregistro = jwt.encode(payload, os.getenv("PASSWORD2"), algorithm='HS256') 
                    
            except jwt.DecodeError as err:
                print("El error de jwt es: ", err)
                
            except jwt.InvalidTokenError as err:
                print("El error de jwt es: ", err)
                
            try:
                verify_domain.send_email(email, username)
                print("se envio el correo")
                
                session['tokenregistro'] = tokenregistro
                
                return render_template ("acceso/vericorreo_registration.html", mensaje1="Ingrese el código que le enviamos por correo")
            
            except Exception as err:
                print(f"el error es: {err}")

            print("quiere retonar ")     

            """if(error_en_login):
                print("NUM_FIELDSET ERROR",error_en_login)
                errores['num_fieldset']=error_en_login"""

            return render_template("acceso/registration.html", **errores,  form_data=form_data)    
           
        except pymysql.Error as err:
            return render_template("acceso/registration.html", mensaje="Error al procesar el registro",**errores, form_data=form_data)

    return render_template ("acceso/registration.html",form_data={})


@app.route ('/v_e_r', methods=['GET', 'POST'])
def v_e_r():

    verification_code = session.get('verification_code')
    tokenregistro = session.get('tokenregistro')
    
    if request.method == "POST":

        codigo = request.form.get('codigo')
        
        if not (str(codigo) == str(codigoveri)):
            return render_template("acceso/v_e_r.html", mensaje1= "Los códigos de verificación no coinciden")

        try:
            payload = jwt.decode(tokenregistro, os.getenv("PASSWORD2"), algorithms=['HS256'])

            names = payload['names']
            surnames = payload['surnames']
            username = payload['username']
            phone_number = payload['phone_number']
            email = payload['email']
            encrypted_password = payload['encrypted_password']
            
            try:
                print("INSERT INTO perfil (id_role, id_foto_perfil,  names, surnames, username, phone_number, email, encrypted_password, active_account) VALUES (3,1, '%s', '%s', '%s', '%s', '%s', '%s', 1)"%( names, surnames, username, phone_number, email, encrypted_password ))

                cbd.cursor.execute("INSERT INTO perfil (id_roleeeee, id_foto_perfil,  names, surnames, username, phone_number, email, encrypted_password, active_account) VALUES (3,1, %s, %s, %s, %s, %s, %s, 1)", ( names, surnames, username, phone_number, email, encrypted_password ))
                cbd.connection.commit()

                return render_template("acceso/login.html", mensaje1 = "Registro exitoso",form_data={})
                
            except pymysql.Error as er:
                print(er)
                return render_template("acceso/v_e_r.html", mensaje1 = "No se pudieron insertar los valores del registro")

        except jwt.InvalidTokenError:
            print("Token inválido.")
            return render_template("acceso/v_e_r.html")

    return render_template("acceso/v_e_r.html")


@app.route ('/login', methods=['GET', 'POST'])
def login():

    print(f"metodo en uso: {request.method}")

    form_data = request.form.to_dict() if request.method == 'POST' else {}
    if request.method == "POST" and 'email' in request.form and 'username' in request.form:

        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        print(email, username, password)
        
        try:            
            form_data = {
                'email': email,
                'username': username
            }
            
            errores = {}

            indexError=-1
            for casilla in (email,username,password):
                if casilla.strip()=="":
                    indexError+=1
                    break
            if indexError!=-1:
                errores['mensajeFieldset']= "Todos los campos son obligatorios"
                errores['num_fieldset']=indexError
                print("entro aca")
                return render_template("acceso/login.html", **errores, form_data=form_data)

            try:
                cbd.cursor.execute("SELECT id_user, id_role, username, email, phone_number, encrypted_password, active_account FROM perfil WHERE username = %s AND email = %s", (username, email))
                perfil_exist = cbd.cursor.fetchone()

                if perfil_exist is None:
                    errores ["mensajeFieldset"] = "El usuario no existe."
                    errores['num_fieldset']=0
                    print("el usuario no existe")
                    return render_template("acceso/login.html", **errores, form_data=form_data)
                
                id_usuario = perfil_exist[0]
                rol = perfil_exist[1]
                username_exist = perfil_exist[2]
                email_exist = perfil_exist[3]
                phone_number_exist = perfil_exist[4]
                encrypted_password = perfil_exist[5]  
                active_account = perfil_exist[6]

                print(perfil_exist)

                if (username == username_exist and email == email_exist):
                    
                    try:
                        cpe = os.getenv("PASSWORD3")
                        comprobacion_password = encrypted.verify_gcm(password, encrypted_password, cpe)
                        
                        if comprobacion_password:
                            
                            print("si llego al token")
                            payload = {
                            'id_usuario': id_usuario,
                            'rol': rol,
                            'username': username,
                            'email' : email,
                            'active_account': active_account,
                            'exp': datetime.now(timezone.utc) + timedelta(minutes=10) 
                            }

                            tokenacceso = jwt.encode(payload, os.getenv("PASSWORD2"), algorithm='HS256')
                            print("token generado: ",tokenacceso)

                            remitente = "peertopeerverificacion@gmail.com"
                            password = os.getenv("PASSWORD")
                            destinatario = email
                            codigoveri = random.randint(100000, 999999)

                            try:
                                asunto = "email de Verificación"
                                body = (f"Hola, {username}. Tu código para verificar que ingresaste un email de tu propiedad es: {codigoveri}")
                                                                                
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
                                print(f"El email no ha podido ser enviado: {err}")
                                return render_template("acceso/login.html", mensaje="Error al enviar el email de verificación.", form_data=form_data)

                            session['tokenacceso'] = tokenacceso
                            session['codigoveri'] = codigoveri
                            return redirect(url_for('veriemail_acceso'))
                        
                        else:
                            print("password incorrecta")
                            errores["mensajeFieldset"] = "password incorrecta"
                            errores['num_fieldset']=2
                            return render_template("acceso/login.html", **errores, form_data=form_data)
                        
                    except Exception as err:
                        print(f"Error durante la verificación de la password o generación del token: {err}")
                        return render_template("acceso/login.html", mensaje="Error interno al iniciar sesión", form_data=form_data)

                else:
                    print("El nombre de usuario o email no coinciden.")
                    errores ["mensajeFieldset"] = "El nombre de usuario o email no coinciden."
                    errores['num_fieldset']=0
                    return render_template("acceso/login.html", **errores, form_data=form_data)
            
            except pymysql.Error as err:
                print(f"Error de base de datos: {err}")
                return render_template("acceso/login.html", mensaje="Error al conectar con la base de datos.", form_data=form_data)
            
        except pymysql.Error as err:
            print("Error en primer Try de inicioSesion")
            return render_template("acceso/registro.html", mensaje="Error al procesar el registro",**errores, form_data=form_data)

    return render_template("acceso/login.html", form_data={})


@app.route ('/veriemail_acces', methods=['GET', 'POST'])
def veriemail_acceso():

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
                username = payload['username']
                email = payload['email']
                active_account = payload['active_account']
                
                if active_account == 1:
                    usuario = Usuario(id_usuario, rol, username, email, active_account)
                    login_user(usuario)

                    return render_template("inicio.html", mensaje1=f"¡Bienvenido {username}!")
                
                else:
                    print("La cuenta no está activa.")
                    return render_template("acceso/veriemail_acceso.html", mensaje1="La cuenta no está activa. Contacta con el administrador.")
                
            except jwt.ExpiredSignatureError:
                return render_template("acceso/veriemail_acceso.html", mensaje1="El token ha expirado")
            
            except jwt.InvalidTokenError:
                return render_template("acceso/veriemail_acceso.html", mensaje1="El token es inválido")
            
            except Exception as err:
                print("Error al decodificar el token:", err)
                return render_template("acceso/veriemail_acceso.html", mensaje1="No se pudo separar el token")
        
        else:
            print("Tu código de verificación no coincide")
            return render_template("acceso/veriemail_acceso.html", mensaje1="Tu código de verificación no coincide")

    return render_template("acceso/veriemail_acceso.html")


@app.route ('/cerrarsesion')
@login_required
def cerrarsesion():

    logout_user()

    return render_template("inicio.html", mensaje1 = "has cerrado sesion")


@app.route('/peticiones', methods=["GET", "POST"])
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
    
    return render_template("biblioteca/peticiones.html")


@app.route ('/categoria_peticion', methods=['GET', 'POST'])
@login_required
def categoria_peticion(): 
    
    myprint(f"categoria peticion")
    
    error=""
    fallido=None
    id_tema=-1
    id_categoria=-1
    tipo= ""
    if(request.method=='POST'):
        tipo = request.form.get('tipo')
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        id_categoria = request.form.get("listaTema")
        id_tema = request.form.get("listaSubtema")
            
            
        if not (tipo and nombre and descripcion):
            error="Debe llenar los campos correctamente"
        
        else: 
            try:
            
                if tipo == "categoria":

                    myprint(f"nombre={nombre}-/-{descripcion}")
                    res=cbd.crearCategoriaCompleta(nombre,descripcion)
                    
                    # cbd.cursor.execute("INSERT INTO categoria (codigo, nombre, descripcion) VALUES (%s, %s, %s)", (codigo, nombre, descripcion))
                    # cbd.connection.commit()
                    myprint(f"res={res}")
                    if(res==1):
                        error="Su categoria fue generada."
                    else:

                        errores=('ya existe la categoria','no se pudo hacer el registro de la categ','ya existe el tema general','no se pudo hacer el registro del tema','ya existe el subtema general','no se pudo hacer el registro del subtema')
                        error=errores[(res*-1)-1]
                    print(error)

                    # try:
                    
                    #     if nombre:
                            
                    #         cbd.cursor.execute("SELECT nombre FROM categoria WHERE nombre = %s", (nombre,))
                    #         nombre_exist = cbd.cursor.fetchone() 

                    #         if nombre_exist and nombre_exist[0] == nombre :  
                    #             error="La categoria que ingreso ya existe"
                    #             #return render_template("biblioteca/peticiones.html", error = "La categoria que ingreso ya existe")
                                
                    #         else:
                    #             cbd.cursor.execute("SELECT MAX(codigo) FROM categoria")
                    #             ultimo_codigo = cbd.cursor.fetchone()[0]  

                    #             if ultimo_codigo is None:
                    #                 ultimo_codigo = 0
                                    
                    #             else:
                    #                 ultimo_codigo = int(ultimo_codigo)

                    #             codigo = f"{ultimo_codigo + 1}"
                                
                    #             #return render_template ("biblioteca/peticiones.html", error= "Su categoria fue generada.")
                                
                    #     else:
                    #         error="Debe proporcionar un nombre de categoria válido."
                    #         #return render_template ("biblioteca/peticiones.html", error= "Debe proporcionar un nombre de categoria válido.")
                    
                    # except Exception as err:
                    #     error=f"Error al procesar la solicitud categoria: {err}"
                    #     #return render_template("biblioteca/peticiones.html", error=f"Error al procesar la solicitud categoria: {err}")
                
                elif tipo == "tema":

                    if nombre:
                        try:
                            if not id_categoria:
                                myprint("selecciona una categ")
                                error="DEBES SELECCIONAR UNA CATEGORIA"
                                fallido=1
                            else:
                                myprint("categ=",id_categoria)
                                # -3->Ya existe el tema
                                # !=0->exito
                                res=cbd.crearTema(id_categoria,nombre,descripcion)
                                if(res<0):
                                    error="Ya existe el Tema en la categoria"
                                else:
                                    error="Tema generado correctamente"
                            # cbd.cursor.execute("SELECT nombre FROM tema WHERE nombre = %s", (nombre,))
                            # nombre_exist1 = cbd.cursor.fetchone()

                            # if nombre_exist1 and nombre_exist1[0] == nombre:
                            #     error="El tema que ingresó ya existe"
                            #     #return render_template("biblioteca/peticiones.html", error="La categoría que ingresó ya existe")
                            # else:
                            #     cbd.cursor.execute("SELECT codigo FROM categoria")
                            #     codigo_padre = cbd.cursor.fetchone()[0]

                            #     cbd.cursor.execute("SELECT MAX(codigo) FROM tema WHERE codigo LIKE %s", (f"{codigo_padre}-%",))
                            #     ultimo_codigo1 = cbd.cursor.fetchone()[0]

                            #     if not id_categoria:
                            #         error="Seleccione una categoria para crear un tema"
                            #     else:

                            #         if ultimo_codigo1 is None:
                            #             nuevo_sub = 1
                            #         else:
                            #             nuevo_sub = int(ultimo_codigo1.split('-')[-1]) + 1

                            #         codigo = f"{codigo_padre}-{nuevo_sub}"

                            #         cbd.cursor.execute("INSERT INTO tema (codigo, nombre, descripcion, id_categoria) VALUES (%s, %s, %s, %s)",(codigo, nombre, descripcion, id_categoria))
                            #         cbd.connection.commit()
                            #         error="Tema generado correctamente"
                                
                        except Exception as err:
                            error=f"Error al procesar la solicitud: {err}"
                            #return render_template("biblioteca/peticiones.html", error=f"Error al procesar la solicitud: {err}")
                    else:
                        error="Debe proporcionar un nombre de tema válido."
                        #return render_template("biblioteca/peticiones.html", error="Debe proporcionar un nombre de categoría válido.")

                elif tipo == "subtema":
                    if nombre:
                        try:
                            
                            if not id_tema:
                                error="DEBES SELECCIONAR UN TEMA"
                                fallido=2
                            else:
                                # -5->ya xiste
                                # 1-> exito
                                res=cbd.crearSubtema(id_tema,nombre,descripcion)
                                myprint(res)
                                if(res<0):
                                    error="Ya existe el Subtema en el tema"
                                else:
                                    error="SubTema generado correctamente"
                            # cbd.cursor.execute("SELECT nombre FROM subtema WHERE nombre = %s", (nombre,))
                            # nombre_exist1 = cbd.cursor.fetchone()

                            # if nombre_exist1 and nombre_exist1[0] == nombre:
                            #     error="El subtema que ingresó ya existe"
                            #     #return render_template("biblioteca/peticiones.html", error="La categoría que ingresó ya existe")
                            # else:
                            #     cbd.cursor.execute("SELECT codigo FROM tema ")
                            #     codigo_padre = cbd.cursor.fetchone()[0]

                            #     cbd.cursor.execute("SELECT MAX(codigo) FROM subtema WHERE codigo LIKE %s", (f"{codigo_padre}-%",))
                            #     ultimo_codigo1 = cbd.cursor.fetchone()[0]

                            #     if ultimo_codigo1 is None:
                            #         nuevo_sub1 = 1
                            #     else:
                            #         nuevo_sub1 = int(ultimo_codigo1.split('-')[-1]) + 1

                            #     nuevo_codigo = f"{codigo_padre}-{nuevo_sub1}"

                            #     if not id_tema:
                            #         error = "Seleccione un tema para crear un subtema"
                            #     else:

                            #         cbd.cursor.execute("INSERT INTO subtema (codigo, nombre, descripcion, id_tema) VALUES (%s, %s, %s, %s)",(nuevo_codigo, nombre, descripcion, id_tema))
                            #         cbd.connection.commit()
                            #         error="Subtema creado con éxito"
                            #         #return render_template("biblioteca/peticiones.html", mensaje="Categoría creada con éxito.")
                        except Exception as err:
                            error=f"Error al procesar la solicitud: {err}"
                            #return render_template("biblioteca/peticiones.html", error=f"Error al procesar la solicitud: {err}")
                    else:
                        error="Debe proporcionar un nombre de subtema válido."
                        #return render_template("biblioteca/peticiones.html", error="Debe proporcionar un nombre de categoría válido.")
            

                else:
                    myprint ("no se pudo enviar") 
                    error="Opción escogida incorrecta"       

            except Exception as err:
                myprint("SU PTM NO JALO")
                error=f"Error no sé: {err}"
                
    cbd.cursor.execute("SELECT id_categoria, nombre FROM categoria")
    resultados = cbd.cursor.fetchall()     

    list_items_html_cate = ""
    for resultado in resultados:
        idc = resultado[0]
        nombre = resultado[1] 

        list_items_html_cate += f'<option value="{idc}" {"selected" if int(id_categoria)==idc else ""}>{nombre}</option>'


    cbd.cursor.execute("SELECT id_tema, nombre FROM tema")
    resultados = cbd.cursor.fetchall()     
    myprint("resultados: ",resultados)

    list_items_html_tema = ""
    for resultado in resultados:
        idt = resultado[0]
        nombre = resultado[1] 
        list_items_html_tema += f'<option value="{idt}" {"selected" if int(id_tema)==idt else ""} >{nombre}</option>'

    return render_template ("biblioteca/categoria_peticion.html", items_cate = list_items_html_cate, items_tema=list_items_html_tema, error=error if error!="" else None, tipo=tipo)


@app.route('/documento_peticion', methods=['GET', 'POST'])
@login_required
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
@login_required
def inicio_biblioteca():
    categorias=cbd.ejecutarQuery("select id_categoria,nombre,descripcion from categoria order by id_categoria asc ,nombre asc;",fetch=0)
    
    # temas=separarSubCategorias(cbd.ejecutarQuery("select id_tema,id_categoria,nombre,descripcion from tema order by id_categoria asc ,nombre asc;",fetch=0))
    temas=separarSubCategorias(cbd.ejecutarQuery("""
    select t.id_tema,t.id_categoria,t.nombre,t.descripcion from tema t 
	join categoria c on t.id_categoria=c.id_categoria 
    order by id_categoria asc,id_tema asc""",fetch=0))

    # subtemas=separarSubCategorias(cbd.ejecutarQuery("select id_subtema,id_tema,nombre,descripcion from subtema order by id_tema;",fetch=0),returnLen=True)
    subtemas=separarSubCategorias(cbd.ejecutarQuery("""
    select s.id_subtema,s.id_tema,s.nombre,s.descripcion from subtema s 
	join tema t on s.id_tema=t.id_tema 
    join categoria c on t.id_categoria=c.id_categoria
    order by c.id_categoria asc, t.id_tema asc, id_subtema asc """,fetch=0),returnLen=False)
    
    myprint("temas=",temas)
    myprint("subtemas=",subtemas)
    return render_template("biblioteca/inicio_biblioteca.html",categorias=categorias,Temas=temas
        ,Subtemas=subtemas,
        limiteTemas=len(temas),
        limiteSubtemas=len(subtemas)
        ,biblioteca=True
    )
def separarSubCategorias(tupla,returnLen=False):
    nuevoOrden=()
    nivel=()
    longitud_registros=len(tupla)
    for index in range(longitud_registros):
        if(nivel==()):
            nivel+=tupla[index][1], # id del padre como primera posicion
        nivel+=(tupla[index][0],tupla[index][2],tupla[index][3]), #generas un nivel con los datos del hijo
        try:
            if(tupla[index][1]!=tupla[index+1][1]): 
                #entra si el siguiente elemento es de un padre diferente
                    #es decir, llegaste al final de los hijos del actual
                if(returnLen):
                    nivel+=len(nivel)-1, # agregamos la cantidad de hijos
                nuevoOrden+=nivel, #agregamos al nuevo orden
                nivel=() #refrescamos el nivel
        except Exception as ex:
            nuevoOrden+=nivel, #salta cuando llegas al final de la tupla
    return nuevoOrden

@app.route('/docs')
def documentos():
    print("#_#_#_#_ ENTRASTE A DOCS")
    # cbd.cursor.execute("select id_documento,nombre_archivo from documentos")
    # docs=cbd.cursor.fetchall()
    cbd.cursor.execute("select id_foto,foto from fotos_perfil")
    docs=cbd.cursor.fetchall()


    return render_template("biblioteca/documentos.html",docs=docs)
    
@app.route('/uploads/<int:id>')
def view_file(id):
    cbd.cursor.execute("select foto from fotos_perfil where id_foto=%s"%(id))
    doc=cbd.cursor.fetchone()
    if(doc):
        response= make_response(doc[0])
        response.headers.set('Content-Type','image/webp')
        response.headers.set('Content-Disposition','inline')
        return response
        # return send_file(io.BytesIO(doc[0]),as_attachment=True)
    return "DOC NO ENCONTRADO"
    # cbd.cursor.execute("select nombre_archivo,documento from documentos where id=%s"%(id))
    # doc=cbd.cursor.fetchone()
    # if(doc):
    #     return send_file(io.BytesIO(doc['documento']),nombre=doc['nombre_archivo'],as_attachment=True)
    # return "DOC NO ENCONTRADO"

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
            myprint("\nTipo archivo: ",tipomime.mime, " Nombre: ", archivobinario.name)

            return Response(archivobinario, headers={"Content-Disposition": f"inline; filename=\"{nombrearchivo}\""}, mimetype=tipomime.mime)
        
        else:
            return render_template("inicio.html", mensaje1 = "No se pudo obtener el archivo")

    except pymysql.Error as err:
        myprint("Error: ", err)
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
    username = current_user.username
    
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
        session["nombre"] = current_user.username
        #print(f"\n\n'room: ', {room}, 'nombre: ', {current_user.username}\n\n")
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
    cbd.cursor.execute("SELECT m.id_msj,m.id_usuario,p.username,m.id_sala,m.mensaje,DATE_FORMAT(m.fecha,'%%d-%%m-%%Y'),m.hora FROM mensaje m, sala s, perfil p WHERE m.id_sala=s.id_sala AND m.id_usuario=p.id_usuario AND s.id_sala=%s ORDER BY m.id_msj DESC LIMIT 100", (idsala[0]))
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
        cbd.cursor.execute("SELECT id_usuario, username, names, surnames, email, phone_number, active_account FROM perfil")
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
            cbd.cursor.execute("UPDATE perfil SET active_account = 0 WHERE id_usuario = %s", (id_usuario))
            cbd.connection.commit()
        
        elif statusAcc == 0:
            cbd.cursor.execute("UPDATE perfil SET active_account = 1 WHERE id_usuario = %s", (id_usuario))
            cbd.connection.commit()
        
    except pymysql.Error as err:
        print(f"No se pudo actualizar el estado de la cuenta: {err}")

    return redirect(url_for('crudusuariosadmin'))

@app.route('/crudpeticionesadmin')
@login_required
@admin_required
def crudpeticionesadmin():
    try:
        cbd.cursor.execute("SELECT pet.id_peticiones, pet.id_usuario, per.username, per.email, pet.mensaje, pet.archivo, pet.link, pet.fecha, pet.hora FROM perfil per JOIN peticiones pet ON per.id_usuario = pet.id_usuario")
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
    
