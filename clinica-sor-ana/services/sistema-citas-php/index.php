<?php
declare(strict_types=1);

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Signature');
header('Content-Type: application/xml; charset=UTF-8');

const SECRET_KEY = 'ClinicaSorAna_ClaveSecretaSegura_2026';

function xmlResponse(string $xml, int $status = 200): never {
    http_response_code($status);
    header('Content-Type: application/xml; charset=UTF-8');
    echo $xml;
    exit;
}

function xmlError(string $message, int $status): never {
    xmlResponse('<response status="error"><message>' . htmlspecialchars($message, ENT_XML1 | ENT_QUOTES, 'UTF-8') . '</message></response>', $status);
}

function base64UrlDecode(string $value): string|false {
    $padding = strlen($value) % 4;
    if ($padding !== 0) $value .= str_repeat('=', 4 - $padding);
    return base64_decode(strtr($value, '-_', '+/'), true);
}

function db(): PDO {
    $host = getenv('DB_HOST') ?: '127.0.0.1';
    $user = getenv('DB_USER') ?: 'root';
    $password = getenv('DB_PASSWORD') ?: 'Sapphire_27';
    return new PDO(
        "mysql:host={$host};dbname=bd_citas;charset=utf8mb4",
        $user,
        $password,
        [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION, PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC]
    );
}

function authenticatedPatient(): int {
    $headers = function_exists('getallheaders') ? getallheaders() : [];
    $authorization = $headers['Authorization'] ?? $headers['authorization'] ?? '';
    if (!preg_match('/^Bearer\s+(\S+)$/', $authorization, $matches)) xmlError('Token JWT requerido', 401);
    $parts = explode('.', $matches[1]);
    if (count($parts) !== 3) xmlError('Token mal formado', 401);
    [$header, $payload, $signature] = $parts;
    $expected = rtrim(strtr(base64_encode(hash_hmac('sha256', "$header.$payload", SECRET_KEY, true)), '+/', '-_'), '=');
    if (!hash_equals($expected, $signature)) xmlError('Fallo de integridad: token adulterado', 403);
    $payloadJson = base64UrlDecode($payload);
    $claims = $payloadJson === false ? null : json_decode($payloadJson, true);
    $patientId = $claims['id_paciente'] ?? null;
    if (!is_int($patientId) && !ctype_digit((string) $patientId)) xmlError('Token sin id_paciente válido', 401);
    if (isset($claims['exp']) && (int) $claims['exp'] < time()) xmlError('Token expirado', 401);
    return (int) $patientId;
}

function audit(PDO $pdo, int $patientId, string $operation, string $details): void {
    $statement = $pdo->prepare('INSERT INTO auditoria_citas (id_paciente, operacion, detalles) VALUES (?, ?, ?)');
    $statement->execute([$patientId, $operation, $details]);
}

function bodySignatureIsValid(string $rawBody): bool {
    $headers = function_exists('getallheaders') ? getallheaders() : [];
    $received = $headers['X-Signature'] ?? $headers['x-signature'] ?? '';
    return $received !== '' && hash_equals(hash_hmac('sha256', $rawBody, SECRET_KEY), $received);
}

function parseCita(string $rawBody): SimpleXMLElement {
    if ($rawBody === '') xmlError('El cuerpo XML es obligatorio', 400);
    $dom = new DOMDocument();
    $dom->preserveWhiteSpace = false;
    libxml_use_internal_errors(true);
    if (!$dom->loadXML($rawBody, LIBXML_NONET) || !$dom->schemaValidate(__DIR__ . '/../../schemas/cita.xsd')) {
        libxml_clear_errors();
        xmlError('El XML de cita no cumple schemas/cita.xsd', 422);
    }
    libxml_use_internal_errors(true);
    $xml = simplexml_load_string($rawBody, SimpleXMLElement::class, LIBXML_NONET);
    if ($xml === false || $xml->getName() !== 'cita') xmlError('XML de cita inválido', 400);
    foreach (['id_paciente', 'medico', 'especialidad', 'fecha'] as $field) {
        if (!isset($xml->{$field}) || trim((string) $xml->{$field}) === '') xmlError("Falta {$field}", 400);
    }
    if (!ctype_digit((string) $xml->id_paciente)) xmlError('id_paciente debe ser integer', 400);
    return $xml;
}

$method = $_SERVER['REQUEST_METHOD'] ?? 'GET';
if ($method === 'OPTIONS') { http_response_code(204); exit; }

try {
    $pdo = db();
    $patientId = authenticatedPatient();

    if ($method === 'GET' && parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH) === '/') {
        $statement = $pdo->prepare('SELECT id, id_paciente, medico, especialidad, fecha FROM citas WHERE id_paciente = ? ORDER BY id');
        $statement->execute([$patientId]);
        $root = new SimpleXMLElement('<citasClinica/>');
        foreach ($statement->fetchAll() as $row) {
            $cita = $root->addChild('cita');
            foreach ($row as $key => $value) $cita->addChild($key, htmlspecialchars((string) $value, ENT_XML1 | ENT_QUOTES, 'UTF-8'));
        }
        audit($pdo, $patientId, 'CONSULTA_CITAS', 'Listado XML consultado');
        xmlResponse($root->asXML());
    }

    if ($method === 'POST' && parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH) === '/') {
        if (stripos($_SERVER['CONTENT_TYPE'] ?? '', 'application/xml') !== 0) xmlError('Content-Type debe ser application/xml', 415);
        $rawBody = file_get_contents('php://input');
        if (!bodySignatureIsValid($rawBody)) xmlError('Fallo de integridad: X-Signature inválida', 400);
        $xml = parseCita($rawBody);
        if ((int) $xml->id_paciente !== $patientId) xmlError('No autorizado para otro paciente', 403);
        $statement = $pdo->prepare('INSERT INTO citas (id_paciente, medico, especialidad, fecha) VALUES (?, ?, ?, ?)');
        $statement->execute([$patientId, trim((string) $xml->medico), trim((string) $xml->especialidad), trim((string) $xml->fecha)]);
        $id = (int) $pdo->lastInsertId();
        audit($pdo, $patientId, 'CREAR_CITA', 'Cita ' . $id . ' creada');
        xmlResponse('<response status="success"><id>' . $id . '</id><message>Cita creada</message></response>', 201);
    }

    if ($method === 'DELETE' && parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH) === '/') {
        $id = filter_input(INPUT_GET, 'id', FILTER_VALIDATE_INT);
        if (!$id) xmlError('El parámetro id es obligatorio', 400);
        $check = $pdo->prepare('SELECT id FROM citas WHERE id = ? AND id_paciente = ?');
        $check->execute([$id, $patientId]);
        if (!$check->fetch()) xmlError('Cita inexistente o no autorizada', 403);
        $statement = $pdo->prepare('DELETE FROM citas WHERE id = ? AND id_paciente = ?');
        $statement->execute([$id, $patientId]);
        audit($pdo, $patientId, 'ELIMINAR_CITA', 'Cita ' . $id . ' eliminada');
        xmlResponse('<response status="success"><id>' . $id . '</id><message>Cita eliminada</message></response>');
    }

    xmlError('Ruta no encontrada', 404);
} catch (Throwable $error) {
    error_log($error->getMessage());
    xmlError('Error interno del servicio de citas', 500);
}
