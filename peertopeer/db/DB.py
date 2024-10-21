import pymysql
from colorama import Back,Fore
import re
import os

class CC():
    resetDBVar=1
    # reset pensado para añadir o quitarle 0 para cambiar su sigificado
        # reset de valor 10 significa que hay que resetear
        # reset de valor 1 es"no hagas nada" 
    pasw=""
    dbName='peertopeer'
    def __init__(self):
        try:
            # print(f"{Back.RED}pymysl.connect(host='localhost', user='{self.usuarioXampp}' , passwd= '{self.pasw}' , port= {self.puertoXampp} , db = 'peertopeer') {Back.RESET}")
            self.conectarDB(self.dbName)
            print("\n Conexion exitosa")
            if((self.resetDBVar!=1)==True):
                #existe
                #es diferente a 1
                print("hay que resetear")
                self.resetDB()
            self.crearTablas()
            if((self.resetDBVar!=1)):
                self.hacerInserts()
            
        except pymysql.Error as err:
            # print(f"{Back.CYAN}FALLO LA PRIMER CONEXION{Back.RESET}")
            self.conectarDB()
            self.crearDB()
            self.cursor.execute("USE peertopeer")
            print("\nCreacion exitosa")

    def resetDB(self):
        print("inicia el reseteo")
        try:
            self.cursor.execute("DROP DATABASE "+self.dbName)
            self.connection.commit()
            self.crearDB()
            self.cursor.execute("USE "+self.dbName)
            self.connection.commit()
        except Exception as e:
            print(e)
        print("reseteo correcto")

    def crearDB(self):
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS "+self.dbName)
        self.connection.commit()
        
    def conectarDB(self,db=None):
        self.connection = pymysql.connect(host='localhost', user=self.usuarioXampp, passwd=self.pasw, port=self.puertoXampp,database=db)
        self.cursor = self.connection.cursor()

    def hacerInserts(self):
        try:
            self.cursor.execute("""
            INSERT INTO motivos_de_quejas ( `motivo`) VALUES 
                ('contenido inadecuado'),
                ('spam'),
                ('incita all odio'),
                ('otro');
    """)
            self.connection.commit()
            print("todas las inseciones correctas")
        except Exception as ex:
            print("Error en los Insert ",ex)

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

    def crearTablas(self):
        try:
            print("empezo la creacion de tablas")
            self.tabla_perfil()
            self.tabla_buzon_quejas()
            self.tabla_materia()
            self.tabla_seccion()
            self.tabla_mensajes_from_seccion()
            self.tabla_peticiones()
            self.tabla_documentos()
            self.tabla_links()
            #self.tabla_peticion_has_files()
            #self.tabla_seccion_has_files()
            self.tabla_motivos_de_quejas()
            self.tabla_queja_has_motivos()
            self.tabla_queja_has_razon_extra()
            self.tabla_chat()
            self.tabla_mensajes_privados()
            self.tabla_bloqueados()
            self.tabla_preguntas()
            self.tabla_pregunta_has_respuestas()

        except pymysql.Error as err:
            print("\n error al intentar crear las tablas " .format(err))
    
    def tabla_perfil(self):
        try:
            #self.cursor.execute("""
            #   create table if not exists perfil(
            #       id_perfil int primary key not null, nom
            #)
            # """)

            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS perfil 
                (id_perfil int unique auto_increment not null,
                nivel varchar (20) not null,
                nombres varchar (40) not null,
                apellidos varchar (40) not null,
                apodo varchar(10) unique not null,
                correo varchar(150) unique not null,
                telefono varchar(10) unique not null,
                contraseña_encript varchar(256) not null,
                cuenta_activa TINYINT not null)""")
            print("la tabla perfil creada ")


        except pymysql.Error as er:
            print("la tabla perfil no fue creada ",er)
        # '1', 'superior', 'Martin Alejandro', 'Perez Bernal', 'sal2', 'martnalej@gmail.com', '4491261629', 
        # 'scrypt:32768:8:1$oKoiiqjn6n7Smym4$ebb71fd4f433ff2ea4c4e64606503e9450e7a598ae0dabc83dcb4e9afd38a0d0d2375eb5788696fee760882c00065be2caaefed4760b43ab84552040ccc0db75'
        # , '1'
        # len('scrypt:32768:8:1$oKoiiqjn6n7Smym4$ebb71fd4f433ff2ea4c4e64606503e9450e7a598ae0dabc83dcb4e9afd38a0d0d2375eb5788696fee760882c00065be2caaefed4760b43ab84552040ccc0db75')
        # 162

    def tabla_buzon_quejas(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS buzon_quejas (
              id_buzon_quejas INT NOT NULL AUTO_INCREMENT,
              id_perfil INT NOT NULL,
              mensaje VARCHAR(256) NOT NULL,
              fecha VARCHAR(11) NOT NULL,
              hora VARCHAR(12) NOT NULL,
              id_entidad_reportada` INT NOT NULL,
              tipoEntidad INT NOT NULL,
              PRIMARY KEY (`id_buzon_quejas`),
              UNIQUE INDEX `idbuzon_quejas_UNIQUE` (`id_buzon_quejas` ASC) VISIBLE,
              INDEX fk_buzon_quejas_perfil1_idx (id_perfil ASC) VISIBLE,
              CONSTRAINT fk_buzon_quejas_perfil1
                FOREIGN KEY (id_perfil)
                REFERENCES perfil (id_perfil))
            ENGINE = InnoDB
            DEFAULT CHARACTER SET = utf8mb3""")
            print("la tabla buzon_quejas creada ")
        except pymysql.Error as er:
            print("la tabla buzon_quejas no fue creada ",er)

    def tabla_materia(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS materia (
              id_materia INT NOT NULL AUTO_INCREMENT,
              nombre VARCHAR(30) NOT NULL,
              descripcion VARCHAR(150) NOT NULL,
              PRIMARY KEY (id_materia),
              UNIQUE INDEX nombre_UNIQUE (nombre ASC) VISIBLE)
            ENGINE = InnoDB""")
            print("la tabla materia creada ")
        except pymysql.Error as er:
            print("la tabla materia no fue creada ",er)

    def tabla_seccion(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS seccion (
              id_seccion INT NOT NULL AUTO_INCREMENT,
              nombre VARCHAR(30) NOT NULL,
              descripcion VARCHAR(150) NOT NULL,
              id_materia INT NOT NULL,
              PRIMARY KEY (id_seccion),
              INDEX fk_seccion_materia1_idx (id_materia ASC) VISIBLE,
              CONSTRAINT fk_seccion_materia1
                FOREIGN KEY (id_materia)
                REFERENCES peertopeer.materia (id_materia)
                ON DELETE NO ACTION
                ON UPDATE NO ACTION)
            ENGINE = InnoDB""")
            print("la tabla seccion creada ")
        except pymysql.Error as er:
            print("la tabla seccion no fue creada ",er)

    def tabla_mensajes_from_seccion(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS mensajes_from_seccion (
              id_mensaje INT NOT NULL AUTO_INCREMENT,
              id_seccion INT NOT NULL,
              id_perfil INT NOT NULL,
              mensaje VARCHAR(256) NOT NULL,
              fecha VARCHAR(11) NOT NULL,
              hora VARCHAR(12) NOT NULL,
              PRIMARY KEY (id_mensaje),
              INDEX fk_mensaje_seccion1_idx (id_seccion ASC) VISIBLE,
              INDEX fk_mensaje_perfil1_idx (id_perfil ASC) VISIBLE,
              CONSTRAINT fk_mensaje_seccion1
                FOREIGN KEY (id_seccion)
                REFERENCES peertopeer.seccion (id_seccion)
                ON DELETE NO ACTION
                ON UPDATE NO ACTION,
              CONSTRAINT fk_mensaje_perfil1
                FOREIGN KEY (id_perfil)
                REFERENCES peertopeer.perfil (id_perfil)
                ON DELETE NO ACTION
                ON UPDATE NO ACTION)
            ENGINE = InnoDB
            DEFAULT CHARACTER SET = utf8mb3""")
            print("la tabla mensajes_from_seccion creada ")
        except pymysql.Error as er:
            print("la tabla mensajes_from_seccion no fue creada ",er)

    def tabla_peticiones(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS peticiones (
              id_peticiones INT NOT NULL AUTO_INCREMENT,
              id_perfil INT NOT NULL,
              tipo INT NOT NULL,
              mensaje VARCHAR(200) NULL,
              fecha DATE NOT NULL,
              hora TIME NOT NULL,
              verificado TINYINT NULL,
              PRIMARY KEY(id_peticiones),
               FOREIGN KEY (id_perfil) REFERENCES perfil(id_perfil)
            )""") 
            print("la tabla peticion creada ")
        except pymysql.Error as er:
            print("la tabla peticion no fue creada ",er)

    def tabla_documentos(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS documentos (
              id_documento INT NOT NULL AUTO_INCREMENT,
              documento BLOB NOT NULL,
              PRIMARY KEY (id_documento))""")
            print("la tabla documentos creada ")
        except pymysql.Error as er:
            print("la tabla documentos no fue creada ",er)

    def tabla_links(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS links (
              id_link INT NOT NULL AUTO_INCREMENT,
              link VARCHAR(256) NOT NULL,
              PRIMARY KEY (id_link))""")
            print("la tabla links creada ")
        except pymysql.Error as er:
            print("la tabla links no fue creada ",er)

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
              `id_motivo` INT NOT NULL AUTO_INCREMENT,
              `motivo` VARCHAR(30) NOT NULL,
              PRIMARY KEY (`id_motivo`))
            ENGINE = InnoDB""")
            print("la tabla motivos_de_quejas creada ")
        except pymysql.Error as er:
            print("la tabla motivos_de_quejas no fue creada ",er)

    def tabla_queja_has_motivos(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS queja_has_motivos (
              `id_registro` INT NOT NULL AUTO_INCREMENT,
              `id_queja` INT NOT NULL,
              `id_motivo` INT NOT NULL,
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
            print("la tabla queja_has_motivos no fue creada ",er)

    def tabla_queja_has_razon_extra(self):
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
            print("la tabla queja_has_razon_extra no fue creada ",er)

    def tabla_chat(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat (
              `id_chat` INT NOT NULL AUTO_INCREMENT,
              `id_integrante1` INT NOT NULL,
              `id_integrante2` INT NOT NULL,
              PRIMARY KEY (`id_chat`),
              INDEX `fk_chat_perfil1_idx` (`id_integrante1` ASC) VISIBLE,
              INDEX `fk_chat_perfil2_idx` (`id_integrante2` ASC) VISIBLE,
              CONSTRAINT `fk_chat_perfil1`
                FOREIGN KEY (`id_integrante1`)
                REFERENCES `peertopeer`.`perfil` (`id_perfil`)
                ON DELETE NO ACTION
                ON UPDATE NO ACTION,
              CONSTRAINT `fk_chat_perfil2`
                FOREIGN KEY (`id_integrante2`)
                REFERENCES `peertopeer`.`perfil` (`id_perfil`)
                ON DELETE NO ACTION
                ON UPDATE NO ACTION)
            ENGINE = InnoDB""")
            print("la tabla chat creada ")
        except pymysql.Error as er:
            print("la tabla chat no fue creada ",er)

    def tabla_mensajes_privados(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS mensajes_privados (
              `id_mensaje` INT NOT NULL AUTO_INCREMENT,
              `id_chat` INT NOT NULL,
              `id_pefil_enviando` INT NOT NULL,
              `mensaje` VARCHAR(250) NOT NULL,
              `fecha` DATE NOT NULL,
              `hora` TIME NOT NULL,
              PRIMARY KEY (`id_mensaje`),
              INDEX `fk_mensajes_privados_chat1_idx` (`id_chat` ASC) VISIBLE,
              INDEX `fk_mensajes_privados_perfil1_idx` (`id_pefil_enviando` ASC) VISIBLE,
              CONSTRAINT `fk_mensajes_privados_chat1`
                FOREIGN KEY (`id_chat`)
                REFERENCES `peertopeer`.`chat` (`id_chat`)
                ON DELETE NO ACTION
                ON UPDATE NO ACTION,
              CONSTRAINT `fk_mensajes_privados_perfil1`
                FOREIGN KEY (`id_pefil_enviando`)
                REFERENCES `peertopeer`.`perfil` (`id_perfil`)
                ON DELETE NO ACTION
                ON UPDATE NO ACTION)
            ENGINE = InnoDB""")
            print("la tabla mensajes_privados creada ")
        except pymysql.Error as er:
            print("la tabla mensajes_privados no fue creada ",er)

    def tabla_bloqueados(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS bloqueados (
              `id_bloqueo` INT NOT NULL AUTO_INCREMENT,
              `id_perfil_bloqueando` INT NOT NULL,
              `id_perfil_bloqueado` INT NOT NULL,
              INDEX `fk_bloqueados_perfil1_idx` (`id_perfil_bloqueando` ASC) VISIBLE,
              INDEX `fk_bloqueados_perfil2_idx` (`id_perfil_bloqueado` ASC) VISIBLE,
              PRIMARY KEY (`id_bloqueo`),
              CONSTRAINT `fk_bloqueados_perfil1`
                FOREIGN KEY (`id_perfil_bloqueando`)
                REFERENCES `peertopeer`.`perfil` (`id_perfil`)
                ON DELETE NO ACTION
                ON UPDATE NO ACTION,
              CONSTRAINT `fk_bloqueados_perfil2`
                FOREIGN KEY (`id_perfil_bloqueado`)
                REFERENCES `peertopeer`.`perfil` (`id_perfil`)
                ON DELETE NO ACTION
                ON UPDATE NO ACTION)
            ENGINE = InnoDB""")
            print("la tabla bloqueados creada ")
        except pymysql.Error as er:
            print("la tabla bloqueados no fue creada ",er)

    def tabla_preguntas(self):
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
                REFERENCES `peertopeer`.`perfil` (`id_perfil`)
                ON DELETE NO ACTION
                ON UPDATE NO ACTION)
            ENGINE = InnoDB""")
            print("la tabla pregunta_has_respuestas creada ")
        except pymysql.Error as er:
            print("la tabla pregunta_has_respuestas no fue creada ",er)


if(__name__=="__main__"):
    CC()