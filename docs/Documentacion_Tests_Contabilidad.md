# Documentación de Pruebas y Reportes QA para `modulos_contabilidad`

Esta guía detalla cómo ejecutar las pruebas automatizadas para el módulo `modulos_contabilidad` en Odoo 17 y cómo generar reportes de calidad (QA) en formato PDF.

## 1. Ejecución de Tests Estándar (Sin Reporte PDF)

Si solo deseas verificar que los tests pasan y ver los resultados en la consola (logs), no necesitas ningún script adicional. Puedes ejecutar el comando estándar de Odoo directamente.

### Comando

Desde la carpeta raíz de tu proyecto Docker (`leandro-docker-odoo`):

```bash
docker compose -f docker-compose.db.yml up -d && \
docker compose -f docker-compose.app.yml run --rm proj \
  odoo -i modulos_contabilidad \
       --test-enable \
       --stop-after-init \
       -d test_contabilidad_clean \
       --http-port=8099 \
       --test-tags=/modulos_contabilidad
```

### ¿Qué hace este comando?
*   `-i modulos_contabilidad`: Instala/Actualiza el módulo.
*   `--test-enable`: Habilita la ejecución de tests tras la instalación.
*   `--stop-after-init`: Detiene el servidor Odoo una vez terminados los tests (no se queda esperando conexiones).
*   `-d test_contabilidad_clean`: Usa una base de datos específica para pruebas (recomendado para no ensuciar la principal).
*   `--test-tags=/modulos_contabilidad`: Ejecuta **solo** los tests de este módulo específico.

---

## 2. Generación de Reporte QA Automático (Recomendado)

Hemos creado un script automatizado `qa.sh` que simplifica todo el proceso. Este script se encarga de:
1.  Actualizar el código de pruebas en el contenedor.
2.  Ejecutar los tests.
3.  **Descargar automáticamente el reporte PDF** a tu carpeta actual.

### Pasos para Ejecutar

Simplemente ejecuta el siguiente comando en tu terminal:

```bash
./qa.sh
```

### Resultado
Al finalizar, encontrarás un archivo llamado **`reporte_qa_mas_reciente.pdf`** en la carpeta raíz del proyecto. Este archivo contiene:
*   Resumen ejecutivo (Status Pass/Fail).
*   Estadísticas (Tiempo, número de tests).
*   **Lista detallada de todas las pruebas ejecutadas.**
*   Detalle de errores (si los hubiera).

*(Nota: Ya no es necesario ejecutar comandos de `docker cp` ni `docker exec` manualmente, el script lo hace por ti).*

---

## 3. Detalles Técnicos (Scripts Internos)
Si necesitas entender cómo funciona internamente, el proceso se compone de dos archivos:

1.  **`qa.sh` (Host)**: Script Bash que orquesta la operación. Copia archivos y extrae el reporte final.
2.  **`run_tests_with_report.py` (Contenedor)**: Script Python que se ejecuta *dentro* de Odoo.

### Explicación del Código Python (`run_tests_with_report.py`)

*   **`run_odoo_tests(...)`**: Usa `subprocess.Popen` para lanzar Odoo. Es equivalente a abrir una terminal y teclear el comando. Captura `stdout` y `stderr` en tiempo real.
*   **`parse_test_results(...)`**: Recorre línea por línea los logs capturados.
    *   Busca `Starting TestClass.test_method` para identificar cada prueba ejecutada.
    *   Busca `modulos_contabilidad: X tests Ys` para el resumen.
    *   Busca `FAIL:` o `ERROR:` para detectar problemas.
    *   Si encuentra un error, captura las líneas siguientes (traceback) para incluir el detalle en el reporte.
*   **`generate_pdf_report(...)`**:
    *   Crea un documento PDF tamaño Carta.
    *   Dibuja una tabla con estadísticas (Total, Fallos, Tiempo).
    *   **Lista detallada:** Incluye una sección nueva listando todas las pruebas que se ejecutaron (Clase -> Test).
    *   Si hubo errores, los imprime en rojo formateados como código.
    *   Si todo pasó, muestra un mensaje de éxito en verde.

---

## Resumen

| Acción | Comando Recomendado | Resultado |
| :--- | :--- | :--- |
| **Desarrollo Rápido** | `odoo ...` manualmente (Opción 1) | Feedback inmediato en consola. |
| **Entrega / QA** | `python3 run_tests_with_report.py` (Opción 2) | Archivo PDF profesional para documentación. |
