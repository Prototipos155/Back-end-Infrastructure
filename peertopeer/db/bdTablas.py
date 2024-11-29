#/////////////////////////////////////////////////////////////////////////
#                            F U N C I O N E S
#///////////////////////////////////////////////////////////////////////////

def codigo_funcion_CrearSoloMateria():
    return """
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
        end"""

def codigo_funcion_CrearSoloTema():
    return """
        create procedure creartema(
            in nomb varchar(100), 
            in descripcion varchar(150),
            in id_categ int,
            in codigotema char(64),
            out resultado int)
        deterministic
        begin
            etiqueta: begin
                if((select codigo from tema where codigo=codigotema) is not null) then 
                    set resultado= -3; # ya existe la tema
                    leave etiqueta;
                end if;
                #se debe crear la tema
                insert into tema(codigo,id_categoria,nombre,descripcion) values(codigotema,id_categ,nomb,descripcion);
                
                set resultado=(select id_tema from tema where codigo=codigotema);
            end etiqueta;
        end"""

def codigo_funcion_CrearSoloSubtema():
    return """
        create procedure crearsubtema(
            in nomb varchar(100), 
            in descripcion varchar(150),
            in idtema int,
            in codigosubtema char(64),
            out resultado int)
        deterministic
        begin
            etiqueta: begin
                if((select id_subtema from subtema where codigo=codigosubtema)is not null) then 
                    set resultado= -5;
                    leave etiqueta;
                end if;
                #se debe crear el subtema 'General' dentro de la tema antes creada
                insert into subtema(codigo,id_tema,nombre,descripcion) values(codigosubtema,idtema,nomb,descripcion);
                set resultado=1;
            end etiqueta;
        end"""

def codigo_funcion_CrearMateriaCompleta():
    return """
        create procedure crearCategoriaCompleta (
            in nomb varchar(100),
            in descripcion varchar(150),
            in codigotema char(64),
            in codigosubtema char(64),
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
                #se debe crear la tema 'General'
                call creartema('General',CONCAT('Apartado general de ',nomb),@idCateg,codigotema,@idtema);
                if(@idtema =-3) then
                    set resultado=-3; # ya existe la categoria
                    leave etiqueta;
                end if;
                if(@idtema is null) then
                    set resultado= -4; # no se pudo hacer el registro de la tema
                    leave etiqueta;
                end if;
                ######################################################################
                call crearsubtema('General',CONCAT('Apartado general de ',nomb),@idtema,codigosubtema,@idsubtema);
                
                if(@idsubtema=-5) then
                    set resultado =-5;
                    leave etiqueta;
                end if;
                if(@idsubtema is null) then
                    set resultado =-6;
                    leave etiqueta;
                end if;
                set resultado=1;
            end etiqueta;
        end"""

def codigo_funcion_crearArticulo():
    return """
        create procedure crearArticulo(
            in nombre varchar(150),
            in idsubtema int,
            in idAutor int,
            out resultado tinyint
        )
        deterministic
        begin
            if exists(select id_subtema from subtema where id_subtema=idsubtema) 
                and exists(select id_usuario from perfil where id_usuario=idAutor)
                and not exists(select id_articulo from articulo where nombre_articulo=nombre) then 
                
                insert into articulo(
                    nombre_articulo,id_autor,id_subtema,id_sala,fecha_creacion,ultima_modificacion,calificacion,num_calificaciones
                ) values(
                    #modifical 'id_sala'
                    nombre,idAutor,idsubtema,0,(select utc_date()),(select utc_date()),null,0
                );
                set resultado=True;
            else 
                set resultado=False;
            end if;
        end"""

def codigo_funcion_calificarArticulo():
    return """
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
        end"""

def codigo_funcion_sacarPromedio():
    return """
        create function sacarPromedio(cantidad double, numero_objetos int, nuevo_elemento double)
        returns double
        deterministic
        begin
            set @resultado=((cantidad*numero_objetos)+nuevo_elemento);
            set numero_objetos=numero_objetos+1;
            #signal sqlstate '45000' set message_text=@resultado;
            set @resultado=(@resultado/(numero_objetos));
            return @resultado;
        end"""

#/////////////////////////////////////////////////////////////////////////
#                           F I N   F U N C I O N E S
#///////////////////////////////////////////////////////////////////////////  

#/////////////////////////////////////////////////////////////////////////
#                            T A B L A S
#/////////////////////////////////////////////////////////////////////////// 
def codigo_tabla_foto_perfil():
    return """
    CREATE TABLE IF NOT EXISTS fotos_perfil(
    id_foto INT NOT NULL AUTO_INCREMENT,
    foto BLOB NOT NULL,
    PRIMARY KEY (id_foto)
    );
    """

def codigo_tabla_rol():
    return """
    create table roles(
	id_rol int primary key auto_increment,
    nombre varchar(30) not null,
    descripcion varchar(200) not null
    );"""

def codigo_tabla_perfil():
    return """
        CREATE TABLE IF NOT EXISTS perfil (
            id_usuario INT primary key AUTO_INCREMENT NOT NULL,
            id_rol int not null,
            nombres VARCHAR (50) NOT NULL,
            apellidos VARCHAR (50) NOT NULL,
            nombre_usuario VARCHAR(20) UNIQUE NOT NULL,
            correo VARCHAR(150) UNIQUE NOT NULL,
            telefono VARCHAR(13) UNIQUE NOT NULL,
            contraseña_encript VARCHAR (256) NOT NULL,
            cuenta_activa BOOLEAN NOT NULL,
            id_foto_perfil int not null,
            
            foreign key(id_rol) references roles(id_rol),
            FOREIGN KEY (id_foto_perfil) REFERENCES fotos_perfil (id_foto)
        )"""
        


def codigo_tabla_buzon_quejas():
    return """
        CREATE TABLE IF NOT EXISTS buzon_quejas (
            id_buzon_quejas INT UNIQUE AUTO_INCREMENT NOT NULL,
            id_usuario INT NOT NULL,
                            
            mensaje VARCHAR(256) NOT NULL,
            fecha DATETIME NOT NULL,
            hora DATETIME NOT NULL,
                            
            PRIMARY KEY (id_buzon_quejas),
            FOREIGN KEY (id_usuario) REFERENCES perfil(id_usuario)
        )"""
        


def codigo_tabla_categoria():
    return """
        CREATE TABLE IF NOT EXISTS categoria (
            id_categoria INT UNIQUE AUTO_INCREMENT NOT NULL,
                            
            codigo char(64) unique NOT NULL,                  
            nombre VARCHAR(100) NOT NULL,
            descripcion VARCHAR(150) NOT NULL,

                            
            PRIMARY KEY (id_categoria))"""
        


def codigo_tabla_tema():
    return """
        CREATE TABLE IF NOT EXISTS tema (
        id_tema INT AUTO_INCREMENT NOT NULL,
        codigo char(64) unique NOT NULL,
        id_categoria INT NOT NULL,

        nombre VARCHAR(100) NOT NULL,
        descripcion VARCHAR(150) NOT NULL,
                            
        PRIMARY KEY (id_tema),
        FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria)
        );"""
        


def codigo_tabla_subtema():
    return """
        create table if not exists subtema(
            id_subtema int auto_increment not null,
            codigo char(64) unique not null,
            id_tema int not null,
            
            nombre VARCHAR(100) NOT NULL,
            descripcion VARCHAR(150) NOT NULL,
            
            primary key(id_subtema),
            FOREIGN KEY (id_tema) REFERENCES tema(id_tema)
        );"""
        


def codigo_tabla_sala():
    return """
        CREATE TABLE IF NOT EXISTS sala(
            id_sala INT UNIQUE AUTO_INCREMENT NOT NULL,
            id_tema INT UNIQUE,
            codigo_sala char(8) UNIQUE NOT NULL,
            
            PRIMARY KEY(id_sala),
            FOREIGN KEY(id_tema) REFERENCES tema(id_tema)
        );"""



def codigo_tabla_mensaje():
    return """
        CREATE TABLE IF NOT EXISTS mensaje(
            id_msj INT UNIQUE AUTO_INCREMENT NOT NULL,
            id_usuario INT NOT NULL,
            id_sala INT NOT NULL,
            mensaje text NOT NULL,
            fecha date NOT NULL,
            hora time NOT NULL,
            id_mensajeAResponder INT,
            
            PRIMARY KEY(id_msj),
            FOREIGN KEY(id_mensajeAResponder) REFERENCES mensaje(id_msj),
            FOREIGN KEY(id_usuario) REFERENCES perfil(id_usuario),
            FOREIGN KEY(id_sala) REFERENCES sala(id_sala)
        );"""



def codigo_tabla_articulo():
    return """
        create table if not exists articulo (
            id_articulo int not null auto_increment,
            nombre_articulo varchar(150) unique not null,
            
            id_autor int not null,
            id_subtema int not null,
            id_sala int,
            
            fecha_creacion date not null,
            ultima_modificacion date not null,
            
            calificacion decimal(3,2),
            num_calificaciones int not null,
            
            primary key(id_articulo),
            foreign key (id_autor) references perfil(id_usuario),
            foreign key (id_subtema) references subtema(id_subtema)
            -- foreign key a la tabla sala
        );"""
        


def codigo_tabla_articulo_calificado():
    return """
        create table if not exists articulo_es_calificado(
            id_calificacion int not null auto_increment,
            id_articulo int not null,
            id_usuario int not null,
            fecha datetime not null,
            
            primary key(id_calificacion),
            foreign key(id_articulo) references articulo(id_articulo),
            foreign key(id_usuario) references perfil (id_usuario)
        );"""
        


def codigo_tabla_calificacion_comentario():
    return """
        create table if not exists calificacion_tiene_comentario(
            id_registro int not null auto_increment,
            comentario varchar(100) not null,
            id_usuario int not null,
            id_calificacion int not null,
            
            primary key(id_registro),
            foreign key(id_usuario) references perfil(id_usuario),
            foreign key (id_calificacion) references articulo_es_calificado(id_calificacion)
        );"""
        


def codigo_tabla_comentario_articulo():
    return """
        create table if not exists comentarios_de_articulo(
            id_comentario int not null auto_increment,
            id_usuario int not null,
            mensaje varchar (250),
            respondiendo_a_mensaje int not null,
            
            id_articulo int not null,
            
            primary key(id_comentario),
            foreign key(id_articulo) references articulo(id_articulo),
            foreign key (respondiendo_a_mensaje) references comentarios_de_articulo(id_comentario)
        );"""
        

def codigo_tabla_peticiones():
    return """
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
            FOREIGN KEY (id_usuario) REFERENCES perfil(id_usuario))""" 
        


def codigo_tabla_documentos():
    return """
        CREATE TABLE IF NOT EXISTS documentos (
            id_documento INT UNIQUE AUTO_INCREMENT NOT NULL,
                            
            documento MEDIUMBLOB NOT NULL,
            nombre_archivo varchar(256) NULL,
                            
            PRIMARY KEY (id_documento))"""
        


def codigo_tabla_links():
    return """
        CREATE TABLE IF NOT EXISTS links (
            id_link INT UNIQUE AUTO_INCREMENT NOT NULL,
                            
            link VARCHAR(256) NOT NULL,
                            
            PRIMARY KEY (id_link))"""
        

def codigo_tabla_motivos_de_quejas():
    return """
        CREATE TABLE IF NOT EXISTS motivos_de_quejas (
            id_motivo INT UNIQUE AUTO_INCREMENT NOT NULL,
                            
            motivo VARCHAR(30) NOT NULL,
                            
            PRIMARY KEY (`id_motivo`))"""
        

def codigo_tabla_bloqueados():
    return """
        CREATE TABLE IF NOT EXISTS bloqueados (
            id_bloqueo` INT NOT NULL AUTO_INCREMENT,
            id_usuario_bloqueado INT NOT NULL,
                            
            PRIMARY KEY (id_bloqueo),
            FOREIGN KEY (id_usuario) REFERENCES perfil(id_usuario)"""

# def codigo_tabla_mensajes_from_seccion():
#     return """
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
#         DEFAULT CHARACTER SET = utf8mb3"""

# def codigo_tabla_peticion_has_files():
#    return """
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
#             ON UPDATE NO ACTION))"""


# def tabla_queja_has_motivos(self):
#    return """
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
#         ENGINE = InnoDB"""

# def tabla_queja_has_razon_extra(self):
#    return """
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
#         ENGINE = InnoDB"""

# def tabla_preguntas(self):
#    return """
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
#         ENGINE = InnoDB"""

# def tabla_pregunta_has_respuestas(self):
#    return """
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
#         ENGINE = InnoDB"""
#/////////////////////////////////////////////////////////////////////////
#                               F I N  T A B L A S
#///////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////
#                               I N S E R T S
#///////////////////////////////////////////////////////////////////////////
def codigo_insert_Roles():
    return """
    insert into roles(nombre,descripcion) values
	('Administrador','Administra a los moderadores y genera reportes de actividad del sistema con la finalidad de mejorarlo')
    ,('Moderador','Coordinan la actividad, relaciones y publicaciones de los miembros de la comunidad')
    ,('Miembro de la Comunidad','Persona interesada en compartir y buscar conocimientos sobre los dievrsos temas de las salas');
    """
#/////////////////////////////////////////////////////////////////////////
#                               F I N  I N S E R T S
#///////////////////////////////////////////////////////////////////////////