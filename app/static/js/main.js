/**
 * Script principal para la aplicación de descarga de YouTube
 */

// Elementos del DOM
const videoForm = document.getElementById('videoForm');
const videoUrlInput = document.getElementById('videoUrl');
const infoBtn = document.getElementById('infoBtn');
const downloadBtn = document.getElementById('downloadBtn');
const videoInfo = document.getElementById('videoInfo');
const progressArea = document.getElementById('progressArea');
const resultArea = document.getElementById('resultArea');
const successMessage = document.getElementById('successMessage');
const errorMessage = document.getElementById('errorMessage');

/**
 * Inicializa la aplicación
 */
function initializeApp() {
    // Esperar a que el CSS se cargue completamente
    setTimeout(() => {
        // Asegurar que todas las áreas estén ocultas al cargar la página
        hideAllAreas();
        
        // Limpiar el formulario
        videoUrlInput.value = '';
        videoUrlInput.style.borderColor = 'var(--border-color)';
        
        // Habilitar botones
        setButtonsState(false);
        
        console.log('Aplicación inicializada correctamente');
        
        // Verificar que los elementos estén ocultos
        verifyHiddenElements();
    }, 100);
}

/**
 * Verifica que todos los elementos ocultos estén correctamente ocultos
 */
function verifyHiddenElements() {
    const elementsToCheck = [
        { element: videoInfo, name: 'videoInfo' },
        { element: progressArea, name: 'progressArea' },
        { element: resultArea, name: 'resultArea' },
        { element: successMessage, name: 'successMessage' },
        { element: errorMessage, name: 'errorMessage' }
    ];
    
    elementsToCheck.forEach(({ element, name }) => {
        if (element && !element.classList.contains('hidden')) {
            console.warn(`Elemento ${name} no está oculto inicialmente, ocultándolo...`);
            element.classList.add('hidden');
        }
    });
}

/**
 * Formatea la duración en segundos a formato HH:MM:SS
 * 
 * @param {number} seconds - Duración en segundos
 * @returns {string} Duración formateada
 */
function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Formatea el número de vistas
 * 
 * @param {number} views - Número de vistas
 * @returns {string} Vistas formateadas
 */
function formatViews(views) {
    if (views >= 1000000) {
        return `${(views / 1000000).toFixed(1)}M`;
    } else if (views >= 1000) {
        return `${(views / 1000).toFixed(1)}K`;
    }
    return views.toString();
}

/**
 * Muestra el área de progreso
 * 
 * @param {string} text - Texto a mostrar
 */
function showProgress(text = 'Procesando...') {
    hideAllAreas();
    progressArea.classList.remove('hidden');
    document.getElementById('progressText').textContent = text;
    setButtonsState(true);
}

/**
 * Oculta todas las áreas de resultado
 */
function hideAllAreas() {
    // Lista de todos los elementos que deben estar ocultos
    const elementsToHide = [
        videoInfo,
        progressArea,
        resultArea,
        successMessage,
        errorMessage
    ];
    
    elementsToHide.forEach(element => {
        if (element) {
            element.classList.add('hidden');
        }
    });
}

/**
 * Establece el estado de los botones
 * 
 * @param {boolean} disabled - Si los botones deben estar deshabilitados
 */
function setButtonsState(disabled) {
    infoBtn.disabled = disabled;
    downloadBtn.disabled = disabled;
}

/**
 * Muestra un mensaje de error
 * 
 * @param {string} message - Mensaje de error
 */
function showError(message) {
    hideAllAreas();
    resultArea.classList.remove('hidden');
    errorMessage.classList.remove('hidden');
    document.getElementById('errorText').textContent = message;
    setButtonsState(false);
}

/**
 * Muestra un mensaje de éxito
 * 
 * @param {string} title - Título del video
 * @param {string} filename - Nombre del archivo
 */
function showSuccess(title, filename) {
    hideAllAreas();
    resultArea.classList.remove('hidden');
    successMessage.classList.remove('hidden');
    document.getElementById('resultTitle').textContent = title;
    
    const downloadLink = document.getElementById('downloadLink');
    downloadLink.href = `/api/file/${encodeURIComponent(filename)}`;
    
    setButtonsState(false);
}

/**
 * Obtiene información del video
 */
async function getVideoInfo() {
    const url = videoUrlInput.value.trim();
    
    if (!url) {
        showError('Por favor ingresa una URL válida');
        return;
    }
    
    showProgress('Obteniendo información del video...');
    
    try {
        const response = await fetch('/api/info', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayVideoInfo(data.info);
        } else {
            showError(data.error || 'Error al obtener información del video');
        }
    } catch (error) {
        showError('Error de conexión: ' + error.message);
    }
}

/**
 * Muestra la información del video
 * 
 * @param {Object} info - Información del video
 */
function displayVideoInfo(info) {
    hideAllAreas();
    
    document.getElementById('thumbnail').src = info.thumbnail;
    document.getElementById('title').textContent = info.title;
    document.getElementById('uploader').textContent = info.uploader;
    document.getElementById('duration').textContent = formatDuration(info.duration);
    document.getElementById('views').textContent = formatViews(info.view_count) + ' vistas';
    
    videoInfo.classList.remove('hidden');
    setButtonsState(false);
}

/**
 * Descarga el video
 * 
 * @param {Event} event - Evento del formulario
 */
async function downloadVideo(event) {
    event.preventDefault();
    
    const url = videoUrlInput.value.trim();
    
    if (!url) {
        showError('Por favor ingresa una URL válida');
        return;
    }
    
    showProgress('Descargando video... Esto puede tardar varios minutos.');
    
    try {
        const response = await fetch('/api/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                url,
                format: 'best'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(data.title, data.filename);
        } else {
            showError(data.error || 'Error al descargar el video');
        }
    } catch (error) {
        showError('Error de conexión: ' + error.message);
    }
}

/**
 * Valida la URL de YouTube
 * 
 * @param {string} url - URL a validar
 * @returns {boolean} Si la URL es válida
 */
function isValidYouTubeUrl(url) {
    const pattern = /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/).+$/;
    return pattern.test(url);
}

/**
 * Maneja el cambio en el input de URL
 */
function handleUrlChange() {
    const url = videoUrlInput.value.trim();
    
    if (url && !isValidYouTubeUrl(url)) {
        videoUrlInput.style.borderColor = 'var(--error-color)';
    } else {
        videoUrlInput.style.borderColor = 'var(--border-color)';
    }
}

// Event Listeners
videoForm.addEventListener('submit', downloadVideo);
infoBtn.addEventListener('click', getVideoInfo);
videoUrlInput.addEventListener('input', handleUrlChange);

// Limpiar mensajes al cambiar la URL
videoUrlInput.addEventListener('focus', () => {
    hideAllAreas();
});

// Inicializar la aplicación cuando se carga la página
document.addEventListener('DOMContentLoaded', initializeApp);
