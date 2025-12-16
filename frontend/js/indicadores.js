// Estado de la sección de indicadores
let areaIndicadoresSeleccionada = 'desarrollo_economico';
let INDICADORES_AREAS = []; // Se carga dinámicamente desde JSON

/**
 * Carga los datos de áreas y subáreas desde el archivo JSON.
 */
async function cargarDatosIndicadores() {
    try {
        // Construir ruta absoluta desde la ubicación de la página actual
        const jsonUrl = new URL('data/indicadores/areas.json', window.location.href);
        const response = await fetch(jsonUrl);
        
        if (!response.ok) {
            throw new Error(`Error al cargar áreas: ${response.statusText}`);
        }
        INDICADORES_AREAS = await response.json();
        inicializarIndicadores();
    } catch (error) {
        console.error('Error al cargar datos de indicadores:', error);
        const contenedor = document.getElementById('indicadores-contenido');
        if (contenedor) {
            contenedor.innerHTML = `
                <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p class="text-red-800">Error al cargar los datos de indicadores.</p>
                    <p class="text-sm text-red-600 mt-1">${error.message}</p>
                </div>
            `;
        }
    }
}

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    cargarDatosIndicadores();
});

function inicializarIndicadores() {
    const nav = document.getElementById('indicadores-areas-nav');
    const contenedor = document.getElementById('indicadores-contenido');
    if (!nav || !contenedor || !Array.isArray(INDICADORES_AREAS)) return;

    // Render de botones de áreas
    let htmlNav = '';
    INDICADORES_AREAS.forEach(area => {
        const isActive = area.id === areaIndicadoresSeleccionada ? 'active' : '';
        htmlNav += `<button class="indicador-area-btn ${isActive}" data-area-id="${area.id}">${area.nombre}</button>`;
    });
    nav.innerHTML = htmlNav;

    // Listeners
    nav.querySelectorAll('.indicador-area-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = e.target.dataset.areaId;
            if (!id) return;
            areaIndicadoresSeleccionada = id;

            nav.querySelectorAll('.indicador-area-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');

            renderIndicadoresArea();
        });
    });

    // Mostrar área inicial
    renderIndicadoresArea();
}

/**
 * Genera un slug URL-friendly a partir de un texto.
 */
function generarSlug(texto) {
    return texto
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '') // Eliminar acentos
        .replace(/[^\w\s-]/g, '') // Eliminar caracteres especiales
        .replace(/[-\s]+/g, '-') // Reemplazar espacios y guiones múltiples
        .trim();
}

function renderIndicadoresArea() {
    const contenedor = document.getElementById('indicadores-contenido');
    if (!contenedor) return;

    const area =
        INDICADORES_AREAS.find(a => a.id === areaIndicadoresSeleccionada) ||
        INDICADORES_AREAS[0];

    const subareasHtml = (area.subareas || [])
        .map(sub => {
            const subareaSlug = generarSlug(sub.nombre);
            const urlSubarea = `indicadores/subarea.html?area=${area.id}&subarea=${subareaSlug}`;
            const cantidadIndicadores = sub.indicadores ? sub.indicadores.length : 0;
            
            return `
                <article class="indicador-subarea-card cursor-pointer hover:shadow-lg transition-shadow" onclick="window.location.href='${urlSubarea}'">
                    <div class="flex justify-between items-start">
                        <div class="flex-1">
                            <h3 class="indicador-subarea-titulo">${sub.nombre}</h3>
                            <p class="indicador-subarea-descripcion">${sub.descripcion}</p>
                        </div>
                        <span class="text-blue-600 ml-4">→</span>
                    </div>
                    ${cantidadIndicadores > 0 
                        ? `<p class="indicador-subarea-meta mt-3">
                            <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                ${cantidadIndicadores} indicador${cantidadIndicadores > 1 ? 'es' : ''} disponible${cantidadIndicadores > 1 ? 's' : ''}
                            </span>
                        </p>`
                        : `<p class="indicador-subarea-meta mt-3 text-gray-400">
                            Haz clic para ver más detalles
                        </p>`
                    }
                </article>
            `;
        })
        .join('');

    contenedor.innerHTML = `
        <header>
            <h2 class="text-lg font-semibold text-gray-900 mb-1">${area.nombre}</h2>
            <p class="text-sm text-gray-600">${area.descripcion}</p>
        </header>
        <section class="indicadores-subareas-grid">
            ${subareasHtml}
        </section>
    `;
}


