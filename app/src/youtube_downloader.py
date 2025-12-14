"""
Módulo para descargar videos de YouTube utilizando yt-dlp.
"""
import os
import logging
import json
import time
import traceback
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
    
    def _get_ydl_opts(self, use_cookies: bool = True) -> Dict:
        """
        Genera la configuración para yt-dlp.
        
        Args:
            use_cookies: Si se deben usar cookies o no.
            
        Returns:
            Diccionario con la configuración.
        """
        cookies_path = os.path.join(os.path.dirname(__file__), 'cookies.txt')
        
        opts = {
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'age_limit': None,
            # 'impersonate': 'chrome', # Deshabilitado temporalmente por error de aserción en servidor
            'extractor_args': {
                'youtube': {
                    'player_client': ['web', 'web_creator', 'android', 'ios'],
                    'skip': ['hls', 'dash', 'translated_subs'],
                    'player_skip': ['webpage', 'configs'],
                }
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Sec-Fetch-Dest': 'document',
                'Upgrade-Insecure-Requests': '1',
            },
        }
        
        # Solo añadir cookies si se solicita y el archivo existe
        if use_cookies and os.path.exists(cookies_path):
            opts['cookiefile'] = cookies_path
            logger.info(f"Usando cookies desde: {cookies_path}")
        else:
            logger.info("No se están usando cookies (archivo no encontrado o deshabilitado)")
            
        return opts

    def get_video_info(self, url: str) -> Optional[Dict]:
        """
        Obtiene información del video sin descargarlo.
        
        Args:
            url: URL del video de YouTube.
        
        Returns:
            Diccionario con información del video o None si hay error.
        """
        try:
            # Intentar usar cookies si existen (True), si no existen el método _get_ydl_opts lo maneja
            opts = self._get_ydl_opts(use_cookies=True)
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return self._process_info(info)
        except Exception as e:
            logger.error(f"Error al obtener información: {str(e)}")
            logger.error(traceback.format_exc())
            return None

    def _process_info(self, info: Dict) -> Dict:
        """Procesa la información cruda de yt-dlp"""
        return {
            'title': info.get('title', 'Sin título'),
            'duration': info.get('duration', 0),
            'thumbnail': info.get('thumbnail', ''),
            'uploader': info.get('uploader', 'Desconocido'),
            'view_count': info.get('view_count', 0),
            'id': info.get('id', '')
        }
    
    def download_video(
        self, 
        url: str, 
        format_id: str = 'bestvideo+bestaudio/best'
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
            
            # Función interna para intentar descarga
            def try_download():
                # Intentar usar cookies si existen
                opts = self._get_ydl_opts(use_cookies=True)
                opts.update({
                    'format': format_id,
                    'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                    'quiet': False,
                    'no_warnings': False,
                    'progress_hooks': [self._progress_hook],
                })
                
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    return {
                        'success': True,
                        'filename': os.path.basename(filename),
                        'filepath': filename,
                        'title': info.get('title', 'Sin título')
                    }

            return try_download()
                
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"Error de descarga final: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': f'Error al descargar el video: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Error inesperado final: {str(e)}")
            logger.error(traceback.format_exc())
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
