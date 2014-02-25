CREATE DATABASE IF NOT EXISTS rmt;
USE rmt;
CREATE TABLE IF NOT EXISTS hosts (
	id serial,
	address varchar(64),
	port int,
	stack varchar(8),
	last_contacted timestamp,
	primary key (id)
);
CREATE TABLE IF NOT EXISTS history (
	id serial,
	host_id bigint(20) unsigned not null,
	cpu float,
	ram float,
	temperature float,
	effective timestamp,
	expiry timestamp,
	primary key (id),
	foreign key (host_id) references hosts(id) on update no action on delete cascade
) ENGINE = InnoDB;
CREATE USER 'rmt-user'@'localhost';
GRANT INSERT,DELETE,UPDATE,SELECT ON rmt.hosts TO 'rmt-user'@'localhost';
GRANT INSERT, SELECT ON rmt.history TO 'rmt-user'@'localhost';
