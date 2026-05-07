
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


