import pymysql
from colorama import Back,Fore
import re
import os

class CC():
    def __init__(self):
        try:
            self.connection = pymysql.connect(host='localhost', user=self.usuarioXampp, passwd='', port=self.puertoXampp, db='peertopeer')
            self.cursor = self.connection.cursor()
            print("\n Conexion exitosa")

            try:
                self.crearTablas()

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
        

    '''def detectarPuertoApache(rutaApache='C:/xampp/apache/conf/httpd.conf'):
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
            return None'''


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

    def crearTablas(self):
        try:
            print("empezo la creacion de tablas")
            self.tabla_perfil()
            self.tabla_buzon_quejas()
            self.tabla_categoria()
            self.tabla_subcategoria()
            self.tabla_peticiones()
            self.tabla_documentos()
            self.tabla_links()

        except pymysql.Error as err:
            print("\n error al intentar crear las tablas " .format(err))
    
    def tabla_perfil(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS perfil (
                id_usuario INT UNIQUE AUTO_INCREMENT NOT NULL,
                rol VARCHAR (15) NOT NULL, 
                nombres VARCHAR (50) NOT NULL,
                apellidos VARCHAR (50) NOT NULL,
                nombre_usuario VARCHAR(20) UNIQUE NOT NULL,
                correo VARCHAR(150) UNIQUE NOT NULL,
                telefono VARCHAR(13) UNIQUE NOT NULL,
                contraseña_encript VARCHAR (256) NOT NULL,
                cuenta_activa BOOLEAN NOT NULL)""")
            
            print("la tabla perfil creada ")

        except pymysql.Error as err:
            print("la tabla perfil no fue creada ",err)

    def tabla_buzon_quejas(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS buzon_quejas (
                id_buzon_quejas INT UNIQUE AUTO_INCREMENT NOT NULL,
                id_usuario INT NOT NULL,
                                
                mensaje VARCHAR(256) NOT NULL,
                fecha DATETIME NOT NULL,
                hora DATETIME NOT NULL,
                                
                PRIMARY KEY (id_buzon_quejas),
                FOREIGN KEY (id_usuario) REFERENCES perfil(id_usuario))""")
            
            print("la tabla buzon_quejas creada ")

        except pymysql.Error as err:
            print("la tabla buzon_quejas no fue creada ",err)

    def tabla_categoria(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS categoria (
              id_categoria INT UNIQUE AUTO_INCREMENT NOT NULL,
                                
              nombre VARCHAR(100) NOT NULL,
              descripcion VARCHAR(150) NOT NULL,
                                
              PRIMARY KEY (id_categoria))""")
            
            print("la tabla categoria creada ")

        except pymysql.Error as err:
            print("la tabla categoria no fue creada ",err)

    def tabla_subcategoria(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS subcategoria (
              id_subcategoria INT UNIQUE AUTO_INCREMENT NOT NULL,
              id_categoria INT NOT NULL,

              nombre VARCHAR(100) NOT NULL,
              descripcion VARCHAR(150) NOT NULL,
                                
              PRIMARY KEY (id_subcategoria),
              FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria))""")
            
            print("la tabla subcategoria creada ")

        except pymysql.Error as err:
            print("la tabla subcategoria no fue creada ",err)

    '''def tabla_mensajes_from_seccion(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS mensajes_from_seccion (
              id_mensaje INT NOT NULL AUTO_INCREMENT,
              id_seccion INT NOT NULL,
              id_usuario INT NOT NULL,
              mensaje VARCHAR(256) NOT NULL,
              fecha VARCHAR(11) NOT NULL,
              hora VARCHAR(12) NOT NULL,
              PRIMARY KEY (id_mensaje),
              INDEX fk_mensaje_seccion1_idx (id_seccion ASC) VISIBLE,
              INDEX fk_mensaje_perfil1_idx (id_usuario ASC) VISIBLE,
              CONSTRAINT fk_mensaje_seccion1
                FOREIGN KEY (id_seccion)
                REFERENCES peertopeer.seccion (id_seccion)
                ON DELETE NO ACTION
                ON UPDATE NO ACTION,
              CONSTRAINT fk_mensaje_perfil1
                FOREIGN KEY (id_usuario)
                REFERENCES peertopeer.perfil (id_usuario)
                ON DELETE NO ACTION
                ON UPDATE NO ACTION)
            ENGINE = InnoDB
            DEFAULT CHARACTER SET = utf8mb3""")
            print("la tabla mensajes_from_seccion creada ")
        except pymysql.Error as er:
            print("la tabla mensajes_from_seccion no fue creada ",er)'''

    def tabla_peticiones(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS peticiones (
                id_peticiones INT UNIQUE AUTO_INCREMENT NOT NULL, 
                id_usuario INT NOT NULL,
                                    
                mensaje VARCHAR(200) NULL,
                archivo MEDIUMBLOB NULL,
                nombre_archivo varchar(256) NULL,
                link VARCHAR(256) NULL,
                fecha DATE NOT NULL,
                hora TIME NOT NULL,
                                    
                PRIMARY KEY(id_peticiones),
                FOREIGN KEY (id_usuario) REFERENCES perfil(id_usuario))""") 
            
            print("la tabla peticones creada ")

        except pymysql.Error as err:
            print("la tabla peticion no fue creada ",err)

    def tabla_documentos(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS documentos (
              id_documento INT UNIQUE AUTO_INCREMENT NOT NULL,
                                
              documento MEDIUMBLOB NOT NULL,
              nombre_archivo varchar(256) NULL,
                                
              PRIMARY KEY (id_documento))""")
            
            print("la tabla documentos creada ")

        except pymysql.Error as er:
            print("la tabla documentos no fue creada ",er)

    def tabla_links(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS links (
              id_link INT UNIQUE AUTO_INCREMENT NOT NULL,
                                
              link VARCHAR(256) NOT NULL,
                                
              PRIMARY KEY (id_link))""")
            
            print("la tabla links creada ")

        except pymysql.Error as err:
            print("la tabla links no fue creada ",err)

    """def tabla_peticion_has_files(self):
        try:
            self.cursor.execute(
            CREATE TABLE IF NOT EXISTS peticion_has_files (
              id_archivo INT NOT NULL AUTO_INCREMENT,
              id_peticion INT NOT NULL,
              id_material INT NOT NULL,
              tipo TINYINT NOT NULL,
              verificado TINYINT NULL,
              PRIMARY KEY (id_archivo),
              INDEX fk_peticion_has_files_peticion1_idx (id_peticion ASC) VISIBLE,
              CONSTRAINT fk_peticion_has_files_peticion1
                FOREIGN KEY (id_peticion)
                REFERENCES peertopeer.peticion (id_peticion)
                ON DELETE NO ACTION
                ON UPDATE NO ACTION))
            print("la tabla peticion_has_files creada ")
        except pymysql.Error as er:
            print("la tabla peticion_has_files no fue creada ",er)"""

    # def tabla_seccion_has_files(self):
    #     try:
    #         self.cursor.execute("""
    #         CREATE TABLE IF NOT EXISTS seccion_has_files (
    #           `id_seccion_file` INT NOT NULL AUTO_INCREMENT,
    #           `id_seccion` INT NOT NULL,
    #           `id_archivo` INT NOT NULL,
    #           PRIMARY KEY (`id_seccion_file`),
    #           INDEX `fk_seccion_has_files_seccion1_idx` (`id_seccion` ASC) VISIBLE,
    #           INDEX `fk_seccion_has_files_peticion_has_files1_idx` (`id_archivo` ASC) VISIBLE,
    #           CONSTRAINT `fk_seccion_has_files_seccion1`
    #             FOREIGN KEY (`id_seccion`)
    #             REFERENCES `peertopeer`.`seccion` (`id_seccion`)
    #             ON DELETE NO ACTION
    #             ON UPDATE NO ACTION,
    #           CONSTRAINT `fk_seccion_has_files_peticion_has_files1`
    #             FOREIGN KEY (`id_archivo`)
    #             REFERENCES `peertopeer`.`peticion_has_files` (`id_archivo`)
    #             ON DELETE NO ACTION
    #             ON UPDATE NO ACTION)
    #         ENGINE = InnoDB""")
    #         print("la tabla seccion_has_files creada ")
    #     except pymysql.Error as er:
    #         print("la tabla seccion_has_files no fue creada ",er)

    def tabla_motivos_de_quejas(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS motivos_de_quejas (
              id_motivo INT UNIQUE AUTO_INCREMENT NOT NULL,
                                
              motivo VARCHAR(30) NOT NULL,
                                
              PRIMARY KEY (`id_motivo`))""")
            
            print("la tabla motivos_de_quejas creada ")

        except pymysql.Error as err:
            print("la tabla motivos_de_quejas no fue creada ",err)

    '''def tabla_queja_has_motivos(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS queja_has_motivos (
              id_registro INT NOT NULL AUTO_INCREMENT,
              id_queja INT NOT NULL,
              id_motivo INT NOT NULL,
              INDEX `fk_queja_has_motivos_buzon_quejas1_idx` (`id_queja` ASC) VISIBLE,
              INDEX `fk_queja_has_motivos_motivos_de_quejas1_idx` (`id_motivo` ASC) VISIBLE,
              PRIMARY KEY (`id_registro`),
              CONSTRAINT `fk_queja_has_motivos_buzon_quejas1`
                FOREIGN KEY (`id_queja`)
                REFERENCES `peertopeer`.`buzon_quejas` (`id_buzon_quejas`)
                ON DELETE NO ACTION
                ON UPDATE NO ACTION,
              CONSTRAINT `fk_queja_has_motivos_motivos_de_quejas1`
                FOREIGN KEY (`id_motivo`)
                REFERENCES `peertopeer`.`motivos_de_quejas` (`id_motivo`)
                ON DELETE NO ACTION
                ON UPDATE NO ACTION)
            ENGINE = InnoDB""")
            print("la tabla queja_has_motivos creada ")
        except pymysql.Error as er:
            print("la tabla queja_has_motivos no fue creada ",er)'''

    '''def tabla_queja_has_razon_extra(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS queja_has_razon_extra (
              `id_registro` INT NOT NULL AUTO_INCREMENT,
              `razon` VARCHAR(250) NOT NULL,
              `id_queja` INT NOT NULL,
              INDEX `fk_queja_has_razon_extra_buzon_quejas1_idx` (`id_queja` ASC) VISIBLE,
              PRIMARY KEY (`id_registro`),
              CONSTRAINT `fk_queja_has_razon_extra_buzon_quejas1`
                FOREIGN KEY (`id_queja`)
                REFERENCES `peertopeer`.`buzon_quejas` (`id_buzon_quejas`)
                ON DELETE NO ACTION
                ON UPDATE NO ACTION)
            ENGINE = InnoDB""")
            print("la tabla queja_has_razon_extra creada ")
        except pymysql.Error as er:
            print("la tabla queja_has_razon_extra no fue creada ",er)'''

    def tabla_bloqueados(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS bloqueados (
              id_bloqueo` INT NOT NULL AUTO_INCREMENT,
              id_usuario_bloqueado INT NOT NULL,
                                
              PRIMARY KEY (id_bloqueo),
              FOREIGN KEY (id_usuario) REFERENCES perfil(id_usuario)""")
            print("la tabla bloqueados creada ")
        except pymysql.Error as err:
            print("la tabla bloqueados no fue creada ",err)

    '''def tabla_preguntas(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS preguntas (
              `id_preguntas` INT NOT NULL AUTO_INCREMENT,
              `pregunta` VARCHAR(256) NOT NULL,
              `fecha` DATE NOT NULL,
              `hora` TIME NOT NULL,
              `solucionada` TINYINT NOT NULL,
              `id_seccion` INT NOT NULL,
              PRIMARY KEY (`id_preguntas`),
              INDEX `fk_preguntas_seccion1_idx` (`id_seccion` ASC) VISIBLE,
              CONSTRAINT `fk_preguntas_seccion1`
                FOREIGN KEY (`id_seccion`)
                REFERENCES `peertopeer`.`seccion` (`id_seccion`)
                ON DELETE NO ACTION
                ON UPDATE NO ACTION)
            ENGINE = InnoDB""")
            print("la tabla preguntas creada ")
        except pymysql.Error as er:
            print("la tabla preguntas no fue creada ",er)

    def tabla_pregunta_has_respuestas(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS pregunta_has_respuestas (
              `id_respuesta` INT NOT NULL AUTO_INCREMENT,
              `id_pregunta` INT NOT NULL,
              `id_salvador` INT NOT NULL,
              `mensaje` VARCHAR(250) NOT NULL,
              `fecha` DATE NOT NULL,
              `hora` TIME NOT NULL,
              `likes` INT NOT NULL,
              `fijado` TINYINT NOT NULL,
              PRIMARY KEY (`id_respuesta`),
              INDEX `fk_pregunta_has_respuestas_preguntas1_idx` (`id_pregunta` ASC) VISIBLE,
              INDEX `fk_pregunta_has_respuestas_perfil1_idx` (`id_salvador` ASC) VISIBLE,
              CONSTRAINT `fk_pregunta_has_respuestas_preguntas1`
                FOREIGN KEY (`id_pregunta`)
                REFERENCES `peertopeer`.`preguntas` (`id_preguntas`)
                ON DELETE NO ACTION
                ON UPDATE NO ACTION,
              CONSTRAINT `fk_pregunta_has_respuestas_perfil1`
                FOREIGN KEY (`id_salvador`)
                REFERENCES `peertopeer`.`perfil` (`id_usuario`)
                ON DELETE NO ACTION
                ON UPDATE NO ACTION)
            ENGINE = InnoDB""")
            print("la tabla pregunta_has_respuestas creada ")
        except pymysql.Error as er:
            print("la tabla pregunta_has_respuestas no fue creada ",er)'''


if(__name__=="__main__"):
    CC()