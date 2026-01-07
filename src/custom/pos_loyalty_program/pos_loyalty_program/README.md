# Punto de Venta - Programa de Fidelización

## Descripción

Este módulo implementa un sistema de puntos de fidelización para clientes en el Punto de Venta (POS) de Odoo 17.

## Funcionalidades

### Acumulación de Puntos
- Los clientes acumulan puntos automáticamente al realizar compras en el POS
- La tasa de acumulación es configurable (ej: 1 punto por cada $10 de compra)
- Se soportan diferentes tipos de redondeo: hacia abajo, hacia arriba, o al más cercano

### Configuración
- Habilitar/deshabilitar el programa por punto de venta
- Configurar la cantidad de puntos a otorgar
- Configurar el monto requerido para obtener puntos
- Seleccionar el tipo de redondeo de puntos

### Histórico
- Cada transacción de puntos se registra en un histórico detallado
- Se puede consultar el balance actual y el historial desde la ficha del cliente
- Reporte PDF con el histórico de puntos por cliente

### Resumen por Sesión
- Vista de resumen de puntos acumulados en cada sesión de POS
- Contador de transacciones de fidelización

## Configuración

1. Ir a **Punto de Venta > Configuración > Punto de Venta**
2. Seleccionar el POS a configurar
3. En la sección "Programa de Fidelización":
   - Activar "Habilitar Programa de Fidelización"
   - Configurar los puntos por monto gastado
   - Seleccionar el tipo de redondeo

## Uso

1. El cliente realiza una compra en el POS
2. Al validar la orden, se calculan los puntos automáticamente
3. Los puntos se suman al saldo del cliente
4. Se crea un registro en el histórico de puntos

## Consultar Puntos del Cliente

1. Ir a **Contactos**
2. Seleccionar un cliente
3. Ver el campo "Puntos de Fidelización" en la ficha
4. Hacer clic en el botón "Histórico de Puntos" para ver el detalle

## Reportes

### Histórico de Puntos del Cliente
Genera un PDF con:
- Información del cliente
- Resumen de puntos (balance, ganados, canjeados)
- Tabla detallada con todas las transacciones

## Dependencias

- `base`
- `point_of_sale`

## Autor

Binaural - https://www.binaural.dev

## Licencia

LGPL-3

