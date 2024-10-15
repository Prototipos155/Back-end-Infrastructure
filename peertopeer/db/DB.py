import pymysql
import re

class CC():
    
    def __init__(self):
        try:
            self.connection = pymysql.connect(host='localhost', user=self.usuarioXampp, passwd='', port=self.puertoXampp, db='peertopeer')
            self.cursor = self.connection.cursor()
            print("\n Conexion exitosa")

            try:
                self.tabla_perfil()
                self.tabla_peticiones()
                self.tabla_filtro_archivos()

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


    def tabla_perfil(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS perfil 
                (id_perfil int unique auto_increment not null,
                nivel varchar (15) not null,
                nombres varchar (50) not null,
                apellidos varchar (50) not null,
                apodo varchar(20) unique not null,
                correo varchar(150) unique not null,
                telefono varchar(12) unique not null,
                contraseña_encript varchar(256) not null)""")
            print("tabla perfil creada")

        except pymysql.Error as er:
            print("\nla tabla perfil no fue creada: ", er)

    def tabla_peticiones(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS peticiones
                (id_peticion int not null auto_increment,
                id_perfil int not null,
                mensaje varchar (256) not null,
                archivo BLOB null,
                fecha varchar (11) not null,
                hora varchar (15) not null,
                                
                primary key (id_peticion),
                foreign key(id_perfil) references perfil(id_perfil)) """)
            print ("tabla peticiones creada")

        except pymysql.Error as er:
            print("\nla tabla peticiones no fue creada: ", er)

    def tabla_filtro_archivos(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS filtro_archivos(
                id_filtro int not null auto_increment
                                
                id_perfil int not null,
                archivo BLOB NOT NULL,
                            
                foreign key(id_perfil) references perfil(id_perfil))""")
            print("Tabla filtro archivos creada")
            
        except pymysql.Error as er:
            print("\la tabla filtro archivos no fue creada ")



