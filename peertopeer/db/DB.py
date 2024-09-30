import pymysql
import re

class CC():
    
    def __init__(self):
        try:
            self.connection = pymysql.connect(host='localhost', user=self.usuarioXampp, passwd='', port=self.puertoXampp, db='peertopeer')
            self.cursor = self.connection.cursor()
            print("\n Conexion exitosa")

            try:
                self.tabla_departamento()
                self.tabla_administrador()
                self.tabla_nivelacademico()
                self.tabla_perfil()
                self.tabla_alumno()
                self.tabla_tutor()
                self.tabla_administrador()
                self.tabla_asignatura()
                self.tabla_tutorias()
                self.tabla_tutorias_alumno()
                self.tabla_tutorias_mensajes()
                self.tabla_guardar_documentos()
                self.tabla_documentos_tutorias()
                self.tabla_catalogo_quejas()

            except pymysql.Error as err:
                print("\n error al intentar crear las tablas " .format(err))

            
        except pymysql.Error as err:
            self.connection = pymysql.connect(host='localhost', user=self.usuarioXampp, passwd='', port=self.puertoXampp)
            self.cursor = self.connection.cursor()
            self.cursor.execute("CREATE DATABASE IF NOT EXISTS peertopeer")
            self.connection.commit()
            self.cursor.execute("USE peertopeer")
            print("\nCreacion exitosa")


    def detectarPuertosXampp(rutaXampp='C:/xampp/mysql/bin/my.ini'):
        try:
            with open(rutaXampp, 'r') as archivo:
                contenido = archivo.read()


            resultado_puerto = re.search(r'port[ ]*=[ ]*(\d+)', contenido)
            if resultado_puerto:
                puerto = int(resultado_puerto.group(1))  
                
            else:
                print("No hay puerto predeterminado")
                puerto =  None
            

            resultado_usuario = re.search(r'user[ ]*=[ ]*(\w+)', contenido)
            if resultado_usuario:
                usuario = resultado_usuario.group(1)
                
            else:
                print("No se encontró un nombre de usuario")
                usuario = "root"
            return puerto, usuario

        except FileNotFoundError:
            print(f"No se encontro Xampp en la ruta {rutaXampp}")
            return None, None
        

    """def detectarPuertoApache(rutaApache='C:/xampp/apache/conf/httpd.conf'):
        try:
            with open(rutaApache, 'r') as archivo:
                contenido = archivo.read()


            resultados = re.findall(r'^Listen[ ]+(\d+)', contenido, re.MULTILINE)
            if resultados:
                return [int(puerto) for puerto in resultados]
            else:
                print("No se encontraron datos 'Listen' en el archivo")
                return None
        except FileNotFoundError:
            print(f"No se pudo encontrar el archivo de configuración en {rutaApache}.")
            return None"""


    puertoXampp, usuarioXampp = detectarPuertosXampp()
    if puertoXampp:
        print(f"\nEl puerto de MySQL es {puertoXampp}")
        print(f"El nombre de usuario de MySQL es {usuarioXampp}")
    else:
        print("No se pudo encontrar el puerto de Xampp")


    """puertoApache = detectarPuertoApache()
    if puertoApache:
        print(f"El puerto de Apache es {puertoApache}")
    else:
        print("No se pudo encontrar")"""
    
    def tabla_departamento(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS departamento(
                    iddepartamento int primary key auto_increment not null,
                    nombre varchar(50) not null)""")
            print("tabla nivel departamento creada")

        except pymysql.Error as er: 
            print("\n la tabla nivel v no fue creada: ",er)

    def tabla_nivelacademico(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS nivelacademico
                    (idNivel int primary key auto_increment not null,
                    nivel varchar(15) not null)""")
            print("tabla nivel academico creada")

        except pymysql.Error as er:
            print("\n la tabla nivel academico no fue creada: ",er)


    def tabla_perfil(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS perfil 
                (id_perfil int unique auto_increment not null,
                rol varchar (20) not null,
                numcontrol varchar(20) primary key not null,
                nombres varchar (40) not null,
                apellidos varchar (40) not null,
                apodo varchar(10) unique not null,
                correo varchar(150) unique not null,
                telefono varchar(10) unique not null,
                grado varchar (1) not null,
                grupo varchar (1) not null,
                contraseña_encript varchar(256) not null)""")
            print("tabla perfil creada")

        except pymysql.Error as er:
            print("\nla tabla perfil no fue creada: ", er)

    def tabla_alumno(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS alumno 
                (id_perfil int primary key not null,
                apodo varchar(30) unique not null, 
                grado int not null, 
                grupo varchar(1) not null, 
                foreign key (id_perfil) references perfil(id_perfil))""")
            print("tabla alumno creada")
        
        except pymysql.Error as er:
            print("\nla tabla alumno o fue creada: ", er)

    
    def tabla_tutor(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tutor(
                idperfil int unique not null,
                nombres varchar(50) not null,
                apellidos varchar(50) not null,
                numTarjetaBienestar varchar(16) unique not null,
                
                nombreEscuela varchar(100) not null,
                idGradoAvance int not null,


                foreign key (idperfil) references perfil(id_perfil),
                foreign key(idGradoAvance) references nivelAcademico(idNivel))""")
            print("Tabla tutor creada")
    
        except pymysql.Error as er:
            print("\nLa tabla tutor no fue creada:", er)

    def tabla_administrador(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS administrador(
                idperfil int primary key  not null,
                departamento int not null,
                nombres varchar(30) not null,
                apellidos varchar(30) not null,
                                
                claveacceso varchar(10) not null,
                                
                foreign key (idperfil) references perfil(id_perfil),
                foreign key (departamento) references departamento(iddepartamento))""")
            print("Tabla administrador creada")
            
        except pymysql.Error as er:
            print("\nLa tabla administrador no fue creada:", er)

    def tabla_asignatura(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS asignatura(
                idasignatura int primary key auto_increment not null,
                nombre varchar(20) not null,
                descripcion varchar(200) not null,
                tutoriasActivas int not null)""")
            print("Tabla asignatura creada")

        except pymysql.Error as er:
            print("\nLa tabla asignatura no fue creada:", er)

    def tabla_tutorias(self):
        try:
            self.cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS tutorias(
                idtutoria int primary key auto_increment not null,
                nombretutoria varchar(50) not null,
                enlaceVideollamada varchar(30) not null,
                horario varchar(150) not null,
                idtutor int not null,
                idasignatura int not null,

                foreign key (idtutor) references perfil(id_perfil),
                foreign key (idasignatura) references asignatura(idasignatura))""")
            print("Tabla tutorias creada")

        except pymysql.Error as er:
            print("\nLa tabla tutorias no fue creada:", er)

    def tabla_tutorias_alumno(self):
        try:
            self.cursor.execute("""  
            CREATE TABLE IF NOT EXISTS tutorias_alumno(
                idregistro int primary key auto_increment not null,
                idtutoria int not null,
                idalumno int not null,
                fechaInicio date not null,
                fechaFin date not null,

                foreign key(idtutoria) references tutorias(idtutoria),
                foreign key(idalumno) references perfil(id_perfil))""")
            print("Tabla tutorias alumno creada")

        except pymysql.Error as er:
            print("\nLa tabla tutorias alumno no fue creada:", er)

    def tabla_tutorias_mensajes(self):
        try:
            self.cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS tutorias_mensajes(
                idmensaje int primary key auto_increment not null,
                idtutoria int not null,
                idperfil int not null,
                fechaenvio date not null,
                horaenvio time not null,
                mensaje varchar(150) not null,
                
                important boolean  not null,
                
                foreign key(idtutoria) references tutorias(idtutoria),
                foreign key(idperfil) references perfil(id_perfil))""")
            print("Tabla tutorias mensajes creada")

        except pymysql.Error as er:
            print("\nLa tabla tutorias mensajes no fue creada:", er)

    def tabla_guardar_documentos(self):
        try:
            self.cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS guardar_documentos(
                #idea : guardar los documentos en drive y acceder por la url
                iddocumento int primary key auto_increment not null,
                url varchar(100) not null)""")
            print("Tabla guardar documentos creada")

        except pymysql.Error as er:
            print("\nLa tabla guardar documentos no fue creada:", er)

    def tabla_documentos_tutorias(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS documentos_tutorias(
                idregistro int primary key auto_increment not null,
                idtutoria int not null,
                iddocumento int not null,
                                
                foreign key(idtutoria) references tutorias(idtutoria),
                foreign key(iddocumento) references guardar_documentos(iddocumento))""")
            print("Tabla documentos tutorias creada")

        except pymysql.Error as er:
            print("\nLa tabla documentos tutorias no fue creada:", er)

    def tabla_catalogo_quejas(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS catalogo_quejas(
                idQueja int primary key auto_increment not null,
                descripcion varchar(30) not null)""")
            print("Tabla catalogo quejas  creada")

        except pymysql.Error as er:
            print("\nLa tabla catalogo quejas no fue creada:", er)



