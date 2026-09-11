# Alcance de integración XML

## Alcance actual

La entrega integra exclusivamente los sistemas autónomos de Citas y Laboratorio mediante XML sobre HTTP. Cada sistema mantiene su propia base MySQL, contrato XSD y bitácora de auditoría. No existe SQL cruzado ni dependencia de facturación.

## Fase futura de ejecución

El portal web consume directamente ambos proveedores y muestra las operaciones de negocio. La autenticación usa `Authorization: Bearer`, la integridad usa `X-Signature` y los cuerpos de escritura se validan contra sus XSD antes de tocar MySQL.

## Evolución prevista

Facturación, pagos, ESB y despliegue cloud están fuera del alcance de esta entrega y no forman parte del flujo evaluado.
