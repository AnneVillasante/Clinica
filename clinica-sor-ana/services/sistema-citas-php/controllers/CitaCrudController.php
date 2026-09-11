<?php
require_once __DIR__ . '/../repositories/CitaRepository.php';

function crearCita(array $payload): void {
    foreach (['pacienteId', 'fechaHora', 'medico', 'especialidad'] as $field) if (empty($payload[$field])) { jsonResponse(['error' => "Falta $field"], 400); return; }
    $id = (new CitaRepository(citasPdo()))->create($payload);
    jsonResponse(['id' => $id, 'estado' => $payload['estado'] ?? 'reservada'], 201);
}

function actualizarCita(int $id, array $payload): void {
    $updated = (new CitaRepository(citasPdo()))->update($id, $payload);
    jsonResponse($updated ? ['id' => $id, 'actualizada' => true] : ['error' => 'Cita no encontrada o sin cambios'], $updated ? 200 : 404);
}

function cancelarCita(int $id): void {
    $updated = (new CitaRepository(citasPdo()))->cancel($id);
    jsonResponse($updated ? ['id' => $id, 'estado' => 'cancelada'] : ['error' => 'Cita no encontrada'], $updated ? 200 : 404);
}
