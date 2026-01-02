# Módulos Contabilidad - Reglas de Descuento Automático

Módulo de Odoo 17 para implementar reglas de descuento automático en facturas según el tipo de cliente.

## Descripción

Este módulo permite configurar y aplicar automáticamente descuentos en facturas de clientes basándose en el tipo de cliente configurado en el partner. Los descuentos se aplican automáticamente al crear o validar facturas.

## Funcionalidades

### 1. Campo Tipo de Cliente en Partners

- Agrega un campo `customer_type` al modelo `res.partner`
- Tipos disponibles: Minorista, Mayorista, VIP, Sin Tipo
- Visible en la vista de formulario y lista de partners

### 2. Reglas de Descuento Configurables

- Modelo `account.discount.rule` para definir reglas de descuento
- Cada regla define:
  - Tipo de cliente objetivo
  - Porcentaje de descuento (0-100)
  - Fechas de validez (opcional)
  - Compañía (multi-compañía)
  - Estado activo/inactivo

### 3. Aplicación Automática de Descuentos

- Los descuentos se aplican automáticamente en las líneas de factura (`account.move.line`)
- Solo se aplica a facturas de clientes (`out_invoice`, `out_refund`)
- No sobrescribe descuentos manuales existentes
- Solo aplica a líneas de producto (no secciones o notas)

### 4. Vista de Configuración

- Menú accesible desde: **Contabilidad > Configuración > Reglas de Descuento**
- Vista de lista con filtros por tipo de cliente y estado
- Vista de formulario para crear y editar reglas

## Estructura del Módulo

```
modulos_contabilidad/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   ├── res_partner.py              # Extiende res.partner con customer_type
│   ├── account_discount_rule.py    # Modelo de reglas de descuento
│   ├── account_move.py             # Lógica de aplicación en facturas
│   └── account_move_line.py        # Hook en líneas de factura
├── views/
│   ├── res_partner_views.xml       # Campo customer_type en partner
│   ├── account_discount_rule_views.xml  # Vistas de reglas
│   └── account_move_views.xml      # Vista de factura extendida
├── security/
│   ├── ir.model.access.csv         # Permisos de acceso
│   └── security.xml                # Grupos de seguridad
├── data/
│   └── account_discount_rule_data.xml  # Datos iniciales (ejemplos)
└── tests/
    ├── __init__.py
    ├── test_res_partner.py         # Tests de partner
    ├── test_account_discount_rule.py  # Tests de reglas
    └── test_account_move_discount.py  # Tests de aplicación de descuentos
```

## Instalación

1. Asegúrate de que el módulo esté en `src/custom/modulos_contabilidad`
2. Reinicia el contenedor de Odoo: `./odoo restart`
3. Actualiza la lista de aplicaciones en Odoo
4. Busca "Módulos Contabilidad" en la lista de aplicaciones e instálalo

## Uso

### Configurar Tipo de Cliente en Partner

1. Abre un partner (Contacto)
2. En la pestaña de información comercial, encontrarás el campo "Tipo de Cliente"
3. Selecciona el tipo apropiado: Minorista, Mayorista, VIP o Sin Tipo

### Crear Regla de Descuento

1. Ve a **Contabilidad > Configuración > Reglas de Descuento**
2. Crea una nueva regla:
   - Nombre: Descripción de la regla (ej: "Descuento Mayorista 10%")
   - Tipo de Cliente: Selecciona el tipo (Minorista, Mayorista o VIP)
   - Porcentaje de Descuento: Ingresa el porcentaje (0-100)
   - (Opcional) Fecha Desde / Fecha Hasta: Define un período de validez
   - Activo: Marca para activar la regla

### Aplicación Automática

Una vez configurado:
1. Al crear una factura de cliente con un partner que tiene tipo definido
2. Al agregar líneas de producto a la factura
3. El descuento se aplicará automáticamente según la regla configurada

**Nota**: Si una línea ya tiene un descuento manual, el descuento automático no se aplicará para esa línea.

## Datos Iniciales

El módulo incluye reglas de ejemplo:
- **Minorista**: 5% de descuento
- **Mayorista**: 10% de descuento
- **VIP**: 15% de descuento

Puedes modificar o eliminar estas reglas según tus necesidades.

## Casos de Uso

### Caso 1: Cliente con Tipo Definido
- Partner con tipo "Mayorista"
- Regla configurada: Mayorista 10%
- Al crear factura, se aplica automáticamente 10% de descuento en todas las líneas

### Caso 2: Cliente Sin Tipo
- Partner con tipo "Sin Tipo" o sin tipo definido
- No se aplica ningún descuento automático

### Caso 3: Factura de Proveedor
- Facturas de proveedor (`in_invoice`) no aplican descuentos automáticos
- Solo facturas de clientes (`out_invoice`, `out_refund`)

### Caso 4: Regla Inactiva
- Si la regla está desactivada, no se aplica descuento
- Útil para deshabilitar temporalmente una regla sin eliminarla

## Pruebas

El módulo incluye pruebas unitarias que validan:

1. **Test de Partner**: Creación y actualización del campo customer_type
2. **Test de Reglas**: Validaciones, duplicados, porcentajes
3. **Test de Aplicación**: Aplicación automática en diferentes escenarios

Para ejecutar las pruebas, usa el framework de pruebas de Odoo.

## Dependencias

- `base`: Módulo base de Odoo
- `account`: Módulo de contabilidad de Odoo

## Versión

- **Odoo**: 17.0
- **Versión del módulo**: 17.0.1.0.0

## Autor

Binaural

## Licencia

LGPL-3

## Notas Técnicas

- El descuento se aplica en el campo `discount` de `account.move.line`
- La lógica de aplicación se ejecuta mediante hooks en `create` y `write` de `account.move.line`
- Las validaciones evitan reglas duplicadas para el mismo tipo de cliente en la misma compañía
- Soporta multi-compañía mediante el campo `company_id` en las reglas
