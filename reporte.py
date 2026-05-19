"""
Generador de reporte HTML con resultados de Sigegen
"""

import sqlite3
import datetime

def generar_reporte():
    conn = sqlite3.connect('sigegen.db')
    cursor = conn.cursor()
    
    # Obtener datos
    cursor.execute("""
        SELECT zona, AVG(alerta_difusa_nivel) as promedio, COUNT(*) as lecturas
        FROM lecturas 
        GROUP BY zona
    """)
    zonas = cursor.fetchall()
    
    cursor.execute("""
        SELECT nodo_id, zona, alerta_difusa_nivel, alerta_difusa_categoria,
               temp_motor_c, voltaje_v, combustible_pct
        FROM lecturas 
        WHERE alerta_difusa_nivel > 50
        ORDER BY alerta_difusa_nivel DESC
    """)
    criticos = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(DISTINCT nodo_id), AVG(alerta_difusa_nivel), MAX(alerta_difusa_nivel) FROM lecturas")
    total_nodos, promedio_global, max_alerta = cursor.fetchone()
    
    # Generar HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sigegen - Reporte de Generadores</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: auto; background: white; padding: 20px; border-radius: 10px; }}
            h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
            .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
            .card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; flex: 1; text-align: center; }}
            .card.critico {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
            .card.normal {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #4CAF50; color: white; }}
            tr:hover {{ background: #f5f5f5; }}
            .critico {{ color: #f5576c; font-weight: bold; }}
            .alerta {{ color: #ff9800; font-weight: bold; }}
            .normal {{ color: #4CAF50; }}
            .footer {{ text-align: center; margin-top: 30px; padding: 20px; color: #666; border-top: 1px solid #ddd; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 SIGEGEN - Monitoreo de Generadores</h1>
            <p>Provincia de Formosa - {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            
            <div class="summary">
                <div class="card">
                    <h2>{total_nodos}</h2>
                    <p>Generadores Monitoreados</p>
                </div>
                <div class="card normal">
                    <h2>{promedio_global:.1f}</h2>
                    <p>Nivel de Alerta Promedio</p>
                </div>
                <div class="card critico">
                    <h2>{max_alerta:.1f}</h2>
                    <p>Nivel Máximo de Alerta</p>
                </div>
            </div>
            
            <h2>📊 Nivel de Alerta por Zona</h2>
            <table>
                <tr><th>Zona</th><th>Nivel Promedio</th><th>Lecturas</th><th>Estado</th></tr>
    """
    
    for zona, promedio, lecturas in zonas:
        estado = "🟢 Normal" if promedio < 20 else "🟡 Precaución" if promedio < 40 else "🔶 Alerta"
        html += f"<tr><td>{zona}</td><td>{promedio:.1f}</td><td>{lecturas}</td><td>{estado}</td></tr>"
    
    html += """
            </table>
            
            <h2>⚠️ Nodos con Problemas (Nivel > 50)</h2>
    """
    
    if criticos:
        html += """
            <table>
                <tr><th>Nodo</th><th>Zona</th><th>Nivel</th><th>Categoría</th><th>Temperatura</th><th>Voltaje</th><th>Combustible</th></tr>
        """
        for nodo, zona, nivel, categoria, temp, volt, comb in criticos:
            html += f"<tr class='critico'><td>{nodo}</td><td>{zona}</td><td>{nivel:.1f}</td><td>{categoria}</td><td>{temp:.0f}°C</td><td>{volt:.0f}V</td><td>{comb:.0f}%</td></tr>"
        html += "</table>"
    else:
        html += "<p>✅ No hay nodos con problemas críticos</p>"
    
    html += """
            <div class="footer">
                <p>Sistema de Monitoreo Sigegen - Alerta Difusa</p>
                <p>Reporte generado automáticamente</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Guardar archivo
    with open('reporte_sigegen.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("✅ Reporte generado: reporte_sigegen.html")
    conn.close()

if __name__ == "__main__":
    generar_reporte()