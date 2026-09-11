CREATE DATABASE IF NOT EXISTS bd_laboratorio CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bd_laboratorio;

CREATE TABLE IF NOT EXISTS examenes (id INT AUTO_INCREMENT PRIMARY KEY, codigo VARCHAR(40) NOT NULL UNIQUE, nombre VARCHAR(160) NOT NULL, unidad VARCHAR(40), activo BOOLEAN NOT NULL DEFAULT TRUE);
CREATE TABLE IF NOT EXISTS resultados (id INT AUTO_INCREMENT PRIMARY KEY, paciente_id VARCHAR(30) NOT NULL, examen_id INT NOT NULL, valor VARCHAR(120) NOT NULL, unidad VARCHAR(40), rango_referencia VARCHAR(120), observaciones TEXT, fecha_muestra DATE NOT NULL, estado ENUM('muestra_recibida','en_proceso','validado','rechazado') NOT NULL DEFAULT 'muestra_recibida', creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (examen_id) REFERENCES examenes(id));
CREATE TABLE IF NOT EXISTS muestras (id INT AUTO_INCREMENT PRIMARY KEY, codigo VARCHAR(50) NOT NULL UNIQUE, paciente_id VARCHAR(30) NOT NULL, tipo VARCHAR(80) NOT NULL, estado ENUM('recibida','procesando','cerrada','rechazada') NOT NULL DEFAULT 'recibida', recibida_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);
