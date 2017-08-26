create table artists (id int primary key, artist varchar(40), albumcount int);
insert into artists values(0, '<all>', 0);
insert into artists values(1, 'Ane Brun', 2);
insert into artists values(2, 'Thomas Dybdahl', 3);
insert into artists values(3, 'Kaizers Orchestra', 3);

create table albums (albumid int primary key, title varchar(50), artistid int, year int);
insert into albums values(1, 'Spending Time With Morgan', 1, 2003);
insert into albums values(2, 'A Temporary Dive', 1, 2005);
insert into albums values(3, '...The Great October Sound', 2, 2002);
insert into albums values(4, 'Stray Dogs', 2, 2003);
insert into albums values(5, 'One day you`ll dance for me, New York City', 2, 2004);
insert into albums values(6, 'Ompa Til Du D\xc3\xb8r', 3, 2001);
insert into albums values(7, 'Evig Pint', 3, 2002);
insert into albums values(8, 'Maestro', 3, 2005);
