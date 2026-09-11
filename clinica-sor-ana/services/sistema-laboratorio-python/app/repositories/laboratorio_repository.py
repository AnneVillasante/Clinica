from . import __name__
from app.database import connection


class LaboratorioRepository:
    def belongs_to(self, result_id: int, patient_id: str) -> bool:
        db = connection()
        cursor = db.cursor()
        cursor.execute('SELECT 1 FROM resultados WHERE id = %s AND paciente_id = %s', (result_id, patient_id))
        found = cursor.fetchone() is not None
        cursor.close()
        db.close()
        return found

    def audit(self, patient_id: str, operation: str, details: str) -> None:
        db = connection()
        cursor = db.cursor()
        cursor.execute('INSERT INTO auditoria_laboratorio (paciente_id, operacion, detalles) VALUES (%s, %s, %s)',
                       (patient_id, operation, details))
        db.commit()
        cursor.close()
        db.close()

    def list_by_patient(self, patient_id: str) -> list[dict]:
        db = connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute('''SELECT r.id, r.paciente_id AS pacienteId, e.codigo, e.nombre AS examen,
                          r.valor, r.unidad, r.rango_referencia AS rangoReferencia,
                          r.observaciones, r.fecha_muestra AS fechaMuestra, r.estado
                          FROM resultados r JOIN examenes e ON e.id = r.examen_id
                          WHERE r.paciente_id = %s ORDER BY r.fecha_muestra DESC''', (patient_id,))
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        return rows

    def create_result(self, payload: dict) -> int:
        db = connection()
        cursor = db.cursor()
        cursor.execute('''INSERT INTO resultados (paciente_id, examen_id, valor, unidad, rango_referencia,
                          observaciones, fecha_muestra, estado) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)''',
                       (payload['pacienteId'], payload['examenId'], payload['valor'], payload.get('unidad'),
                        payload.get('rangoReferencia'), payload.get('observaciones'), payload['fechaMuestra'],
                        payload.get('estado', 'muestra_recibida')))
        db.commit()
        result_id = cursor.lastrowid
        cursor.close()
        db.close()
        return result_id

    def update_result(self, result_id: int, payload: dict) -> bool:
        allowed = {'valor', 'unidad', 'rango_referencia', 'observaciones', 'estado'}
        values = {key: value for key, value in payload.items() if key in allowed}
        if not values:
            return False
        assignments = ', '.join(f'{key} = %s' for key in values)
        db = connection()
        cursor = db.cursor()
        cursor.execute(f'UPDATE resultados SET {assignments} WHERE id = %s', (*values.values(), result_id))
        db.commit()
        updated = cursor.rowcount > 0
        cursor.close()
        db.close()
        return updated
