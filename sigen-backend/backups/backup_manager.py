# sigen-backend/backups/backup_manager.py
"""
Módulo de Backups Automáticos.
Realiza copias de seguridad de la base de datos SQLite y exporta 
datos recientes de InfluxDB si está configurado.
"""
import os
import shutil
import logging
from datetime import datetime
import glob
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import get_settings

logger = logging.getLogger("sigegen.backups")

class BackupManager:
    def __init__(self):
        self.settings = get_settings()
        self.backup_dir = self.settings.backup_path
        os.makedirs(self.backup_dir, exist_ok=True)
        self.scheduler = AsyncIOScheduler()
        
        # Backup diario a las 3 AM
        self.scheduler.add_job(
            self.run_backup,
            'cron',
            hour=3,
            minute=0,
            id='daily_backup'
        )

    def start(self):
        self.scheduler.start()
        logger.info(f"BackupManager iniciado. Directorio: {self.backup_dir}")

    def stop(self):
        self.scheduler.shutdown()

    async def run_backup(self):
        """Ejecuta el proceso completo de backup."""
        logger.info("Iniciando proceso de backup automático...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            self._backup_sqlite(timestamp)
            self._clean_old_backups()
            logger.info("Proceso de backup completado con éxito.")
            return True, f"Backup {timestamp} completado."
        except Exception as e:
            logger.error(f"Error durante el backup: {e}")
            return False, str(e)

    def _backup_sqlite(self, timestamp: str):
        """Copia de seguridad de los archivos SQLite."""
        # 1. Base de datos de telemetría (fallback)
        if os.path.exists(self.settings.sqlite_db_path):
            dest = os.path.join(self.backup_dir, f"telemetry_{timestamp}.db")
            shutil.copy2(self.settings.sqlite_db_path, dest)
            
        # 2. Base de datos de la aplicación (CRUD)
        if os.path.exists(self.settings.app_db_path):
            dest = os.path.join(self.backup_dir, f"app_{timestamp}.db")
            shutil.copy2(self.settings.app_db_path, dest)

    def _clean_old_backups(self):
        """Elimina backups anteriores a los días de retención."""
        retention_days = self.settings.backup_retention_days
        now = datetime.now()
        
        pattern = os.path.join(self.backup_dir, "*.db")
        for f in glob.glob(pattern):
            if os.path.isfile(f):
                mtime = datetime.fromtimestamp(os.path.getmtime(f))
                if (now - mtime).days > retention_days:
                    try:
                        os.remove(f)
                        logger.debug(f"Backup antiguo eliminado: {f}")
                    except OSError as e:
                        logger.error(f"Error eliminando backup {f}: {e}")

# Singleton
_backup_mgr = None

def get_backup_manager() -> BackupManager:
    global _backup_mgr
    if _backup_mgr is None:
        _backup_mgr = BackupManager()
    return _backup_mgr
