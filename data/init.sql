/*Store messages to keep ChatGPT assistant types*/
CREATE DATABASE IF NOT EXISTS `chatgpt`;

CREATE USER IF NOT EXISTS 'dev'@'%' IDENTIFIED BY 'dev';
GRANT ALL PRIVILEGES ON chatgpt.* TO 'dev'@'%';
