"""
Módulo para descargar videos de YouTube utilizando yt-dlp.
"""
import os
import logging
import json
import time
from typing import Dict, Optional
import yt_dlp


# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constantes
AEP_MAX_FILESIZE_MB = 500
AEP_DEFAULT_DOWNLOAD_PATH = os.path.join(os.getcwd(), 'downloads')


class AEPYouTubeDownloader:
    """
    Clase para gestionar la descarga de videos de YouTube.
    
    Attributes:
        download_path: Ruta donde se guardarán los videos descargados.
    """
    
    def __init__(self, download_path: str = AEP_DEFAULT_DOWNLOAD_PATH) -> None:
        """
        Inicializa el descargador de YouTube.
        
        Args:
            download_path: Ruta del directorio de descargas.
        """
        self.download_path = download_path
        self._ensure_download_directory()
    
    def _ensure_download_directory(self) -> None:
        """
        Asegura que el directorio de descargas exista.
        """
        os.makedirs(self.download_path, exist_ok=True)
        if not os.path.exists(self.download_path):
            logger.info(f"Directorio de descargas creado: {self.download_path}")
    
    def get_video_info(self, url: str) -> Optional[Dict]:
        """
        Obtiene información del video sin descargarlo.
        
        Args:
            url: URL del video de YouTube.
        
        Returns:
            Diccionario con información del video o None si hay error.
        """
        try:
            cookies_path = os.path.join(os.path.dirname(__file__), 'cookies.txt')
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extractor_args': {
                    'youtube': {
                        'player_client': ['web_creator', 'mediaconnect', 'android', 'ios'],
                        'skip': ['hls', 'dash', 'translated_subs'],
                        'player_skip': ['webpage', 'configs'],
                    }
                },
                'nocheckcertificate': True,
                'age_limit': None,
                # Usar cookies si existen
                'cookiefile': cookies_path if os.path.exists(cookies_path) else None,
                # Impersonar navegador para evitar detección de bots (requiere curl_cffi)
                'impersonate': 'chrome',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
                'referer': 'https://www.youtube.com/',
                # Configuración adicional para evitar bloqueos
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                    'Sec-Fetch-Mode': 'navigate',
                },
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Sin título'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'uploader': info.get('uploader', 'Desconocido'),
                    'view_count': info.get('view_count', 0),
                    'id': info.get('id', '')
                }
        except Exception as e:
            logger.error(f"Error al obtener información del video: {str(e)}")
            return None
    
    def download_video(
        self, 
        url: str, 
        format_id: str = 'best'
    ) -> Dict[str, any]:
        """
        Descarga un video de YouTube.
        
        Args:
            url: URL del video de YouTube.
            format_id: Formato de descarga ('best', 'worst', o ID específico).
        
        Returns:
            Diccionario con el resultado de la descarga.
        """
        try:
            # Validar URL
            if not url or not isinstance(url, str):
                return {
                    'success': False,
                    'error': 'URL inválida'
                }
            
            # Configuración de yt-dlp
            cookies_path = os.path.join(os.path.dirname(__file__), 'cookies.txt')
            ydl_opts = {
                'format': format_id,
                'outtmpl': os.path.join(
                    self.download_path, 
                    '%(title)s.%(ext)s'
                ),
                'quiet': False,
                'no_warnings': False,
                'progress_hooks': [self._progress_hook],
                # Evitar detección de bot con estrategia avanzada
                'extractor_args': {
                    'youtube': {
                        'player_client': ['web_creator', 'mediaconnect', 'android', 'ios'],
                        'skip': ['hls', 'dash', 'translated_subs'],
                        'player_skip': ['webpage', 'configs'],
                    }
                },
                'nocheckcertificate': True,
                'age_limit': None,
                # Usar cookies si existen
                'cookiefile': cookies_path if os.path.exists(cookies_path) else None,
                # Impersonar navegador para evitar detección de bots (requiere curl_cffi)
                'impersonate': 'chrome',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
                'referer': 'https://www.youtube.com/',
                # Configuración adicional para evitar bloqueos
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                    'Sec-Fetch-Mode': 'navigate',
                },
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                return {
                    'success': True,
                    'filename': os.path.basename(filename),
                    'filepath': filename,
                    'title': info.get('title', 'Sin título')
                }
                
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"Error de descarga: {str(e)}")
            return {
                'success': False,
                'error': f'Error al descargar el video: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return {
                'success': False,
                'error': f'Error inesperado: {str(e)}'
            }
    
    def _progress_hook(self, d: Dict) -> None:
        """
        Hook para monitorear el progreso de descarga.
        
        Args:
            d: Diccionario con información del progreso.
        """
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%')
            logger.info(f"Descargando: {percent}")
        elif d['status'] == 'finished':
            logger.info("Descarga completada, procesando archivo...")
