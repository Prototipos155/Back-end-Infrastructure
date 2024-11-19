import pymysql
from colorama import Back,Fore
import re
import os
from hashlib import sha256

class CC():
    def __init__(self):
        try:
            self.connection = pymysql.connect(host='localhost', user=self.usuarioXampp, passwd='', port=self.puertoXampp, db='peertopeer')
            self.cursor = self.connection.cursor()
            print("\n Conexion exitosa")

            try:
                self.crearTablas()
                self.crearProcedimientos()

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
        

    # def detectarPuertoApache(rutaApache='C:/xampp/apache/conf/httpd.conf'):
    #     try:
    #         with open(rutaApache, 'r') as archivo:
    #             contenido = archivo.read()


    #         resultados = re.findall(r'^Listen[ ]+(\d+)', contenido, re.MULTILINE)
    #         if resultados:
    #             return [int(puerto) for puerto in resultados]
    #         else:
    #             print("No se encontraron datos 'Listen' en el archivo")
    #             return None
    #     except FileNotFoundError:
    #         print(f"No se pudo encontrar el archivo de configuración en {rutaApache}.")
    #         return None


    puertoXampp, usuarioXampp = detectarPuertosXampp()
    if puertoXampp:
        print(f"\nEl puerto de MySQL es {puertoXampp}")
        print(f"El nombre de usuario de MySQL es {usuarioXampp}")
    else:
        print("No se pudo encontrar el puerto de Xampp")


    # puertoApache = detectarPuertoApache()
    # if puertoApache:
    #     print(f"El puerto de Apache es {puertoApache}")
    # else:
    #     print("No se pudo encontrar")

    def crearTablas(self):
        try:
            print("empezo la creacion de tablas")
            self.tabla_perfil()
            self.tabla_buzon_quejas()
            self.tabla_categoria()
            self.tabla_subcategoria()
            self.tabla_tema()
            self.tabla_peticiones()
            self.tabla_documentos()
            self.tabla_links()

            self.tabla_articulo()
            self.tabla_articulo_calificado()
            self.tabla_calificacion_comentario()
            self.tabla_comentario_articulo()
            

        except pymysql.Error as err:
            print("\n error al intentar crear las tablas " .format(err))
    def crearProcedimientos(self):
        try:
            print("empezo la creacion de procedimientos")
            self.funcion_CrearSoloMateria()
            self.funcion_CrearSoloSubtema()
            self.funcion_CrearSoloTema()
            self.funcion_CrearMateriaCompleta()

            self.funcion_sacarPromedio()
            self.funcion_crearArticulo()
            self.funcion_calificarArticulo()
            

        except pymysql.Error as err:
            print("\n error al intentar crear los procedimientos " .format(err))

        @staticmethod
#/////////////////////////////////////////////////////////////////////////
#                            F U N C I O N E S
#///////////////////////////////////////////////////////////////////////////
        def crearHashParaBd(data):
            # Datos a hashear
            data = data.encode()
            # Crear hash
            hash_object = sha256(data)
            hash_hex = hash_object.hexdigest()

            print(f"Hash SHA-256: {hash_hex}")
            return hash_hex

        def crearMateriaCompleta(self,nombre_Materia,descripcion):
            subCate=self.crearHashParaBd(f"{nombre_Materia}-General")
            tema=self.crearHashParaBd(f"{nombre_Materia}-General-General")
            # print(f"('{nombre_Materia}',' desc ','{subCate}','{tema}')")
            self.cursor.callproc("crearCategoriaCompleta",(nombre_Materia,descripcion,subCate,tema))

        def funcion_CrearSoloMateria(self):
            try:
                self.cursor.execute("""
                create procedure crearCategoria(
                    in nomb varchar(100), 
                    in descripcion varchar(150),
                    out resultado int)
                deterministic
                begin
                    etiqueta: begin
                        if ((select id_categoria from categoria where nombre=nomb) is not null) then
                            set resultado= -1;# ya existe la categoria/materia
                            leave etiqueta;
                        end if;
                        insert into categoria(nombre,descripcion) values(nomb,descripcion); #creamos la categoria
                        
                        set resultado=(select id_categoria from categoria where nombre=nomb);
                    end etiqueta;
                end""")
            except Exception as ex:
                print("no se pudo crear la funcion 'CrearMateria'",ex)
        
        def funcion_CrearSoloSubtema(self):
            try:
                self.cursor.execute("""
                create procedure crearSubCategoria(
                    in nomb varchar(100), 
                    in descripcion varchar(150),
                    in id_categ int,
                    in codigoSubcateg char(64),
                    out resultado int)
                deterministic
                begin
                    etiqueta: begin
                        if((select codigo from subcategoria where codigo=codigoSubcateg) is not null) then 
                            set resultado= -3; # ya existe la subcategoria
                            leave etiqueta;
                        end if;
                        #se debe crear la SubCategoria
                        insert into subcategoria(codigo,id_categoria,nombre,descripcion) values(codigoSubcateg,id_categ,nomb,descripcion);
                        
                        set resultado=(select id_subcategoria from subcategoria where codigo=codigoSubcateg);
                    end etiqueta;
                end""")
            except Exception as ex:
                print("no se pudo crear la funcion 'CrearSubTema'",ex)
        
        def funcion_CrearSoloTema(self):
            try:
                self.cursor.execute("""
                create procedure crearTema(
                    in nomb varchar(100), 
                    in descripcion varchar(150),
                    in idSubCateg int,
                    in codigoTema char(64),
                    out resultado int)
                deterministic
                begin
                    etiqueta: begin
                        if((select id_tema from tema where codigo=codigoTema)is not null) then 
                            set resultado= -5;
                            leave etiqueta;
                        end if;
                        #se debe crear el tema 'General' dentro de la subcategoria antes creada
                        insert into tema(codigo,id_subcategoria,nombre,descripcion) values(codigoTema,idSubCateg,nomb,descripcion);
                        set resultado=1;
                    end etiqueta;
                end""")
            except Exception as ex:
                print("no se pudo crear la funcion 'CrearTema'",ex)

        def funcion_CrearMateriaCompleta(self):
            try:
                self.cursor.execute("""
                create procedure crearCategoriaCompleta (
                    in nomb varchar(100),
                    in descripcion varchar(150),
                    in codigoSubcateg char(64),
                    in codigoTema char(64),
                    out resultado int
                )
                deterministic
                begin
                    etiqueta: begin
                        call crearCategoria(nomb, descripcion, @idCateg);
                        if(@idCateg=-1) then
                            set resultado=-1; #ya existe la categoria
                            -- signal sqlstate '45000' set message_text="error -1";
                            leave etiqueta;
                        end if;
                        if (@idCateg is null) then
                            set resultado= -2; # no se pudo hacer el registro de la Categoria
                            leave etiqueta;
                        end if;
                        ######################################################################
                        #se debe crear la SubCategoria 'General'
                        call crearSubCategoria('General',CONCAT('Apartado general de ',nomb),@idCateg,codigoSubcateg,@idSubCateg);
                        if(@idSubCatg =-3) then
                            set resultado=-3; # ya existe la categoria
                            leave etiqueta;
                        end if;
                        if(@idSubCateg is null) then
                            set resultado= -4; # no se pudo hacer el registro de la subcategoria
                            leave etiqueta;
                        end if;
                        ######################################################################
                        call crearTema('General',CONCAT('Apartado general de ',nomb),@idSubCateg,codigoTema,@idTema);
                        
                        if(@idTema=-5) then
                            set resultado =-5;
                            leave etiqueta;
                        end if;
                        if(@idTema is null) then
                            set resultado =-6;
                            leave etiqueta;
                        end if;
                        set resultado=1;
                    end etiqueta;
                end""")
                print("funcion 'CrearMateria' creada con exito")
            except Exception as ex:
                print("no se pudo crear la funcion 'CrearMateriaCompleta'",ex)
        
        def funcion_crearArticulo(self):
            try:
                self.cursor.execute("""
                create procedure crearArticulo(
                    in nombre varchar(150),
                    in idTema int,
                    in idAutor int,
                    out resultado tinyint
                )
                deterministic
                begin
                    if exists(select id_tema from tema where id_tema=idTema) 
                        and exists(select id_usuario from perfil where id_usuario=idAutor)
                        and not exists(select id_articulo from articulo where nombre_articulo=nombre) then 
                        
                        insert into articulo(
                            nombre_articulo,id_autor,id_tema,id_sala,fecha_creacion,ultima_modificacion,calificacion,num_calificaciones
                        ) values(
                            #modifical 'id_sala'
                            nombre,idAutor,idTema,0,(select utc_date()),(select utc_date()),null,0
                        );
                        set resultado=True;
                    else 
                        set resultado=False;
                    end if;
                end""")
                print("la funcion crearArticulo fue creada")
            except pymysql.Error as err:
                print("la funcion crearArticulo no fue creada ",err)
        
        def funcion_calificarArticulo(self):
            try:
                self.cursor.execute("""
                create procedure calificarArticulo(
                    in idArticulo int,
                    in Calif_ingresada decimal (3,2),
                    in idUsuario int,
                    in Comentario varchar(100),
                    out resultado tinyint
                )
                deterministic
                begin    
                    label :begin
                        select 
                            calificacion,num_calificaciones 
                        into 
                            @calif,@num 
                        from articulo where id_articulo=idArticulo;
                        
                        -- signal sqlstate '45000' set message_text=@calif;
                        if exists(select id_calificacion from articulo_es_calificado where id_usuario=idUsuario and id_articulo=idArticulo)then 
                            set resultado=False;
                            leave label;
                        end if;
                        
                        if not exists(select id_usuario from perfil where id_usuario=idUsuario) 
                            or not exists(select  @num )then 
                            #no existe el usuario o el articulo
                            set resultado=False;
                            leave label ;
                        end if;
                        
                        if(Calif_ingresada>5) then 
                            set Calif_ingresada=5;
                        end if;
                        
                        set @nuevaCalif:=null;
                        
                        if(@num=0) then 
                            set @nuevaCalif=Calif_ingresada;
                        else
                            set @nuevaCalif=(select SacarPromedio(@calif, @num,Calif_ingresada));
                        end if;
                        -- set @txt=concat(idArticulo,id_Usuario);
                        
                        set @num=@num+1;
                        
                        -- signal sqlstate '45000' set message_text=@txt;
                        insert into articulo_es_calificado(id_articulo,id_usuario,fecha) values(idArticulo,idUsuario,(select utc_timestamp()));
                        update articulo set calificacion =@nuevaCalif, num_calificaciones=@num where id_articulo=idArticulo;
                        
                        if (comentario != "") then 
                            insert into calificacion_tiene_comentario(comentario,id_usuario,id_calificacion ) 
                                values(Comentario,idUsuario,(select id_calificacion from articulo_es_calificado 
                                where id_articulo=idArticulo and id_usuario=IdUsuario));
                        end if;
                        set resultado=True;
                    end label;
                end""")
                print("la funcion calificarArticulo fue creada")
            except pymysql.Error as err:
                print("la funcion calificarArticulo no fue creada ",err)
        
        def funcion_sacarPromedio(self):
            try:
                self.cursor.execute("""
                create function sacarPromedio(cantidad double, numero_objetos int, nuevo_elemento double)
                returns double
                deterministic
                begin
                    set @resultado=((cantidad*numero_objetos)+nuevo_elemento);
                    set numero_objetos=numero_objetos+1;
                    #signal sqlstate '45000' set message_text=@resultado;
                    set @resultado=(@resultado/(numero_objetos));
                    return @resultado;
                end""")
                print("la funcion sacarPromedio fue creada")
            except pymysql.Error as err:
                print("la funcion sacarPromedio no fue creada ",err)
            
#/////////////////////////////////////////////////////////////////////////
#                           F I N   F U N C I O N E S
#///////////////////////////////////////////////////////////////////////////  

#/////////////////////////////////////////////////////////////////////////
#                            T A B L A S
#///////////////////////////////////////////////////////////////////////////         

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
            id_subcategoria INT AUTO_INCREMENT NOT NULL,
            codigo char(64) unique NOT NULL,
            id_categoria INT NOT NULL,

            nombre VARCHAR(100) NOT NULL,
            descripcion VARCHAR(150) NOT NULL,
                                
            PRIMARY KEY (id_subcategoria),
            FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria)
            );""")
            
            print("la tabla subcategoria creada ")

        except pymysql.Error as err:
            print("la tabla subcategoria no fue creada ",err)

    def tabla_tema(self):
        try:
            self.cursor.execute("""
            create table if not exists tema(
                id_tema int auto_increment not null,
                codigo char(64) unique not null,
                id_subcategoria int not null,
                
                nombre VARCHAR(100) NOT NULL,
                descripcion VARCHAR(150) NOT NULL,
                
                primary key(id_tema),
                FOREIGN KEY (id_subcategoria) REFERENCES subcategoria(id_subcategoria)
            );""")
            
            print("la tabla subcategoria creada ")

        except pymysql.Error as err:
            print("la tabla subcategoria no fue creada ",err)

    def tabla_articulo(self):
        try:
            self.cursor.execute("""
            create table if not exists articulo (
                id_articulo int not null auto_increment,
                nombre_articulo varchar(150) unique not null,
                
                id_autor int not null,
                id_tema int not null,
                id_sala int,
                
                fecha_creacion date not null,
                ultima_modificacion date not null,
                
                calificacion decimal(3,2),
                num_calificaciones int not null,
                
                primary key(id_articulo),
                foreign key (id_autor) references perfil(id_usuario),
                foreign key (id_tema) references tema(id_tema)
                -- foreign key a la tabla sala
            );""")
            
            print("la tabla articulo creada ")

        except pymysql.Error as err:
            print("la tabla articulo no fue creada ",err)

    def tabla_articulo_calificado(self):
        try:
            self.cursor.execute("""
            create table if not exists articulo_es_calificado(
                id_calificacion int not null auto_increment,
                id_articulo int not null,
                id_usuario int not null,
                fecha datetime not null,
                
                primary key(id_calificacion),
                foreign key(id_articulo) references articulo(id_articulo),
                foreign key(id_usuario) references perfil (id_usuario)
            );""")
            
            print("la tabla articulo_es_calificado creada ")

        except pymysql.Error as err:
            print("la tabla articulo_es_calificado no fue creada ",err)

    def tabla_calificacion_comentario(self):
        try:
            self.cursor.execute("""
            create table if not exists calificacion_tiene_comentario(
                id_registro int not null auto_increment,
                comentario varchar(100) not null,
                id_usuario int not null,
                id_calificacion int not null,
                
                primary key(id_registro),
                foreign key(id_usuario) references perfil(id_usuario),
                foreign key (id_calificacion) references articulo_es_calificado(id_calificacion)
            );""")
            
            print("la tabla calificacion_tiene_comentario creada ")

        except pymysql.Error as err:
            print("la tabla calificacion_tiene_comentario no fue creada ",err)

    def tabla_comentario_articulo(self):
        try:
            self.cursor.execute("""
            create table if not exists comentarios_de_articulo(
                id_comentario int not null auto_increment,
                id_usuario int not null,
                mensaje varchar (250),
                respondiendo_a_mensaje int not null,
                
                id_articulo int not null,
                
                primary key(id_comentario),
                foreign key(id_articulo) references articulo(id_articulo),
                foreign key (respondiendo_a_mensaje) references comentarios_de_articulo(id_comentario)
            );""")
            
            print("la tabla comentarios_de_articulo creada ")

        except pymysql.Error as err:
            print("la tabla 'comentarios_de_articulo' no fue creada ",err)


    # def tabla_mensajes_from_seccion(self):
    #     try:
    #         self.cursor.execute("""
    #         CREATE TABLE IF NOT EXISTS mensajes_from_seccion (
    #           id_mensaje INT NOT NULL AUTO_INCREMENT,
    #           id_seccion INT NOT NULL,
    #           id_usuario INT NOT NULL,
    #           mensaje VARCHAR(256) NOT NULL,
    #           fecha VARCHAR(11) NOT NULL,
    #           hora VARCHAR(12) NOT NULL,
    #           PRIMARY KEY (id_mensaje),
    #           INDEX fk_mensaje_seccion1_idx (id_seccion ASC) VISIBLE,
    #           INDEX fk_mensaje_perfil1_idx (id_usuario ASC) VISIBLE,
    #           CONSTRAINT fk_mensaje_seccion1
    #             FOREIGN KEY (id_seccion)
    #             REFERENCES peertopeer.seccion (id_seccion)
    #             ON DELETE NO ACTION
    #             ON UPDATE NO ACTION,
    #           CONSTRAINT fk_mensaje_perfil1
    #             FOREIGN KEY (id_usuario)
    #             REFERENCES peertopeer.perfil (id_usuario)
    #             ON DELETE NO ACTION
    #             ON UPDATE NO ACTION)
    #         ENGINE = InnoDB
    #         DEFAULT CHARACTER SET = utf8mb3""")
    #         print("la tabla mensajes_from_seccion creada ")
    #     except pymysql.Error as er:
    #         print("la tabla mensajes_from_seccion no fue creada ",er)

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

    # """def tabla_peticion_has_files(self):
    #     try:
    #         self.cursor.execute(
    #         CREATE TABLE IF NOT EXISTS peticion_has_files (
    #           id_archivo INT NOT NULL AUTO_INCREMENT,
    #           id_peticion INT NOT NULL,
    #           id_material INT NOT NULL,
    #           tipo TINYINT NOT NULL,
    #           verificado TINYINT NULL,
    #           PRIMARY KEY (id_archivo),
    #           INDEX fk_peticion_has_files_peticion1_idx (id_peticion ASC) VISIBLE,
    #           CONSTRAINT fk_peticion_has_files_peticion1
    #             FOREIGN KEY (id_peticion)
    #             REFERENCES peertopeer.peticion (id_peticion)
    #             ON DELETE NO ACTION
    #             ON UPDATE NO ACTION))
    #         print("la tabla peticion_has_files creada ")
    #     except pymysql.Error as er:
    #         print("la tabla peticion_has_files no fue creada ",er)"""

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

    # def tabla_queja_has_motivos(self):
    #     try:
    #         self.cursor.execute("""
    #         CREATE TABLE IF NOT EXISTS queja_has_motivos (
    #           id_registro INT NOT NULL AUTO_INCREMENT,
    #           id_queja INT NOT NULL,
    #           id_motivo INT NOT NULL,
    #           INDEX `fk_queja_has_motivos_buzon_quejas1_idx` (`id_queja` ASC) VISIBLE,
    #           INDEX `fk_queja_has_motivos_motivos_de_quejas1_idx` (`id_motivo` ASC) VISIBLE,
    #           PRIMARY KEY (`id_registro`),
    #           CONSTRAINT `fk_queja_has_motivos_buzon_quejas1`
    #             FOREIGN KEY (`id_queja`)
    #             REFERENCES `peertopeer`.`buzon_quejas` (`id_buzon_quejas`)
    #             ON DELETE NO ACTION
    #             ON UPDATE NO ACTION,
    #           CONSTRAINT `fk_queja_has_motivos_motivos_de_quejas1`
    #             FOREIGN KEY (`id_motivo`)
    #             REFERENCES `peertopeer`.`motivos_de_quejas` (`id_motivo`)
    #             ON DELETE NO ACTION
    #             ON UPDATE NO ACTION)
    #         ENGINE = InnoDB""")
    #         print("la tabla queja_has_motivos creada ")
    #     except pymysql.Error as er:
    #         print("la tabla queja_has_motivos no fue creada ",er)

    # def tabla_queja_has_razon_extra(self):
    #     try:
    #         self.cursor.execute("""
    #         CREATE TABLE IF NOT EXISTS queja_has_razon_extra (
    #           `id_registro` INT NOT NULL AUTO_INCREMENT,
    #           `razon` VARCHAR(250) NOT NULL,
    #           `id_queja` INT NOT NULL,
    #           INDEX `fk_queja_has_razon_extra_buzon_quejas1_idx` (`id_queja` ASC) VISIBLE,
    #           PRIMARY KEY (`id_registro`),
    #           CONSTRAINT `fk_queja_has_razon_extra_buzon_quejas1`
    #             FOREIGN KEY (`id_queja`)
    #             REFERENCES `peertopeer`.`buzon_quejas` (`id_buzon_quejas`)
    #             ON DELETE NO ACTION
    #             ON UPDATE NO ACTION)
    #         ENGINE = InnoDB""")
    #         print("la tabla queja_has_razon_extra creada ")
    #     except pymysql.Error as er:
    #         print("la tabla queja_has_razon_extra no fue creada ",er)

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

    # def tabla_preguntas(self):
    #     try:
    #         self.cursor.execute("""
    #         CREATE TABLE IF NOT EXISTS preguntas (
    #           `id_preguntas` INT NOT NULL AUTO_INCREMENT,
    #           `pregunta` VARCHAR(256) NOT NULL,
    #           `fecha` DATE NOT NULL,
    #           `hora` TIME NOT NULL,
    #           `solucionada` TINYINT NOT NULL,
    #           `id_seccion` INT NOT NULL,
    #           PRIMARY KEY (`id_preguntas`),
    #           INDEX `fk_preguntas_seccion1_idx` (`id_seccion` ASC) VISIBLE,
    #           CONSTRAINT `fk_preguntas_seccion1`
    #             FOREIGN KEY (`id_seccion`)
    #             REFERENCES `peertopeer`.`seccion` (`id_seccion`)
    #             ON DELETE NO ACTION
    #             ON UPDATE NO ACTION)
    #         ENGINE = InnoDB""")
    #         print("la tabla preguntas creada ")
    #     except pymysql.Error as er:
    #         print("la tabla preguntas no fue creada ",er)

    # def tabla_pregunta_has_respuestas(self):
    #     try:
    #         self.cursor.execute("""
    #         CREATE TABLE IF NOT EXISTS pregunta_has_respuestas (
    #           `id_respuesta` INT NOT NULL AUTO_INCREMENT,
    #           `id_pregunta` INT NOT NULL,
    #           `id_salvador` INT NOT NULL,
    #           `mensaje` VARCHAR(250) NOT NULL,
    #           `fecha` DATE NOT NULL,
    #           `hora` TIME NOT NULL,
    #           `likes` INT NOT NULL,
    #           `fijado` TINYINT NOT NULL,
    #           PRIMARY KEY (`id_respuesta`),
    #           INDEX `fk_pregunta_has_respuestas_preguntas1_idx` (`id_pregunta` ASC) VISIBLE,
    #           INDEX `fk_pregunta_has_respuestas_perfil1_idx` (`id_salvador` ASC) VISIBLE,
    #           CONSTRAINT `fk_pregunta_has_respuestas_preguntas1`
    #             FOREIGN KEY (`id_pregunta`)
    #             REFERENCES `peertopeer`.`preguntas` (`id_preguntas`)
    #             ON DELETE NO ACTION
    #             ON UPDATE NO ACTION,
    #           CONSTRAINT `fk_pregunta_has_respuestas_perfil1`
    #             FOREIGN KEY (`id_salvador`)
    #             REFERENCES `peertopeer`.`perfil` (`id_usuario`)
    #             ON DELETE NO ACTION
    #             ON UPDATE NO ACTION)
    #         ENGINE = InnoDB""")
    #         print("la tabla pregunta_has_respuestas creada ")
    #     except pymysql.Error as er:
    #         print("la tabla pregunta_has_respuestas no fue creada ",er)
    
#/////////////////////////////////////////////////////////////////////////
#                               F I N  T A B L A S
#///////////////////////////////////////////////////////////////////////////

cx=None
if(__name__=="__main__"):
    cx=CC()
