drop schema if exists educamesta;
create schema if not exists EducamEsta;

use EducamEsta;


-- ====================================================================================================== funciones 
drop function if exists obtener_ID_Perfil;

DELIMITER //
create function obtener_ID_Perfil(numControl varchar(20))
returns int
deterministic
begin
    return (select id_Perfil from educamesta.perfil p where p.numeroControl=numControl);
end //

DELIMITER ;
/*=========================================================================================================tablas*/
create table nivelAcademico(
	idNivel int primary key auto_increment not null,
    nivel varchar(15) not null
);


insert into nivelAcademico(nivel) values('BACHILLERATO'),('UNIVERSIDAD');

create table departamento(
	idDepartamento int primary key auto_increment not null,
    nombre varchar(50) not null
);

insert into departamento(nombre) values
('depa 1'),('depa2');

create table perfil(
    numeroControl varchar(20) primary key not null,
    correoInstitucional varchar(150) unique not null,
    id_perfil int unique auto_increment not null,
    telefono varchar(10) unique not null
    
    #,nickName varchar(10) unique not null
);

insert into perfil(correoInstitucional,telefono,numeroControl) values
('22301061550038@cetis155.edu.mx','4491261629','22301061550038')
,('22301061550037@cetis155.edu.mx','4491121629','22301061550037')
,('22301061550036@cetis155.edu.mx','4491261822','22301061550036')
,('22301061550035@cetis155.edu.mx','4491236713','22301061550035')
;

create table alumno(
	idPerfil int primary key not null,
    nickName varchar(30) unique not null,
    grado int not null,
    grupo varchar(1) not null,

    foreign key (idPerfil) references perfil(id_perfil)
);

insert into alumno values
((select obtener_ID_Perfil('22301061550035')),'paquitoelpro87',3,'A'),
((select obtener_ID_Perfil('22301061550038')),'xxTentationXx',1,'B');

-- select * from tutor;
create table tutor(
	idPerfil int unique not null,
    nombres varchar(30) not null,
    apellidos varchar(30) not null,
    numTarjetaBienestar varchar(16) unique not null,
    
    nombreEscuela varchar(100) not null,
    idGradoAvance int not null,


    foreign key (idPerfil) references perfil(id_perfil),
    foreign key(idGradoAvance) references nivelAcademico(idNivel)
    #escuela?
);

insert into tutor values
((select obtener_ID_Perfil('22301061550036')),'Nombre1 Nombre2','Apellido1 Apellido2','1231123133987888','JOSEFA ORTIZ DE DOMINGUEZ',1);

create table administrador(
	idPerfil int primary key  not null,
    departamento int not null,
    nombres varchar(30) not null,
    apellidos varchar(30) not null,
    
    claveAcceso varchar(10) not null,
    #para acceder hay que ingresar numero de control, validando con la clave de acceso
    
    foreign key (idPerfil) references perfil(id_perfil),
    foreign key (departamento) references departamento(idDepartamento)
);

insert into administrador values ((select obtener_ID_Perfil('22301061550037')),1,'Nombre1 Nombre2','Apellido1 Apellido2','Acceso123');

create table asignatura (
	idAsignatura int primary key auto_increment not null,
    nombre varchar(20) not null,
    descripcion varchar(200) not null,
    tutoriasActivas int not null
);
insert into asignatura(tutoriasActivas,nombre,descripcion) values
(0,'artimetica','Asignatura de las matematicas basada en las operaciones basicas como suma, resta, multiplicacion y division'),
(0,'geometria','Asignatura de las matematicas centrada en el estudio de las figuras geometricas'),
(0,'Calculo Diferencial','Ni idea');

create table tutorias(
	idTutoria int primary key auto_increment not null,
    nombreTutoria varchar(50) not null,
	enlaceVideollamada varchar(30) not null,
    horario varchar(150) not null,
    idTutor int not null,
    idAsignatura int not null,

    foreign key (idTutor) references perfil(id_perfil),
    foreign key (idAsignatura) references asignatura(idAsignatura)
);

/*
select * from tutor where idPerfil =(select obtener_ID_Perfil('22301061550036'));
select * from asignatura;
*/
insert into tutorias(nombreTutoria,enlaceVideollamada,horario,idTutor,idAsignatura) values
('Geometrica con tu compa el Temach','https://zoom.edoaspk.com','jueves y sabado de 7-8 pm',(select obtener_ID_Perfil('22301061550036')),2);

-- select * from tutorias;

create table tutoria_has_alumno(
	idRegistro int primary key auto_increment not null,
    idTutoria int not null,
    idAlumno int not null,
    fechaInicio date not null,
    fechaFin date not null,

    foreign key(idTutoria) references tutorias(idTutoria),
    foreign key(idAlumno) references perfil(id_perfil)
);

create table tutoria_has_mensajes(
	idMensaje int primary key auto_increment not null,
    idTutoria int not null,
    idPerfil int not null,
    fechaEnvio date not null,
    horaEnvio time not null,
    mensaje varchar(150) not null,
    
    important boolean  not null,
    
    foreign key(idTutoria) references tutorias(idTutoria),
    foreign key(idPerfil) references perfil(id_perfil)
);

-- select * from tutorias;

-- select * from alumno a join perfil p on a.idPerfil=p.id_perfil;

insert into tutoria_has_alumno(idTutoria,idAlumno,fechaInicio,fechaFin) values(1,4,'2024-03-12','2024-04-12');

-- select * from tutoria_has_alumno where idTutoria=1;


insert into tutoria_has_mensajes(idTutoria,idPerfil,fechaEnvio,horaEnvio,mensaje,important) values
(1,1,'2024-03-12','15:00:00','hola que hacen',false),
(1,1,'2024-03-12','15:02:00','hay alguien??',false);

-- select * from tutoria_has_mensajes where idTutoria=1;

create table documentos(
	#idea : guardar los documentos en drive y acceder por la url
	idDocumento int primary key auto_increment not null,
    url varchar(100) not null
);

create table tutorias_has_documentos(
	idRegistro int primary key auto_increment not null,
    idTutoria int not null,
    idDocumento int not null,

    foreign key(idTutoria) references tutorias(idTutoria),
    foreign key(idDocumento) references documentos(idDocumento)
);

create table catalogoQuejas(
	idQueja int primary key auto_increment not null,
    descripcion varchar(30) not null
);
insert into catalogoQuejas(descripcion) values
('spam'),
('contenido violento'),
('contenido ofensivo'),
('otro');

create table buzon_quejas(
	idReporte int primary key auto_increment not null,
    idPerfilReportando int not null,

    -- aqui va el ID de la tutoria, mensaje o usuario reportado
    idElementoReportado int not null,
    
    -- idPerfilReportado int,
    -- idTutoriaReportada int,
    -- idMensajeReportado int,
    
    fechaEnvio datetime not null,
    
    foreign key(idPerfilReportando) references perfil(id_perfil)
    
    -- foreign key(idPerfilReportado) references perfil(id_perfil),
    -- foreign key(idTutoriaReportada) references tutorias(idTutoria),
    -- foreign key (idMensajeReportado) references tutoria_has_mensajes(idMensaje)
);

create table buzon_has_quejas(
	idRegistroMotivo int primary key auto_increment not null,
	idReporte int not null,
    idMotivo int not null,

    foreign key(idReporte) references buzon_quejas(idReporte), 
    foreign key (idMotivo) references catalogoQuejas(idQueja) 
);

create table queja_has_razon(
	idOtroMotivo int primary key auto_increment not null,
    descripcion varchar(150) not null,
    idQueja int not null,
    
    foreign key (idQueja) references buzon_quejas(idReporte)
);