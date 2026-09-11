USE bd_citas;
INSERT IGNORE INTO pacientes (identificador, nombre, documento, telefono, email) VALUES ('PAC-1002', 'Ana María López', 'CC-1002', '+57 300 100 2002', 'ana.lopez@example.test');
INSERT IGNORE INTO medicos (id, nombre, especialidad, consultorio) VALUES (1, 'Dra. Valentina Rojas', 'Medicina interna', 'Consultorio 204');
INSERT IGNORE INTO turnos (id, medico_id, inicio, fin, estado) VALUES (1, 1, '2026-10-15 09:30:00', '2026-10-15 10:00:00', 'reservado'), (2, 1, '2026-10-16 11:00:00', '2026-10-16 11:30:00', 'disponible');
INSERT INTO citas (paciente_id, turno_id, fecha_hora, medico, especialidad, motivo, estado) SELECT 'PAC-1002', 1, '2026-10-15 09:30:00', 'Dra. Valentina Rojas', 'Medicina interna', 'Control preventivo', 'confirmada' WHERE NOT EXISTS (SELECT 1 FROM citas WHERE paciente_id = 'PAC-1002');

USE bd_laboratorio;
INSERT IGNORE INTO examenes (id, codigo, nombre, unidad) VALUES (1, 'HEMOGRAMA', 'Hemograma completo', 'g/dL');
INSERT INTO resultados (paciente_id, examen_id, valor, unidad, rango_referencia, observaciones, fecha_muestra, estado) SELECT 'PAC-1002', 1, 'Valores dentro de rango', 'g/dL', 'Según laboratorio', 'Sin observaciones clínicas', '2026-09-02', 'validado' WHERE NOT EXISTS (SELECT 1 FROM resultados WHERE paciente_id = 'PAC-1002');

USE bd_facturacion;
INSERT IGNORE INTO conceptos_medicos (id, codigo, descripcion, precio) VALUES (1, 'CONSULTA-MI', 'Consulta medicina interna', 85000.00);
INSERT IGNORE INTO comprobantes (paciente_id, numero, concepto, subtotal, impuesto, total, estado, emitido_en) VALUES ('PAC-1002', 'FAC-2026-0042', 'Consulta medicina interna', 85000.00, 0, 85000.00, 'pagado', '2026-09-01');
