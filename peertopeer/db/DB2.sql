create schema irrepetible;

use irrepetible;

create table persona(
    id int primary key auto_increment,
    nombre varchar(20)
);
insert into persona(nombre) values('paco'),('coco'),('melon'),('batman')


--prueba de commit