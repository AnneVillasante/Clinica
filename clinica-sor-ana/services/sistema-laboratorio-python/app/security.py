import base64
import hashlib
import hmac
import json
import os
from flask import jsonify

SECRET_KEY = (os.getenv('SECURITY_SECRET') or 'ClinicaSorAna_ClaveSecretaSegura_2026').encode()


def verify_token(request, expected_patient=None):
    authorization = request.headers.get('Authorization', '')
    if not authorization.startswith('Bearer '):
        return None, (jsonify({'error': 'No autenticado: token requerido'}), 401)
    parts = authorization[7:].split('.')
    if len(parts) != 3:
        return None, (jsonify({'error': 'Token mal formado'}), 401)
    header, payload, signature = parts
    expected = base64.urlsafe_b64encode(
        hmac.new(SECRET_KEY, f'{header}.{payload}'.encode(), hashlib.sha256).digest()
    ).decode().rstrip('=')
    if not hmac.compare_digest(expected, signature):
        return None, (jsonify({'error': 'Fallo de integridad del token'}), 403)
    try:
        padding = '=' * (-len(payload) % 4)
        claims = json.loads(base64.urlsafe_b64decode(payload + padding))
    except (ValueError, json.JSONDecodeError):
        return None, (jsonify({'error': 'Token inválido'}), 401)
    patient_id = claims.get('id_paciente')
    if not isinstance(patient_id, str) or not patient_id:
        return None, (jsonify({'error': 'Token sin paciente'}), 401)
    if claims.get('exp') is not None and int(claims['exp']) < __import__('time').time():
        return None, (jsonify({'error': 'Token expirado'}), 401)
    if expected_patient is not None and patient_id != expected_patient:
        return None, (jsonify({'error': 'No autorizado'}), 403)
    return patient_id, None


def verify_body_signature(request):
    received = request.headers.get('X-Signature', '')
    expected = hmac.new(SECRET_KEY, request.get_data(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, received)
