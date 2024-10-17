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
                self.tabla_buzon_quejas()
                self.tabla_categorias()
                self.tabla_subcategorias()

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
            CREATE TABLE IF NOT EXISTS perfil (
                id_perfil INT UNIQUE AUTO_INCREMENT NOT NULL,
                nivel VARCHAR (15) NOT NULL,
                nombres VARCHAR (50) NOT NULL,
                apellidos VARCHAR (50) NOT NULL,
                apodo VARCHAR(20) UNIQUE NOT NULL,
                correo VARCHAR(150) UNIQUE NOT NULL,
                telefono VARCHAR(12) UNIQUE NOT NULL,
                contraseña_encript varchar(256) not null,
                cuenta_activa TINYINT not null)""")
            print("tabla perfil creada")

        except pymysql.Error as er:
            print("\nla tabla perfil no fue creada: ", er)

    def tabla_peticiones(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS peticiones(
                id_peticion INT UNIQUE NOT NULL AUTO_INCREMENT,
                id_perfil INT NOT NULL,
                mensaje VARCHAR (256) NOT NULL,
                archivo BLOB null,
                fecha VARCHAR (11) NOT NULL,
                hora VARCHAR (15) NOT NULL,
                                
                PRIMARY KEY (id_peticion),
                FOREIGN KEY (id_perfil) REFERENCES perfil(id_perfil)) """)
            print ("tabla peticiones creada")

        except pymysql.Error as er:
            print("\nla tabla peticiones no fue creada: ", er)

    def tabla_filtro_archivos(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS filtro_archivos(
                id_filtro INT UNIQUE NOT NULL AUTO_INCREMENT,
                id_peticion INT NOT NULL,            
                id_perfil INT NOT NULL,
                fecha VARCHAR (11) NOT NULL,
                hora VARCHAR (12) NOT NULL,
                verificado TINYINT NULL,
                            
                PRIMARY KEY(id_filtro),
                FOREIGN KEY(id_perfil) REFERENCES perfil(id_perfil))""")
            print("Tabla filtro archivos creada")
            
        except pymysql.Error as er:
            print("\nla tabla filtro archivos no fue creada ")

    def tabla_buzon_quejas(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS buzon_quejas(
                id_buzon_quejas INT UNIQUE AUTO_INCREMENT NOT NULL,
                id_perfil INT NOT NULL,
                mensaje VARCHAR(256) NOT NULL,
                fecha VARCHAR(11) NOT NULL,
                hora VARCHAR(12) NOT NULL, 

                PRIMARY KEY(id_buzon_quejas),
                FOREIGN KEY(id_perfil) REFERENCES perfil(id_perfil))""")
            print("Tabla buzon quejas creada")

        except pymysql.Error as er:
            print(f"la tabla buzon quejas no fue creada: ", er)

    def tabla_categorias(self):
        try:
            self.cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS categorias(
                id_categoria INT UNIQUE AUTO_INCREMENT NOT NULL,
                categoria VARCHAR (90) NOT NULL,
                                    
                PRIMARY KEY(id_categoria) )""")
            print("Tabla categorias creada") 

        except pymysql.Error as er:
            print("\nla tabla categorias no fue creada ",er)

    def tabla_subcategorias(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS subcategorias(
                id_subcategorias INT UNIQUE AUTO_INCREMENT NOT NULL,
                id_filtro INT NOT NULL,
                subcategoria VARCHAR (45) NOT NULL,
                                
                PRIMARY KEY(id_subcategorias),
                FOREIGN KEY(id_filtro) REFERENCES filtro_archivos(id_filtro))""")
            print("la tabla subcategoria creada ")

        except pymysql.Error as er:
            print("\nla tabla subcategorias no fue creada ",er)


