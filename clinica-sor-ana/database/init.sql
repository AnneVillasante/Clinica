CREATE DATABASE IF NOT EXISTS bd_citas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS bd_laboratorio CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE bd_citas;
CREATE TABLE IF NOT EXISTS citas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_paciente INT NOT NULL,
    medico VARCHAR(100) NOT NULL,
    especialidad VARCHAR(100) NOT NULL,
    fecha VARCHAR(50) NOT NULL,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS auditoria_citas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_paciente INT NOT NULL,
    operacion VARCHAR(50) NOT NULL,
    detalles TEXT,
    fecha_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO citas (id_paciente, medico, especialidad, fecha)
SELECT 101, 'Dra. Valentina Rojas', 'Medicina interna', '2026-10-15 09:30'
WHERE NOT EXISTS (SELECT 1 FROM citas WHERE id_paciente = 101);
INSERT INTO citas (id_paciente, medico, especialidad, fecha)
SELECT 102, 'Dr. Carlos Mendoza', 'Pediatría', '2026-10-16 14:00'
WHERE NOT EXISTS (SELECT 1 FROM citas WHERE id_paciente = 102);

USE bd_laboratorio;
CREATE TABLE IF NOT EXISTS resultados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_paciente INT NOT NULL,
    examen VARCHAR(100) NOT NULL,
    diagnostico VARCHAR(255) NOT NULL,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS auditoria_lab (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_paciente INT NOT NULL,
    operacion VARCHAR(50) NOT NULL,
    detalles TEXT,
    fecha_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO resultados (id_paciente, examen, diagnostico)
SELECT 101, 'Hemograma', 'Valores dentro de rango'
WHERE NOT EXISTS (SELECT 1 FROM resultados WHERE id_paciente = 101);
INSERT INTO resultados (id_paciente, examen, diagnostico)
SELECT 102, 'Glucosa', 'Resultado normal'
WHERE NOT EXISTS (SELECT 1 FROM resultados WHERE id_paciente = 102);
