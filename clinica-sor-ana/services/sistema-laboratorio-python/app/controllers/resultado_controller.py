from flask import Blueprint, jsonify, request
from app.repositories.laboratorio_repository import LaboratorioRepository
from app.security import verify_token

resultado_blueprint = Blueprint('resultado', __name__)
repository = LaboratorioRepository()

@resultado_blueprint.get('/resultados/paciente/<patient_id>')
@resultado_blueprint.get('/resultados/<patient_id>')
def results(patient_id):
    user_id, error = verify_token(request, patient_id)
    if error:
        return error
    repository.audit(user_id, 'CONSULTA_RESULTADOS', 'Consulta por paciente')
    return jsonify(repository.list_by_patient(patient_id))
