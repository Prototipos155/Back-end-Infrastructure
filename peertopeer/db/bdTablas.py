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
                and exists(select id_user from perfil where id_user=idAutor)
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
                if exists(select id_calificacion from articulo_es_calificado where id_user=idUsuario and id_articulo=idArticulo)then 
                    set resultado=False;
                    leave label;
                end if;
                
                if not exists(select id_user from perfil where id_user=idUsuario) 
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
                -- set @txt=concat(idArticulo,id_user);
                
                set @num=@num+1;
                
                -- signal sqlstate '45000' set message_text=@txt;
                insert into articulo_es_calificado(id_articulo,id_user,fecha) values(idArticulo,idUsuario,(select utc_timestamp()));
                update articulo set calificacion =@nuevaCalif, num_calificaciones=@num where id_articulo=idArticulo;
                
                if (comentario != "") then 
                    insert into calificacion_tiene_comentario(comentario,id_user,id_calificacion ) 
                        values(Comentario,idUsuario,(select id_calificacion from articulo_es_calificado 
                        where id_articulo=idArticulo and id_user=IdUsuario));
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
    create table if not exists roles(
	id_role int primary key auto_increment,
    nombre varchar(30) not null,
    descripcion varchar(200) not null
    );"""

def codigo_tabla_perfil():
    return """
        CREATE TABLE IF NOT EXISTS perfil (
            id_user INT primary key AUTO_INCREMENT NOT NULL,
            id_role int not null,
            names VARCHAR (50) NOT NULL,
            surnames VARCHAR (50) NOT NULL,
            username VARCHAR(20) UNIQUE NOT NULL,
            email VARCHAR(150) UNIQUE NOT NULL,
            phone_number VARCHAR(13) UNIQUE NOT NULL,
            encrypted_password VARCHAR (256) NOT NULL,
            active_account BOOLEAN NOT NULL,
            id_foto_perfil int not null,
            
            foreign key(id_role) references roles(id_role),
            FOREIGN KEY (id_foto_perfil) REFERENCES fotos_perfil (id_foto)
        )"""
        


def codigo_tabla_buzon_quejas():
    return """
        CREATE TABLE IF NOT EXISTS buzon_quejas (
            id_buzon_quejas INT UNIQUE AUTO_INCREMENT NOT NULL,
            id_user INT NOT NULL,
                            
            mensaje VARCHAR(256) NOT NULL,
            fecha DATETIME NOT NULL,
            hora DATETIME NOT NULL,
                            
            PRIMARY KEY (id_buzon_quejas),
            FOREIGN KEY (id_user) REFERENCES perfil(id_user)
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
            id_user INT NOT NULL,
            id_sala INT NOT NULL,
            mensaje text NOT NULL,
            fecha date NOT NULL,
            hora time NOT NULL,
            id_mensajeAResponder INT,
            
            PRIMARY KEY(id_msj),
            FOREIGN KEY(id_mensajeAResponder) REFERENCES mensaje(id_msj),
            FOREIGN KEY(id_user) REFERENCES perfil(id_user),
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
            foreign key (id_autor) references perfil(id_user),
            foreign key (id_subtema) references subtema(id_subtema)
            -- foreign key a la tabla sala
        );"""
        


def codigo_tabla_articulo_calificado():
    return """
        create table if not exists articulo_es_calificado(
            id_calificacion int not null auto_increment,
            id_articulo int not null,
            id_user int not null,
            fecha datetime not null,
            
            primary key(id_calificacion),
            foreign key(id_articulo) references articulo(id_articulo),
            foreign key(id_user) references perfil (id_user)
        );"""
        


def codigo_tabla_calificacion_comentario():
    return """
        create table if not exists calificacion_tiene_comentario(
            id_registro int not null auto_increment,
            comentario varchar(100) not null,
            id_user int not null,
            id_calificacion int not null,
            
            primary key(id_registro),
            foreign key(id_user) references perfil(id_user),
            foreign key (id_calificacion) references articulo_es_calificado(id_calificacion)
        );"""
        


def codigo_tabla_comentario_articulo():
    return """
        create table if not exists comentarios_de_articulo(
            id_comentario int not null auto_increment,
            id_user int not null,
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
            id_user INT NOT NULL,
                                
            mensaje VARCHAR(200) NULL,
            archivo MEDIUMBLOB NULL,
            nombre_archivo varchar(256) NULL,
            link VARCHAR(256) NULL,
            fecha DATE NOT NULL,
            hora TIME NOT NULL,
                                
            PRIMARY KEY(id_peticiones),
            FOREIGN KEY (id_user) REFERENCES perfil(id_user))""" 
        


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
            id_user_bloqueado INT NOT NULL,
                            
            PRIMARY KEY (id_bloqueo),
            FOREIGN KEY (id_user) REFERENCES perfil(id_user)"""

# def codigo_tabla_mensajes_from_seccion():
#     return """
#         CREATE TABLE IF NOT EXISTS mensajes_from_seccion (
#           id_mensaje INT NOT NULL AUTO_INCREMENT,
#           id_seccion INT NOT NULL,
#           id_user INT NOT NULL,
#           mensaje VARCHAR(256) NOT NULL,
#           fecha VARCHAR(11) NOT NULL,
#           hora VARCHAR(12) NOT NULL,
#           PRIMARY KEY (id_mensaje),
#           INDEX fk_mensaje_seccion1_idx (id_seccion ASC) VISIBLE,
#           INDEX fk_mensaje_perfil1_idx (id_user ASC) VISIBLE,
#           CONSTRAINT fk_mensaje_seccion1
#             FOREIGN KEY (id_seccion)
#             REFERENCES peertopeer.seccion (id_seccion)
#             ON DELETE NO ACTION
#             ON UPDATE NO ACTION,
#           CONSTRAINT fk_mensaje_perfil1
#             FOREIGN KEY (id_user)
#             REFERENCES peertopeer.perfil (id_user)
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
#             REFERENCES `peertopeer`.`perfil` (`id_user`)
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
    insert into roles(id_role,nombre,descripcion) values
	(1,'Administrador','Administra a los moderadores y genera reportes de actividad del sistema con la finalidad de mejorarlo')
    ,(2,'Moderador','Coordinan la actividad, relaciones y publicaciones de los miembros de la comunidad')
    ,(3,'Miembro de la Comunidad','Persona interesada en compartir y buscar conocimientos sobre los dievrsos temas de las salas');
    """

def codigo_insert_Imagenes():
    return """
    insert into fotos_perfil values(
	4,UNHEX('ffd8ffe000104a46494600010100000100010000ffdb00840009060712121215131212151515151512151515151715151515151515161615151515181d2820181a251b151521312125292b2e2e2e171f3338332d37282d2e2b010a0a0a0e0d0e1b10101a2d1d1d1e2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2b2d2d2d2d2d2d2d2d2d2d2d2d2d2d2b2d2d2d2d2d2dffc000110800d700eb03012200021101031101ffc4001c0000020203010100000000000000000000040503060001070208ffc4005110000201030203050405050a0a0b0100000102030004111221051331062241516114718191073252a1b123426272c1153335748292b2b3b4d1172434546373c2d3e1f03643537584859394a2d2f126ffc400190100030101010000000000000000000000010203000405ffc400261100020202020202020203000000000000000102110321123141510413223205f07191c1ffda000c03010002110311003f00a168ef0a2163f1ad84ef0f754d2425860123cf1e35e5367a11a6f6646957afa3ed2b148c7192d8f8552a38b4a601ce053fecc711312952acc0efdddc8f85341d481287a2ed7a0489b75154fe2509077a7fc36f448c421c9fb2766f91a9f8bf08d4ba8f5ce0f81e9d7d6ba3b22d35d9465196ab6709830a3dc294af0d2b260f4ab670d836071e5591898390b8a126b8de8ee2071e1d2abb2cf9727c00a6629eedbda2ea5682d11599706592424430861ddd58dddc8dc20f0dc9029f47f47931c349c4640dfe8a185101f412073f7d33fa30b509c3a1931deb80d72e7c4b4c750c9f45d0a3d1452ffa41ed55c59dd584509409349f950cba8b2f3ade2d2a73ddda6639f302aca091272601c67b3f7f688d2c720bb8d412c823e5dc2a8eac9a4e9948eba4053e593b147d9fb09f89bcbc8b98a38e258082d134a5f9a1ce72245c0eef4f5aecd5cffe8eec560e21c6224d944f6eca3c179a8f2903c866435b82b373742f7fa34bc3d6fa0ffdb3ff00bfa49da7ec6dcd841ed0f7314abcc850a2c2c84f32454c86329c63567a785759ed1f175b3b696e594b88975155c027703009dbc6b917d21f6fcde58c90a5a4b13068e40eef0951ca712745624fd5ace31326cd766fb3b757f9680a450a92a6e2405c3329c32c31820be0ec589033b0ce0e2d8bf45c71bf109f3e915b85f91427efabb704e1cb6d6f0c0830b146883f92a067de7afc6a9fc67b59731f1986d10a7208815d4ae598cc273ab5e76c72976f5345452036d95de2fd98bce1a3da35adcc09de91d10c72c4a3abb47921d00ea54e475d38e96be07c61255503ae33e8479835746504608c83b107c4795711e0a4dbc9244b9020b8b8857f523999507f302d433635568783bd1d4b143de4c883bde3d00dc93e405452dfeca106a7600851e19f163e02a0d4236cb132cc7a01e03c87d91eb5c6cb463ec1e6b1693bd2f754744fdae7f6504f116fde86df6ba2fc3ce9b3c3f9f70c3d231f547c3f38d6ee799223089346ddd2fb1f828e94a52cabf09b29e277323641e807bfafa53db7bb22bc705e1932c679e4162d903ae054b35a115833db1841740d1a920355bdd68bb7bbac4e50b1dd6e8586e41a203d1b24e2d1f3d69eff00c2882848383838eb51e9effc28941419d3175b21b7b72aa46ac9c934df80c3233a044d673d01c13e3e34aa581d9c107ba3e7eb569ec824ab23344c80a2e70ea48df6f03b53476d15c9edb5b2cf25d598509730344c3c644c60f9ac8bd3e74bef0b8ff279f9898fa921d63dc1c6e3e39addff00189f712421c78e86c8fe6b5571eead5d8e92616df383a37f51d0ef5d4d8914ff00bb4311c48060255319c8dceebf06ab0da5c9c0d276f9d54e259cf4d33aedb6c1bfb8d619151ff26cd03f8c7203a09f774f91a0981e34fafeff00d2df7d26a5c9c7fcfe1558e2526c40f5a2c71a0302e13467a32ef193fade1f1a12f9d4e4ae0e73bf5a3645c1a3a4fd1e7f05d8ff0015b7fead6a8ff4cee56ef87b852dcbe649a4100b08ee2d1c804ed9c29eb578fa3cfe0bb1fe2b6ffd5ad527e99222f7760a1b4eb1247ab009512dcd9c6480762407f1aea9747347b0ff00f0b917f98dcff3adff00de549f463c4bdaaf38a5c08da312bd9b0472a58010b26fa491d54f8d43fe0997fcfe7ffd3b7ffe9537d1870df66bce296fcc32089ecd43b055621a167dc2803ab914172f233e3e0b7f6a783fb65a4d6c1f97cd5d3af4ebd3b839d3919e9e75c63e91fb1b370fb33335d24c1db945040633df473a83735ba69e98aecfda9e2e6ced26b909cc312ea09ab4eadc0c6ac1c75f2ae37f495dabb8bfb3685ed638551b9a5967690f711c690bca5ebabae7c2b49c57608a93e8ef35c8fb49ff0048a0fd6b0fe8ddd75cae45da53ff00f4707eb58ff46ee8b023aed705bc9c8bbbb551def6cbac9f051cc3b9aef55c21adcbdf5d0c123db6e7babf59ff002a7e42a59dd44ae049cb65db863e230b09c0c0324ede78dc2e7afe02a58ee0856f675ce012d2bfe711e5e26a6b5e18ce179d80ab8d30afd551fa5e6698ce80230030349fc2bce6ce9724982767d049124cdde760724ef839fcdf214df14a7b29fe4cbef6fc69b53c5688e5fdda308af0d1035eeb745c49db009ecf34be5b5229f5787881a471a28b27b2beb215a296f28a9ece82368694a2699c7d97bff0a956bcb0effc2a50b458c8f694efb3972125c1e8e349f4f2a4c82a653413a0b45b2fe2319237f43554e1c8a4488c01d32b8c119d8eff00b6ac5c3f88f3579521ef63bade7e8692f20c57850ffd62823debb1fd95d4a4a5d0b04d5a1e708ecaea0190bc271f595b6f8a9adf14b2b940564115d20db7011f1e1e86ac9c3c158f567d281e2126c7cf6a7e3a1566979d9487b90a742b343e0629c168cfb8f852cb898c67ba3979f5d509f77955b38a056d3a806076208cd57e4e0c1a40b11299f0eabf106925a3a619232d3d1d77e8cae03f0bb3c7e6c2b19f468b31b0f9a1a41f49dc2e79af3873450bc8a24d2ecaa488ff00c66d25cb91f5574c4e7276daab7d99e3b77c29e446839f6ccdadd613868e423bcf12b6010d8194c8df707720dca3fa56e16477a5950f8ab5bcf91e874a11f7d7546719a3832619c25545e2a89d84b95938971965391cfb54cfac71346df26461f0a5dc6fe9304cad170f470c763712ae858c1f18e26efbbf96405f7f42a3b15c697873ce3d9ae265956df4b45ca6394e66b32192453a897ce77ce4d179237562fd53aba3a576c3853ddd94f6f195579134a97ce907503be0138dab90f6d7b1b7d6d65713caf6c5153bc11e5d587609b02807e755ee7fa50853eb58df0fe45b7fbfaae76cfe90e1bdb396da3b5bb5793960348b0041a64463a8aca4e30a7c0d06e0f6c294d692eceb36572b2c69229caba2ba91d0860083f235ccfb45c22e5bb416d2ac1234445bb1942931a8896e03867e8a7bebb1eb9149fb1df487ec082dae2369605fde9e3c196252768d9091ad067620e40db076abc7f84ee198c99261e86daeb3fd5e29949490258e50ed172ae59d899e36b8ba936ccd7576e8de69cf70b8f42003f1af5da4fa456b84686ca39230e0ab5cca341553b1e4c67bdaf1d1980c75c1a45c14888a051854d200f2036151ced38d071da76752c50f78d846fd56fc2a5593207ba80e372e216f36c28f8d70d5148ab67aecd2e2dd3f947efa695058c5a2345f2502a7a78f42e47736662b056eb46984355bacc561ac6355e4c62bdd66295c506ce0cc7bff000a985560f186ce702bd8e36fe95bea9175345a54d6c1aaafeedbfa56bf769fcc56fa641e68b707c6e2bd5dddb4891c877785b39f165f107e154f1c61fed0a2ad38a636326deea68e3920ac8933b070ebdd702b2ee08cd2ebab8ce7ddf8557fb2bc542a0859bf272126273d03f8c67cb3d4519c40b2e73f0ab5fb1251a7ae9915dcdb0f4228be03186724d239e5cd58fb3719099f3a965952298636c637ea3603e355de31c36371ba8cf98d8fce9bdfcd83d6964d7b8f23518bd1e8c6d229f75c3a488ea8db3e87affc698709ed00fab277587879fbaa7bbb94249760bff3e54bc468ec1908386183e39fff0033546f469493d30cbfbbb9946a1180a3ed75a50b70c76d3de3b01e1574e1d60d22609c034938ef678db9e6a92403de18df49ea47e34b164ee2df44561c3d23ef48c19baf981eea264983823e22915fdd843dc60c3486ce719cf979d49c36f0b0ce3075631e1a71b9a772756249f2d31bc069bf0c84bb051d4d246942feca73d97bc22652318240f9ed4d29aa38beb76749b64d2a0790a5f27e5ae153f322ef37ab780af7c46f8ae238c6a95b651e5fa47d28ee1360214c672c7776f363514acd7c77fe836b75acd6ea8739acd6eb55bac632b2b2b558c6eb2b2b2b18f99d780fa9a957b3e3ccd5b96d2a45b5143ee65f822a23b3c3ccd7b5ecf2fad5bd6d6bd0b6143ed97b0f045562ecea791a6b69d9688f5534ee1837a756508adf6335203e15d9e8442f194d4ade04e083e0ca7c0d25bc796dfb93e5a3e8b2e33b7807f5f5a7fc7e678ca046d209fbe8596ef52e897193b64f4343ec67662c4b85bda657255d446923af87955d7852e88c7baa8a6d0a4a796da77e8775f955aadafee15007b7d63ed46c0fff0013bd093e43c7124bf1665f93a83e036372a7a1144dadfdabf40a87c8800fcfc6849f8b29eb04a0e3a68f1f9d27b8be6fcd831eaf81f70de968af06d6c47c7f864924d26582c664d5af6ce318001f751bc0ec0330541b7867a9f366f7d64b1c921cc8738e806ca3e1e3563ec9db01a9be14fc9d512a51ff00233b41cb217c0530bfb51221dbc2a19a2cd30b43951589b7e4e49c5f8518642ca01527ea9e80fa1f0a1a1b940770cbf0c8fbaba0768ac8124636354b9ecb4b1142c7b36d3c447d7cf9614e7f0a77d9389e5902c6ba483ab5b7863c97c4ef4a6da220d5dfb37018d4b11bbfe141b166d45596de17c3922048259dbeb3b7d63fdc29852bb5bca6092034c9a3ce95bdb24acad56e98432b75aadd14632b42b75958c65656565131cad12a4d15b8c54b8ae33ac88257b58ea402a5893344c4423a2eda5c51115be6bc4b6a453a159e78adaf3e3c0fac3753ea2a83daabd70635dc30ddc7bb61fdf57c472a6b9df6b2e7993bb78741f0ade4f4bf8f4e72717d10d971025b0c771f78aba70be27ddc66b9cb02a437a0a75617876a66859fe3268b94d724d046207ad0d6f3eaa390500b9681e68c014e7b3cb88c7ae4d2c9a99767e618d3e23f0ac4d8eb46d52daedb5644335bc629c405e356fa90d53afa0d433e23f0abf5c26548f4aa85c47a5c8a56186c596106a751e640ae90d6015401e000f9573d8e13ab03ae76aea36ea742eaeba467df8a0433b12b4654d1305d62984b6e0d2f9ad315892d8ce0b9068806abeac568db7bdf3aca42ca034aca8e3941a905553b24d51bacacaca2032b2b2b28d18e629528a1d5aa457ae4a3ac985176cb40a9a65662b518696f1d4cd166bcc3d2a70d4e89b155e5a6c71eb5c8f89a779b3e75dc1c035cc78a7671cc8cc582a927d4f5f01599eaff0015963094b93ad0925b2cdbc6ff00ac0fbc1a0acdb048ab60892da30921255881a4e36f5f7d49c4786a72872946720e46e48c79f953ae88fc897e6dae980f0e6a6e64da90d8b60d3167cd0153082d9ad072a720e08af0240064d57b8bf1e6d5a625c9f1a2a366e4743e15c683775b00fdc69d29cd7115e25727f340ff009f7d5bbb23da8910e8b82083f558751e8de9478b46b4ce8c7a55678e4786c8ab1c52860307349b8d264507d1a3a6228e5c48adee3f2ae9d0481941f300fceb94bb6e3e35d1b80cfaa04f418f952a23f2168695e5933581ab0351390166b6cd012c2453a26a196306850ea42b86e4a9a656f780d01736d413b15ac33a659d5c1af555eb7e218a6705e834ea44dc3d070add46b2035eb553290947205bb15ec5e0aa89bb715225cc949c0e82e30dd0a6f67702a85693b938f1a776ed2819adc0c5de3ba1528ba154d86e656008f1af735d4c98cf8f4a146a65c567c9aad5d3996e73f9910d4dea7f347edf857be1734bafbc36208af50c788e63e6ff00ecd0674618d6ce75dacbe6967d2093a48000fb556c91cda5ba472383238e9e448c95149fb1dc34497b34ae32b0924796b63ddf9004d29ed5f1532dd919eea7747bfc4fcff0aaa5aa3aa94aa232b63bd1e8d4af87c9a87a8d8fbe99474842517174c8ef093dd15ab3e0283bc464fad48a3bc29e5bae456e8c9098d828e8054125be3c2ac12c5424b0503510f08e38f0774f797cbcbdd4eee38d432264360f91eb557ba8684d383581634e6e5bf0abbf666eb1163d4d73e5980009a6f6fc4de35ee8c835a84c9b4744f6b1e75b1742a809c7a423214d6ff77e4fb268d339b897ff006b15a3742a86bc7a423214e3ceb47b4327d9a146e25ecce0d097001aa7a76864232149158dda07fb06b51b88f2e463a5411df95f1a48fc75d86741c5033f1473f9868d068bddaf181e7478e26be75ca7f7564f006a51c7a4f235a8145724144475148b45c294de0624b453a8d3642d8c0cd45c1ac1a5934a8f7fa0f335d07877044846fbb799fd94638dc8dc944abf0ee0f3328cf747af5f951adc106dae4638df6ab0ced8a065355fa9217ec6c82da0452319f89adb44796e31d5cfe15093b8f7d3c44e9529c117c3265716c85bc2da4619c966f538c0cd716773cc6cf5d4d9f7e6bbbf181b1ae1779fbf49faedf8d363f274c1fe43ee0d2f7f1f6933f15ab0c7d2aadc3090c5f190a02fcfad592da4046474a497653e4b5cc954f7a9dd93f4a45e34d6c8d2b2086fcbcd432c144c3d2bdb25018afdec14a9937ab45dc1b521b88b7ac2340cd1e46298dac0e54018db6f8d08b474326053256c493a465b5b4aaa460753e22b52875ea289f68dabc8b9a678d115300b2b921319f135ee4b8daa792d15877363d71e1403291906a6e343a764f65707401ea688331c50161f57e2688cd2d0c8f563707411e1a8d4ccd50db4380749ce4e6a5c11d45063716096ebf587e957be47a54963f9dfad53e2b360a29ec28eb75c900753b0a10d5a3b1961cdb85c8eea778fbfc3efabc55ba39ecbb766f848822191df6dd8feca3e77a29a81b96aef51515473ddb049da839057a924c1ad3d49b1d02baef4f63e9f0a4c45398fa7c054267462629e31f54fbab905ef0290cacf18d409248ce3049fc2baff0018faa6aa56f0e013e66a716d33a39f15622b3b3d0814f5ea7df53dbc457a743e1e5eea6171083419caf5f9ff007d3b473cb2394b93250734cec9a95a9a63646a6d51784ac7d6c68c0b9a06d5b6a611528ec8278b6a417d160d5a596927158a882c44454a0ed5a61589463d939ad1b0d5a06bd2ad78b838aa9cc110cb5eeea2d6323a8fbe818a4a32de4acd586e802c8774fbcd4e46d534b001b8e84e7e35181b573b54cb2e8531cb219005f3fba9b9bb283bc71d36343476b9198dfbd5e24b93f5264fe578563a22b4156728d4c3cf7fefa24b1a530c3a5832b657ca9b52b126a9954c5751ec15872e1e611bbee3dc3a573fe0dc3ccf2a463a13b9f203a9aec504611428d80007cabbb0c77670cdea8f6e696de351d23529be7ae893d128a16dcbd6ad27c823caa099ea1b0d465c01d41ae672d964866064d375d87c2bc5bdb851eb5e2ee6d20d4e6ecbc23428e372f748f3da9148314c19b984b1e8361fdf42ce9420bc9b24bc00b0a89968865af0569888049011bafcbc0d4f612ef83b1a9585425683568a4254cb0d9bd3484d21e1f3669d42d523a6f41cbd296f158b6a6708a86fa2c8a22a7b29d20deb4288bb4c1a80d05d9a7d1b41505ff85109507111b03e46ac720329dea78e4a1d47df5ed4d630ce27d430686618cfc6b227c54f36e357a6f4935e4783f00611241dd3a5c7956e295bea4a01f5a5f6084c99e837de9adebe4003af9d4e8eb4f447ec603774ede2289c54168db11e39fd95383492124ecb0f60384e88cccc377fabe8bff1ab448d50c6ba11517a2803e551c886bd58a5189e73db3734d4a6f66a96e339c0dcf95797e1a401afab1d8790f5a9c98d142b82dda56c01b789f0a7d6766b18dbaf89f1ad5adac934decd6ec22088b24f2e90cca1cb2c691a9ee973a1ce4e42851b1d43040ecdb3090daf12926922628c930b778b9800631c9ca89190e186e0ed90707a19fd5292b2bf6420e8f12c98a41c5ae4b1083c7f0f1a6fd9ee052de5b24f25d4b0b3997312a5b911e991d3465909380b8273d734a66ecdcc3882dac372640f0739e691633ca5121460ab1850ccd95001fd23be3043f8f31d7c88118500607850f325594762a26778a2e27399e30a5d1c5ab85d60943246b12b00707a30f7d56d0382f1c80092291a2900395d4b82197f4594ab0cef8619a7963714454f930374a89968a9e4018200ccec0958e347924206012110138191be31bd0b77308bf7e4961d891ce8a488100163a59d4062002700e76a4e2c368f056a275ab370eec897b51757371340186a114506b75463840ea519d9c8c12028c671e19356b297544aec7aae49c69e9d491e1eea32838ab608cd3e8f56d21561eb565b29722aaa27c61cc53e938c37b3dc6925b0130dcbc1c9200f3c8c75a36def5a27589e29d647fa913413091c7fa342b97c78e338f1c54a58e5dd1d10cb15a6cb8c0d524e322945bf148c07e66623100645995a2640738665700e938383d0e0e28a938b284d4d15caa7fda35b5c2c607da2c53017f48edeb4aa327e07738af220e24b86a0cd15c52f11c968d65914672f1c33491edd7f288854e3df4b45ea94e60594c7b9e6886631601c16e684d1a73e39c568c257d0324e35d842579be5ca1f9d7881f5c90291731c523e1a65b59db09ca91d4c798c86cb2a0d81d893eb537188e38a658a192eae03c52390f69323a956551a556152570c727040db7deaff005caace5e6ac5e1b6ada5416b0ccc5956dae58a0cb016f3e541e848d1b66a4849908585249588d5a62479182f4d44283a4676c9c6fb52f17e83c913ac95eaeae34c67cc8c0f8d471b100e21b8660486c5b5c1d2c3aab773623ca96cf702461a5b50c0391d0e77c8f4a0d34b63476f41b6ac00a9a19324fa54108dab2ddb127bf6a8b3a7c065a7e71fd2a9b5543036357bebde6905475360050533963a5773f87beb77121274af5f13e59fdb46c1084181f13e24d7add9e7ad115bda84f53e742f15eaa7c8d3263415fc7a948a128fe34184bf2b25ec6b667bbffc37f41eaabc3fb546c6e2fd047149ccbe9a4de66465eec69a59444df633d7a30a7bd82bb1ed575136ce52ddc0fb4a3988d8f3c10b9f2d6be74d7b2bc364b66bf79b4aacd7935c21d431ca31443537d9fa8dd7cab43f5469d72643d8c1ed1c3067bbcef6bce0ea0bcd9e6e84819c6af219c78524ec27675787f119add59187b15bbea58d6224b4d32f7829393f93073eb4ebb1e45cf0bcc6769fdb4a139e92cf3152475e8c290f617817ee6dff00224e42b4f6a4a724150e609175eac8196c480f8eca6984197673f86f8aff00aae1dfd5bd57f88aff008f5fff00188ffb1db55c3837069a3e277f72c072a78ecd633904931232be57a8c123e755199c3dd5ec8a4147b92148e87950c30bfc9e271f0a5c9fa8d0ecb27d1c5aa88ae26c7e5249dd59bc7444022203f64778e3cdd8f8d016139e27d9f692ec2bbcb6f70cc42800346d268651d010514fbc532fa3b957933c79efa5c48587881205746f7107af9823c0d05c1ec5f87f0030dce15e2b7b8560086cb3b49a1548facc4ba800789c5347a15f614bc7271c0bdb350e7fb073b5695c73395ab3a718ebe15ce24b5d10b2e49c23ee71927049271b75aba918ecc7fe567fa8aabf115fc9bfea37e06a59bc14c5e4e81c5b8a496bc2a29a2d3ad52c40d432312490c6db647e6b9c7ae28eed1f116865b20814f3ae840c586488da19a43a4f81d5127ca91f6bff008113f5786ff5f6f4c7b69fbf70dffbc13fb2dcd58903f68387c72716e1e5d73a61be7c7833446df97a878e932330cf43bd3e4173ed6e495f65e447a06daf9fadf593e38d1a3e54938fdda47c5b868738e645c4635cf42e7d9580cfa853f1c0ad5ff670dc7127927590db8b485534cd246bcee6ca5fbb1b839d253722b18f7d96b6443c46d900544ba7d2a3a289eda099801e035c926d4b785f0ecf66d620377e1ae40fd29202e3ef6a83e8e9a34e23c522873c9d76cd192ccf9288d0cdde6249c3a11b9f0a7a2755be8b878faa387cad8fd1124312fddaa81886f5f97fb9110db332823f452c6e36f9e9a9aebf8660fe2177fda2d695f6b66238b70688740d7ac7e16e557fdba6975fc3307f10bbfed16b44c1761c51defeeadce9d11436922e077b54a660fa8f8ed1ad2dec35a224fc4caa804dfb038f2e443263f9f2c87dec6a5e13fc2f7dfc5b87ff004aea95f65f8f471dff0013b791641fe34b2ac823768ce6de15642ea08561a01c1ebaab186dd89e3725e59bcd2850dcdb94ee02062391917a93be00f95704e049f928ff00513fa22bbef6363b44b37166ecf0896e8ea7ce759918c80640ee86240dba0f1ea783f0418863ff00569f7a8ae7f93faa3a3e3fec354a8a61b835206af2fbd711da1309c827ccd4849a8ecbea9f7d118a0c4474ae150f7031eadde3f1e9469359595eac7a3cf7d91b1a89eb2b2899151ed670f2313a16474dc3a31475f3d2ca411ea3c7c6aa1c438b5cdc0e54b753c884e3433e10febaa81ac7a366b7595c795b4e933af1a4e36d0dacad5d23c25c5d2019c2c7757288327274a2b803724ec3c68d8f86ab90d2493c8e0775e49e791e3df3989d9c98ce7c548359594549fb26d219ba4ceba5eeee993c579c5723c8ba61c8f7b6f5ee2815142aa8555002a80000074000e959594edb62a544725b77c48acf1c80603c6ec8da7ecb153de5c9ce96c8a8e6b7672ad34b2cc50e579ae5954fda118c2eafd2c6479d6eb2b5b3520193852e8e5736e795a74f2bda6e795a318d1cbd7a74636d38c636a9258c36c7a1ce7dde359594926c64a80e7e1daa3e5b4d74d1f74046bab928341053ba64c6c4291e5815e6e6ccb152d7176c5183216bbb9628f82bad7326cd86619f227ceb7595b94bd838a04bab4e63fe5649a6d2085e74d2cda7515625398c749ca21c8c1ee8f2a34dd5c94d06f2e4a631a79cd9c7919077cff3ab2b2979cbd8dc501a5b69c729e5874ae81c896487bbd749e5b0c8cf9d7936a799cde7dcf374e8e6fb4dc7374673cbe66bd5a3273a738cef59595949fb37146ded8b32bb4d72cebf5246b89da48f620f2e42fa932188382339adb44fac49ed177ac2940fed573ac23105943733214955247e88f2acaca3ce5ecdc57a02bee7216952e6e95db4abb8b9b8d4cab9d2acdaf240d4d8f2d47cea5ecd769aeac5e4789b9c2620ca970d239770301c4b92cad8c039d408036dab7594164927d8382f436e21dafba9a16812282d2390bf3391a99d84849934b155085896cb609dc9041deabf35b0c02b8180063c303c2b7595a5272ec314a3d0224b5297dab2b2a0fb3a5744b0be147a9cd4bcc3595941888fffd9')
	),(3,UNHEX('ffd8ffe000104a46494600010100000100010000ffdb00840009060713121215131313151615171815161517181817161615171516181815171615181d2820181a251b171721312225292b2e2e2e181f3338332d37282d2e2b010a0a0a0e0d0e1a10101b2d261f262d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2dffc000110800e100e103011100021101031101ffc4001c0000010501010100000000000000000000040001020305060708ffc4004e100001030105030804090a0502070100000100020311040512213141517106071322618191a132b1c1d114152342525472e1f0335362829294a3c2d2d3164493b2f143632434557383a2c317ffc4001a010002030101000000000000000000000000010203040506ffc4003c110002010204030506050401030500000000010203110412213113415105326171812291a1b1c1f0142342d1e1153352f1620624341643728292ffda000c03010002110311003f00f28f833bb3c56ccaccf990cf85c05527a026995e245c761624ee161f122e161b546e0c7c253b32371375403d8d20ae2a5b0a8900f853b05c83c64787e382aea775a1c756072c6d637117699119120eb868755549d91747560125b247970a9a3b2c234a572006c15a2a1ce4cb545207963c24b4d2a3234d2bb545ab3b0d3b9a11df2e14c4d6c8030b3e5063398a543b270232a6796cd53536b6138a0bb1411cae0d6ccd8dc180c9d3d22682298c31c0bb1ed3421a4e8012ae555732b7168d6bcb9292c74e8e5b3da41a96fc1e6648f701b44550f3a8c9a0a9e6441332ec4e05b91daad8bd2e424b52de9dbbc238888d98ba66ef46788598ba56ef467886a374adde967886a46491b439a84e49ab21abdc0d3d0b752fb1ed4e2427ba0a53222400aa80124329b57a2aba9c894770560528ad06dea278519f208bd4828931c02a49322ec4b194f3316543b65cf44d4c4e069078dcadcc8a945d8714d76643c519a23b3336df7a0cba3d1b50d76dad4124b4e54396cae4b254ab7d8d10a76dcceb55a1ce2417022ba3726f700a9949b2c5148a0d7daa248be3b516021848a8eb1da786e1e6a4a4d6c45c6fb8392a24848024ca6dad33d37d32f3a200d8bae53190219dec32823aa435c1edc981e413d42e272aee3b02688bd4f61e4e5c564b7d81b100ec51b58c65a242d320a8340c735df28c6b816069a018481a555f07a6864a9752d4f24bca030cb2445cd7e0739989a416bb09a55a47e066362b54d93cb706e9519d86519cf4af7771a446a8b8ec2aa2e02085a85cb63242795917664f13b7a323ea168912f7ef4b2482d11637a324bc42d12cf869dc13cf20c9e234969a8a512777b828d88b4856c6d613dc4f014676d071218428d9121c052488bb09c2a9b8b1292430666a191927256345ad0337138466ea6e0ac6adab2b8bbe8806d17934ca5b186b63750121a49769996d4768ef2b34aa272b4762f8c1a8ebb99134385d4241d331a50eddea86accb53b9744d6123227b3324d6940294cf50a4ac277216c9313b420000341ad43469aa52776348a144624009002401759a091c6ac6b890466d072399198d0f549ee2803b5e6eaf9b5d92d5030cad8a07d1cf1298c31d139f84e1738d490e2eeab4d43b165e929c5b4caaa46324c1f9712b9f6d99cf7b64a96e17b3d0730b1a5859d622841ae4695ae416982d0ab958c2c2a560b8b0a328661604b2867108d3c819c4c19a515660ddd16299112062aa2e02aa002ec376995e18dd4e82b4edd54953bbd052a8a2aecd57722ad14ab709ecc401f3a29bc348a962e0016ab8a78b27b083c41f514b8335a58971e9be6032d9de3e6bbc0aaea424ad744e338bd98385596936a9a762128dc92b0a98edd53130db7616c2e2f268ec8347ce233153b330abaed65d49504efa1830cad69c5871035ab33a346ceb782c49a4ee6c69bd01e47926a542e4878f69dc2bdfb3de9a131a47971249a9286ee34ac4520120048012009c72b9b9b491a6869a10479807b8200363bde40d8db469744e6989e5ad2e6005e4b731d66973ab47569872a669dc563acbdecd13acd67b635ae64969748646d28cc518607b9bd8e73b10a6ced5b70cee998eae8ec62160dcb4e54559990744ab947524a5d4816151ca4ee889694acc6ac4311517264b2dc7c6a3790f28b1145e4194588ee46690651623b919a4194f40e405db52e988fd067f31f678ae8d18f339f889fe93af2c0d1e64ad1631a7a1c65e968e91e4ecd9c126bdaf41dc7b2c60296542b9ab046d764e635df6803eb438a7ba1a935b33422e4e592415759e3ee187fdb45454843a17d3ab53fc98d27226c4465196f071fe6aacee9c4d0aacfa804dcda42efc9cd234f686b87b141c6dccb1546f91c4f2eee37d8e919707b4e170384b6952e196673a820f11a6dcd5ef63450b6871a0f9eab21a464009002400900240090024009004e2c388622436a31100120573a0240269da1007aa5ff152e5bb2a08cdf4018c0d21c1ce6b9ce06a1c5b43913524d730b661dbba461abbc8e370add628b917355725aa1a656e052689a6452b12b95b85555245b1d886051b13b8a8900c801200f71ba6c8d8636b1a3268a57b7695d78c6cac70e72ccee03ca293a981b405d9701b7dde28518add10b5f439a8ec2778534e2b6435161d0d8cef087343cacd6b0588955caa244e34db37a265000a872b9a231b20bb2d9cbc80056ba76aab88ad72c8c1b674365b9dcd69d2b4592759366a8d1691c073ad7397591b218cbc31e03f0ead63e9d639834c619a6fdd552724f46118b5aa3c16dfd1e33d1d437b77fafc5659e5bfb3b1a637b6a420b3b9fa0f70e25409a5735ecd73b2957bc9ec6e43c4eaa562c54d7336eeeb0460559660e1bdc5b53c319534bc0b1457246a0a0a03039bc1ad23c5a53f425a741ed51478492c047d9c47c13760691cf5b2c103b589d1ee70141e032f250b22b718b32ad172ed8de1dd8723e3a28e520e9f432e48cb49041046a144ac959a12f7b580805ce0d049a01534a93b0200f58e5232365cf63c06a3a4c0d71a627b58c94baa4d096b64748064323a6753bb0da330554db67121e16cb9459889517ba041d1d91a4039f97b90c71d508d859dbe5ee489203b7595ad6922b5c95151ea8ba1733eaa25a3512016145863511603e817dd56b8c1ac4d753e838127b8d16e8e2e9b3992c254463b6ed74d579143a106b5143421593ac914c6936c5f103bb3cd438f12ce132d8ae670fc1471a21c266859ec85b951572a8996c63608e84ee50cc89d8eb6e2b006b0135c475cb4cf40573a552eade7f336d2a76d4d1918fce84537772827a963cc8c5b7d8d93c4f8a468731ed2d737783ea3daaf2bbf33e5fe5cdcff0006b7cf00ce8feae60d43c6269272a1208a8d86bb1553d65a16434895dcf17c93ddfa407801ef56c29de94a4494ed351346286a05034f1aaad1aac69d9438571bda45342001eb5243f3058ad201ab24e8c1de31b0f6b08f528dc57e858eb482685e6777cd68185a3b5dbd170b8d6999c7abd246d20025800caba5094c2e0bd1119d013bdb4090015e508746e2410e68ab49d450e7c7249919ad0cab9626bed10b1c68d74b1b49342002e009208208ec20a8a33bd8fa72c376c7d0c6c7c6d760608c07319906939600d0d1c5ad00d2a32a2b8a23d416d3c8fb03eb8ac910aeb85bd19f1650a9a9cba838a6030f359774aec38658f227a92b8eefce62519569a686a9c5944dcd2434a476995b4c8636b5fa7d9c2a7c77cd108d156d0ccb47353691f93b444ffb41ecf5624f8e8382605f5cdddbd8c3f26c7edea48dd07dac2967cf28a5f7a038a82bb390b4f272d6cf4acd2feab0bfc4b2aad74a6b91155a9bda48ce9a1733d36b9bf6816fad41a68b134f6201c90c7c4803db997bda5b974af3c7adeb5d47429be4715622a2e62b0db482e711e9124ec04d7334509d3bab0e151e66cd017c3771557019771d742d6dea0ec2a3c11f1826cf68c6680150946c89c6770fb3c19d4aaa4fa1746dccdc321643504e5a69975b82c74d27f1343a8d2d0cab75f8626627bcedcb2a9a6bae837939057c69ddd90711daecf2de5173a524956594068d3a4ce9fab5a1771ea8fb4a9ab5e14f45abf81d0c1f66d5afed4bd98f53cb2f06be699ee24be4775dc4d33ad2b901bce400e0aba4e5555f986329430f51c23b69f23760b098e06b1d4ad093d85c6b4fc6e5d69d274a86596e73a94d4eadd03dbeeb68188cae2760a0a786c5cdb58e83899df028f6979fd9f714b423951ad76d97183951a3203cfbf8f6a695c9c517db2c458cc4c27515a6e4dab0da31278038d4eaa042c282c0dafa44704c14436d3039b139a5d8851d84eda53429b1b4ec73d0c75341afcdd99e5ecaf92adb495d95d3a72a92518eecf7ab8b9cc825a36d3f20f3f4b388eec328f472a64f0dfb454e15e320af82af43bd1d3aa3b78276bc02d20d454768de08c9c3b4542b4cb734ae8fca7ea9f62aea6e89c3709dfc4fad314761d2260d6a8ea477fa94a0ed2455515d1c8cccc2e20ec242efc5dd2670a4acda20e15d734ec2322f5b9ecef00ba088f69636be3455ca9c5f22c8559ad9b327fc3b65fcc47e0a1c18742ce354ea73570deb6b7c8019e42dd4826b5eca9cd510949bb5cd75214d46f647a4d86ee8dcc04b9c0d3653dcad9a9df430a8c5ead96b6eb8b3ebbf5de3dca1f984b2c3ab262ed887ce778fdc8cb30b43a9386d11466a1ce76cead5dea0a2e9396ec92bfe9b91b7728d910c4e219db2bdad6f8035770a855ca825bbb17c2127cd9cbdf3cef441858c7ba4d7f26cc235afa72674aed0b3a5421b5d9ad539bdcf3fbd39433db49321c116c8c1271d36c8f39bfbf2ec58f138a6fd98e9e4773b37b3632fcda9b72f1fe3e667c922c3189d9ab592d103d8ddff008a889de3da02ea6034ab1f33cd76a49caefc0e8ef592941db5f05d3ed196891cfc04756ccc99ee933c2e23b294f335f25cab37b23a2d82c8ca6fefd546c04a3b439b9028bb0b96fc2dda14eec2ec19e7bc9d9bd2105456670cc820eb4dbeef3525097404cbe0c52911b4549c80da4934a50eda9a512b926ec87e56c31c169659238cb059b1079249c6e928ec441da0616d76868d802aeb775a1e074ad1902b4d5606ac7ab8cd4d05dd7ca0b458487c0eac75abe1754c4efd20df98efd26d0f6ad342abbe56713b4f01151e2d356b6f6f99e817073d1670e06686688e9505b3b00de6b81fe656a7a9c2cb25b1dd5cdcbcb0da728ed113893e897745213ae51ca1a4f713de9893b2d51d17c2d9a9701f6babe4ea209269ec3f4ac768f69d7420ec4af6921495d1cd5f31524aef155dbc34af0b1c6c4c6d3b802d26629b59187334498d19f8dbbc28d891c65d6c82cb5335aecc0d41a35e6434153a346f03c1618d48c356d1d39d294d59234ed1ce258d828d7bdff6222d3e321a79293c6c57fafdc82c0f5322d5ce7b7fe9c323bb5ef0cf28c7b5532c6f445b1c143998d69e5f5b24f4191b7751ae908ef793ea544f192f05f7e269a58252ee45bf2467da2f6b7cde9da2403707601e0ca2cd3c6b7fa99d2a5d9155fe94bcfed818bbaa6af7927cfc4d5659625f247429f63c577e5ee2f658d83e68efcd54eb4df33753c061e1b46fe7a96bc6540a2996d58da368a0495a55d168e5558cdea46c313ba58dc03a81ed1880c8124644f0aadd85baa916baa3918b5ecb5e0ce92f48aae04e9a15d2ed187b5197231e024b2b8f315bac9570e8a521a400722da83e934d694cf3dc72dcb9f593725936f3b58d4b37345d7cd8e2c2cc2fabc5316440396673d73575654da595ea3a79deeac0b62ba839ccc7501c4f1a509aacea25ca2156eba582a19a84dc50dc503dd7044d907484edd29af791929d2c8a57915ce32b7b24add77833636c8436b5070d0015184efa81b2999f151947f36e9e97dff82b59adaad4f43e6a6e98647cd6819e0718d8081518803888d991a0a6943bd49a8b936b62155c92499e57cbcb4996f2b54a336ba57b5a73a111f506bd8d59e7a96d1bc5a33a079dcb2ca28ec61eaceeb40c1a66a87be876229b8da40cebb98778e07dead58899825d95877b5d7afef7297dd63638f78aa9ac4be68cf3ec68fe99fbd17c32dae21862b44ad68d03257b40e001002b1622264a9d91596d67f7e25c39457937fcddab8196478f0248562ab17ccc93c0568ef0f87ec4ff00c6f780d6727edc713bfdec2ac527c99965452d2482ecbce3db99a985fc618c7fb0354d56a8bf532b787a6f906339cd9cfe52cf03c7619d9c7d1914d626aafd441e1293e411ff00f498fea03f7897dca5f8badd48fe0e99c4c7773ceb41c7ee581d782d8eed3ecbaf2decbcff008088eeb1b5c4f0c954f12f923753ec782efc9bf2d3f7098ec8c1a3477e7eb553ab37ccdb4f03421b457aebf32d7380d4803c14126cd129c29ad5a4bdc0f25bd836d782b63426cc553b4e843677f20592f43f35a3bf356c70cb9b3054ed89bee452f3d41a4b63cfce3dd97a95aa9417230d4c7579ef27e9a7c89596d45a732688a94d496c4b0d8b9d396af434db202b238b476e35a153565961b518e4a0cdafc15074a870cc768c96dc1ced25e6be671fb4a9656fc627436c0085dec6b591a670b069e64d19a6020e448e0485c5b1d8b05d8eca0759da7ad49219a163cdd88e54d3b3f1440caadc68f2e1a200cdb4c15cc68934458198d46c2b1e9bcc64a41b603e881677703f2c0f901e09d37b99b11c8f27b5cfd34ee7ecabdffb6e247ad67ad3f64e8e068e7abaec97f048bc0592cd9db73a54c0ed1789d1be3ee57c30ebf51cdc476acb6a5ef2a6de6fdc0f729bc3c0a23dad5d6e93fbf32c17a1dadf350fc32ea5f1ed97ce1f12d65e4d3a823cd41e1a5c8d10ed7a4fbc9af884c7686bb470f6f82add392dd1b69e2e8d4eec91610a1b17b49ad4a64b230ead1dd97a9591ad35cccb530187a9bc7dda03beeb6ec711c73562c4be68c53ec7a6fb926bcf5fd8afe2b3f4878297e27c0a7fa34bfcd7b8365b4b1bab870d4f92a234a52d91d5ab8ca14bbd2f76a0925e83e6b49e392ba3867cd9cea9db115dc8fbc1a4b7bceda70f7aba3420b9182a7696227cede5f7729631cf700039ce3a000b89e0066ad4b9230ce6dfb527ef3a4baf9bfb7cf9887a31be42194e2df4bc95cb0f51f2b7999e589a6b9dfc8ecae4e66b139bf08b4e4756c4df53dffd2a6f0ed2bb656b1599d923d0ac5ccfdd2c03140f908daf964cf886168f259ec59c460979f36d77cad7305944799c2f8f135edd4020e61dfac0a93ca1094b53cbb949cda5bac64ba163ed30d722c638c8dfb518cfbc547054ca3166ca588943439a659a52e2c746f63da09a3c169a804d33a6791cbb0a54e0e32ba3455aeab432bdcdb967ab9a761a1f1cd7531752ece7e16163522631daac68e8015e779889c68da8686e11b2a4fa47f1bd272b1093327e3e73f2a509dda28395c8a9154f7b3da47b744aec6e41960bdcbc805801c4d196841343929a95c14ae1b7940d02a9b24775cdfb5b65ba2d96c3e9384a46fa44c2d8dbc71b9dfb488e8ae65aaef348f2bbaae6b44eec10412ca74ea309196552ed1a38959a506d9d0a75a9d386fab3b4b073356f918649e58acedcbaa0f4afccd2870f576ec729c20ae65ab8894fc8dbbaf99cb23339e69663b85226f80a9f3576532e60e7f349771d04e3849ef6946541999977873316777e46d32c67f4dad90796128ca19ce62f3e682dd1d4c4f8661b007163cf73c61ffec96563cc8e36f5b8ad366349e0923d95734869e0ff0044f715124051cee6e8e23d5e0a2e1196e8ba9e22ad3eec9a098ef278d687cbd4aa7878bd8dd4fb5ab47bd67f7e010cbcdbb411e6aa7867c99b29f6c537df8b5f1fd8b3e308f79f02a3c099a3faa61fabf718cb71e5cd3b9ee1b45a8d228c91b5e7260e2e39770cd590a529f7515d4ab087799dfdc7cdb42d15b4bccaefa2d258c1d951d6771c96d860d2ef3b98aa6364fb8ac76d765d6c83ab045130760a13c4ea7bd69a718c6f6462a9294deaee74177d9677834115064755555a918bd6e5d4694a4b4b1b560bb2406aec3d9427dab254ae9ab1aa9e1da7736030acd745d92447a60d3435d116bec4a0f2bd4ba29438542817277398e72393eeb6d93a38cb5b2b5ed9222ed3132b9123404122bb2aa510cd668f9eedd6192026295b8648ce078a8342dcb51a8a50d7b5699fb5493e83a7653b16d8a4272aaa11a9045f161ab43a953a771dfbfef4da1b465c776d057a31e19f82562394bcddb8c570e9bc2761d885db13592b6a282b971de925a824197e3a992721b3d0ae5b8fe1173c1642f318b438cb2103ac238e405d8468097060cfe91343a212f66c629cad36cedac7666c51b2260a318d6b1a3735a280780522b35dbff963c7f9d551ef13fd2672b480900240090219eda8a11507507307b92926d590c1afee6caecb554bacac8de6a71c3f246a752437aae3c4154f32de4792729399f31126cd68c42a406ca28453fee3323fb216b8e1dcfbaccaf12a3de479e5f170da2ca69344e68d8ed58783c65ddaaa674e50ef22f85584fbaccd50267a6dc7c818a2a3ad044aff00a0328c71daff0021d8ba34f0896b3d4e754c5b7a4343b28c068000000c8002800dc00d16b5a18dea5f1b9311a9632a2b797df211d4727c755dc7d8b062b7474709dd66eb42c4cdc387552b02926ae645e168ebd29a65afdca70d56842a46cc6b3de384530d73aebf7279014ac8b45b7a42061a533d6bec4f2d95c4e5768f26e78ae7c1332d0d194c303fff007183227b4b29fe9aba93ba7025b3b9e7565750ace8da8da7dbc060ad3ef5272d095c00de543507c94333019f7c93b7c0279d85cb227b66fb633a8da9a77103dada5f23580124902835cd1223267b8dc165c11301cf0b19103bc4628e701fa4f2f3da30a9a30b7766a20468b7ff002c78ff003aaa3de27fa4ce56902c81809a14f90afaa0cf82b543316e9d05f056a33069d05f046f6a149869d0b2d97d59e06639a6631a0664b8507154493e27a3fa0a2d28d8f35e54f39177b7188e574a6b88606d5bdcff0044f8ad94aaca0ee65ab8773ba4ce0ed9ce7d6ad1670e691f39c33ec2dc2e14567e2e5b596a463815bb6efee303fc5917fe9f64fd86ff004aab8fff0018fb8bf81ff27ef3a58f97d09f4a299bc0b6414dbad1c7c56958aea8a5e111b160e5059e6a619467b0931bbf65d4f225594ead37bbfa19aae166b546dc3426809aeea907c0e6b52845ff00b66394651dcd8b100067e7f7a251515a0e074d715aa3008e919ae989bbb8ae5e25dd9d5c2ab23799334e8e07810563360a3d0700a4f7214fbabc8c4bc3d329d2ee92abbaf2075615928e423443d44d187cbc84cf6295940e7818e21b4c8ccda1bda4547025115669a05a6ecf0e8ce7d87f1423614545ed5d7336d2778835eb687343680694cf666aa64e4ec644b3b9da9ee190512b6db1a390b4d42015d1af72da897d48c8035214a3b938cae749c97318b4b6695ed6343b0b1ce200123812dcce550d0e70ae550d07552215a5647b6d9f0d035a294028d20820532ea9cc2b12b98eeb70bf81bfe894ae8b3872fb64ad56d8e2b3b848e0da1cea451b57e588e8def2154b4904bd956671f79f2eac50e2c53b09683d567cab8915ea8c24341cab5c54ed53cc57abd91893f3b36561ab63b4bb75040dda41caae3b13e41965e053273d510d20b41e2f807ff994b2925988d9f9ef8aa71c1281b28e8e43de28ca79a5a0ed2f0392e5173b16cb412233d0b340051ee23f49c461af0684683cbd4e1add78c933b148f7bddbdee73dc3812517e83492052a23120048024d908d0a69d80b1b3e95fc77279ba8ac6b5d3ca59a1a343eacfa0eeb332dc0660f685385471d88ca09ee19272e2d07411b3ecb3fa9c54de226254a243fc6b6bafe5dd4d808141e19f9a5c7a9fe4c3851e85ece5ada6b426278d7acd3ec214d6227d45c289d3dc1ce7cd1d03c9681f41cec34a1ad18f2e09678befc57a682cad7759dfddfcb16cd476363f16cc98fae6694df4072a6c56470f06bf2e5e8c8caa4bf52365b7bc4454920ee20d7caa3cd41d19a76b0f3c7a98d7b72ce1847a4d190767d6384e84341a11c09470d47beec176f6479ddfdce44afa88727508c6ea12dc8d30b6941b3c3343a892b415bc79870efde390bb2da5ce707bb13892f0e3ab893d7af6d73555eeacfcff73553766683c07501a6d5548d0674f75907a998dc751ef51b11ca345753c9eb100789ee45832b66908c3006b72fc6d5244b6332f3bcb1b9b1b4d18c6b9a3f49ce3591c41a8d8d1fa81496bb9966eeceb391fcbb9e0735aef94801ce3712e2c05c286176b19ccf6766e7dd2994148edf945ce9b581cd831485b9073cd60a16b5c0d1a03a422b4a1edcca8e80b3b5ab3cb6fce56cf69756595cf0dae06d4b236e6685b1368d191a5680d32aa76ea49452d8c2b45e4e35188d32a0190c8535d77a774895815d683f8cd199858adcf276949b191510120048012004801200480120048012004801513b012c4788fc7827a81a560bccb052a41a646b4a675a13bbdc9a6268eaaede56cdd1963e4120c2e2d20fcab5d81d415199ce99ebeb5a238895acd953a4af7471b2da5d9876b5cc6791db5aacc9d8b6c0ef989436d8ec332520823506a0a433720b50780e1de3721ea5e9df50c86d7c0f61fbb34895c98b6537243b815bad946970d746f13b7f1b9344252b2b98aeab682a34af8d7d8ac5a233936c8322767e021db98879ed8e7655141bbb05025e43b0339d5da9360320064804900900240090038081a4dbb2088ac2f76ca71cbc9552ad046da5d9d5ea72b2f1d3f92ff8acfd21e0abfc4ae86cfe8d3ff35ee2a92ef78d80f05355e0ccb53b32bc3657f2067c646a08e215aa49ec629d39c3bc9af32299012004801ea9dc070534c0643603a76013c9352733b5260452012405904e586a3bc6c281a760b16d69d5a7b8a09e7431b68d8df13ec09d833ae4578dce357674d360ee1f8d14ec41b6c84d5a9fc782045490090032403240248048010081a57d105456079d94e3ee554abc11ba9766d7a9adacbc7eee1915dad1e9127c82a25886f63a74bb229c7beeff000414c635b900070d4aa5b94b737c61468af65246ad9f93d6c9055b66970ea1ce61634f073e80ab21879cf6466adda5429ef25f3f9037c5b2fd11e216cfe975fc3de73bff005061fc7dc265db31150ca8ec23d5aa8cbb36b6f157f2274fb770db4ddbcff74532c4f6fa4c70e2080b2cf0f561de8b5e8746963f0f5748ce2fd5033ecec76ad1eaf528aa935b3253c2e1ea6f15f2f9143eed61d091e6ac58892dcc953b268cbb8daf8834976386841f2f5ab56222f73154ec9ad1eeb4fe1f7ef059227375042ba3252d8e7d4a3529bb4d344132a1200929808a180ce4980ca2024016c71575069bea07ad4ac049d84572af7fb93d100dd267ba80d0790437a81073b7a2e0320048022a2024809471971a004a4e496e594e94ea3b415cd1b25d0e790332490035a313893a014dbc1512c4728ab9d4a5d94d2cd5a565f7cf6f99dadd5cdb5bdf42db29603f3a473587bc38e2f255b8559ee69862b0587ee6fe0b5f7b3a7bbb99f9dd9cf688d83746d74869c4e103cd4961bab2aa9db2bf447de76373f35177b05646c93107e7bc81e11e1f3aa9c694537a186a768d79f3b791d7dd970596cff90b3c319dec63438f170153deac492d8c929ca5de7707e5337aac3b8bbd8b4507ab33d65a238df88acff416ce248cb92279f5dde89e3ec0b6e1f630e2370a5acc6512d92377a4c69e2057c5553a14e7de8a7e85f4f135a97726d793653f14c27fe98f3f7aa7fa7e19fe846a5dad8d5b5466adcbc8782d6f31873a2381ce0e04b86205a0626b8e6dcf6107b573b1d80a3086682b3b9d4ecdedbc5caa5aa4b32b735e4737cabe47da2c0693343a371c2d91b9b1c684806b9b5d40723b8d2baae1ce9ca9ea7aec3e329629657bf34ce16db67c0eec3a7b96ba5533a3838dc2ba152dc9ec0eac318e14900e80114d80ca202233a25744b2bbdb9927b6848d6888caeae3a90c9271e830cd36c8a5776139841a1d5454935744a709424e2f719c08343aa69df514a2e2ecf71553b91192012004803a0b1c0406b00a934141a927ef5ce9cb34ae7afc3525428a8be4b5fa9ef3cdcf21db63636799a0da5c36d08841f9adfd2a6a7b8655aeca54b22bbdcf3d8ec6baf2cb1eeaf8f89dc2b8c024009005b65f4bbbda1572ef7a0d155f165748d01a2baeda6ea2b212cac8ce37472ff17cbf47cc2d5c4f03265678bc36895ba16f92d717523b19e71a72dcb3e1736f6f8056f16b7815f0a8f88be153ef6f8238b5bc05c2a3e2236b9f7b7c10ead65d038547c49dddca7b547235d1e10e6e9b41ec2368509aa938b52b0e0a14a69c43b941cb3b6da607413744e63e9a30020b4820835c8d563960f89ec9d1a38d7466aa2e4fe1cce1adf062691b46617129b74e767e4cf638ba71c561f3435d2ebefc5184b79e584801d4b9008a4c0bac31e278ae9a9ee555595a2ec6bc0d2552bc53db7f705456438b1be807a446dde2a1552aab2e58f91ba960a7c4e355b25deb73ea50f1156a5ce27b0003cd58b89c9232cd612edb949bf0492f88df25fa63c0a3f33c05ff0066ff00cd7b9844f135e0383e9f36aecaa4695dcab84a506e2d789aebd1a55e11a919dbf4eba5daea5779454c2ede33e23b54a84af7453da549c5c276dd6be68095e730480120026ee8b13c6e19f868aaad2cb13776751e2d757d96bf7ea753733e564ad962c9ec3569a35d476c385c08247052c0e1b3fe635a1a3b6f1f92d878bd5eafcb923a96f2d2f43a5a1c783213fc8ba5f87f03ce71fc471cb2bd695e9dd4dfd1c54cb339e0ec3e08fc3ae81c7f123fe36bd3eb07f621fe947e1fc038fe22ff001b5e7f593fb10ff423f0fe01c7f11dbcb8bd069693fb10ff00425f875d038fe273d7cbe4b5ca66b452491c002e21a090d14193401a052549ad120e2df980fc58dfcdb7c9191f40e2f89d3fc56cfad41fc5fedad3a992e2f8b1bf5a83f8bfdb45d8ae3fc5adfad41fc5feda7760237737eb307f17fb6937a6c08cf8aef60754daa0f197fb6accda6c427bfa974d628cd296a835df2ff6d285f35ec0e578b4677286c022782d918f0e15ab31501edc4d0bcff68d3cb53325a33da7fd3b89e261f84f78fc9ff271f784385e771cc254659a265ed0a1c2acedb3d5032b4c22400ed692401aa1b496a4a31726a2b7668b5a226388357fa35d80ed0382ccdba9249edb9d88c6384a329c5de7b5f95f9a5e435add8630df9ceccfaca29acd51be48317374b0b1a6fbd2d5fccce5a4e289001b633898e8f6fa4dee5454f664a675308f8b42741efbaf42cb13818dc1c2a067dc7779a8d54d4d35ccbb0538cf0d384d5d475f4f0f2d40ed30e13bc1cc1de15f096647371143852b2d53d53ea8a948ce2401af764546577fa82c55e59a5951e8fb2e92a745d47cfe48edee6b108a8e16ab357ff94ea3307e4fb57a1a54d53a51a6f91e2b158975f133abd7e5b2f81b0db5b87f9ab2e6003f96cc0ecc14fc0dc292cb12ae2319d682411f08b2e6083f96d08a6d6f69f5699232adf50e236671bb99f5ab3f8cbfdb53ce476226ed67d6acfe32ff006d2b8ee57258636eb6a83f8bfdb4b36b64833158b3c67fccc3fc5fe84eefa3fbf5239fc097c0d9f588bf89fd095df47f7ea1c4f026db9263a4d65ff5e3f7ab2f1f1051bfeafbf7109ae995bacd66ee9987da84d3dafee0e1cad74eff007e457f17c9f9db3ffaacf7a76f062c93f1f77f031bbe4fcf59ff00d567bd16f063c93f1f714fc4aefced9ffd66295fc1864974f81265caea8f95b3ff00accf7a945ebb31384adb7c03efbb98f425dd2c04b062a09585c40d4000e67dcb998ea7c4a4f4db53abd8b88e062217d9e8fd76f89c0def1e41db8d3c7fe171f0d2d5a3d376c53bc233e9a7bccb5acf3e2400559fa8c2fdbe8b7b379554fda928fab37e1df0694ab737ecc7eacbdd1e71c7faceefcfdeabcda4a7e88d52a57951c3ff00f67eba835e126279ecc8777deada31cb0463ed0abc4af2e8b4f77f20eac3109005d63930bda7b7d7928548e68b469c1d5e1d78cbc7e6190b704c5bb1d5a77e63dca893cf493e874a843f0f8d74ded2faebfc153195c511d41259c46a3bd4dbb5aa2f533c219f3e165ba6dc7d397aa02579cc1200ec793b7774b2363c4c686b711c6e0c6d1b4caa7b48c951838f12bdfa6bfb1deed4a9f86c0e45bbb47f7f81b56eb84e2eacf6568ddf088c79557769cb35eeb9f43c449037c42efacd93f788fdeacb47a7c08d916c374c8dd2d163efb4467da9495f4d42d677456fb8de4d4da6c9fbc47ef446314ad6f80debb8df10bbeb364fde23f7a768f4f80ac87f885df58b27ef11fbd3565cbe0161db71b87f98b27ef11fbd3cde0c2c59f143feb164fde23f7a337831587b3c829a8f1509265916b52ec63784b51dd0c64036846a17447a76fd21e211a8b3c7a8ba76fd21e211a8b3c7a930f1bc2352574c72e1b48f14ec2b9c95e767a6366b4ad3d63d8bcdd48706bb8f8fc19ef2153f1b81cdcdaf8afe51ce2d679b1200d031d5ec8f63467c752b3e6b4253ea761d2cd5e9e1f9477f3dd937bcb2473dcd34390234a65ee51494e0a3165b3a92c3e26556ac5d9e8adf7d0a6d163cb1333073a6d0a70abae596e66c4606eb8b45de3bf8a2c96cc7a36868ad685de1928c6a2cef37a16d5c2496160a92bb7abf7683d86cc68f0e04034d77e79a556a2ba712781c24f254855564d2dfd750686c95189c70b77ed3c02b6556cf2c75661a382728712a3cb1ebcdf9209a3a47348140df9c752abd29a69eef91b5f1317384e0ad18fea7ccaedfd59038761f0cbd89d1f6a9e5655da1f938a5523e0ca2dada3dc06faf8e7ed56d2778231e360a15e4975f9ea46c8cabda3b7d59a2a3b45b2385867ad18f89dbdc4d0039c4ee1e199f58f05a7b329da129f5d3dc4bfea2af7ab1a5d15fdffe8aef478c7a8d06de2ba94568fcd9e6e5aec098c6f0ae23662c6378f140598b18de3c501662c6378f140598b18de3c501958b18de3c501958b18de3c501667d4303881e837c970a56ea756f67b16b5ffa2d1e09683cc0b6cb6b346807c1118b1e74510da438d03076e941e4a56b7312770bc0370f051243d382059504c0d14d078224091e49cfadcf47416a68c8830c9c455d1e5c31f8058f131da477bb1ab6b2a4fcd7d7e87845a63c2e70edf2d8b442578a6737134f875650e8ff00d0accdabda3b4226ed16c30d0cf5a31f142b4beaf71ed2882f6521e266e55e52f16111de041eb7581a64aa9504f6d19b29769ce2ed3f6a3d02e20d775a3750ed1b3bc7b9532728e9347429469557c4c3cacfa72f55fb05aa0e9ad16a4414cae32bb289211e948716e14341dc3556a9beec343254a114f8b8879ba2b68bd3f7059ef227268a769d7ee57430e96b239f88ed594bd9a4acbe3fc0039c4ea6ab42496c7265272776ee1178fa6780f505551ee1b3b47fbefc97c8b2ea655f5dc3d797bd4710ed1b17764d3cd5b37447d47c85b07c1ec1678eac07007baa457149d720e5b3153b95f4e3960958e762eaf12b4a57e66f62fd28fcbdca666b8d886d7b070c2543f5fa016f427e90fd96a9e9d0351d91d3520fea80861726fa015c20f6002a9587733a4b60ae41c3b0b1aac512b7204b65e98299135afcc68d13c8acd89c997fc33b0fec351957db1dd963a8732d3de48f255a94b920cde02e887d0f328cd2e819bfe24e83f363c0257974f88f3bff0012b32d0901a07729dba829df90dd394650b9264a494582e4db79b5b96669b943da96a91173b33079721b6bb0cd0869c5871b3edb0e21e34a77a854a72945ab1a3098ae1568cedcf5f2e67cc77b33ac0ef1eafc05461dfb363b1daf0b5552eabe40b67751cd3da15d3578b473f0f3c956327c9a0a634094b5c01049d7b74a2a9b6e9de2cdd08c618c70a8934df3f1d8b259887e0646daf0d76a846178e69499a2ae21d3ace8d2a51bfdf9170136d2d6850fcae49b34a58d7ac9c62befef72c6cc342f048d6996d51707ba562d8e2216cb29a6f9919276533391da0eee19a2309df4442a6228287b52d1f35fc6a54c6d7d098f039956376ef40a21173d28577e4f7fbf41a2738c981f85c2999a04494543346e8546552788e0d5cb25e4814303a5a01962f21ff0aebe5a777d0e72846a62f2c5699be08a6d3262738ef27c3629c15a2919f1153895653eacd8e4cd93a57b59b649191fed103f99515bda9c62753b39f0f0f52afde8aff53e9b14190d0641746c79ab8b122c17299dca297e67a7d4527a075df787cc71fb27d854a5012985be77051b12cc47e125194330be14519433025eb35437bfd89db4645b34b1a561e628f8414651e62e8e43b5160cc4fa44585980e47f58f1f6052b118bd591c495895c8c99834cbb6954ec1733a3824a641db7d68a76cbeff9906d954ed95a46455b1499072699f3e72eec1d15a2565298647506e6bfacdf2217312c95a513d356971b034aaf35a7d3e872eae3961721c4c6bb6b723be9f34aa97b336b933a151bab878d45de8e8fcb93fa175adf9c728ecaf77e0f82ae9ad254cd38b9fb54b12b9dafe9f6caaf4690ed4d0e614e83594a7b523255af76d3d501ab8e6163dfd568cb2af1cf7a8a5ab65b39b74e31e97f8845d8284bb635a4fe3cd575f5497536f662cb39547b4532cb0ba8d9243aece3ff003451aaaf28c0b7033c94eae21eff005ff762a87a8c2fdaeeab7da54a5ed4947a6a5146f4684ab3de5ecafab04571cf3bae6c6cb8ad767150285cf24e830b5ce07c40544166c46875abbe1f65be4dfd5fec7bb53feeb3c0fb9743248f2d79751d919268256d78232cba8af2ea556a6169a38d4f0cbc538c35b8eef9b28c4adb0ae5c2dcfd311f24b2a1e617c39ff4bc87b91910b31759af120f5b31c05424e03ce557ade2cead01dbb382591d9839077c6acfd2f0fbd1918660b6368a3625989e3458330b1a2c2cc5263249a119f67de934c4afc87e80ef1e07dea3ed12d402f19cb3aad70aea72d14e319323293402db4bb7ab230b2b11cc573db1e299efd815918a22e5a9e4dceb59c99b19f9f1835ed61a1f201733171c95e32ea7a5ecc971701569f38bbfd7e8cf364cc25b669b09de0e446f0a338e6468c3d7e14efba7a35d5073e2f93737503aec3bc7e2be2b3a97b6a5e8cea4e8ff00dbce9ad52f6a2fc3f82330c70876d6ff00c1f614e3ec556ba91acb8f828cf9c7fd7eccce5a4e289001a3ab0f6bcf90fc79aa3bd57c8e9afcac137ce6fe0befe24df11c0c8c6a7aceec1b2bf8d89292cce6fc8b274a7c0a78782d5fb4fc3a5fef9145b65068d6e8dcabbfb54e9c5abc9eeccd8cad1965a70da3a5faf8832b4c27a9f3516173ad0e2013822a65bdc5a079072af05ad59499d3edb7c3c252a5e5f05fc9eaf1581eed94e350ba8e48f2d66582ec937b7c4fb92cc82cc366b317b28ea621b46ffbd453b0ecccf92c0e68a92df3f729a7722d5868ec2e768e69ef3ee437605aec5f1d8481d60d3c2b54ae3b0ba26fd108d43407b5d89afa528295d9bd0ef61685fd0b7e8846a3ba351446248064c45769f41dddeb4b98d6c65153103c9a952132050228b46a3bd4e245ee79ef3a1ff47eccbfcab9bda1de87df43d2760772bf92fa9e52a2651200d8b0fe4bf6bdab155fee7b8f4980ff00c3ff00f45362fc8bff005bfdaacabfdc8fdf33360bff000aafafc8cd5a4e20900196df423e07d8a9a5de91d2c6ff00628f93fa1a16af45ff00647b566877a3e675f17fdba9ff00c5186b79e584981edfcc9fa76afb317adea9c0ef2f43a7ff00517fedfafd0f562ba479820751de8112480aad5e83b82947714b605bbfd23c3daa73d884370f551619ced5584064084803ffd9')
	),(2,UNHEX('ffd8ffe000104a46494600010100000100010000ffdb008400090607131312151312131515151715151717161718161a1818181815161715171716181d2820181a251d151521312125292b2e2e2e171f3338332d37282d2e2b010a0a0a0e0d0e1a10101a2d251f252d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2b2d2d2d2d372b372d37ffc0001108012c00a803012200021101031101ffc4001b00000105010100000000000000000000000501020304060007ffc4004210000201030105050505050703050000000102030004112105123141510613226171328191a1b114425262c107233372821516245392d1f144e1f0436373a2b2ffc4001a010002030101000000000000000000000003040102050006ffc400251100030002020202020301010000000000000102031112210431134122510514322361ffda000c03010002110311003f00b7fb3f86313ca9b8beca91e11a7a56badc6eca4000562fb1b2eede01f8a323e06b68e3130abe16572aec2aa69f9a6053522c47a530034c6d64bb7e9a23791ad9081ba565bf68118ee93c4b904e9919a0f91a70d06c09ab410b07cc687aaafd2a7cd0cecf4dbd6f11fcb8f8511ac0668e87834ecd301a7554ed0b9a514874192401d4d744436aa41f439aed3236875762826dfed55bdaf84e64979469c7fa8f051591bbededf37b02080721ba5dbde4e94c62f13264f40ab2cc9e9c919e9597bc8c866047335e7979da5bc66df7bc981e5b98451fd2b4fb2ed45c6b993bdf39319f88a3d7f1d5a2b3e52d9b6349406c3b5018eecca13f303a7fdab40b82320820f02292c9e3dc7b431196686d2d2915d8a0051a6ba9f4950498fb5bc78e459a3ddde5ce01e1af5c510b8ed75db1cefc287f2a13f5aa32911cab850543e0a9e18cd6e7723382218d4f2d2b7b1c53eb623752bbd1916ed4dfb7fd4bff00442a3eb4cfb5dfc9ff00ab7ade995fa0add25f4838776be88b4e3b426ff308f40051be1afb60be59fa4611761dec9c62ba6fe795ff00de9d2f672e225df78371799dec9f99ada9b873c6573fd46a9ed41985fc44fa926a2bc7ebd9d39bbf42f631f36c07e1661f3a3e0565bb0cfe1957a3e7e228a6d5da9ba4223609e27a564fc6db1bab482c51b963dfc2a1b78ddb3bd2703a841fa9a1bb36ff0011e14348f93ed1d3dec6a6b792e58b02d145a83855def9d331825217acad89b5b67c5805f7db278963ff0014393675b8d555d5b3c55dc13eb83ad10da4936e6b3271fc19ff008a0d2c77435530b0ebe2068ae17e81aa33bda8b1ee67c8de60e33bc78fbcd009b3cc569fb64d3342ad22a82871bca4f0340b655e2b9eea5e07d93e7fa5378ad25a074b60c962dee7502daeba1a2f77b3dd09e639556788819dc6f5a6392069145e1ead9a2dd8dda8d1ce2267251b4009d01f2a0b2381c8d742ca19581d43034be78552c2636d33d748aea485b7954f503e94fc579cbe99ad0f68662ba9fbb5d42d97d194ed0405257079303f3add7d8f76347ce4151f4acb76e21c4edf99335abd9726fd8c47f20f957a69ead9977dca65b8366a328258eb532ecb8bf31a5d9e7f762ac8a64598c8f67c43eee6a3bdb28cc6e0281e1356d2ba45e23a835cfd1d2cf34d8d7062ef483ab607c39d3c9cb024ff00dea9ced890a8fc47eb52dc4eb1789fc3a716c7cb3c3eb59ae3b1aaad9a9d9f790c508ef6444d49f11d7e1c4d559fb5f688f95ef65cae0944207ff6c66b087b416bbc4b12c7a904d598fb4107b2b8c75dcd7e228896914d1a99fb756cc0a986500f33ba3f5a1f176bed32478d41d324647ca81c97b6cfc743d7fe6abb476dc5e518e98c9ae7a3b4cd5ed29609ede4eee557c6b8075f8560ae6c88c153c0d5e996cb3bd14a636e983834d8240c3033d41208cfa54a654b3f6a210968fbcc00774923e743ff00bcf6dc0db48be624cfc0115ab64578432819dc20fa8af3abfd9d2e492bf0a9f97eb65d46d6c3515f453122307d1b19a46d93be41c11a8d71593dc653cc1f2cd39ee653a177f7b1abf3da23868f62b3b95dd015836001a1cd5e8a7cd798f60d5fbd2467771af4cd7a029ac5f231a543b8ade82a0d7554825a4a57431c8eedec5e346eaa4512ec63ef5828fc3bcbf0351f6f62f046dd0e2a1fd9dbe61993f0c87e6335e91f590cbf78cd1eca3e0c7435782d0fd93c5879d12029942cc722d3c2eb4d5a781d2a4e47946dcfdc4f3c8c30158eee799eb8e82b017174d70e5a462dae82b43fb43dac6698c7a82aec08e475d2866c7b2035349e47c76c6b1cf2071d96d9c81a0ad86cab42e0054074e8288ec78a20351927ad5e136e36ea80079566e5ced9a38f024517ecc90e0bee807a0071524bd9b87a6f7b80fa51d89b786b4f48c01c4505e5a617e293ce7b41b2638802aa14f95345d86b7880cef2123dc6b43b7edc4c18210c57a56523b322366e418034e61c9b5d89e7c697a34bd9ddaf181ddc831ae84f039e545ee2d627e00560846479d1ab3db823401cebc075a1f930fa688f1e92da64db46c117ee8f856376bc7bd26ea2fc056a64daa921e3a9e5567636ca55265392c791e554c791c7b0972abd137676c445128c6a464fad16a6e6bb340badbd9c968950d25229a4a132e8d276d63cdae7a30340ff00670ffbd9d3a856fd2aa5ff006c2e27431bc312a9e61893f4a13b3b694d6f2192128188dd3bc0918f756e5e64eb684a713e3a67a66cf18918515dd35e547b537bbdbc24854ff2123eb492f6b36873bb55fe5897f5a2ff0066413f1e8f5848cf4a95626e95e3a3b497cdff005d27b9231fa546db62e8fb57b71ee283e82a3fb524af1d91fed52dfbbba3fe1d23cea1d4e77c1e64723406ced5e450cad8d3855ced0caf2459795e52a7da739383e7563b3919ee11c0270581c0ce99a065b4d6c3e39d3d152d7693c470ea4f98a310ed1320df4563bbc74a8af648e425562656c7b4c08147bb236a511b787b47f4a432e87b1b6679fb4129d113e27148b6d3c9acb3145e833f5ad1df6c18e5f239e2343f114b67b0e05237cb311c99988f81354dce826995fb3bb3955495d41e679d0aed1c2122900e728fa56e249005c018ac5f6913bc8ce3fcdfd2ad85fe60bc85f81938e720d3e7837f045326b66534d92e7756b4aa792d233a1e99aad8165b8bbc40c9e78a2c4d79ed96df9a3fbfbc3a1ad158f6a636d241ba7a8e141c9e0e5d6d175e4cfa668335d51c13a38ca3034f3485e3a9f68626957a1c0d75228aea1e8b81fec13ff92e3dd4e8b665c3e8b0b1af4a07cf34bf2f4a639943ced7b39787ff00431eac2b9bb2d7878c6a3fa857a14833ccfc69a615d091923d6a79906162ec75d9e1dd0f22d4f3d8abbe05a2cf4deadb88d739e7598edc6dd31810c470e7da61c40e80f2a2e19792b8a2977c16d998dabb29a20f1c8f196c7b2a7274eb527616f805688f10723d0f1f9d058f3bd9cf3d4d53590c326f83ec9d7cc53fe4788f1ce8062cfcab67a55c283f740f3ab7b3ce7872340b66df031349c74c8ab3b2a79224691d490c77b03881e958d52f66a4d2d066e14a93a79d598a459172319a136fb4e5b827ba0a88300bba9c9ea1574f8d12b8b18d70cafb8ff26f515472c2aa450da1315d09acdfb4930e6aeadee346afa6de238646871c3340a2204cca783ae3dfca8b8274f603c87b5a28b2ea7340b6da8e55a429e5a8aaf3765ae27f126e05c680b6a7dd5a5392675c999b38eab7c56cc5d2a362b596ff00b3abe7f6562f7caba7ad67768ecf786468e42bbca7070723e35a58bc8c75d4b17bc373ed0b6d78c872ac456b363f688361653a9e0dfef589c54a8d44cd82334e9a071750fa3d5e215d427b35b43bc8864f897435d5e633e1716d1ab17ca767a0479e74e04d341a703420829ae51d6babb352410df5d08a3690fdd04ffb0af29be7691da47392c73e9d056ebb7173885507de3afa0ac2470bcafddc6bbcfd3863cc9e42bd17f138a661e4a32fcbb6eb8a2a17aabb50f88f9806b670ec2b68155ee77646c6ab93bb9e8069bd598dba55e50517714f05c6300790e144f333cdbd23b04345cd8121ee8afa102b416bb74818789c8fcb83598d9b36e37951f00fb4958791766a627d04bfbc487458652790271504914d36b2bf7487ee21cb1fe673fa5514bcb8def0c391d71456c6da57d64f870a5eba1a44696ca8005e1e74276a0c3061d6b45731e08acfeda619c0abc74815f6c89237793201dd6c127a0e75a48061801c0554b387f76839ee9fad11eeb0693f329bd1a1e0624b63365131cee34d4e479835636c59ecb9b3f6a9618d8f43871f0d684ed3b3559127591d9ff0e7418f2ad05a6d38231bcb6c9be752d85c93eb8cd1bc4a98adec5bcd9aa5e8c26dbfd9f0ee8dc6ce9fed318382bba430f4c8f1561dc153bac0ab0d082307e15eff0069b7649404002b1917742f251a9cd41dbdecec17632155675190c00f179375addc5e4ebbd98978bf67917666f7bb94746d0d7548d6cc3eee0a1c118e95d53971ce4ae474372b47b18a70a8e16c8cd4958068a1694536a39ae4272c9e9565d90c11776925c4e402563418ce389e6147334ffb04c8491dddac79c173bad3b8ea5b82fa5104ed091e0911770fe11823ce877f60accc4c738233901c9247b8d69e3bd4e909d4f7d99cdaf696b14dbe1a49f3a8690e7079f9502da9286937c0e5c3a57a2dd7636364dd96e1539823031f13591da70da5b38549c5c3608f002de2e5c34a9d53f64a73f40fb0b762aeac31bc3794fa71a27b06e78a37114d8ece565df6937377c4b1e07c09aa9728558489c0ff00e1142b41b1b362d77dd818abb6f7ab22f2cd629f6b65403a115d69b51d7242b11d4501c8c261fda52015992a5df3caa5333cada82074a2d63b3f503142a7ae917945a45c2a7f29a99a9245f163a694ad597e556d9afe24ea362c962c1524d374934fb66b752ddfb6ea819073814e7d949dd09bbf93781d10b7846bc376b8ee8c1640e0710403a7be8b3f854b035ff49a45fd8db5ec59cb5b9deeed48ce0e327a13c6bb653bcd2973cb2c4fe95476aed3578904518501f1a6071c8c6956e2bd30c4b144019a4e4790e64f90ada96ab5af46154b9dec05da9d8f24dbb3dae5bbc72a5174c91a649e9a5751fba9b2638a37ddc69bcbd79d7532b201e259415253452d630e8a07be905d5ec6329608ebff00ccbbe47a15e3e59a82efbcc011839e248aa4db52e633ed37a30a6b06a7b680e5efa44b36d8b398f77711bda4c780906e827c9fd9341b6ad87d9e45ef419216e0cad8c8e63228d1dbb1cca63ba855d71c719fad0ebad9bb8b19b793bcb4790031b1c988b1c784f1c79539b9a5d00ed7b2cc7b2764637fbadfcebe32edff00e8d3e6bfb6dc31456eaabf7480060f223154f666c7691a588150d1b635e383c0d12fec38a204cd301819c65541f2cb5553c944ea1188da50cbbf9dd665e1bc01c0f5e9535a593c7a48331373e2549fd2b53b176bcb721a2b24b70a321c4cd96f5dc4e23cea497b2218ff008bb90037dc88776a3d3249357f8ff647c9fa32e7b3722be24f029f609e7446c57b96eea651afb2c381ad04b3c102886695a6838076d5a3f561c479d4779b225dccc056e613aa8c8de1e8697c9877e98ce3cfaff4519ac978a015241e0258f21438dfb2e55e19908e451beb8ab56314b39c04654fbcec080079678d2bf156fd0cfcd1af672a1e279eb4c6a27b4f1bd81c1540143cad667933abd1b1e35ffcb625bec69e4de2a32a78674c54c91b0186d08d0fba8858c7b466c2a98ed62031bf8df918750382d549367b412346f3198fb5bc700ebc46053d9b025855233f0676f2d4b196d1dba06696400af8c292070e839d2584ab1c6d70c3f79267741fba9caabdd2db6f299e25620f8588ce2a16be0eed2e0948b01547162780029cf169542d08f952d6465fd9b6dbaa669485500919ebcabaa11134c44b7842229ca400f3e5bdd4f970aea6924851ec360538525238246175359690db2530ed053983ece508f664df0dfea155a7dbb711e975b3d8af37859641ebbba35511f694275907c69f1edfb84e277fc987eb5a31914ad342b50dbdec481aceed8adbc8a1c8c843a1f3054ea0d657682cd6f1cb1ea192552075d4118ad2ed1b7b4bd5de23b8b85390ea774fc471a13da0bc921664ba0195d17bb9c6a18a918dee868ba97da29b6bd934a52678ee3be9210ca16528dba430ea795103b1b662e5e426e1f190d2bbca7dd938a137610cdbab8292a2e7f9b157f64767e724a3055c1d327ee9e150dd2f48ed27ec11b522b69477b668f04c9a1eebf7671cf3bbc69b0ed2591424f3089d71e2998807dfd6b4571b062b7904b24dbaada1e007cea1da32ec8625047f6994f28833b7c5741efa9e2ebfd1dc92f44d69b15a55051d194fde46de53efa9bfbbf0da03277ed1b7165490a2b7a8cd50d83b0ee42916c89631f13bd99666f3249dd5f4a81f64408e65b8135d30f093360a93f917400d4cc4c90e9d1793b6513691dc5d9fca2dfbdcff002c806b4e4dbb7529c416b349d1ee776241e7b83534916da30a6208c444f056fbbd069a542ddab9e4183b8bc9828d73ea6a979a653098f155521f2c929fe3152fcf77d9f75370719a52d9e34f8fbbe12388d4f16240c7bcd79bade4cbd1e9fac78859b6a3480277840fc20e2abcb67223ab90db874c9ebcaaf4575b381dcb60d7528ff2c1723d5fd95f8d2b5a6d4954ab086184f00732483a6a3415b7fd6758f54cc19f214e4da451bf8508cc8dbaa3527a50ab08c407bd130915c928800c7f331e744a463b8eaf8254107a1f3a0fb16c13f761f798393ba8b8c81e64f0141f125ced07f31a6d32f5a4135d3e46bd49e02ba8a4970e0fd9e2516f1fde75c34ade48a387f31e15d4e719fb621dbf413a7c314ec7fc3ee071ce404afc06b4ca0fb7ace7768845746242c032ae8c7cc371f75278f4ab6c3dadad2348cdb55753159c83a06910fcc1aa173b7597c37bb3e441cde2c4a9eb95f10f85360d8718c7efeef787defb43e73e9c3e557c47748331dc0987e09d4063e424403e629f59658abc7480f26c9867432d9cab20e6bcc791e60fad05da3391188651950d800f15c8a30d6ab2c8d2da136d78bac903681c73de5e0c0fe2143f6cc82ea0790811cd17f110f22398ea2aca57b446dfd8176788c94c3317ef37483c00e58a3adb2e7332193683c6afa6102ae00e0326b2bb2af0131924646f31c733ca9f776d2c8a1f759b0d9d7352de89d6cd6de766b67aab77b234ee35cbc8ce7e19c0ab5b3fb436f1c6160842e063450bf4a1f6bb025902c80050cb839ab567b0638c1efe55500f5007c4d53791fa476a57b286dced2c8c0299194138c467075fad4e01b8758c6f15551e323c00f3f17e2a65eedeb256dd831315e413bcc1f26e1526cf5bf9c111a2da447892a19ce7980745ab287f6c8e5fa2fdd6c6b78577ae25503a96c0f89a1ebb52c1ce2dfc527063badba71c0ef6314dfecab2b771f6a76b873c1a462f83e4a3c2bf0ab125fab8dd48c2053a1d351eea07955318da1af0e2af2a199cd4f6d6d6ee717215946bbac3393e95596a558b7fc3dcb49e9cbcf3587e3275911b7e6529c6d16a6b9b488ee4117727a8f0a9f70e342e64da0edfb9b90dff00b6e3c2474c8a3b6fb293bbcdcf840fc447d6a3375e131d82027f1be77079e799ade536fdb3ceba95e8cc0b3b88e42b3c6b1ef292406c83a7114eeca82c7bd6c7872a83cb3c4d4fb4b6698e589e4b932c8c18142461743ec81c0555ecccf84dde8cdf5a5a970a7a1b97ce56cd7c36aabe2e2c789aea5b6932b5d4374d9753ae868351b0c91e5ceb9240c0329041d41156ad22e753a288b16ebd6ad31c0a646b515dcb8157921f6c09da7c32ef03bb2a78a371ed291cb3d0f4ac7ed2bc79db25563764c31ce8feb8a2bda7da2151893c8d08d93dc5c468cb22a4a060a31c64f519a6637a01696c1d240d1e31198dd7ef2f894f9d118966910837a174e0aaa3e24d5eda3b166c02064f2653f2340adf6431621c6e9f338a26c1e8d36c2b296680abed270a9f753714fbd8eb55e6b3d9d0b665ccec786fb34873f4143767ec378e7507770fe1e3d785139bb2b731b0660ac80e7c27247af4ab2a655a41b7da86388158d1b8000855c0f774aa37fb49a4006f9d7ee83f2d2aaadac28c65bab9419e0a4e303a62ad5a768e0071656924edf8c2e17fd6f5152ebece9a488edf604b28395dd1c8b69534565dd7877b7bcea6b88af27c1ba956de3ff2e23e23e4ce7f4a8638c2e153240e193f526b37ce5333a357f8e6dd364aa71a9e552ecfdaf7b20dcb68e341c37a6627de1147eb54369ed6fb3207c2939c00751429fb5b34fa2b63c9063e942f0571fc8bff00217c9f1367059423c577377f37353a283d150701eb5627daf8522340a318ff00cc5636cf644b3ead84fccc75a7c8f140776399e7981d62072a473cf4ad2e56fd195c650fda11fefa16f08277b87a507d933eec8e87939fad107ba1712a4c0088ae54c5904af9e959dda12ee5ebf46c1a5ebb6d0dcf5299e8bb3e7d2ba87ec397780aea51bd30fa32ff00b3cdb4cae2de43956f673c8f4af5586bc6367c3bb244c38ab8fad7b15b3e829acdd50be37b92d938141b6b4f8144a77c0ac6f6a76a88d0b13cb4f5a8c7f93d1d5d2d987edb6d3de7eec1d071f5ab7d8eda08f6ef0cd04732a36472700f43cc5632ee72ec58f3345fb197e22b95de52cad952071d69fd697429ed9b7820b7ce12e2e2dfc83657e608a7dfecf3a6fceb7118d75187f732e2af35bd8b9c77e11b3ecb100fbc1a6cbd9f75cb412c720fc048f91154db2748cf1b4b3901c995186a3c6c7e1566d5a170ca6fee125e00331dd900e008c6b535d416ea33292927351afc3154e08ac663bad3bc2e3d9674214ff511a5726ce69042d2fecc784db209c732b90de619abae7b5336770058ba6050eef2c3063bc69b797d89a304af96a38d14b0bb22125ec1ee621fc3b85dd0d8e458370153f9323f1228d6f09569919e363e1973a0f75111900918d3a8cd3526bbdc05da21011e04460c7cb788e753c006ee091922b1bcceef46ef8492c5b1e9b7ec507f8951249c93773f01c055b8b66bdd78add61b343cceebb9fe9070b42cec18e7c165538e674f98a747d97b3886f181e5238aab381eec1d69ef1b24a948cdf271d3a6cedafd8ac025ef669db92a955507cc2d055bd518b7310b6978071c24fe63d6885aec289f32fd98db47a800cf2063e675a4bc906e7731d8c6cb9d1da76273d413afce997698b28681f696822b9653abeef888e0683f6c24c5c020721ad1989248e401a1ddc8fb859fe26887f7652e2412cc18018c2f5f5a4b9256d8ef1dc2452d81348e008c1c736e5ee34b5b186dd5000a3007015d4b5f6f6167a479cf6324134a8adff38af4d8d8a9e3a5787767af4c5346d9e0e33e99d6bda65934cfbeb433c762986ba25bab8383ad795f6fae1cca10fb206479d7a1ef6f9c721587fda1dbea8f8e4455b02299abe8c2b0a96dd8a90c0e08208f7534ad59b3b5773bb1a3487a22963f214d36051e9f0dcdbdc46ad7108746507bc55cb211c49035352c9b1367801bbb6dde52445c291e601d0d0eecd5b4f6f0e27b6940ce9c37b07f26735786d9b54248668c9f6a36560add7008d0fa508b3d0c75b6886f5b3307fcf961f3a8e6ed06f8dc9e28d7a488b907f994f0a2d6d26cf9c65265638fe03611c9e8acd8cd5d9766cea0775b3d654c70ef93787ae74350a68af246763ed3cd6e9b92c50cb6edc1c0ceee7d34a458a4dd2f6f78cb13722bbd164f238e02ae99b6842c4aecd5543ed248c841f81d0d43613dd2bbb5b2c3661bda8256de8d8f5518d2a6b6976c99edf4476f62c9edac6ac4e498cf84f9d4b7565de3028fba399e7eea91236607bc2bbc7392830bee14366cc6008e407271af2ac7e2aed9b74dc4246a763d8a46be0de63ccb9c9f872abcb36b8047ba80db6cdc6b2cf211f843045f96b8a2f6f2a0188f774e40e7e7454b8806f657bab58ddb1329719d012777e156d366c001c4483d054572c58825715344c4ae2a76ca71443dd2a021740790a6c52919c1ab58a1f7126e31ded06389c01f3a849b27a48916e86b9aea0b3ed7b7071dea13d17c47e0b9aea22c15fa29f2cfecf1f89f15ea7b13b402689117f8980b83e5cf35e52b5ea9d8ed970c96885a31bc49f10c83c7ad3de4fad89e17d9a8b38374753ccd43b5765c7711f772120678ae323d3353db43ba319c8f3a9f14be1a2f916c0b0764ac22462b0778c1490d2b16d47e5e1f2a396b70422ee05452a34450a3e54d2bcbdd506c96cc4a3a657e04d5f236d1112b649b450942ea4875d41cfd68245b70aff1a257c73c0ad2f7618153c08c566b685fdb80e934320dcd37d5490df0e3518a9b47644903e7bdfb5b1c428b1af124671e9e74346cd9647221b89774720ed81f03c2b4a97db37bb58f7ca702c08707dfa55c87fb3a5fdddbdd3da103c4cbfbbdf1eb20d7dd4cca605b464c6cd9236c4d78d1799949c7aa934522d949ed1da226e815975f51c68d45b3ad61044725b5e3713dfee337fac70f8500bfdaf69bfba2ce08a41ce365724fe50a3351917e2cb61afcd16eeef2341824372c6baf969425bba74cc5b3e44d756ef19b3e8a75a21b2acefdcef4366c41e0f2feed47fab53f0a32db1ae86249aeada161f755805fea66393ee14a60c1c67d0d791e472af645b1eeed8a01dc7880e0519dbe868c2ddae9fbb75f311103e38a0edb7bbbc779b4ecd31c4448f2b1f98a6bf6d6c07f12f2e66fca918553f2fd6adf0329fd8416bbbb5032cf9e9a6be800e34b69f6a7fe15b045ff0032e1b707ba31963efc566e5fda8dba1ff0d6249fc523007e593546e7f6af7adec25bc63f959cfccd123025ed94bcf4ff00c9e8b6fb1253acb72cdf9618c22ffa8e58fc6a76ecadab1de92dd643d6525fe4c715e3f73fb44da4ff00f53bbfc8883f4342aeb6e5d5c11dfdccb20fc25885f80c0a36a101ddb3dc67db1b3ed060cd6d0e3eec6177be0bad757853c601c22e49e4ab93f214b5df27fe1df1b33112e4e2bd9bb209bb6c8bd0579dd8d92060715e85d9b9bc38a1791da0987a0f0ae6f2a683583db3da1bc495e3efc2853a6140d3952f85761723e8f449971ad018efde12ebdd920b920e0f035849bb47798c7da6403cb747e94365da13bfb7348deac69b729a03c99e9b26df61c88ff48fd6a8bedc2338744cebe2209c8af3a249e64fbcd21849e55131c4e6f66d6fb6fabead720750a3e9a50d3b5ac836f48925c11c03018f99ace8b56e9522599ab95d1a297b69181886c2041e7fa818cd45fdfcbd0376130c03ff006a2453f1393413ec948600389aeec8e89af76d5d4dacb7333fabb63e034a1c62cea467d75fad5a69e31f78533fb41070c9aed33b68842f4a9444dc315bdb1da1b2de05797b956dd019483bd9c6ba0e341f68eded96ba4368f21ebbc517e1c6a7890e8ceada1f21520b40352d8ad76c8d8e9711098e230dc117271ea4d06ed76c910aaba924671ad7713b9032248b232def3c079d6821d9108198c3ce719de037221ef3ab7bab3904fb9bae143630774f03eb5ac8fb4d0ca235c98f270547007a7a5528b6c31b1a336f1ea7058f10387419aea9ef64c21f4d3f4a5a1ec2266061e35a6ecf5c60d65c020e0e946b634f875f5ab5ada220d92de0fc2df0aa77db2ece73bd2c277cfde04827e156fed4838b0a6bdfc439d0657165ebb4672ebb2b6e58ac526e37e06c9a8adfb1e4b053220ce75e1c3d68fcf22ab2cdba0f227c8f0a4fb50f680ce3ad30dad01d1417b04bceed47a0cd4ffdc3b65196ba95bf9420fd2ba5da6c782a8aa1737721e78f4a13ca5b88236b6cbdc6dd84923ab6a6a97f654a789c56eb67f67d4207763bcc33a9d0678694b73040bed1cfa1a9f9193c0c3a767e46fbd56a1ec629f6e463e43fdeb432de4406103b1e805451cd331f0c614757d7e42abf251dc50257b256ebd4f96a4d487b3718f65028ead814525b697efcf81d1405f9f1aafdcc63ee873d5b27ea6bb9b3b8a06b6c4b61ed3a93d06bf4a097369bb2108a31c8d6c95fa6e81e400a43301c97e009a959191c493b288cb00563c18d41db7877ad49e8c0d12d90e4ef0231cc549b6adb7addc6390a3c5740ea7b30bb0ad965886548c1c16ad0bec4882f840c52d85a776bbaa0807a9a9a581b180697abd84489231de615bd944249eb8e15d4bb32ce6549084660718c71e3ae94951b274652cf131f14a919eaf9c7caae5b46aae02c8b279a8207ceb3d66f86a3f0b70a2fd166bb0e62bb76ba23a0a796a03f6497cc7bd6e7c87d2a9c0dc475144f60f8c3a7fe6b41f1bae57a1228d3dc947d338d3264c83529a46c50297659068deab4084b0c6e853e4472a1f0490f42e7a2a9fa9abfd9999024c8c0600de19d7caa17da99d3418e0000335c49242739f0841e78cd5294bf26029925c10379f005541725bc4741c87335620b6d1e352735564cb6829e189d2a75402a0e208ad80f334e685789d48a90b526e7335c713ecd93f784751446e1731b8fca685d938ef056806cf668d9d480141e347c7e81d7b3291cb8c06386c70a2b6b6e48de6c81e628a6ccba508077681bf163535665ba56e84f4234a5e9761115238980c21f9d7548250070c57546d92787a49ad1cd9d364567a886cb90ef629a671b7b539414ecd45b2e3054d48d41a442616ecc4d8b80a783291ef1ad47da2b6dcb9f2600d53d9ee44d111c77d7e7a51dedaaf8e23cf5144c5da68a5fb003f1a616a7cfc6a226876bb2d25dd8e417743f7e3207a820d75c2a26b8d6aa59c85658c8e3bc3e7a1a4bc05aed93799578e0635f88aaa258e8a2df3bce33d01e02a765ab023038576ed7338ad0a64d4ac00d780a98a01c2a395060695524809cf3a576046335234631c0536dd01600d49c36c6262c1c0d148d4d6c51b10ce3f2e7e343e6402220797d4559bd90885b1cc0068f8ba0760bb35c8d388e5564c66ab6ee99e0401ad4e17794649a1365d167bbc8aeae8d02e82ba87b2fa3ffd9')
	),(1,UNHEX('89504e470d0a1a0a0000000d49484452000000e1000000e10803000000096d224800000033504c5445e4e6e7aeb4b7e7e9eaabb1b4e9ebece0e2e3b0b6b9c9cdcfe3e5e6abb1b5b4b9bcb8bdc0d0d3d5c6caccd4d7d8dddfe1bfc4c6a60afc030000052e49444154789ced9dd9b2db200c406d8137b031ffffb5856cf7dec46e0c88201c9d69a7af3923211683da340cc3300cc3300cc3300cc3300cc3300cc3300cc3300cc3300cc3300cc39c1090725ccdec31661da584d2bf081390a359f42484fbe3f1ffa8c57467b194dda09c54fb841355c30ad54b02182da667bb1f4b3537553b4233b42fc17b965cc67a1d61106ffc2e8ed35269ae4ab39f9ecf719c65e95f1b0e34fa40fc1e8eaaab2d8c2e80c7fd2e8e435d61041b28d8b693ae2a8a2119fa8862df95fed98719c3f5ae8e6b2561ec2202589562bc60258addc149b05ec53e45d029522f37a0d204dbb62fadf07f64f83cf812444d79ea87d095cc16d34078288e0882beda94f6d845260fc22b3dd520c28c124217c485aa229220d92923623fb10bcd7a9ab25a7b66a2586ca4c5136c5b4530889821243963608e420fc191882b48b09c62cd850f436a7322d672e69722b1345d93f6bd9b86a6b4d35f06e424755852698a9fa4d4d21467dbf464486a4ac4d8f9be1852da0903ea8aed0ea563fe1cc3d041c810322429ad65cd9ac570223423622fd9ae102a3530a0af682ed099f3f394524a3b28d0790c159d186632a4736e9afe396687d2620f20f18bda1ea2b4d8033664c30a0ccf5f69ce3f5b9c7fc63fffaa6dc8634867e59de59886d4ee29d30e98d299709e538c89d029c6179c449dfe3431cb410da542d3346386831a5aa7fa32c3da5b500aa17f1d836e4868bef7e0cf8894ce833df8694aebf321e2adbd8720b59b0ae8df48695552cf17dc1842bef545acce78ce7f730f35881443f80d3768cf7f0bfa1b6eb2a36d84a90a62151b7a93fd0f28794a37473d082fbbc8d6d11b081f694a2bbc23f695f31dca83f0465ab5a9e1956cd2765f980a041b887feb5c8760826215297a434564ead4d6d4df24629f2174e91f1d860c5ddd907edfbc098c2a60348abea221f8c085f1681c6b6bbf730760796dd3b6e567ebed6806cdf22e8e42d89a4ae82bd0cc6a5f524cfd506ffcee00ac8b9a362c85e897137415bc00b2338b12bf982665e7ee247a374042b79a7970cc66ede02c7d2fbf0800907f8093a4a8f3824bebd9c55aad54dff7adfbdb2baded72c9d6c6bb96fe9571f818ad66b1aabdd6968d52ea9bd2b6bdb6b313ad4cd3cbcdd6379e3db46cf3fe7a315d25890bb2318b76d3c111b7bf9abd9b40a8975890eba00fafb73734a7d69a86ec2a1cc0d8ad01171c4c3d8f0425dddacca6db3d24153549d92d3dee4505174943a6f05c1a5ae7b89bd80f24ba4403ccc8e1fbe528ec5a3a59dd363e47f87e49eaa28e07b6f0088eca94723c7a0c83e058268e30bf6b288fe8a83f7f96036b9fe785fa9ee3f2d9f31c1891efe91d506c3ff95d4ace473be66332e94f8531ac633e26e2335535b8633ea6e2271e99802d90a03f8a6dee2f38d0c57cfb4475ccfb1107a51372aa62ce7718c19f3db320f275fc960b05c1d65f3fcd134659b4c6fc61ca526f409311cc73f1064a4df3dbe02b1213c45794d404b12f50615c8c4507f3427f8ef79318e0091258c96c82d61904f7cd1622c2e2ac517375104240cc1851245965ee60541bb283f04a8f90a7a405111a2fc84c0d92d0486e80423b473d89af4d09d7d13b690b549809ed987649322cfde38f90526ca8ae479f397908538288deeb221bd186f40be995e8462f79bab0e520f2d969ae6e8819885d805713c2d85a437fc1f643d416a3a2248d4c53595108dd663fc2b09e4aea89f9e456cd747f257c2056350ca336c239fa046624a229519ea6abf9089f11c91e03ef105e6a6a9aef3dc127fcf5ec9c6e04f76ff7777f6b62a2f3bf0c300cc3300cc3300cc3300cc3305fca3f4f55526c410222370000000049454e44ae426082')
	),(5,UNHEX('89504e470d0a1a0a0000000d49484452000000e1000000e10803000000096d224800000084504c5445ffffff000000fcfcfcf8f8f8535353f5f5f5c5c5c5040404f3f3f3e3e3e3e8e8e8a7a7a7efefef1a1a1ad2d2d2dfdfdf414141b6b6b6616161aeaeaed8d8d8474747c7c7c7272727868686939393aaaaaa595959bdbdbd6868687979799f9f9f7373733a3a3a9090903333334b4b4b8181811616162121216565652e2e2e10101036363634291f1700000bcb49444154789ced9d07bbaa38108649024a13a588202058b0ddffffff7626286287a362d9bc7b9fb3a2947ccca44d42902481402010080402814020100804028140201008040281402010080402814020100804821f80c27ff8afceaeb02f3dec5aefa0f7432b7fcf7fbba5a2aaf693a1dea22bdb37d24a99a2eb9ae5c7b6110679963949924c8234ee2bed25f22154826c421fe8c4b6edba699a86b36092656b475e4ce72372859e63e885ebbe5bc36d6c4c6cf79a8a7b2456e1ac9fecb1e9b5c4d7508dbb247a5154b1770bb94ae7afe62bb1c182aaab7cacb39abdbffbe88e99c458b8d13e56a24bba0f49848313caa49060967cb7984b302978d08470831c286952d2f94c898c3237ba6bc4d1c0c9c3b1edfb502fba6132df29db29ec928c5b31fe4c899826330e27933c0826eb042ac1485ec8f2228a9c750655bb1b5b7d53394e39d5ed841c8a5b9018c0790294f81e11f7a8912c4a8b7aef50c39beeb0e2a7c4056fc8b9153f54e4356ea6d74af6be0a7f2c90e880d02f13780b14ef25a5157b3a548b32193f2671e72bc7dbef730bbcb41715f9b128509508243ea21173423f1ecf823c0fd2b16d696f6fdf438afc29ea032b1a205949feeca83c83ab6e74528c6f07c9ccf5dfa8143dc8d816f9b14f296309f11b4b84933074086d72a3c25aac0323f634959607552ef34a3fc60be913eeaa4315365846bca6f5221dcfb08c0ec9e5067fb7daeaeaae865037bb1d4f3f35eb0bb32b54f7d61c13176256844ac36b724f2935873263527f7aafdd71ca761e653323b63ccf379261a8be52226fb511f453dcf4e546d7b2c8041a8f76537d674cd517fa2a77d535217356748759836b8d490a024ffaa9ddcadfabecabe2e2ff5d28e35e0a68b29744970ab93515c26e013687a4d9c316049df9ab9b1b6046af6956a06bec9280c0edb1bd96f2641686e16c12adea2b345ea3ab92da86cd0ff4ec21d42d5517459dbdccd62aa751fa71b89e97bf5ff3dc2e99abcfd7f42850ba60e569542d98f9bc16282516f78c9a961d38ff6ed970de7f978c2b30498bc84a839ac6e7cd055ee7fdb36f47b4a8e941ff3477e4cdf654e0d06c29e175a1140c1829e0d65e9948c76ad238514c0c5463a43a854eacfe799d1a8b60b7993175b3cb5a59bf56dcb5eca99e7efda274fe196a66364f9653d82fd7de9da2674359618b905b30d3be2f38500b4a7d14e878977fad175e697acd7b873c7724a60ff65b3c1468fdd3a18a6eb961162d103972926c324b0dd78eadbe5ed4a9cf9368938d2f5d6b2718f27d92c6ad6d6be64c79ce5f2ed67910e493241af42ab5ce460ed2c64db3ab405571e35457c7f5aa580dd3a2c331db288cfbc7152fa5aadeb73ae389cc0b76fd690a5576e36ee99d7bf81dabe9dd66637bdff6290f3dce785a274c5fd90f6b0ead9b19f7c5f7e138e95a0dfc510225d3a839ec45b9c8726bdf6c38293bdb11875781e60e531405fed2cb41d3fdf6986004b3c64969d8f37707154ae112a6ae9b2ab61d99a29aa6d2a4e7fe0070796b32581e4a93ed76d90336f3e97430041651d0514aff82e65f9df01e653221e97e4392543b8be4c1a8d71b4d87f260ba19ad96dbde683e8c922c87bac3375fd91054b29db4e559d17920ebec130065eea08677a5d0b8e8ef53ed05774beaf5ab7a630ad5a1bb3bb37470d0c1c945bb24d23ccf83969e8c9b139f27d8a8556930e86fc93c2e083977c04fd683fade199e491b86b33cc3afdd17cd4e00af9b63339c4aeba30e7d77b02a221594ae486c8e17f0dd3fdc4f41b1774f1bc3c11dde50e46dfd648cbe0ddbd373eb75707f7582e3f7cf87424a885c64b2ea248a2e71d422648c1d41978cc0665a3a88f821e0d4db3b517fbc5dfc202ac1391c5b91666851494a2e39a8c9f338dc83ece99911231a7c40193fca470a3d1caeeee17d85cb4fa1f8646555dd819fad3b67c699516812ca7c17a3017ae1d9d6a9b8d538cef9782f9cbf53dcece74a0c080925c615ead578298e32a3a781074bdcbc4b46770d5a4acdbd67ddc0da65565a4474a59cacf11e4d4e235b18f95b10f4080cc32fc9487fa63cca924af68e4feeee6012f1e4f04b6647a1432817ef147c3c56528ed553aa7177a77474aaf09f6dcd8a1c8a40a1d7f58a3bfe145419cfbdaf75c7e7f98347ab500b98ad57c979a0f04e2411edbc2d1d0e4de8a225cd4bb9b08cbc1603a2cf9a6382636b73b2ed57db2a67a151fe45612d17e7621d140eee9e1eac7148a84e86bc2bac5fba89f02f3d1c09c59821ddea20d41708396550c9d7d4bf329569672d797330c9f26eb81badd63d6c86a4082b5cb621a99c8e62b83a6f3410732d053696cdc1d42fbf512f8fcc0c773f9ba48c7de858eedc094d6038e1105185e28c374ca5cd6585d6e1384b8702a17947fb3c051e2fccc1eb27e63e67271714f2b1f4e2d25ed97bf6c8e540cf31c1a1e163c9fb2ff38bd7d8aafbae959a41f6b570f0f761857a84599fcd2a2ed2bf74777b4ad9af3b984da97187199d953d775a1e70f11a58e7163fbb981cc8aea3bbb5510d89fb4b8219476e514e5e9afb7aa8d9b1a4db1f56272827ed3acbc7fbe6174cb8548abd700e86cc83e9ccbf78ce3f80678e719c2931fcbea63b673e340d2659e2c80bdedde9fda1e10855a1ebda76a763797d4dd34d737a7e17b9cfeb63f865141f2a98274aa4f1e2a2ef5c20687e81d396e8d9100f91c32077b008da1a6570f5e97d45dd9dc89bde123abeabd56820f3598479300bc314ee7fdcf12d4f030330a979f786522fc893b513c9437082e5b9be122766af0a69d41d67a57fa988e949138c9aa6ae6b7dcbf27d3f8ec7a9912246c7c3863dfddcd9eb02814020100804028140201008040281402078199f355df115bcf589eb56a092d7d2ccc53781cfd7dd9b0ef1e5e094a31fb62195941e79f533aa6f858fab663f5d9e8e09593d61dad0a7c218ce9dba37fbf19ba1d2f035b3693f879490c1efbaa88473ae70bee02f2b9cf2795a3fab904a21218bdfd5271553dfb4dfcd858c97a3c6073e48fd2c1885ba7ef8bbfa8a2706c8adc740bf9fac32dbf427b1b03dfaee44bc105eccc4bf6c417caa65f8633e7aa26684c5cc0f293c8ba6d984246f4acb8b304fa269f3bbcf537d131417541b5414521aff96098b87a0ccea1703727870f807a0f4b423ef1312fd54411a4047fe281f263f169bc10780345679a8d1c4e7557f06fe8035898fbe49c9eb97b86b111b57eeac3e9f42b1aa78da222eef05abf9b078c2a85a577884381ffc3e8406146b1b92dd33970766d8e6fe0d1b2a68405cc3fa480efd77f7e9e92f0035a9292e12353debc66b84acdf92a827d32f5e9b909e0f601b5f3d98b6d3a31bc5da29b97a21dcebec9636f85a542b2ce475838b4268976cda6cb13d654983f2936985fb65d1659b5d0e85425df1f2357bab30c5b61f3ac13e9fa99631291fc1978deb7ee8b69d0df3e3265573a8eed981735893789ac7d804bd5ae1652df77d717199dacbf51fbf1e0ea4c5e944aeac0ab58cc2ce9d42844a03d26db5b6f79b0f329b7dcb4e736770b49856cf09638db7c4ee249fe270539b60bb384d4fd73a3c8332ddb36c2398c87372c2663db3bd5d1ba5c67ae3fd3a2b4f3d9378bfccc948ce6686ddf1adbe86f4f913d8ae91ceb2249a5e5ac56385ef8eb0b4a62d689f5417706901abe93ba956f86e23dbd7ccddba814d9bd0e9fd65999e0b2e23935a4620df5c466e3370d0c2bea7d75909e42679eb61c401068538a6e7dbae11063b52c3756d5c62e148d4c3c5a07314756b836245c09bbb1c453a1fbdde94acdaed1af250668b851beded97326a8be2dd02edadf86d6204a36de436cb6f0ddbdd2d43cd4dadc5a09e83d5767528f12aadc5b8578c6fe6fc698cb62bfcd609498b59e22d4cda2cb8df4242c8dbdf68f75a22427e24dc7d0d7ff0536faabccc8fdb502010080402814020f89ff3a30dfe832c7a73c88532e56be6a1d1dd12eabc9306b28a0dfc78cb8c4a6591f64f872a002499a90c3f33868b5483fde0c37533e132d65f135dc1c4f2894a1806e60b70837d50de2d37859fe8f728e489c5d7ae51be015b6843aade7acd84223df18530af863b241a04ed82f30b8af9d794d1c3fb9ee97e00bb3ce84e41f44960d6c3f432cc8c683e483e9a13f2204ae59a77a22b53cf952f2a4af90b014bfbec3fd3fd2b2a8e6d7838ec8bc2635fe36c7fe66b9c4d201008040281e0f7f80f086c861f170e83430000000049454e44ae426082'))
    """

def obtenerBlobsDeCarpeta():
    import os
    import pyperclip
    def corregir(s):
        s=s.replace("\\","/")
        return s.split(":",1)[1]

    ej_dir=None
    #ej_dir="/Users/Computo 2/Documents/ejemplos_html

    if(ej_dir is None):
        ej_dir=input("Direccion:")
        ej_dir=(corregir(ej_dir))
        print(ej_dir)
        
    os.chdir(ej_dir)
    for archivo in os.listdir():
        with open(archivo,"rb") as contenido:
            pyperclip.copy(contenido.read().hex())
            # print(contenido.read().hex())
            # print("")
#/////////////////////////////////////////////////////////////////////////
#                               F I N  I N S E R T S
#///////////////////////////////////////////////////////////////////////////