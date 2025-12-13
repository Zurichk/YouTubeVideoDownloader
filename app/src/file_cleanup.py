"""
Módulo para la limpieza automática de archivos descargados.
"""
import os
import time
import threading
import logging
from typing import Optional


logger = logging.getLogger(__name__)

# Constantes
AEP_CLEANUP_INTERVAL_SECONDS = 300  # 5 minutos
AEP_FILE_MAX_AGE_SECONDS = 3600  # 1 hora


class AEPFileCleanupService:
    """
    Servicio para limpiar archivos antiguos automáticamente.
    
    Attributes:
        download_path: Ruta del directorio de descargas.
        max_age_seconds: Edad máxima de los archivos en segundos.
        cleanup_interval: Intervalo entre limpiezas en segundos.
        _running: Estado del servicio.
        _thread: Hilo de ejecución del servicio.
    """
    
    def __init__(
        self,
        download_path: str,
        max_age_seconds: int = AEP_FILE_MAX_AGE_SECONDS,
        cleanup_interval: int = AEP_CLEANUP_INTERVAL_SECONDS
    ) -> None:
        """
        Inicializa el servicio de limpieza.
        
        Args:
            download_path: Ruta del directorio de descargas.
            max_age_seconds: Edad máxima de archivos antes de eliminar.
            cleanup_interval: Intervalo entre ejecuciones de limpieza.
        """
        self.download_path = download_path
        self.max_age_seconds = max_age_seconds
        self.cleanup_interval = cleanup_interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
    
    def start(self) -> None:
        """
        Inicia el servicio de limpieza en segundo plano.
        """
        if self._running:
            logger.warning("El servicio de limpieza ya está en ejecución")
            return
        
        self._running = True
        self._thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True
        )
        self._thread.start()
        logger.info(
            f"Servicio de limpieza iniciado. "
            f"Archivos se eliminarán después de {self.max_age_seconds}s"
        )
    
    def stop(self) -> None:
        """
        Detiene el servicio de limpieza.
        """
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Servicio de limpieza detenido")
    
    def _cleanup_loop(self) -> None:
        """
        Bucle principal del servicio de limpieza.
        """
        while self._running:
            try:
                self.cleanup_old_files()
            except Exception as e:
                logger.error(f"Error en limpieza automática: {str(e)}")
            
            # Esperar antes de la próxima limpieza
            time.sleep(self.cleanup_interval)
    
    def cleanup_old_files(self) -> int:
        """
        Elimina archivos más antiguos que max_age_seconds.
        
        Returns:
            Número de archivos eliminados.
        """
        if not os.path.exists(self.download_path):
            return 0
        
        current_time = time.time()
        deleted_count = 0
        
        try:
            for filename in os.listdir(self.download_path):
                filepath = os.path.join(self.download_path, filename)
                
                # Solo procesar archivos, no directorios
                if not os.path.isfile(filepath):
                    continue
                
                # Obtener tiempo de modificación del archivo
                file_age = current_time - os.path.getmtime(filepath)
                
                # Eliminar si es más antiguo que max_age_seconds
                if file_age > self.max_age_seconds:
                    try:
                        os.remove(filepath)
                        deleted_count += 1
                        logger.info(
                            f"Archivo eliminado: {filename} "
                            f"(edad: {int(file_age)}s)"
                        )
                    except OSError as e:
                        logger.error(
                            f"Error al eliminar {filename}: {str(e)}"
                        )
            
            if deleted_count > 0:
                logger.info(
                    f"Limpieza completada: {deleted_count} archivo(s) eliminado(s)"
                )
        
        except Exception as e:
            logger.error(f"Error durante la limpieza: {str(e)}")
        
        return deleted_count
    
    def get_directory_size(self) -> int:
        """
        Obtiene el tamaño total del directorio de descargas.
        
        Returns:
            Tamaño en bytes.
        """
        total_size = 0
        
        if not os.path.exists(self.download_path):
            return 0
        
        try:
            for filename in os.listdir(self.download_path):
                filepath = os.path.join(self.download_path, filename)
                if os.path.isfile(filepath):
                    total_size += os.path.getsize(filepath)
        except Exception as e:
            logger.error(f"Error al calcular tamaño del directorio: {str(e)}")
        
        return total_size
    
    def get_file_count(self) -> int:
        """
        Obtiene el número de archivos en el directorio.
        
        Returns:
            Número de archivos.
        """
        if not os.path.exists(self.download_path):
            return 0
        
        try:
            return len([
                f for f in os.listdir(self.download_path)
                if os.path.isfile(os.path.join(self.download_path, f))
            ])
        except Exception as e:
            logger.error(f"Error al contar archivos: {str(e)}")
            return 0
