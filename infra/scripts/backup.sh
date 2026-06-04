#!/bin/bash
export INFLUX_TOKEN=$(cat /home/florencia/sigegen/token.txt)
FECHA=$(date +%Y%m%d_%H%M%S)
DESTINO="/home/florencia/sigegen/backups/backup_$FECHA"

mkdir -p "$DESTINO"

influx backup "$DESTINO" --host http://localhost:8086

echo "Backup completado en: $DESTINO"
ls -lh "$DESTINO/"
