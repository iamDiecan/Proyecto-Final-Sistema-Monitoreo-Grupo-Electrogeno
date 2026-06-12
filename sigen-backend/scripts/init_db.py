# sigen-backend/scripts/init_db.py
"""
Script de inicialización de la Base de Datos SIGEGEN v3.0.
Crea las tablas y puebla los datos iniciales de los nodos.
"""
import sys
import os
import logging
from datetime import datetime

# Añadir el path del backend para poder importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import init_db, get_session, NodeConfig, User, UserRole
from auth.service import get_password_hash
from sqlmodel import Session, select
from config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("init_db")

def seed_users(session: Session):
    """Crea el usuario administrador por defecto si no existe."""
    statement = select(User).where(User.username == "admin")
    admin = session.exec(statement).first()
    
    if not admin:
        new_admin = User(
            username="admin",
            password_hash=get_password_hash("admin123"),
            full_name="Administrador del Sistema",
            email="admin@sigegen.gob.ar",
            role=UserRole.ADMIN.value
        )
        session.add(new_admin)
        session.commit()
        logger.info("✅ Usuario 'admin' creado (password: admin123)")
    else:
        logger.info("ℹ️ Usuario 'admin' ya existe.")

def seed_nodes(session: Session):
    """Crea la configuración geográfica de los 30 nodos del simulador."""
    
    nodos_data = [
        # Capital
        {"id": "nodo_01", "loc": "Formosa Capital", "z": "capital", "lat": -26.18, "lon": -58.18},
        {"id": "nodo_02", "loc": "San Francisco de Laishi", "z": "capital", "lat": -26.24, "lon": -58.60},
        {"id": "nodo_03", "loc": "Villa del Carmen", "z": "capital", "lat": -26.15, "lon": -58.20},
        {"id": "nodo_04", "loc": "Gran Guardia", "z": "capital", "lat": -25.85, "lon": -58.80},
        {"id": "nodo_05", "loc": "Mariano Boedo", "z": "capital", "lat": -26.18, "lon": -58.35},
        {"id": "nodo_06", "loc": "Colonia Pastoril", "z": "capital", "lat": -25.75, "lon": -58.38},
        
        # Norte
        {"id": "nodo_07", "loc": "Clorinda", "z": "norte", "lat": -25.28, "lon": -57.72},
        {"id": "nodo_08", "loc": "Pilcomayo", "z": "norte", "lat": -25.28, "lon": -57.65},
        {"id": "nodo_09", "loc": "Laguna Blanca", "z": "norte", "lat": -25.13, "lon": -58.25},
        {"id": "nodo_10", "loc": "Palo Santo", "z": "norte", "lat": -25.55, "lon": -59.33},
        {"id": "nodo_11", "loc": "Comandante Fontana", "z": "norte", "lat": -25.33, "lon": -59.68},
        {"id": "nodo_12", "loc": "El Colorado", "z": "norte", "lat": -26.30, "lon": -59.37},
        {"id": "nodo_13", "loc": "Ibarreta", "z": "norte", "lat": -25.22, "lon": -59.85},
        {"id": "nodo_14", "loc": "Estanislao del Campo", "z": "norte", "lat": -25.05, "lon": -60.10},
        {"id": "nodo_15", "loc": "Pirané", "z": "norte", "lat": -25.73, "lon": -59.10},
        {"id": "nodo_16", "loc": "Misión Tacaaglé", "z": "norte", "lat": -24.95, "lon": -58.75},
        
        # Sur (Oeste/Mixto)
        {"id": "nodo_17", "loc": "Laguna Yema", "z": "sur", "lat": -24.25, "lon": -61.25},
        {"id": "nodo_18", "loc": "Las Lomitas", "z": "sur", "lat": -24.70, "lon": -60.58},
        {"id": "nodo_19", "loc": "Pozo del Tigre", "z": "sur", "lat": -24.90, "lon": -60.32},
        {"id": "nodo_20", "loc": "Villa General Güemes", "z": "sur", "lat": -24.75, "lon": -59.50},
        {"id": "nodo_21", "loc": "El Espinillo", "z": "sur", "lat": -24.98, "lon": -58.55},
        {"id": "nodo_22", "loc": "Buena Vista", "z": "sur", "lat": -25.05, "lon": -58.42},
        {"id": "nodo_23", "loc": "Subteniente Perín", "z": "sur", "lat": -25.80, "lon": -59.95},
        {"id": "nodo_24", "loc": "San Martín II", "z": "sur", "lat": -24.53, "lon": -59.60},
        {"id": "nodo_25", "loc": "Bartolomé de las Casas", "z": "sur", "lat": -25.20, "lon": -59.50},
        {"id": "nodo_26", "loc": "Posta Cambio A Zalazar", "z": "sur", "lat": -24.38, "lon": -60.15},
        {"id": "nodo_27", "loc": "Colonia Cano", "z": "sur", "lat": -26.35, "lon": -58.28},
        {"id": "nodo_28", "loc": "Portón Negro", "z": "sur", "lat": -25.08, "lon": -58.62},
        {"id": "nodo_29", "loc": "Ingeniero Guillermo N. Juárez", "z": "sur", "lat": -23.90, "lon": -61.85},
        {"id": "nodo_30", "loc": "Frontera", "z": "sur", "lat": -23.85, "lon": -62.00},
    ]

    count = 0
    for data in nodos_data:
        statement = select(NodeConfig).where(NodeConfig.node_id == data["id"])
        existing = session.exec(statement).first()
        if not existing:
            nodo = NodeConfig(
                node_id=data["id"],
                nombre=f"Generador {data['loc']}",
                localidad=data["loc"],
                zona=data["z"],
                lat=data["lat"],
                lon=data["lon"],
                capacidad_kw=50.0,
                fecha_instalacion=datetime.utcnow()
            )
            session.add(nodo)
            count += 1
            
    if count > 0:
        session.commit()
        logger.info(f"✅ Se inicializaron {count} nodos geográficos.")
    else:
        logger.info("ℹ️ Nodos ya estaban inicializados.")

def main():
    logger.info("Iniciando setup de la base de datos...")
    
    # Crea tablas
    init_db()
    
    # Obtiene sesión
    from models.database import _get_engine
    engine = _get_engine()
    with Session(engine) as session:
        seed_users(session)
        seed_nodes(session)
        
    logger.info("✨ Setup completado con éxito.")

if __name__ == "__main__":
    main()
