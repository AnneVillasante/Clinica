import base64
import hashlib
import hmac
import json
import os
import time
import xml.etree.ElementTree as ET
from functools import wraps
from pathlib import Path

import mysql.connector
import xmlschema
from flask import Flask, Response, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}}, allow_headers=['Content-Type', 'Authorization', 'X-Signature'])
SECRET_KEY = (os.getenv('SECURITY_SECRET') or 'ClinicaSorAna_ClaveSecretaSegura_2026').encode()
RESULTADO_SCHEMA = xmlschema.XMLSchema((Path(__file__).resolve().parents[2] / 'schemas' / 'resultado.xsd').as_uri())


@app.errorhandler(404)
def not_found(_error):
    return xml_error('Ruta no encontrada', 404)


@app.errorhandler(Exception)
def internal_error(error):
    app.logger.error('%s', error)
    return xml_error('Error interno del servicio de laboratorio', 500)


def xml_response(root: ET.Element, status: int = 200) -> Response:
    body = ET.tostring(root, encoding='utf-8', xml_declaration=True)
    return Response(body, status=status, content_type='application/xml; charset=utf-8')


def xml_error(message: str, status: int):
    root = ET.Element('response', {'status': 'error'})
    ET.SubElement(root, 'message').text = message
    return xml_response(root, status)


def get_db():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', '127.0.0.1'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'Sapphire_27'),
        database='bd_laboratorio',
    )


def audit(patient_id: int, operation: str, details: str):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute(
        'INSERT INTO auditoria_lab (id_paciente, operacion, detalles) VALUES (%s, %s, %s)',
        (patient_id, operation, details),
    )
    connection.commit()
    cursor.close()
    connection.close()


def decode_base64url(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + '=' * (-len(value) % 4))


def authenticated_patient():
    authorization = request.headers.get('Authorization', '')
    if not authorization.startswith('Bearer '):
        return None, xml_error('Token JWT requerido', 401)
    parts = authorization[7:].split('.')
    if len(parts) != 3:
        return None, xml_error('Token mal formado', 401)
    header, payload, signature = parts
    expected = base64.urlsafe_b64encode(
        hmac.new(SECRET_KEY, f'{header}.{payload}'.encode(), hashlib.sha256).digest()
    ).decode().rstrip('=')
    if not hmac.compare_digest(expected, signature):
        return None, xml_error('Fallo de integridad: token adulterado', 403)
    try:
        claims = json.loads(decode_base64url(payload))
        patient_id = int(claims['id_paciente'])
        if 'exp' in claims and int(claims['exp']) < int(time.time()):
            return None, xml_error('Token expirado', 401)
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None, xml_error('Token sin id_paciente válido', 401)
    return patient_id, None


def requires_patient(handler):
    @wraps(handler)
    def wrapped(*args, **kwargs):
        patient_id, error = authenticated_patient()
        if error:
            return error
        return handler(patient_id, *args, **kwargs)

    return wrapped


def valid_signature():
    received = request.headers.get('X-Signature', '')
    expected = hmac.new(SECRET_KEY, request.get_data(), hashlib.sha256).hexdigest()
    return bool(received) and hmac.compare_digest(expected, received)


@app.route('/', methods=['GET'])
def home():
    return xml_response(ET.Element('service', {'name': 'laboratorio', 'status': 'active'}))


@app.route('/resultados', methods=['GET'])
@requires_patient
def get_resultados(patient_id: int):
    connection = get_db()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        'SELECT id, id_paciente, examen, diagnostico FROM resultados WHERE id_paciente = %s ORDER BY id',
        (patient_id,),
    )
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    root = ET.Element('resultadosClinica')
    for row in rows:
        item = ET.SubElement(root, 'resultado')
        for field in ('id', 'id_paciente', 'examen', 'diagnostico'):
            ET.SubElement(item, field).text = str(row[field])
    audit(patient_id, 'CONSULTA_RESULTADOS', f'Total recuperados: {len(rows)}')
    return xml_response(root)


@app.route('/resultados', methods=['POST'])
@requires_patient
def add_resultado(patient_id: int):
    if not request.content_type or not request.content_type.startswith('application/xml'):
        return xml_error('Content-Type debe ser application/xml', 415)
    if not valid_signature():
        return xml_error('Fallo de integridad: X-Signature inválida', 400)
    try:
        RESULTADO_SCHEMA.validate(request.get_data())
        root = ET.fromstring(request.get_data())
        if root.tag != 'resultado':
            return xml_error('XML de resultado inválido', 400)
        values = {child.tag: (child.text or '').strip() for child in root}
        required = ('id_paciente', 'examen', 'diagnostico')
        if any(not values.get(field) for field in required):
            return xml_error('Faltan campos obligatorios', 400)
        if int(values['id_paciente']) != patient_id:
            return xml_error('No autorizado para otro paciente', 403)
    except (ET.ParseError, ValueError, xmlschema.XMLSchemaException):
        return xml_error('El XML de resultado no cumple schemas/resultado.xsd', 422)

    connection = get_db()
    cursor = connection.cursor()
    cursor.execute(
        'INSERT INTO resultados (id_paciente, examen, diagnostico) VALUES (%s, %s, %s)',
        (patient_id, values['examen'], values['diagnostico']),
    )
    connection.commit()
    result_id = cursor.lastrowid
    cursor.close()
    connection.close()
    audit(patient_id, 'CREAR_RESULTADO', f'Resultado {result_id} creado')

    response = ET.Element('response', {'status': 'success'})
    ET.SubElement(response, 'id').text = str(result_id)
    ET.SubElement(response, 'message').text = 'Resultado creado'
    return xml_response(response, 201)


@app.route('/resultados/<int:item_id>', methods=['DELETE'])
@requires_patient
def delete_resultado(patient_id: int, item_id: int):
    connection = get_db()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT id FROM resultados WHERE id = %s AND id_paciente = %s', (item_id, patient_id))
    item = cursor.fetchone()
    if not item:
        cursor.close()
        connection.close()
        return xml_error('Resultado inexistente o no autorizado', 403)
    cursor.execute('DELETE FROM resultados WHERE id = %s AND id_paciente = %s', (item_id, patient_id))
    connection.commit()
    cursor.close()
    connection.close()
    audit(patient_id, 'ELIMINAR_RESULTADO', f'Resultado {item_id} eliminado')

    response = ET.Element('response', {'status': 'success'})
    ET.SubElement(response, 'id').text = str(item_id)
    ET.SubElement(response, 'message').text = 'Resultado eliminado'
    return xml_response(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '8002')))
