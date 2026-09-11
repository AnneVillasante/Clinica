from .database import connection


def results_by_patient(patient_id: str) -> list[dict]:
    db = connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT examen, resultado, fecha, estado FROM resultados WHERE paciente_id = %s ORDER BY fecha DESC', (patient_id,))
    rows = cursor.fetchall()
    cursor.close()
    db.close()
    return rows
