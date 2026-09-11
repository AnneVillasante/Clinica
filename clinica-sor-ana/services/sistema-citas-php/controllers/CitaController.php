<?php
require_once __DIR__ . '/../models/Cita.php';
require_once __DIR__ . '/../repositories/CitaRepository.php';

function consultarCitas(string $pacienteId): void {
    $repository = new CitaRepository(citasPdo());
    jsonResponse($repository->byPatient($pacienteId));
}
