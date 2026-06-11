# SIGEGEN v3.0 - Plataforma IoT de Monitoreo

SIGEGEN (Sistema Inteligente de Gestión de Grupos Electrógenos) es una plataforma IoT diseñada para el monitoreo remoto, mantenimiento predictivo y gestión inteligente de generadores eléctricos en la Provincia de Formosa.

## Novedades en v3.0

Esta nueva versión transforma el sistema de un simple monitor a una plataforma de gestión inteligente integral:

- **Motor de Inferencia Difusa (Fuzzy Logic v3)**: Analiza múltiples variables concurrentes para detectar anomalías con precisión.
- **Gemelo Digital y Health Score**: Visualización en tiempo real del estado físico y salud general del equipo.
- **Centro de Alertas y Watchdog**: Monitor activo de conectividad (nodo offline) y motor determinista de evaluación de riesgo para generación de alarmas.
- **Mantenimiento Predictivo**: Estimación de vida útil, control de horas de servicio y planificación de intervenciones.
- **Arquitectura Robusta**: Soporte dual database (InfluxDB para telemetría + SQLite/SQLModel para gestión de entidades y usuarios), rutinas de backup automatizadas y autenticación con JWT.
- **Dashboard Jerárquico**: Rediseño completo de la UI con Glassmorphism, incluyendo KPIs gerenciales y un mapa geográfico interactivo de los nodos.

## Arquitectura

- **Edge**: ESP32 (Sensores) → Mosquitto Local → Orange Pi Zero 3 (Buffer Offline y Sincronización) → VPN NetBird.
- **Core Backend**: FastAPI, SQLModel (SQLite), InfluxDB, APScheduler.
- **Core Frontend**: Reflex (React/Python), Leaflet, CSS Custom Properties (Glassmorphism).

## Instalación y Despliegue Local

### 1. Requisitos Previos
- Python 3.9+
- InfluxDB v2 en ejecución local (puerto 8086).
- Entorno virtual (recomendado).

### 2. Backend
```bash
cd sigen-backend
pip install -r requirements.txt
python scripts/init_db.py  # Inicializa SQLite (crea admin y 30 nodos mock)
uvicorn main:app --reload --port 8001
```

### 3. Frontend
```bash
cd sigen-frontend
pip install reflex
reflex init
reflex run
```

### 4. Simulador (Generación de Datos)
Para simular el comportamiento de la red provincial completa:
```bash
cd sigen-backend
python simular_30_nodos.py
```

## Credenciales por Defecto
- **Usuario:** `admin`
- **Contraseña:** `admin123`

---
*Desarrollado para la gestión de infraestructura crítica provincial.*
