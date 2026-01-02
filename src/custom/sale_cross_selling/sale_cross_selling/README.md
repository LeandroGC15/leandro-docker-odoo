# Ventas - Reglas de Cross-Selling

## Descripción

Este módulo permite definir relaciones de cross-selling entre productos para sugerir automáticamente productos complementarios cuando se añaden productos a un pedido de venta.

## Características

### Modelo de Reglas de Cross-Selling
- **Producto Origen**: El producto que dispara la sugerencia
- **Producto Sugerido**: El producto que se sugiere como complementario
- **Relación Bidireccional**: Opción para que la sugerencia funcione en ambos sentidos
- **Secuencia**: Orden de prioridad para mostrar las sugerencias
- **Descripción**: Campo opcional para documentar la relación

### Integración con Pedidos de Venta
- Botón "Ver Sugerencias" en el formulario de pedido de venta
- Wizard interactivo para revisar y seleccionar productos complementarios
- Añadir productos sugeridos directamente al pedido con un clic

### Integración con Productos
- Pestaña "Cross-Selling" en el formulario de producto
- Botón estadístico para ver el número de reglas de cross-selling
- Vista rápida para crear/editar reglas desde el producto

## Instalación

1. Copiar el módulo a la carpeta de addons personalizados
2. Actualizar la lista de módulos
3. Buscar "Cross-Selling" e instalar

## Dependencias

- `base`
- `sale`
- `product`

## Configuración

### Acceso al menú de configuración

1. Ir a **Ventas > Configuración > Cross-Selling**
2. O ir a **Ventas > Productos > Reglas de Cross-Selling**

### Crear una regla de cross-selling

1. Hacer clic en "Crear"
2. Seleccionar el **Producto Origen** (el producto que el cliente está comprando)
3. Seleccionar el **Producto Sugerido** (el producto complementario)
4. Opcionalmente marcar **Bidireccional** si la relación funciona en ambos sentidos
5. Guardar

### Ejemplo de uso

- **Laptop** sugiere **Mouse**, **Teclado**, **Funda**
- **Cámara** sugiere **Tarjeta de memoria**, **Trípode**, **Funda**
- **Teléfono** sugiere **Funda protectora**, **Cargador inalámbrico**

## Uso en Pedidos de Venta

1. Crear o editar un pedido de venta
2. Añadir productos al pedido
3. Si existen productos sugeridos, hacer clic en el botón **"Ver Sugerencias"**
4. En el wizard, seleccionar los productos que se desean añadir
5. Hacer clic en **"Añadir Seleccionados al Pedido"**
6. Los productos se añadirán automáticamente al pedido

## Permisos

### Grupos de usuarios

- **Usuario / Cross-Selling**: Puede ver sugerencias en pedidos
- **Manager / Cross-Selling**: Puede crear, editar y eliminar reglas

### Acceso por rol

- **Vendedor**: Puede ver sugerencias activas y usar el wizard
- **Manager de Ventas**: Acceso completo a la configuración

## Pruebas

El módulo incluye pruebas unitarias que cubren:

- Creación de reglas de cross-selling
- Validaciones de unicidad y coherencia
- Obtención de sugerencias
- Funcionamiento del wizard
- Integración con pedidos de venta

Para ejecutar las pruebas:

```bash
odoo-bin -d database_name -i sale_cross_selling --test-enable --stop-after-init
```

## Autor

**Binaural**  
Website: https://www.binaural.dev

## Licencia

LGPL-3

