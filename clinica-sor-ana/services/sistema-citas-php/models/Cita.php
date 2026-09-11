<?php
class Cita {
    public function __construct(public ?int $id, public string $pacienteId, public string $fechaHora, public string $medico, public string $especialidad, public ?string $motivo, public string $estado) {}
}
