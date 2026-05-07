# Crear directorio de logs
sudo mkdir -p /var/log/sigegen
sudo chown -R $USER:$USER /var/log/sigegen

# Instalar dependencias Python
pip install paho-mqtt influxdb-client python-dotenv

# O mejor, crear un virtualenv
python3 -m venv venv
source venv/bin/activate
pip install paho-mqtt influxdb-client python-dotenv