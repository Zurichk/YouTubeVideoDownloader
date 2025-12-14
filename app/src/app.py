"""
Aplicación Flask para descargar videos de YouTube.
"""
import os
import logging
from flask import (
    Flask, 
    render_template, 
    request, 
    jsonify, 
    send_file,
    redirect,
    url_for
)
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from youtube_downloader import AEPYouTubeDownloader
from file_cleanup import AEPFileCleanupService


# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constantes de configuración
AEP_SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
AEP_MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500 MB
AEP_FILE_MAX_AGE_HOURS = int(os.environ.get('FILE_MAX_AGE_HOURS', '1'))
AEP_CLEANUP_INTERVAL_MINUTES = int(os.environ.get('CLEANUP_INTERVAL_MINUTES', '5'))

# Obtener rutas correctas para templates y static
AEP_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AEP_TEMPLATE_DIR = os.path.join(AEP_BASE_DIR, 'templates')
AEP_STATIC_DIR = os.path.join(AEP_BASE_DIR, 'static')
AEP_DOWNLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')

# Inicializar Flask
app = Flask(
    __name__,
    template_folder=AEP_TEMPLATE_DIR,
    static_folder=AEP_STATIC_DIR
)
app.config['SECRET_KEY'] = AEP_SECRET_KEY
app.config['DOWNLOAD_FOLDER'] = AEP_DOWNLOAD_FOLDER

# Habilitar CORS para todas las rutas
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = AEP_MAX_CONTENT_LENGTH

# Inicializar descargador
downloader = AEPYouTubeDownloader(download_path=AEP_DOWNLOAD_FOLDER)

# Inicializar servicio de limpieza
cleanup_service = AEPFileCleanupService(
    download_path=AEP_DOWNLOAD_FOLDER,
    max_age_seconds=AEP_FILE_MAX_AGE_HOURS * 3600,
    cleanup_interval=AEP_CLEANUP_INTERVAL_MINUTES * 60
)


@app.route('/')
def index():
    """
    Ruta principal que muestra la interfaz de descarga.
    
    Returns:
        Template HTML renderizado.
    """
    return render_template('index.html')


@app.route('/api/info', methods=['POST'])
def get_video_info():
    """
    Obtiene información de un video de YouTube.
    
    Returns:
        JSON con la información del video.
    """
    try:
        # Log para depuración
        logger.info(f"Info Request Headers: {request.headers}")
        logger.info(f"Info Request Body: {request.get_data(as_text=True)}")

        data = request.get_json(force=True, silent=True)
        
        if not data:
            logger.error("No se pudo parsear el JSON del body")
            return jsonify({
                'success': False,
                'error': 'Datos inválidos o formato incorrecto'
            }), 400

        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'Por favor proporciona una URL válida'
            }), 400
        
        info = downloader.get_video_info(url)
        
        if info:
            return jsonify({
                'success': True,
                'info': info
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo obtener información del video'
            }), 400
            
    except Exception as e:
        logger.error(f"Error en get_video_info: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/download', methods=['POST'])
def download_video():
    """
    Descarga un video de YouTube.
    
    Returns:
        JSON con el resultado de la descarga.
    """
    try:
        # Log para depuración
        logger.info(f"Download Request Headers: {request.headers}")
        logger.info(f"Download Request Body: {request.get_data(as_text=True)}")

        data = request.get_json(force=True, silent=True)
        
        if not data:
            logger.error("No se pudo parsear el JSON del body")
            return jsonify({
                'success': False,
                'error': 'Datos inválidos o formato incorrecto'
            }), 400

        url = data.get('url', '').strip()
        format_id = data.get('format', 'best')
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'Por favor proporciona una URL válida'
            }), 400
        
        result = downloader.download_video(url, format_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error en download_video: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/file/<path:filename>')
def download_file(filename: str):
    """
    Envía el archivo descargado al usuario.
    
    Args:
        filename: Nombre del archivo a descargar.
    
    Returns:
        Archivo para descarga.
    """
    try:
        # Decodificar el nombre del archivo
        from urllib.parse import unquote
        decoded_filename = unquote(filename)
        
        # Construir la ruta completa
        filepath = os.path.join(app.config['DOWNLOAD_FOLDER'], decoded_filename)
        
        # Verificar que el archivo existe y está dentro del directorio de descargas
        filepath = os.path.abspath(filepath)
        download_folder = os.path.abspath(app.config['DOWNLOAD_FOLDER'])
        
        if not filepath.startswith(download_folder):
            return jsonify({
                'success': False,
                'error': 'Acceso no autorizado'
            }), 403
        
        if not os.path.exists(filepath):
            logger.error(f"Archivo no encontrado: {filepath}")
            return jsonify({
                'success': False,
                'error': 'Archivo no encontrado'
            }), 404
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=decoded_filename
        )
        
    except Exception as e:
        logger.error(f"Error al enviar archivo: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """
    Manejador de error 404.
    
    Args:
        error: Objeto de error.
    
    Returns:
        JSON con mensaje de error.
    """
    return jsonify({
        'success': False,
        'error': 'Recurso no encontrado'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """
    Manejador de error 500.
    
    Args:
        error: Objeto de error.
    
    Returns:
        JSON con mensaje de error.
    """
    logger.error(f"Error interno del servidor: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Error interno del servidor'
    }), 500


if __name__ == '__main__':
    # Asegurar que existe el directorio de descargas
    os.makedirs(AEP_DOWNLOAD_FOLDER, exist_ok=True)
    
    # Iniciar servicio de limpieza automática
    cleanup_service.start()
    
    try:
        # Ejecutar aplicación
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5038
        )
    finally:
        # Detener servicio de limpieza al cerrar
        cleanup_service.stop()
