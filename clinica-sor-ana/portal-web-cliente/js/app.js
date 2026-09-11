const form = document.querySelector('#patient-form');
const status = document.querySelector('#status');
const summary = document.querySelector('#summary');
const soaUrl = 'http://localhost:3000/api/paciente';
const securitySecret = 'ClinicaSorAna_ClaveSecretaSegura_2026';

function base64UrlEncode(value) {
  return btoa(value).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

async function createPatientToken(patientId) {
  const header = base64UrlEncode(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const payload = base64UrlEncode(JSON.stringify({ id_paciente: patientId, exp: Math.floor(Date.now() / 1000) + 3600 }));
  const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(securitySecret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const signature = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(`${header}.${payload}`));
  const encodedSignature = base64UrlEncode(String.fromCharCode(...new Uint8Array(signature)));
  return `${header}.${payload}.${encodedSignature}`;
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const patientId = document.querySelector('#patient-id').value.trim();
  if (!patientId) return;

  status.textContent = 'Consultando los tres sistemas independientes mediante SOA...';
  try {
    const token = await createPatientToken(patientId);
    const response = await fetch(`${soaUrl}/${encodeURIComponent(patientId)}`, { headers: { Authorization: `Bearer ${token}` } });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    document.querySelector('#patient-name').textContent = data.pacienteId;
    document.querySelector('#appointments').textContent = JSON.stringify(data.citas.datos, null, 2);
    document.querySelector('#results').textContent = JSON.stringify(data.laboratorio.datos, null, 2);
    document.querySelector('#invoices').textContent = JSON.stringify(data.facturacion.datos, null, 2);
    summary.hidden = false;
    status.textContent = 'Consulta completada.';
  } catch (error) {
    summary.hidden = true;
    status.textContent = 'No fue posible consultar el orquestador SOA. Verifica que las aplicaciones estén encendidas.';
  }
});
