CREATE DATABASE IF NOT EXISTS rmt;
USE rmt;
CREATE TABLE IF NOT EXISTS hosts (
	id serial primary key,
	address varchar(64),
	port int,
	stack varchar(8),
	last_contacted timestamp
);
CREATE USER 'rmt-user'@'localhost';
GRANT INSERT,DELETE,UPDATE,SELECT ON rmt.hosts TO 'rmt-user'@'localhost';
