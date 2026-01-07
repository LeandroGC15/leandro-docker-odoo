
import subprocess
import sys
import re
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

def run_odoo_tests(db_name, module_name, http_port):
    """Ejecuta los tests de Odoo y captura la salida."""
    cmd = [
        "odoo",
        "-i", module_name,
        "--test-enable",
        "--stop-after-init",
        "-d", db_name,
        "--http-port", str(http_port),
        "--test-tags", f"/{module_name}"
    ]
    
    print(f"Ejecutando tests para {module_name} en {db_name}...")
    
    # Capturamos stdout y stderr combinados
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    output_lines = []
    # Leemos línea por línea para mostrar progreso y guardar
    for line in process.stdout:
        sys.stdout.write(line) # Mostrar en consola en tiempo real
        output_lines.append(line)
        
    process.wait()
    return output_lines, process.returncode

def parse_test_results(output_lines, module_name):
    """Analiza los logs para extraer estadísticas y lista de tests."""
    stats = {
        'total_tests': 0,
        'failures': 0,
        'errors': 0,
        'time': '0.00s',
        'details': [],
        'module_status': 'Unknown',
        'executed_tests': []  # Lista para almacenar tests ejecutados
    }
    
    # Regex patterns - Dinámicos basados en el nombre del módulo
    summary_pattern = re.compile(rf"{module_name}: (\d+) tests (\d+\.\d+)s")
    test_start_pattern = re.compile(r"Starting (Test\w+)\.(test_\w+)")
    module_load_fail = re.compile(rf"Module {module_name}: (\d+) failures, (\d+) errors")
    
    capture_error_detail = False
    current_error = []

    for line in output_lines:
        line = line.strip()
        
        # Detectar inicio de tests individuales
        match_test = test_start_pattern.search(line)
        if match_test:
            test_class = match_test.group(1)
            test_name = match_test.group(2)
            stats['executed_tests'].append(f"{test_class} -> {test_name}")
            
        # Detectar resumen final
        match_summary = summary_pattern.search(line)
        if match_summary:
            stats['total_tests'] = int(match_summary.group(1))
            stats['time'] = f"{match_summary.group(2)}s"
            
        # Detectar conteo de fallos en carga
        match_load = module_load_fail.search(line)
        if match_load:
            stats['failures'] = int(match_load.group(1))
            stats['errors'] = int(match_load.group(2))
            if stats['failures'] == 0 and stats['errors'] == 0:
                stats['module_status'] = 'PASSED'
            else:
                stats['module_status'] = 'FAILED'

        # Detectar detalles de fallos
        if "FAIL:" in line or "ERROR:" in line:
            if current_error:
                stats['details'].append("\n".join(current_error))
                current_error = []
            capture_error_detail = True
            current_error.append(line)
        elif capture_error_detail:
            # Capturar líneas subsiguientes del traceback hasta encontrar fecha
            if re.match(r"\d{4}-\d{2}-\d{2}", line): 
                capture_error_detail = False
                if current_error:
                    stats['details'].append("\n".join(current_error))
                    current_error = []
            else:
                current_error.append(line)

    # Si terminamos y quedó algo pendiente
    if current_error:
        stats['details'].append("\n".join(current_error))

    # Si no detectamos status explícito pero hubo tests
    if stats['module_status'] == 'Unknown' and stats['total_tests'] > 0:
        if stats['failures'] > 0 or stats['errors'] > 0:
            stats['module_status'] = 'FAILED'
        else:
            stats['module_status'] = 'PASSED'
            
    return stats

def generate_pdf_report(filename, stats, module_name, module_title):
    """Genera el reporte PDF."""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # --- Título ---
    title_style = styles['Title']
    elements.append(Paragraph("Reporte de Ejecución de Tests QA", title_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # --- Información General ---
    info_style = styles['Normal']
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elements.append(Paragraph(f"<b>Fecha:</b> {timestamp}", info_style))
    elements.append(Paragraph(f"<b>Módulo:</b> {module_title}", info_style))
    elements.append(Paragraph(f"<b>Nombre Técnico:</b> {module_name}", info_style))
    elements.append(Paragraph(f"<b>Estado Global:</b> {stats['module_status']}", info_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # --- Tabla de Resumen ---
    data = [
        ['Métrica', 'Valor'],
        ['Total Tests Ejecutados', str(stats['total_tests'])],
        ['Fallos (Failures)', str(stats['failures'])],
        ['Errores (Errors)', str(stats['errors'])],
        ['Tiempo de Ejecución', stats['time']]
    ]
    
    # Estilo condicional para la tabla
    table = Table(data, colWidths=[2.5*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    if stats['failures'] > 0 or stats['errors'] > 0:
        table.setStyle(TableStyle([
             ('TEXTCOLOR', (1, 2), (1, 3), colors.red),
             ('FONTNAME', (1, 2), (1, 3), 'Helvetica-Bold'),
        ]))
        
    elements.append(table)
    elements.append(Spacer(1, 0.5*inch))

    # --- Lista de Pruebas Ejecutadas ---
    if stats['executed_tests']:
        elements.append(Paragraph("<b>Pruebas Realizadas:</b>", styles['Heading2']))
        elements.append(Paragraph("A continuación se listan los casos de prueba verificados:", styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
        
        test_list_style = ParagraphStyle('TestList', parent=styles['Normal'], leftIndent=20, bulletIndent=10)
        
        for test_name in stats['executed_tests']:
            elements.append(Paragraph(f"• {test_name}", test_list_style))
            
        elements.append(Spacer(1, 0.3*inch))
    
    # --- Detalles de Errores ---
    if stats['details']:
        elements.append(Paragraph("<b>Detalles de Fallos/Errores:</b>", styles['Heading2']))
        error_style = ParagraphStyle('ErrorStyle', parent=styles['Code'], textColor=colors.red, fontSize=8)
        
        for detail in stats['details']:
            # Limpiar un poco el texto para HTML
            detail_html = detail.replace('\n', '<br/>').replace(' ', '&nbsp;')
            elements.append(Paragraph(detail_html, error_style))
            elements.append(Spacer(1, 0.1*inch))
    else:
        elements.append(Paragraph("<i>No se detectaron errores ni fallos. ¡Excelente!</i>", styles['Normal']))

    # --- Pie de página ---
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("Generado automáticamente por Odoo Test Runner", 
                              ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey)))

    doc.build(elements)
    print(f"\nReporte PDF generado exitosamente: {filename}")

if __name__ == "__main__":
    MODULE = "hr_performance_review"
    MODULE_TITLE = "RRHH - Evaluaciones de Desempeño"
    DB = "test_rrhh_clean"
    PORT = 8098  # Puerto diferente para evitar conflictos
    
    # 1. Ejecutar Tests
    logs, return_code = run_odoo_tests(DB, MODULE, PORT)
    
    # 2. Analizar Resultados
    statistics = parse_test_results(logs, MODULE)
    
    # 3. Generar PDF
    pdf_filename = f"/home/odoo/qa_report_{MODULE}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    try:
        generate_pdf_report(pdf_filename, statistics, MODULE, MODULE_TITLE)
    except Exception as e:
        print(f"Error al generar PDF: {e}")
