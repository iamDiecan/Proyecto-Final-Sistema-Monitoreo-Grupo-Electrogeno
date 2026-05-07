# Instalar InfluxDB 2.x (si no está instalado)
wget -q https://repos.influxdata.com/influxdata-archive_compat.key
echo '23a1c8836f0afc5edffe3dcb928bebd3dfb2ed0e' | sudo tee /etc/apt/trusted.gpg.d/influxdata.asc
echo "deb https://repos.influxdata.com/ubuntu jammy stable" | sudo tee /etc/apt/sources.list.d/influxdata.list
sudo apt update
sudo apt install influxdb2

# Iniciar servicio
sudo systemctl enable influxdb
sudo systemctl start influxdb

# Configurar inicial (crear org, bucket, token)
# Acceder a http://localhost:8086 y seguir wizard