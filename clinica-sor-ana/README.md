# Clínica Sor Ana · Integración SOA XML

Proyecto demostrativo de Arquitectura Orientada a Servicios para una clínica. Los servicios de citas PHP y laboratorio Python son autónomos: cada uno usa su propio esquema MySQL y expone un contrato XML sobre HTTP. El portal web actúa como consumidor y no accede directamente a las bases de datos.

## Requisitos

- MySQL 8 o compatible.
- PHP 8.1+ con extensiones `pdo_mysql` y `simplexml`.
- Python 3.10+.
- Node.js no es necesario para esta versión XML.
- Un navegador moderno con `crypto.subtle`.

## 1. Crear las bases de datos

Ejecuta `database/init.sql` en MySQL Workbench, phpMyAdmin o la consola MySQL. Crea `bd_citas`, `bd_laboratorio`, sus tablas de negocio, las tablas `auditoria_citas` y `auditoria_lab`, y datos de prueba para los pacientes `101` y `102`.

La configuración predeterminada de los servicios es:

```text
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=Sapphire_27
```

Puedes cambiarla mediante variables de entorno. El secreto HMAC predeterminado es `ClinicaSorAna_ClaveSecretaSegura_2026`; en una instalación real debe configurarse como `SECURITY_SECRET` y nunca exponerse en el frontend.

## 2. Levantar el servicio de citas PHP

En una terminal:

```powershell
cd "c:\Users\suemy\OneDrive\Escritorio\Clínica\clinica-sor-ana\services\sistema-citas-php"
php -S localhost:8001 index.php
```

Contrato:

```text
GET    http://localhost:8001/
POST   http://localhost:8001/
DELETE http://localhost:8001/?id=1
Content-Type: application/xml
```

## 3. Levantar el servicio de laboratorio Python

En otra terminal:

```powershell
cd "c:\Users\suemy\OneDrive\Escritorio\Clínica\clinica-sor-ana\services\sistema-laboratorio-python"
python -m pip install -r requirements.txt
python main.py
```

Contrato:

```text
GET    http://localhost:8002/resultados
POST   http://localhost:8002/resultados
DELETE http://localhost:8002/resultados/1
Content-Type: application/xml
```

## 4. Levantar el portal consumidor

En otra terminal:

```powershell
cd "c:\Users\suemy\OneDrive\Escritorio\Clínica\clinica-sor-ana\portal-web-cliente"
python -m http.server 8080
```

Abre [http://localhost:8080](http://localhost:8080). Selecciona el paciente 101 o 102. El portal genera un JWT HMAC para la demostración, firma los XML de escritura con `X-Signature` y consume directamente ambos servicios.

## Flujo XML

Ejemplo de XML enviado para crear una cita:

```xml
<cita>
  <id_paciente>101</id_paciente>
  <medico>Dra. Valentina Rojas</medico>
  <especialidad>Medicina interna</especialidad>
  <fecha>2026-10-20 10:00</fecha>
</cita>
```

Ejemplo de XML enviado para crear un resultado:

```xml
<resultado>
  <id_paciente>101</id_paciente>
  <examen>Glucosa</examen>
  <diagnostico>Resultado normal</diagnostico>
</resultado>
```

Los esquemas formales están en `schemas/cita.xsd` y `schemas/resultado.xsd`. El visor inferior del portal muestra el cuerpo exacto enviado, la respuesta exacta recibida, la hora, el método y el estado HTTP.

## Guion para demostrar los cinco pilares

1. **Autenticación:** abre DevTools, elimina la cabecera `Authorization` de una solicitud o usa Postman sin ella. El backend responde XML `401`.
2. **Autorización:** selecciona el paciente 101 y observa sus datos. Cambia al 102; el backend genera un JWT distinto y solo devuelve los registros pertenecientes al paciente autenticado. Modificar el `id_paciente` del XML produce XML `403`.
3. **Confidencialidad:** el diseño de los endpoints es compatible con HTTPS/TLS. Para producción, publica ambos servicios detrás de un proxy TLS y cambia las URLs del portal a `https://`. El servidor PHP/Flask de desarrollo local usa HTTP deliberadamente.
4. **Integridad:** modifica un carácter del XML sin recalcular `X-Signature`. El backend responde XML `400` y no inserta el registro.
5. **Auditoría:** consulta `auditoria_citas` y `auditoria_lab` en sus esquemas respectivos. Cada lectura, inserción y eliminación registra `id_paciente`, operación, detalles y `fecha_hora`.

## Detener los servicios

Presiona `Ctrl+C` en cada terminal. Si una terminal se cerró y el puerto sigue ocupado, identifica el proceso con `Get-NetTCPConnection -LocalPort 8001` o `8002` y detenlo con `Stop-Process -Id <PID> -Force`.

## Nota de seguridad

La generación del token y el secreto dentro de `index.html` existen únicamente para hacer visible el flujo criptográfico en una demostración local. No es un mecanismo de autenticación de producción. En producción, un servidor de identidad debe emitir los tokens, el secreto debe permanecer en los backends y toda la comunicación debe usar HTTPS/TLS.
