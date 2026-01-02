# Inventario - Alertas de Stock Crítico

Módulo de Odoo 17 para generar alertas automáticas cuando el stock de productos cae por debajo de un umbral configurable.

## Características

- **Campo Stock Mínimo**: Campo configurable en `product.template` para definir el umbral mínimo de stock.
- **Alertas Automáticas**: Generación automática de alertas cuando el stock disponible (`qty_available`) está por debajo del umbral.
- **Notificaciones**: Notificaciones vía `mail.message` integradas con el chatter de Odoo.
- **Dashboard**: Vista de tablero con productos en estado crítico, agrupados por categoría.
- **Sin Duplicados**: Sistema inteligente que evita alertas duplicadas para el mismo producto.
- **Cron Job**: Verificación automática programada cada hora.

## Instalación

1. Copiar el módulo a la carpeta `src/custom/`
2. Actualizar la lista de aplicaciones en Odoo
3. Instalar el módulo "Inventario - Alertas de Stock Crítico"

## Uso

### Configurar Stock Mínimo

1. Ir a **Inventario > Productos > Productos**
2. Abrir un producto almacenable
3. En la pestaña **Inventario**, encontrar la sección "Alertas de Stock"
4. Configurar el campo **Stock Mínimo**

### Ver Alertas

- **Dashboard**: Inventario > Operaciones > Dashboard Stock Crítico
- **Lista de Alertas**: Inventario > Configuración > Alertas de Stock > Alertas de Stock
- **Productos Críticos**: Inventario > Configuración > Alertas de Stock > Productos con Stock Crítico

### Estados de Alertas

- **Abierta**: Alerta activa que requiere atención
- **Resuelta**: Alerta cerrada (manual o automáticamente cuando el stock se normaliza)
- **Cancelada**: Alerta descartada

## Criterios de Aceptación

✅ Campo "stock mínimo" en `product.template`  
✅ Acción automática que genera notificación en `mail.message`  
✅ Vista de tablero con productos críticos agrupados por categoría  
✅ Pruebas que validan generación de alertas sin duplicados  

## Dependencias

- `base`
- `stock`
- `mail`
- `product`

## Autor

**Binaural**  
https://www.binaural.dev

## Licencia

LGPL-3

