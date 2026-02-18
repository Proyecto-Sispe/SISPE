create database leo_db2;
	use leo_db2;

create table usuario
(
id_us bigint not null,
username varchar(20) not null,
password varchar(20) not null,
nom_us varchar(45) not null,
ape_us varchar(45) not null,
dir_us varchar(45) not null,
tel_us bigint null,
estado_us tinyint not null,
pregunta_seg int not null,
resp_preg varchar(50) not null,
primary key (id_us, pregunta_seg)
);

create table preguntas
(
id_preg int auto_increment not null,
desc_pregseguridad varchar(50) not null,
primary key (id_preg)
);

alter table usuario add
foreign key (pregunta_seg)
references preguntas (id_preg);