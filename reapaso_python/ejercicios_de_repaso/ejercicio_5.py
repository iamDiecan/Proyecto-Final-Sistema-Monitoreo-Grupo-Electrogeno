print(f" ")
print(f"Tenés un CSV con 24 horas de lecturas del nodo_01.")
print(f"ejecicion 5")
print(f" ")
print(f"Leé el archivo con el módulo csv, calculá el promedio de voltaje y temperatura por hora, y detectá en qué hora ocurrió el valor máximo de temperatura.")
print(f" ")


import csv
import io

datos_csv = """hora,voltaje,temperatura,rpm
00:00,222,71,1500
02:00,219,73,1500
04:00,221,69,1500
06:00,218,75,1498
08:00,215,82,1500
10:00,213,87,1495
12:00,218,91,1490
14:00,220,89,1492
16:00,222,84,1498
18:00,225,78,1500
20:00,223,74,1500
22:00,221,72,1500"""

reader = csv.DictReader(io.StringIO(datos_csv))
filas = list(reader)

voltajes = [int(f["voltaje"]) for f in filas]
temperaturas = [int(f["temperatura"]) for f in filas]

prom_voltaje = sum(voltajes) / len(voltajes)
prom_temp = sum(temperaturas) / len(temperaturas)

fila_max = max(filas, key=lambda f: int(f["temperatura"]))
hora_max_temp = fila_max["hora"]
max_temp = fila_max["temperatura"]

print(f"Promedio voltaje: {prom_voltaje:.1f}V")
print(f"Promedio temperatura: {prom_temp:.1f}°C")
print(f"Temperatura máxima: {max_temp}°C a las {hora_max_temp}")