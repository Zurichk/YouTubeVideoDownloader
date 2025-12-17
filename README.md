# YouTube Video Downloader

Aplicación web desarrollada con Flask para descargar videos de YouTube de forma segura y legal.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🚀 Características

- ✅ Interfaz web moderna y responsive
- ✅ Descarga de videos en la mejor calidad disponible
- ✅ Vista previa con información del video
- ✅ Limpieza automática de archivos (1 hora)
- ✅ Validación de URLs de YouTube
- ✅ Descargo de responsabilidad legal
- ✅ Listo para despliegue en Docker/Coolify
- ✅ Logging completo de operaciones

## ⚠️ Descargo de Responsabilidad Legal

**IMPORTANTE:** Esta aplicación está diseñada exclusivamente para descargar videos de los cuales tienes los derechos de autor o permiso explícito del propietario. El uso de esta herramienta para descargar contenido protegido por derechos de autor sin autorización puede violar las leyes de propiedad intelectual.

**Al usar esta aplicación, aceptas que:**
- Solo descargarás contenido del cual tienes derechos o permiso explícito
- Respetarás los términos de servicio de YouTube
- No utilizarás el contenido descargado con fines comerciales sin autorización
- Eres el único responsable del uso que hagas del contenido descargado

Los desarrolladores no se hacen responsables del uso indebido o ilegal de esta aplicación.

## 📋 Requisitos

- Python 3.10 o superior
- Docker (opcional, para despliegue)
- ffmpeg (instalado automáticamente en Docker)

## 🔧 Instalación Local

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/youtube-downloader.git
cd youtube-downloader
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
cp .env.example .env
# Edita .env con tu configuración
```

### 5. Ejecutar la aplicación
```bash
cd app/src
python app.py
```

La aplicación estará disponible en `http://localhost:5038`

## 🐳 Despliegue con Docker

### Usando Docker Compose (Recomendado)
```bash
docker-compose up -d
```

### Usando Docker directamente
```bash
docker build -t youtube-downloader .
docker run -d -p 5038:5038 \
  -e SECRET_KEY=tu-clave-secreta \
  -e FILE_MAX_AGE_HOURS=1 \
  youtube-downloader
```

## ☁️ Despliegue en Coolify

Consulta la [Guía de Despliegue](DEPLOYMENT.md) para instrucciones detalladas sobre cómo desplegar en Coolify, Hetzner u otros proveedores VPS.

## 🎯 Uso

1. Accede a la aplicación en tu navegador
2. Lee y acepta el descargo de responsabilidad
3. Pega la URL del video de YouTube
4. (Opcional) Haz clic en "Ver Información" para previsualizar
5. Haz clic en "Descargar Video"
6. Descarga el archivo una vez completado

**Los archivos se eliminan automáticamente después de 1 hora**

## 🔒 Seguridad

- ✅ Sin credenciales hardcodeadas
- ✅ Validación de rutas de archivo
- ✅ Sanitización de inputs
- ✅ Usuario no privilegiado en Docker
- ✅ Variables de entorno para configuración sensible
- ✅ Límite de tamaño de archivo (500 MB)

## 📁 Estructura del Proyecto

```
youtube-downloader/
├── app/
│   ├── src/
│   │   ├── app.py                  # Aplicación Flask principal
│   │   ├── youtube_downloader.py   # Lógica de descarga
│   │   └── file_cleanup.py         # Limpieza automática
│   ├── templates/
│   │   └── index.html              # Interfaz web
│   └── static/
│       ├── css/style.css           # Estilos
│       └── js/main.js              # JavaScript frontend
├── Dockerfile                      # Configuración Docker
├── docker-compose.yml              # Orquestación Docker
├── requirements.txt                # Dependencias Python
├── .env.example                    # Ejemplo de variables de entorno
└── DEPLOYMENT.md                   # Guía de despliegue
```

## ⚙️ Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Clave secreta de Flask | `dev-secret-key-change-in-production` |
| `FILE_MAX_AGE_HOURS` | Horas antes de eliminar archivos | `1` |
| `CLEANUP_INTERVAL_MINUTES` | Intervalo de limpieza | `5` |
| `FLASK_ENV` | Entorno de Flask | `development` |

## 🛠️ Tecnologías Utilizadas

- **Backend:** Flask 3.0.0
- **Descarga:** yt-dlp
- **Servidor:** Gunicorn (producción)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Containerización:** Docker
- **Procesamiento:** ffmpeg

## 📊 Características Técnicas

- Limpieza automática cada 5 minutos
- 2 workers Gunicorn con 4 threads cada uno
- Timeout de 300 segundos para descargas largas
- Health checks integrados
- Logging estructurado

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## ⚠️ Nota Legal

Esta herramienta se proporciona "tal cual" sin garantías de ningún tipo. El uso de esta herramienta es bajo tu propio riesgo. Asegúrate de cumplir con todas las leyes aplicables y los términos de servicio de las plataformas de las que descargues contenido.

## 🔗 Enlaces Útiles

- [Documentación de yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [Documentación de Flask](https://flask.palletsprojects.com/)
https://github.com/yt-dlp/yt-dlp/wiki/Extractors#po-token-guide
https://github.com/yt-dlp/yt-dlp/wiki/PO-Token-Guide

## 📧 Contacto

Para preguntas o soporte, por favor abre un issue en GitHub.

---

**Desarrollado siguiendo estándares AEP**
