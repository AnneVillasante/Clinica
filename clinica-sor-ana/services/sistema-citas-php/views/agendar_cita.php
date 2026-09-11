<!doctype html>
<html lang="es">
<head><meta charset="utf-8"><title>Admisión | Agendar cita</title></head>
<body>
  <main>
    <h1>Agendar cita</h1>
    <form method="post" action="/citas">
      <label>Paciente <input name="pacienteId" required></label>
      <label>Fecha y hora <input type="datetime-local" name="fechaHora" required></label>
      <label>Médico <input name="medico" required></label>
      <label>Especialidad <input name="especialidad" required></label>
      <button type="submit">Guardar cita</button>
    </form>
  </main>
</body>
</html>
