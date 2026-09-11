<?php
require_once __DIR__ . '/../config/database.php';

class CitaRepository {
    public function __construct(private PDO $db) {}

    public function db(): PDO { return $this->db; }

    public function byPatient(string $patientId): array {
        $query = 'SELECT id, paciente_id AS pacienteId, fecha_hora AS fechaHora, medico, especialidad, motivo, estado FROM citas WHERE paciente_id = ? ORDER BY fecha_hora';
        $statement = $this->db->prepare($query);
        $statement->execute([$patientId]);
        return $statement->fetchAll(PDO::FETCH_ASSOC);
    }

    public function recent(): array {
        return $this->db->query('SELECT id, paciente_id AS pacienteId, fecha_hora AS fechaHora, medico, especialidad, estado FROM citas ORDER BY id DESC LIMIT 5')->fetchAll(PDO::FETCH_ASSOC);
    }

    public function belongsTo(int $id, string $patientId): bool {
        $statement = $this->db->prepare('SELECT 1 FROM citas WHERE id = ? AND paciente_id = ?');
        $statement->execute([$id, $patientId]);
        return (bool) $statement->fetchColumn();
    }

    public function create(array $data): int {
        $statement = $this->db->prepare('INSERT INTO citas (paciente_id, fecha_hora, medico, especialidad, motivo, estado) VALUES (?, ?, ?, ?, ?, ?)');
        $statement->execute([$data['pacienteId'], $data['fechaHora'], $data['medico'], $data['especialidad'], $data['motivo'] ?? null, $data['estado'] ?? 'reservada']);
        return (int) $this->db->lastInsertId();
    }

    public function update(int $id, array $data): bool {
        $allowed = ['fecha_hora', 'medico', 'especialidad', 'motivo', 'estado'];
        $fields = [];
        $values = [];
        foreach ($allowed as $field) {
            if (array_key_exists($field, $data)) { $fields[] = "$field = ?"; $values[] = $data[$field]; }
        }
        if (!$fields) return false;
        $values[] = $id;
        $statement = $this->db->prepare('UPDATE citas SET ' . implode(', ', $fields) . ' WHERE id = ?');
        $statement->execute($values);
        return $statement->rowCount() > 0;
    }

    public function cancel(int $id): bool {
        return $this->update($id, ['estado' => 'cancelada']);
    }
}
