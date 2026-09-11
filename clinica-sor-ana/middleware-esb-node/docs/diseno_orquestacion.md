# Diseño de orquestación futura

## Alcance actual

Esta entrega termina en Inicio y Planificación. Los sistemas de citas, laboratorio y facturación son aplicaciones autónomas, con bases aisladas y contratos publicados. No existe comunicación backend-a-backend ni SQL cruzado.

## Fase futura de ejecución

El ESB Node.js deberá consumir las tres capacidades de grano grueso y construir un resumen unificado mediante llamadas concurrentes. La autorización deberá separar permisos clínicos y financieros antes de exponer datos al portal.

## Evolución prevista

La pasarela de pagos, el despliegue cloud y la expansión del catálogo a más de 75 servicios se realizarán en Ejecución y Despliegue para la entrega final del 10 de diciembre.
