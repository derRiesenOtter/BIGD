CREATE USER 'debezium'@'%' IDENTIFIED WITH mysql_native_password BY 'dbz';
CREATE USER 'replicator'@'%' IDENTIFIED BY 'replpass';

GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT  ON *.* TO 'debezium';
GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'replicator';

create database Lebensmittelwarnungen;

GRANT ALL PRIVILEGES ON demo.* TO 'debezium'@'%';

use Lebensmittelwarnungen;

create table Warnungen (
	id MEDIUMINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	product_type VARCHAR(50),
	product_name VARCHAR(100),
  manufacturer VARCHAR(200),
  category VARCHAR(200),
  bundeslaender VARCHAR(200),
  description VARCHAR(1000),
  consequence VARCHAR(1000),
  reseller VARCHAR(200),
  article VARCHAR(200),
	CREATE_TS TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
);
