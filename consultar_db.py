"""
Consultas a la base de datos SQLite de Sigegen
"""

import sqlite3
import pandas as pd
from tabulate import tabulate
import sys

# Forzar codificación UTF-8 para stdout en Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def consultar():
    conn = sqlite3.connect('sigegen.db')
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("📊 SIGEGEN - ESTADÍSTICAS DE LOS 30 GENERADORES")
    print("="*80)
    
    # 1. Total de lecturas por nodo
    print("\n📈 TOTAL DE LECTURAS POR NODO:")
    cursor.execute("""
        SELECT nodo_id, COUNT(*) as lecturas 
        FROM lecturas 
        GROUP BY nodo_id 
        ORDER BY nodo_id
    """)
    resultados = cursor.fetchall()
    for nodo, lecturas in resultados:
        print(f"  {nodo}: {lecturas} lecturas")
    
    # 2. Nivel de alerta promedio por zona
    print("\n📊 NIVEL DE ALERTA PROMEDIO POR ZONA:")
    cursor.execute("""
        SELECT zona, 
               ROUND(AVG(alerta_difusa_nivel), 1) as promedio_alerta,
               COUNT(*) as lecturas,
               SUM(CASE WHEN estado='falla' THEN 1 ELSE 0 END) as fallas
        FROM lecturas 
        GROUP BY zona
    """)
    resultados = cursor.fetchall()
    for zona, promedio, lecturas, fallas in resultados:
        nivel_icono = "🟢" if promedio < 20 else "🟡" if promedio < 40 else "🔶" if promedio < 60 else "🔴"
        print(f"  {nivel_icono} {zona:8} | Promedio: {promedio:5.1f} | Lecturas: {lecturas:3} | Fallas: {fallas}")
    
    # 3. Top 10 nodos con mayor nivel de alerta
    print("\n⚠️ TOP 10 NODOS CON MAYOR NIVEL DE ALERTA:")
    cursor.execute("""
        SELECT nodo_id, 
               alerta_difusa_nivel, 
               alerta_difusa_categoria,
               temp_motor_c, 
               voltaje_v, 
               combustible_pct,
               estado
        FROM lecturas 
        ORDER BY alerta_difusa_nivel DESC 
        LIMIT 10
    """)
    resultados = cursor.fetchall()
    print(f"{'Nodo':10} {'Nivel':>6} {'Categoría':12} {'Temp':>6} {'Volt':>6} {'Comb':>6} {'Estado':>8}")
    print("-" * 65)
    for nodo, nivel, categoria, temp, volt, comb, estado in resultados:
        icono = "🔴" if nivel > 70 else "🔶" if nivel > 50 else "⚠️"
        print(f"{icono} {nodo:8} {nivel:>6.1f} {categoria:12} {temp:>5.0f}°C {volt:>5.0f}V {comb:>5.0f}% {estado:>8}")
    
    # 4. Distribución de estados
    print("\n📊 DISTRIBUCIÓN DE ESTADOS:")
    cursor.execute("""
        SELECT estado, COUNT(*) as cantidad 
        FROM lecturas 
        GROUP BY estado
    """)
    resultados = cursor.fetchall()
    for estado, cantidad in resultados:
        icono = "✅" if estado == "normal" else "⚠️" if estado == "alerta" else "🔴"
        print(f"  {icono} {estado}: {cantidad} lecturas ({cantidad/30:.1f}%)")
    
    # 5. Resumen general
    cursor.execute("SELECT COUNT(DISTINCT nodo_id) FROM lecturas")
    total_nodos = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(alerta_difusa_nivel), MAX(alerta_difusa_nivel) FROM lecturas")
    promedio_global, max_alerta = cursor.fetchone()
    
    print("\n" + "="*80)
    print("📋 RESUMEN GENERAL:")
    print(f"  • Total de nodos únicos: {total_nodos}/30")
    print(f"  • Nivel de alerta promedio global: {promedio_global:.1f}")
    print(f"  • Nivel máximo de alerta registrado: {max_alerta:.1f}")
    print("="*80)
    
    conn.close()

if __name__ == "__main__":
    consultar()
    input("\nPresiona Enter para salir...")