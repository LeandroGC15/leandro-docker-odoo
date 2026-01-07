#!/bin/bash

# Este script automatiza la ejecución de tests QA para el módulo Punto de Venta - Programa de Fidelización
# y la obtención del reporte PDF

CONTAINER_NAME="proj"
REMOTE_SCRIPT="/home/odoo/run_tests_pos_loyalty_with_report.py"
LOCAL_SCRIPT="./run_tests_pos_loyalty_with_report.py"
FINAL_REPORT_NAME="reporte_qa_pos_loyalty_mas_reciente.pdf"
MODULE_NAME="pos_loyalty_program"

echo "=== Iniciando Proceso de QA para Punto de Venta - Programa de Fidelización ==="

# 1. Asegurar que el script Python en el contenedor sea la última versión
echo "1. Actualizando script de pruebas en el contenedor..."
docker cp $LOCAL_SCRIPT $CONTAINER_NAME:$REMOTE_SCRIPT

# 2. Ejecutar los tests (capturando la salida para ver errores si los hay)
echo "2. Ejecutando tests (esto puede tomar unos segundos)..."
docker exec -u root $CONTAINER_NAME python3 $REMOTE_SCRIPT

# 3. Detectar el archivo PDF más reciente generado en el contenedor
echo "3. Recuperando reporte PDF..."
# Buscamos el archivo pdf más reciente en /home/odoo/ creado por el script
LATEST_PDF=$(docker exec -u root $CONTAINER_NAME sh -c "ls -t /home/odoo/qa_report_${MODULE_NAME}_*.pdf | head -n 1")

if [ -z "$LATEST_PDF" ]; then
    echo "❌ Error: No se encontró ningún reporte PDF generado en el contenedor."
    exit 1
fi

# 4. Copiar el archivo al host
docker cp $CONTAINER_NAME:"$LATEST_PDF" "./$FINAL_REPORT_NAME"

if [ $? -eq 0 ]; then
    echo "✅ Éxito! El reporte se ha guardado como: $FINAL_REPORT_NAME"
    echo "   (Origen: $LATEST_PDF)"
else
    echo "❌ Error al copiar el archivo desde el contenedor."
fi
