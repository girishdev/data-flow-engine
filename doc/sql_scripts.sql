CREATE DATABASE IF NOT EXISTS dataflowengine
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

CREATE USER 'dfe_user'@'localhost' IDENTIFIED BY '123456';
GRANT ALL PRIVILEGES ON dataflowengine.* TO 'dfe_user'@'localhost';
FLUSH PRIVILEGES;

USE dataflowengine;
SHOW TABLES;

INSERT INTO users (username, email) VALUES ('TestUser', 'testuser@example.com');
SELECT * FROM users;
SELECT * FROM data_automation;
