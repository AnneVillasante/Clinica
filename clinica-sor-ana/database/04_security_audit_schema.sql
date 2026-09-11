CREATE DATABASE IF NOT EXISTS bd_citas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bd_citas;
CREATE TABLE IF NOT EXISTS auditoria_citas (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    paciente_id VARCHAR(30) NOT NULL,
    operacion VARCHAR(50) NOT NULL,
    detalles TEXT,
    fecha_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE DATABASE IF NOT EXISTS bd_laboratorio CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bd_laboratorio;
CREATE TABLE IF NOT EXISTS auditoria_laboratorio (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    paciente_id VARCHAR(30) NOT NULL,
    operacion VARCHAR(50) NOT NULL,
    detalles TEXT,
    fecha_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE DATABASE IF NOT EXISTS bd_facturacion CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bd_facturacion;
CREATE TABLE IF NOT EXISTS auditoria_facturacion (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    paciente_id VARCHAR(30) NOT NULL,
    operacion VARCHAR(50) NOT NULL,
    detalles TEXT,
    fecha_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
