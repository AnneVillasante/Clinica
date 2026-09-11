from flask import Blueprint, jsonify, request
from app.repositories.laboratorio_repository import LaboratorioRepository
from app.security import verify_body_signature, verify_token

crud_blueprint = Blueprint('examen_crud', __name__)
repository = LaboratorioRepository()

@crud_blueprint.post('/resultados')
def create_result():
    user_id, error = verify_token(request)
    if error:
        return error
    if not verify_body_signature(request):
        return jsonify({'error': 'Fallo de integridad del cuerpo'}), 400
    payload = request.get_json(silent=True) or {}
    required = ['pacienteId', 'examenId', 'valor', 'fechaMuestra']
    missing = [field for field in required if not payload.get(field)]
    if missing:
        return jsonify({'error': 'Faltan campos', 'campos': missing}), 400
    if payload['pacienteId'] != user_id:
        return jsonify({'error': 'No autorizado'}), 403
    result_id = repository.create_result(payload)
    repository.audit(user_id, 'CREAR_RESULTADO', f'Resultado: {result_id}')
    return jsonify({'id': result_id}), 201

@crud_blueprint.put('/resultados/<int:result_id>')
def update_result(result_id):
    user_id, error = verify_token(request)
    if error:
        return error
    if not repository.belongs_to(result_id, user_id):
        return jsonify({'error': 'No autorizado'}), 403
    if not verify_body_signature(request):
        return jsonify({'error': 'Fallo de integridad del cuerpo'}), 400
    if not repository.update_result(result_id, request.get_json(silent=True) or {}):
        return jsonify({'error': 'Resultado no encontrado o sin cambios'}), 404
    repository.audit(user_id, 'ACTUALIZAR_RESULTADO', f'Resultado: {result_id}')
    return jsonify({'id': result_id, 'actualizado': True})
