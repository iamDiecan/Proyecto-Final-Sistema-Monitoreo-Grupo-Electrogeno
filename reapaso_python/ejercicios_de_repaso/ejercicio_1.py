#El generador del nodo 01 manda 10 lecturas de temperatura (°C) durante la ultima hora

#Calcula el promedio, el maxiomo y el minimo. Luego contá cuántas lecturas superaron 85°C

print(f"ejecicion 1")
print(" ")
print(f"El generador del nodo 01 manda 10 lecturas de temperatura (°C) durante la ultima hora. Calcula el promedio, el maxiomo y el minimo. Luego contá cuántas lecturas superaron 85°C")
print(" ")
lecturas = [72, 78, 85, 91, 88, 76, 83, 90, 69, 74]

# Calculá promedio, máximo y mínimo
promedio = sum(lecturas)/len(lecturas)
maximo = max(lecturas)
minimo =  min(lecturas)

# Contá cuántas superan 85°C
alertas = len([0 for x in lecturas if x > 85])

print(f"Promedio: {promedio:.1f}°C")
print(f"Máximo: {maximo}°C  |  Mínimo: {minimo}°C")
print(f"Lecturas sobre 85°C: {alertas}")


print(f" ")
print(f" ")
print(f"ejecicion 2")
print(f" ")
print(f"Cada generador manda sus datos como un diccionario Python. Acceer a los valores del nodo, calculá si el voltaje está dentro del rango normal (entre 210V y 230V) e imprimí un resumen del estado.")
print(f" ")
print(f" ")
#Cada generador manda sus datos como un diccionario Python.

#Acceer a los valores del nodo, calculá si el voltaje está dentro del rango normal (entre 210V y 230V) e imprimí un resumen del estado.

nodo = {
    "id": "nodo_03",
    "zona": "Capital",
    "voltaje": 204,
    "temperatura": 78,
    "rpm": 1500,
    "combustible_pct": 62
}

nodo = { "id": "nodo_03", "zona": "Capital", "voltaje": 204, "temperatura": 78, "rpm": 1500, "combustible_pct": 62 }

# Accedé a los valores
nodo_id = nodo["id"]
zona = nodo["zona"]
voltaje = nodo["voltaje"]

voltaje_ok = 210 <= voltaje <= 230

# Imprimí el resumen
print(f"Nodo: {nodo_id} | Zona: {zona}")
print(f"Voltaje: {voltaje}V — {'OK' if voltaje_ok else 'ALERTA'}")
print(f"Temperatura: {nodo['temperatura']}°C")
print(f"Combustible: {nodo['combustible_pct']}%")


print(f" ")
print(f" ")
print(f"ejecicion 3")
print(f" ")
print(f"Tenés una lista con los datos actuales de 5 nodos de SIGEGEN. Filtrá los nodos que están en alerta (voltaje fuera de rango O temperatura mayor a 85°C). Mostrálos con su id, zona y el motivo de la alerta. ")
print(f" ")

nodos = [ {"id":"nodo_01","zona":"Norte","voltaje":225,"temperatura":72},
          {"id":"nodo_02","zona":"Sur","voltaje":198,"temperatura":68}, 
          {"id":"nodo_03","zona":"Este","voltaje":220,"temperatura":91}, 
          {"id":"nodo_04","zona":"Oeste","voltaje":215,"temperatura":80}, 
          {"id":"nodo_05","zona":"Capital","voltaje":232,"temperatura":88}
]


alertas = []

for nodo in nodos:
    motivos = []
    if not (210 <= nodo["voltaje"] <= 230):
        motivos.append(f"voltaje {nodo['voltaje']}V")
    if nodo["temperatura"] > 85:
        motivos.append(f"temp {nodo['temperatura']}°C")
    if motivos:
        alertas.append({"id": nodo["id"], "zona": nodo["zona"], "motivos": motivos})

print(f"Nodos en alerta: {len(alertas)}")
for a in alertas:
    print(f"  {a['id']} ({a['zona']}): {', '.join(a['motivos'])}")


print(f" ")
print(f"El backend de SIGEGEN debe guardar cada lectura en un archivo de log.")
print(f"ejecicion 4")
print(f" ")
print(f"Escribí una función guardar_lectura() que reciba un diccionario de nodo y lo agregue al archivo sigegen_log.txt con fecha y hora. Luego leé el archivo y mostrá las últimas 3 líneas.")
print(f" ")

import datetime

_log_simulado = []

def guardar_lectura(nodo):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"{timestamp} | {nodo['id']} | {nodo['zona']} | {nodo['voltaje']}V | {nodo['temperatura']}°C"
    _log_simulado.append(linea)

lecturas = [
    {"id":"nodo_01","zona":"Norte","voltaje":225,"temperatura":72},
    {"id":"nodo_02","zona":"Sur","voltaje":198,"temperatura":91},
    {"id":"nodo_03","zona":"Capital","voltaje":220,"temperatura":78},
]

for lectura in lecturas:
    guardar_lectura(lectura)

print(f"Log guardado ({len(_log_simulado)} entradas). Últimas 3:")
for l in _log_simulado[-3:]:
    print(l)

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