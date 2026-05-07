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

