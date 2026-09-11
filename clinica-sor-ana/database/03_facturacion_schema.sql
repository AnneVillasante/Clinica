CREATE DATABASE IF NOT EXISTS bd_facturacion CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bd_facturacion;

CREATE TABLE IF NOT EXISTS comprobantes (id INT AUTO_INCREMENT PRIMARY KEY, paciente_id VARCHAR(30) NOT NULL, numero VARCHAR(40) NOT NULL UNIQUE, concepto VARCHAR(160) NOT NULL, subtotal DECIMAL(12,2) NOT NULL, impuesto DECIMAL(12,2) NOT NULL DEFAULT 0, total DECIMAL(12,2) NOT NULL, estado ENUM('pendiente','pagado','anulado') NOT NULL DEFAULT 'pendiente', emitido_en DATE NOT NULL, creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS pagos (id INT AUTO_INCREMENT PRIMARY KEY, comprobante_id INT NOT NULL, referencia VARCHAR(80) NOT NULL UNIQUE, medio ENUM('tarjeta','transferencia','efectivo') NOT NULL, monto DECIMAL(12,2) NOT NULL, estado ENUM('iniciado','aprobado','rechazado','reembolsado') NOT NULL DEFAULT 'iniciado', pagado_en TIMESTAMP NULL, FOREIGN KEY (comprobante_id) REFERENCES comprobantes(id));
CREATE TABLE IF NOT EXISTS conceptos_medicos (id INT AUTO_INCREMENT PRIMARY KEY, codigo VARCHAR(40) NOT NULL UNIQUE, descripcion VARCHAR(160) NOT NULL, precio DECIMAL(12,2) NOT NULL, activo BOOLEAN NOT NULL DEFAULT TRUE);
