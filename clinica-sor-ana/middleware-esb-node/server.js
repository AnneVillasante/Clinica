const http = require('http');
const { URL } = require('url');

const port = Number(process.env.PORT || 3000);
const services = {
  citas: process.env.CITAS_URL || 'http://localhost:8001/citas/paciente',
  laboratorio: process.env.LABORATORIO_URL || 'http://localhost:8002/resultados/paciente',
};

function sendJson(response, status, payload) {
  response.writeHead(status, {
    'content-type': 'application/json; charset=utf-8',
    'access-control-allow-origin': 'http://localhost:8080',
    'access-control-allow-headers': 'Content-Type, Authorization, X-Signature',
  });
  response.end(JSON.stringify(payload));
}

async function queryService(url, authorization, timeout = 5000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  try {
    const result = await fetch(url, { signal: controller.signal, headers: { Authorization: authorization } });
    if (!result.ok) throw new Error(`HTTP ${result.status}`);
    return await result.json();
  } finally {
    clearTimeout(timer);
  }
}

const server = http.createServer(async (request, response) => {
  const requestUrl = new URL(request.url || '/', `http://${request.headers.host || 'localhost'}`);

  if (request.method === 'OPTIONS') {
    response.writeHead(204, {
      'access-control-allow-origin': 'http://localhost:8080',
      'access-control-allow-methods': 'GET, OPTIONS',
      'access-control-allow-headers': 'Content-Type',
    });
    response.end();
    return;
  }

  const match = requestUrl.pathname.match(/^\/api\/paciente\/([^/]+)$/);
  if (request.method === 'GET' && match) {
    const authorization = request.headers.authorization || '';
    if (!/^Bearer\s+\S+$/.test(authorization)) {
      sendJson(response, 401, { error: 'No autenticado: token requerido' });
      return;
    }
    const patientId = decodeURIComponent(match[1]);
    const entries = await Promise.all(Object.entries(services).map(async ([name, baseUrl]) => {
      try {
        return [name, { estado: 'disponible', datos: await queryService(`${baseUrl}/${encodeURIComponent(patientId)}`, authorization) }];
      } catch (error) {
        return [name, { estado: 'no disponible', datos: [], error: error.name === 'AbortError' ? 'Tiempo de espera agotado' : error.message }];
      }
    }));
    sendJson(response, 200, { pacienteId: patientId, ...Object.fromEntries(entries) });
    return;
  }

  if (request.method === 'GET' && requestUrl.pathname === '/') {
    sendJson(response, 200, {
      servicio: 'middleware-esb-node',
      estado: 'activo',
      mensaje: 'Orquestador SOA de consultas de solo lectura.',
      endpoint: '/api/paciente/{id}',
    });
    return;
  }

  sendJson(response, 404, { error: 'Ruta no encontrada' });
});

server.listen(port, () => {
  console.log(`Middleware ESB base disponible en http://localhost:${port}`);
});

module.exports = server;
