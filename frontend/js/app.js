// Estado de la aplicación
let noticias = [];
let resumenesPorCategoria = null; // { categoria: { resumen, cantidad_noticias, fecha_generacion } }
let categoriaSeleccionada = 'internacional'; // Por defecto la primera categoría
let fuenteSeleccionada = 'todas';
let todasLasCategorias = [];
let todasLasFuentes = [];

// DOM Elements
const contenedorNoticias = document.getElementById('noticias-container');
const estadoCarga = document.getElementById('estado-carga');
const mensajeError = document.getElementById('mensaje-error');
const sinNoticias = document.getElementById('sin-noticias');
const contadorNoticias = document.getElementById('contador-noticias');
const fechaActualizacion = document.getElementById('fecha-actualizacion');
const btnActualizar = document.getElementById('btn-actualizar');

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    cargarNoticias();
    btnActualizar.addEventListener('click', cargarNoticias);
});

/**
 * Carga las noticias del archivo JSON
 */
async function cargarNoticias() {
    try {
        // Mostrar estado de carga
        mostrarEstadoCarga();
        
        // Obtener fecha en zona horaria Argentina (UTC-3)
        const ahora = new Date();
        const offsetArgentina = -3 * 60; // UTC-3 en minutos
        const fechaArgentina = new Date(ahora.getTime() + (offsetArgentina + ahora.getTimezoneOffset()) * 60000);
        const hoy = fechaArgentina.toISOString().split('T')[0];
        
        // Calcular también fecha de ayer por si acaso
        const ayer = new Date(fechaArgentina);
        ayer.setDate(ayer.getDate() - 1);
        const ayerStr = ayer.toISOString().split('T')[0];
        
        // Intentar cargar el archivo de hoy primero, si falla intentar ayer
        let archivoNoticias = `data/noticias_${hoy}.json`;
        let response = await fetch(archivoNoticias);
        
        if (!response.ok) {
            // Intentar con fecha de ayer
            archivoNoticias = `data/noticias_${ayerStr}.json`;
            response = await fetch(archivoNoticias);
            
            if (!response.ok) {
                throw new Error(`No se pudieron cargar los archivos de noticias (intentado: ${hoy} y ${ayerStr})`);
            }
        }
        
        const data = await response.json();
        
        // Extraer noticias del dataset
        noticias = data.noticias || [];
        
        if (noticias.length === 0) {
            mostrarSinNoticias();
            return;
        }
        
        // Extraer categorías y fuentes únicas
        extraerCategoriasYFuentes();
        
        // Generar filtros de navegación
        generarNavegacionCategorias();
        generarNavegacionFuentes();
        
        // Cargar resúmenes del mismo día (no bloqueante)
        try { await cargarResumenes(); } catch (_) {}
        
        // Ocultar estado de carga
        ocultarEstadoCarga();
        
        // Mostrar noticias filtradas y resumen
        mostrarNoticias();
        mostrarResumenCategoria();
        
        // Actualizar fecha de actualización
        fechaActualizacion.textContent = `Última actualización: ${data.fecha_consolidacion || hoy}`;
        
    } catch (error) {
        console.error('Error al cargar noticias:', error);
        mostrarError(error.message);
    }
}

/**
 * Extrae las categorías y fuentes únicas de las noticias
 */
function extraerCategoriasYFuentes() {
    const categoriasSet = new Set();
    const fuentesSet = new Set();
    
    noticias.forEach(noticia => {
        // Siempre priorizar categoria_url sobre categoria
        let categoria = noticia.categoria_url;
        
        // Si no hay categoria_url, usar categoria como fallback
        if (!categoria && noticia.categoria) {
            // Ignorar categorías inválidas como "No categorizada"
            const categoriaLower = noticia.categoria.toLowerCase().trim();
            if (categoriaLower !== 'no categorizada' && categoriaLower !== '') {
                categoria = 'otros'; // Convertir categorías antiguas sin URL a "otros"
            } else {
                categoria = 'otros'; // Si es "No categorizada", usar "otros"
            }
        }
        
        // Si aún no hay categoría, usar "otros" por defecto
        if (!categoria || categoria.trim() === '') {
            categoria = 'otros';
        }
        
        // Normalizar: convertir a minúsculas y quitar espacios
        categoria = categoria.toLowerCase().trim();
        
        if (categoria) categoriasSet.add(categoria);
        if (noticia.fuente) fuentesSet.add(noticia.fuente);
    });
    
    todasLasCategorias = Array.from(categoriasSet).sort();
    todasLasFuentes = Array.from(fuentesSet).sort();
}

/**
 * Genera los botones de navegación de categorías
 */
function generarNavegacionCategorias() {
    const navCategorias = document.getElementById('categorias-nav');
    
    // Categorías permitidas en el orden específico
    const categoriasPermitidas = ['internacional', 'politica', 'economia', 'sociedad'];
    
    // Filtrar solo las categorías permitidas que existen en los datos
    const categoriasDisponibles = categoriasPermitidas.filter(cat => todasLasCategorias.includes(cat));
    
    let html = '';
    
    // Botones para cada categoría en el orden especificado
    categoriasDisponibles.forEach((categoria, index) => {
        const nombreFormateado = formatearNombreCategoria(categoria);
        // Primera categoría activa por defecto
        const isActive = index === 0 ? 'bg-blue-600 text-white' : 'bg-gray-200 hover:bg-gray-300 text-gray-700';
        html += `<button class="categoria-btn px-4 py-2 rounded-lg ${isActive} font-medium whitespace-nowrap transition-colors" data-categoria="${categoria}">${nombreFormateado}</button>`;
    });
    
    navCategorias.innerHTML = html;
    
    // Agregar event listeners
            navCategorias.querySelectorAll('.categoria-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            categoriaSeleccionada = e.target.dataset.categoria;
            
            // Actualizar clases activas
            navCategorias.querySelectorAll('.categoria-btn').forEach(b => {
                b.classList.remove('active', 'bg-blue-600', 'text-white');
                b.classList.add('bg-gray-200', 'text-gray-700');
            });
            e.target.classList.add('active', 'bg-blue-600', 'text-white');
            e.target.classList.remove('bg-gray-200', 'text-gray-700');
            
            // Generar filtros de fuentes según categoría
            actualizarFiltrosFuentes();
            mostrarNoticias();
                    mostrarResumenCategoria();
        });
    });
    
    // Activar primera categoría por defecto
    if (categoriasDisponibles.length > 0) {
        categoriaSeleccionada = categoriasDisponibles[0];
        const primerBoton = navCategorias.querySelector(`[data-categoria="${categoriasDisponibles[0]}"]`);
        if (primerBoton) {
            primerBoton.classList.add('active');
        }
    }
}

/**
 * Carga el archivo de resúmenes del día y lo guarda en memoria
 */
async function cargarResumenes() {
    try {
        // Usar misma lógica de fecha que cargarNoticias (zona horaria Argentina)
        const ahora = new Date();
        const offsetArgentina = -3 * 60;
        const fechaArgentina = new Date(ahora.getTime() + (offsetArgentina + ahora.getTimezoneOffset()) * 60000);
        const hoy = fechaArgentina.toISOString().split('T')[0];
        
        const ayer = new Date(fechaArgentina);
        ayer.setDate(ayer.getDate() - 1);
        const ayerStr = ayer.toISOString().split('T')[0];
        
        // Intentar cargar resúmenes de hoy, si falla intentar ayer
        let archivoResumenes = `data/resumenes_${hoy}.json`;
        let response = await fetch(archivoResumenes);
        
        if (!response.ok) {
            archivoResumenes = `data/resumenes_${ayerStr}.json`;
            response = await fetch(archivoResumenes);
        }
        
        if (!response.ok) throw new Error('No se encontraron resúmenes');
        
        const data = await response.json();
        resumenesPorCategoria = data.resumenes || null;
        
        // Actualizar fecha en cabecera si existe
        const fechaResumen = document.getElementById('resumen-fecha');
        if (fechaResumen && data.fecha_consolidacion) {
            fechaResumen.textContent = `Fecha: ${data.fecha_consolidacion}`;
        }
    } catch (e) {
        resumenesPorCategoria = null;
        ocultarResumenCategoria();
    }
}

/**
 * Muestra el resumen de la categoría seleccionada si existen resúmenes
 */
function mostrarResumenCategoria() {
    const contenedor = document.getElementById('resumen-categoria');
    const texto = document.getElementById('resumen-texto');
    if (!contenedor || !texto) return;
    
    if (!resumenesPorCategoria) {
        ocultarResumenCategoria();
        return;
    }
    const cat = (categoriaSeleccionada || '').toLowerCase();
    const entrada = resumenesPorCategoria[cat];
    if (!entrada || !entrada.resumen || String(entrada.resumen).trim() === '') {
        ocultarResumenCategoria();
        return;
    }
    texto.textContent = entrada.resumen;
    contenedor.classList.remove('hidden');
    
    // Configurar toggle si no está ya configurado
    configurarToggleResumen();
}

function configurarToggleResumen() {
    const toggle = document.getElementById('resumen-toggle');
    const contenido = document.getElementById('resumen-contenido');
    const icono = document.getElementById('resumen-icon');
    
    if (!toggle || !contenido || !icono) return;
    
    // Solo agregar listener una vez
    if (toggle.dataset.listenerAdded) return;
    
    toggle.addEventListener('click', () => {
        contenido.classList.toggle('hidden');
        icono.classList.toggle('rotate-180');
    });
    
    toggle.dataset.listenerAdded = 'true';
}

function ocultarResumenCategoria() {
    const contenedor = document.getElementById('resumen-categoria');
    const texto = document.getElementById('resumen-texto');
    if (contenedor) contenedor.classList.add('hidden');
    if (texto) texto.textContent = '';
}

/**
 * Genera los botones de navegación de fuentes
 */
function generarNavegacionFuentes() {
    actualizarFiltrosFuentes();
}

/**
 * Actualiza los filtros de fuentes según la categoría seleccionada
 */
function actualizarFiltrosFuentes() {
    const navFuentes = document.getElementById('fuentes-nav');
    
    // Obtener fuentes disponibles en la categoría seleccionada
    const fuentesEnCategoria = new Set();
    noticias.forEach(n => {
        // Siempre usar categoria_url, si no existe usar "otros"
        let categoria = n.categoria_url;
        if (!categoria || categoria.trim() === '') {
            categoria = 'otros';
        }
        categoria = categoria.toLowerCase().trim();
        
        if (categoria === categoriaSeleccionada && n.fuente) {
            fuentesEnCategoria.add(n.fuente);
        }
    });
    const fuentesDisponibles = Array.from(fuentesEnCategoria).sort();
    
    let html = '<button class="fuente-btn px-3 py-1 rounded-lg bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium whitespace-nowrap text-sm transition-colors" data-fuente="todas">Todas las fuentes</button>';
    
    fuentesDisponibles.forEach(fuente => {
        html += `<button class="fuente-btn px-3 py-1 rounded-lg bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium whitespace-nowrap text-sm transition-colors" data-fuente="${fuente}">${fuente}</button>`;
    });
    
    navFuentes.innerHTML = html;
    
    // Agregar event listeners
    navFuentes.querySelectorAll('.fuente-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            fuenteSeleccionada = e.target.dataset.fuente;
            
            // Actualizar clases activas
            navFuentes.querySelectorAll('.fuente-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            
            mostrarNoticias();
        });
    });
    
    // Activar botón "Todas" por defecto
    navFuentes.querySelector('[data-fuente="todas"]').classList.add('active');
}

/**
 * Muestra las noticias filtradas
 */
function mostrarNoticias() {
    // Filtrar noticias
    let noticiasFiltradas = noticias.filter(noticia => {
        // Siempre usar categoria_url, si no existe usar "otros"
        let categoria = noticia.categoria_url;
        if (!categoria || categoria.trim() === '') {
            categoria = 'otros';
        }
        categoria = categoria.toLowerCase().trim();
        
        // Filtro: mostrar solo noticias de la categoría seleccionada (ya no hay "todas")
        const cumpleCategoria = categoria === categoriaSeleccionada;
        
        // Excluir Infobae de la categoría Internacional
        if (categoriaSeleccionada === 'internacional' && noticia.fuente === 'Infobae') {
            return false;
        }
        
        const cumpleFuente = fuenteSeleccionada === 'todas' || noticia.fuente === fuenteSeleccionada;
        return cumpleCategoria && cumpleFuente;
    });
    
    // Intercalar noticias por fuente para evitar noticias consecutivas de la misma fuente
    function intercalarPorFuente(noticias) {
        // 1. Agrupar noticias por fuente
        const noticiasPorFuente = {};
        noticias.forEach(noticia => {
            const fuente = noticia.fuente || 'Sin fuente';
            if (!noticiasPorFuente[fuente]) {
                noticiasPorFuente[fuente] = [];
            }
            noticiasPorFuente[fuente].push(noticia);
        });
        
        // 2. Ordenar cada grupo por fecha (más recientes primero)
        Object.keys(noticiasPorFuente).forEach(fuente => {
            noticiasPorFuente[fuente].sort((a, b) => {
                const fechaA = a.fecha_local || '';
                const fechaB = b.fecha_local || '';
                return fechaB.localeCompare(fechaA); // Descendente (más recientes primero)
            });
        });
        
        // 3. Intercalar usando algoritmo round-robin
        const resultado = [];
        const fuentes = Object.keys(noticiasPorFuente);
        const indices = {}; // Trackear qué índice hemos usado de cada fuente
        fuentes.forEach(fuente => {
            indices[fuente] = 0;
        });
        
        let hayMasNoticias = true;
        while (hayMasNoticias) {
            hayMasNoticias = false;
            
            // Intentar agregar una noticia de cada fuente en orden
            fuentes.forEach(fuente => {
                const colaFuente = noticiasPorFuente[fuente];
                if (indices[fuente] < colaFuente.length) {
                    resultado.push(colaFuente[indices[fuente]]);
                    indices[fuente]++;
                    hayMasNoticias = true;
                }
            });
        }
        
        return resultado;
    }
    
    // Aplicar intercalación por fuente
    noticiasFiltradas = intercalarPorFuente(noticiasFiltradas);
    
    // Generar HTML de las tarjetas
    contenedorNoticias.innerHTML = '';
    
    if (noticiasFiltradas.length === 0) {
        mostrarSinNoticias();
        return;
    }
    
    noticiasFiltradas.forEach(noticia => {
        const card = crearTarjetaNoticia(noticia);
        contenedorNoticias.appendChild(card);
    });
    
    // Actualizar contador
    contadorNoticias.textContent = `Mostrando ${noticiasFiltradas.length} noticias`;
}

/**
 * Convierte HTML a texto plano
 */
function htmlATexto(html) {
    if (!html) return '';
    // Crear un elemento temporal para extraer solo el texto
    const temp = document.createElement('div');
    temp.innerHTML = html;
    // Reemplazar <li> con saltos de línea o guiones para mejor legibilidad
    const listItems = temp.querySelectorAll('li');
    listItems.forEach(li => {
        li.textContent = '• ' + li.textContent.trim() + ' ';
    });
    // Retornar solo el texto, limpiando espacios múltiples
    return temp.textContent || temp.innerText || '';
}

/**
 * Crea una tarjeta de noticia
 */
function crearTarjetaNoticia(noticia) {
    const card = document.createElement('div');
    card.className = 'bg-white rounded-lg shadow-md p-4 noticia-card flex flex-col h-full';
    
    // Formatear fecha
    const fechaFormateada = formatearFecha(noticia.fecha_local);
    
    // Obtener categoría: siempre usar categoria_url, nunca categoria
    let categoriaDisplay = noticia.categoria_url;
    
    // Si categoria_url no existe, es null, undefined, vacío o es "No categorizada", usar "otros"
    if (!categoriaDisplay || 
        categoriaDisplay === null || 
        categoriaDisplay === undefined ||
        categoriaDisplay.toString().trim() === '' || 
        categoriaDisplay.toString().toLowerCase().trim() === 'no categorizada') {
        categoriaDisplay = 'otros';
    } else {
        categoriaDisplay = categoriaDisplay.toString().toLowerCase().trim();
    }
    
    // Convertir resumen HTML a texto plano
    const resumenTexto = htmlATexto(noticia.resumen) || 'Sin descripción';
    
    card.innerHTML = `
        <div class="flex items-center justify-between mb-2 flex-shrink-0">
            <span class="inline-block bg-blue-100 text-blue-800 text-xs font-semibold px-2 py-0.5 rounded">${noticia.fuente || 'Sin fuente'}</span>
            <span class="inline-block bg-gray-100 text-gray-800 text-xs font-medium px-2 py-0.5 rounded">${formatearNombreCategoria(categoriaDisplay)}</span>
        </div>
        
        <h3 class="text-base font-bold text-gray-900 mb-2 flex-shrink-0">${noticia.titulo || 'Sin título'}</h3>
        
        <p class="text-xs text-gray-600 mb-2 flex-grow">${resumenTexto}</p>
        
        <div class="flex items-center justify-between text-xs text-gray-400 mb-2 flex-shrink-0">
            <span>🕒</span>
            ${noticia.horas_atras ? `<span>⏱️ ${Math.round(noticia.horas_atras)}h</span>` : ''}
        </div>
        
        <a href="${noticia.link || '#'}" target="_blank" rel="noopener noreferrer" 
           class="mt-auto block w-full bg-blue-600 hover:bg-blue-700 text-white text-center font-medium py-1.5 rounded text-xs transition-colors flex-shrink-0">
            Leer más →
        </a>
    `;
    
    return card;
}

/**
 * Capitaliza la primera letra de un string
 */
function capitalizarPrimeraLetra(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Formatea el nombre de la categoría para mostrarlo en español
 */
function formatearNombreCategoria(categoria) {
    // Normalizar entrada
    if (!categoria) return 'Otros';
    categoria = categoria.toString().toLowerCase().trim();
    
    // Si viene como "no categorizada", convertir a "otros"
    if (categoria === 'no categorizada') {
        categoria = 'otros';
    }
    
    const nombres = {
        'politica': 'Política',
        'economia': 'Economía',
        'sociedad': 'Sociedad',
        'deportes': 'Deportes',
        'cultura': 'Cultura',
        'espectaculos': 'Espectáculos',
        'tecnologia': 'Tecnología',
        'internacional': 'Internacional',
        'salud': 'Salud',
        'ciencia': 'Ciencia',
        'otros': 'Otros'
    };
    return nombres[categoria] || 'Otros';
}

/**
 * Formatea la fecha para mostrar
 */
function formatearFecha(fechaStr) {
    if (!fechaStr) return 'Sin fecha';
    
    try {
        const fecha = new Date(fechaStr.replace(' ', 'T'));
        return fecha.toLocaleString('es-AR', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (e) {
        return fechaStr;
    }
}

/**
 * Muestra el estado de carga
 */
function mostrarEstadoCarga() {
    estadoCarga.classList.remove('hidden');
    contenedorNoticias.classList.add('hidden');
    mensajeError.classList.add('hidden');
    sinNoticias.classList.add('hidden');
}

/**
 * Oculta el estado de carga
 */
function ocultarEstadoCarga() {
    estadoCarga.classList.add('hidden');
    contenedorNoticias.classList.remove('hidden');
}

/**
 * Muestra un mensaje de error
 */
function mostrarError(mensaje) {
    estadoCarga.classList.add('hidden');
    mensajeError.classList.remove('hidden');
    document.getElementById('error-texto').textContent = mensaje;
}

/**
 * Muestra mensaje cuando no hay noticias
 */
function mostrarSinNoticias() {
    estadoCarga.classList.add('hidden');
    sinNoticias.classList.remove('hidden');
    contadorNoticias.textContent = 'No hay noticias disponibles';
}

