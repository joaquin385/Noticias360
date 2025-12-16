/**
 * Script para renderizar dinámicamente la página de subárea basándose en parámetros de URL.
 */

let INDICADORES_AREAS = []; // Se carga dinámicamente desde JSON
let pilarSeleccionado = null; // Pilar seleccionado para Política macroeconómica

/**
 * Carga los datos de áreas y subáreas desde el archivo JSON.
 */
async function cargarDatosIndicadores() {
    try {
        // Construir ruta absoluta desde la ubicación de la página actual
        const jsonUrl = new URL('../data/indicadores/areas.json', window.location.href);
        const response = await fetch(jsonUrl);
        if (!response.ok) {
            throw new Error(`Error al cargar áreas: ${response.statusText}`);
        }
        INDICADORES_AREAS = await response.json();
        renderizarSubarea();
    } catch (error) {
        console.error('Error al cargar datos de indicadores:', error);
        document.body.innerHTML = `
            <div class="container mx-auto px-4 py-6">
                <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p class="text-red-800">Error al cargar los datos de indicadores.</p>
                    <p class="text-sm text-red-600 mt-1">${error.message}</p>
                </div>
            </div>
        `;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    cargarDatosIndicadores();
});

/**
 * Obtiene parámetros de la URL.
 */
function obtenerParametrosURL() {
    const params = new URLSearchParams(window.location.search);
    return {
        area: params.get('area'),
        subarea: params.get('subarea')
    };
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

/**
 * Encuentra una subárea por su nombre en slug.
 */
function encontrarSubarea(areaId, subareaSlug) {
    const area = INDICADORES_AREAS.find(a => a.id === areaId);
    if (!area) return null;
    
    return area.subareas.find(sub => {
        const slug = generarSlug(sub.nombre);
        return slug === subareaSlug;
    });
}

/**
 * Formatea la descripción detallada en HTML.
 */
function formatearDescripcionDetallada(texto) {
    if (!texto) return '';
    
    const lineas = texto.split('\n');
    const htmlParts = [];
    let parrafoActual = [];
    
    for (let i = 0; i < lineas.length; i++) {
        const linea = lineas[i].trim();
        
        if (!linea) {
            if (parrafoActual.length > 0) {
                htmlParts.push(`<p class="text-gray-700 mb-3 leading-relaxed">${parrafoActual.join(' ')}</p>`);
                parrafoActual = [];
            }
            continue;
        }
        
        // Detectar títulos (empiezan con número y punto)
        if (/^\d+\.\s/.test(linea)) {
            if (parrafoActual.length > 0) {
                htmlParts.push(`<p class="text-gray-700 mb-3 leading-relaxed">${parrafoActual.join(' ')}</p>`);
                parrafoActual = [];
            }
            htmlParts.push(`<h3 class="text-lg font-semibold text-gray-900 mt-6 mb-3">${linea}</h3>`);
        } else {
            parrafoActual.push(linea);
        }
    }
    
    if (parrafoActual.length > 0) {
        htmlParts.push(`<p class="text-gray-700 mb-3 leading-relaxed">${parrafoActual.join(' ')}</p>`);
    }
    
    return htmlParts.join('\n');
}

/**
 * Renderiza el contenido de la subárea.
 */
function renderizarSubarea() {
    const { area, subarea } = obtenerParametrosURL();
    
    if (!area || !subarea) {
        document.body.innerHTML = '<div class="container mx-auto px-4 py-6"><p class="text-red-600">Error: Parámetros de URL inválidos.</p></div>';
        return;
    }
    
    const subareaData = encontrarSubarea(area, subarea);
    const areaData = INDICADORES_AREAS.find(a => a.id === area);
    
    if (!subareaData || !areaData) {
        document.body.innerHTML = '<div class="container mx-auto px-4 py-6"><p class="text-red-600">Error: Subárea no encontrada.</p></div>';
        return;
    }
    
    // Actualizar título de la página
    document.title = `${subareaData.nombre} - ${areaData.nombre} - Noticias360`;
    
    // Renderizar header
    const header = document.getElementById('subarea-header');
    if (header) {
        // Si tiene pilares, no mostrar la descripción detallada completa (se mostrará por pilar)
        const descripcionHTML = (subareaData.pilares && subareaData.pilares.length > 0)
            ? `<p class="text-gray-700 mt-3 max-w-3xl">${subareaData.descripcion}</p>`
            : (subareaData.descripcion_detallada
                ? `<div class="mt-3 max-w-4xl bg-white rounded-lg border border-gray-200 p-6">${formatearDescripcionDetallada(subareaData.descripcion_detallada)}</div>`
                : `<p class="text-gray-700 mt-3 max-w-3xl">${subareaData.descripcion}</p>`);
        
        header.innerHTML = `
            <div class="flex items-center gap-3 mb-2">
                <span class="text-3xl">${areaData.icono || '📊'}</span>
                <div>
                    <h1 class="text-3xl font-bold text-gray-900">${subareaData.nombre}</h1>
                    <p class="text-sm text-gray-600 mt-1">${areaData.nombre}</p>
                </div>
            </div>
            ${descripcionHTML}
        `;
    }
    
    // Verificar si tiene pilares (Política macroeconómica)
    if (subareaData.pilares && subareaData.pilares.length > 0) {
        renderizarPilares(subareaData);
    } else {
        // Renderizar indicadores normalmente (sin pilares)
        renderizarIndicadores(subareaData.indicadores || []);
    }
}

/**
 * Renderiza los botones de pilares y maneja la selección
 */
function renderizarPilares(subareaData) {
    const pilaresNav = document.getElementById('pilares-nav');
    const pilarContenido = document.getElementById('pilar-contenido');
    const indicadoresSection = document.getElementById('indicadores-section');
    
    if (!pilaresNav || !pilarContenido) return;
    
    // Mostrar navegación de pilares
    pilaresNav.classList.remove('hidden');
    
    // Renderizar botones de pilares
    pilaresNav.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            ${subareaData.pilares.map(pilar => `
                <button 
                    class="pilar-btn px-4 py-3 rounded-lg border-2 border-gray-200 bg-white hover:border-blue-500 hover:bg-blue-50 transition-all text-left"
                    data-pilar-id="${pilar.id}">
                    <h3 class="font-semibold text-gray-900 mb-1">${pilar.nombre}</h3>
                    <p class="text-xs text-gray-600 line-clamp-2">${pilar.descripcion.substring(0, 100)}...</p>
                </button>
            `).join('')}
        </div>
    `;
    
    // Agregar event listeners
    pilaresNav.querySelectorAll('.pilar-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const pilarId = e.currentTarget.dataset.pilarId;
            const pilar = subareaData.pilares.find(p => p.id === pilarId);
            
            if (pilar) {
                // Actualizar estado
                pilarSeleccionado = pilar;
                
                // Actualizar clases activas
                pilaresNav.querySelectorAll('.pilar-btn').forEach(b => {
                    b.classList.remove('border-blue-500', 'bg-blue-50');
                    b.classList.add('border-gray-200', 'bg-white');
                });
                e.currentTarget.classList.remove('border-gray-200', 'bg-white');
                e.currentTarget.classList.add('border-blue-500', 'bg-blue-50');
                
                // Mostrar contenido del pilar
                mostrarContenidoPilar(pilar, subareaData.indicadores || []);
            }
        });
    });
    
    // Ocultar sección de indicadores normal
    if (indicadoresSection) {
        indicadoresSection.classList.add('hidden');
    }
}

/**
 * Muestra el contenido del pilar seleccionado
 */
function mostrarContenidoPilar(pilar, todosLosIndicadores) {
    const pilarContenido = document.getElementById('pilar-contenido');
    if (!pilarContenido) return;
    
    // Filtrar indicadores del pilar
    const indicadoresDelPilar = todosLosIndicadores.filter(ind => 
        pilar.indicadores_codigos.includes(ind.codigo)
    );
    
    // Renderizar contenido
    pilarContenido.classList.remove('hidden');
    pilarContenido.innerHTML = `
        <div class="bg-white rounded-lg border border-gray-200 p-6 mb-6">
            <h2 class="text-2xl font-bold text-gray-900 mb-3">${pilar.nombre}</h2>
            <p class="text-gray-700 leading-relaxed mb-6">${pilar.descripcion}</p>
            
            ${indicadoresDelPilar.length > 0 ? `
                <div class="mt-6">
                    <h3 class="text-lg font-semibold text-gray-900 mb-4">Indicadores</h3>
                    ${renderizarIndicadoresHTML(indicadoresDelPilar)}
                </div>
            ` : `
                <div class="mt-6 text-center py-8 bg-gray-50 rounded-lg">
                    <p class="text-gray-500">No hay indicadores disponibles aún para este pilar.</p>
                    <p class="text-sm text-gray-400 mt-2">Los indicadores se agregarán próximamente.</p>
                </div>
            `}
        </div>
    `;
    
    // Cargar gráficos si hay indicadores
    if (indicadoresDelPilar.length > 0) {
        setTimeout(() => cargarGraficosIndicadores(), 100);
    }
}

/**
 * Renderiza los indicadores en HTML
 */
function renderizarIndicadores(indicadores) {
    const container = document.getElementById('indicadores-container');
    if (!container) return;
    
    if (indicadores.length === 0) {
        container.innerHTML = `
            <div class="bg-white rounded-lg border border-gray-200 p-6 text-center">
                <p class="text-gray-500">No hay indicadores disponibles aún para esta subárea.</p>
                <p class="text-sm text-gray-400 mt-2">Los indicadores se agregarán próximamente.</p>
            </div>
        `;
    } else {
        container.innerHTML = renderizarIndicadoresHTML(indicadores);
        // Cargar gráficos después de renderizar
        setTimeout(() => cargarGraficosIndicadores(), 100);
    }
}

/**
 * Genera el HTML para los indicadores
 */
function renderizarIndicadoresHTML(indicadores) {
    return indicadores.map(ind => `
        <article class="bg-white rounded-lg border border-gray-200 p-6 mb-4 shadow-sm hover:shadow-md transition-shadow">
            <div class="flex justify-between items-start mb-3">
                <div class="flex-1">
                    <h3 class="text-lg font-semibold text-gray-900 mb-2">${ind.nombre}</h3>
                    <p class="text-gray-700 mb-3">${ind.descripcion}</p>
                    <div class="flex items-center gap-4 text-sm text-gray-600">
                        <span><strong>Código:</strong> <code class="bg-gray-100 px-2 py-1 rounded">${ind.codigo}</code></span>
                        <span><strong>Unidad:</strong> ${ind.unidad}</span>
                    </div>
                </div>
            </div>
            
            <!-- Contenedor para gráfico -->
            <div id="grafico-${ind.codigo}" class="mt-4 p-4 bg-gray-50 rounded-lg" data-archivo-json="${ind.archivo_json}" data-codigo="${ind.codigo}">
                <div class="text-center text-gray-500 py-8">
                    <p class="text-sm">Cargando datos del indicador...</p>
                </div>
            </div>
        </article>
    `).join('');
}

/**
 * Carga los gráficos de todos los indicadores en la página.
 */
function cargarGraficosIndicadores() {
    const contenedores = document.querySelectorAll('[id^="grafico-"]');
    
    contenedores.forEach(contenedor => {
        const archivoJson = contenedor.dataset.archivoJson;
        const codigoIndicador = contenedor.dataset.codigo;
        
        if (archivoJson && codigoIndicador) {
            cargarDatosIndicador(archivoJson, codigoIndicador, contenedor);
        }
    });
}

/**
 * Carga los datos de un indicador desde un archivo JSON y renderiza el gráfico.
 */
async function cargarDatosIndicador(archivoJson, codigoIndicador, contenedor) {
    try {
        const ruta = `../data/indicadores/${archivoJson}`;
        const response = await fetch(ruta);
        
        if (!response.ok) {
            throw new Error(`Error al cargar ${archivoJson}: ${response.statusText}`);
        }
        
        const data = await response.json();
        renderizarGrafico(data, contenedor);
        
    } catch (error) {
        console.error(`Error al cargar indicador ${codigoIndicador}:`, error);
        contenedor.innerHTML = `
            <div class="text-center text-gray-500 py-8">
                <p class="text-sm">⚠️ No se pudieron cargar los datos del indicador.</p>
                <p class="text-xs text-gray-400 mt-1">${error.message}</p>
            </div>
        `;
    }
}

/**
 * Renderiza un gráfico simple con los datos del indicador.
 */
function renderizarGrafico(data, contenedor) {
    const { indicador, paises } = data;
    
    if (!paises || paises.length === 0) {
        contenedor.innerHTML = `
            <div class="text-center text-gray-500 py-8">
                <p class="text-sm">No hay datos disponibles para este indicador.</p>
            </div>
        `;
        return;
    }
    
    // Crear tabla con los datos
    let html = `
        <div class="mb-4">
            <h4 class="text-sm font-semibold text-gray-700 mb-2">${indicador.nombre}</h4>
            <p class="text-xs text-gray-500">Unidad: ${indicador.unidad}</p>
        </div>
        <div class="overflow-x-auto">
            <table class="min-w-full text-sm">
                <thead>
                    <tr class="bg-gray-100 border-b">
                        <th class="px-4 py-2 text-left font-semibold text-gray-700">País</th>
    `;
    
    // Obtener todos los años únicos
    const años = new Set();
    paises.forEach(pais => {
        Object.keys(pais.valores || {}).forEach(año => años.add(año));
    });
    const añosOrdenados = Array.from(años).sort();
    
    // Encabezados de años
    añosOrdenados.forEach(año => {
        html += `<th class="px-3 py-2 text-center font-semibold text-gray-700">${año}</th>`;
    });
    
    html += `
                    </tr>
                </thead>
                <tbody>
    `;
    
    // Filas de países
    paises.forEach((pais, idx) => {
        const bgClass = idx % 2 === 0 ? 'bg-white' : 'bg-gray-50';
        html += `
            <tr class="${bgClass} border-b">
                <td class="px-4 py-2 font-medium text-gray-900">${pais.nombre}</td>
        `;
        
        añosOrdenados.forEach(año => {
            const valor = pais.valores[año];
            const display = valor !== undefined && valor !== null 
                ? valor.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
                : '-';
            html += `<td class="px-3 py-2 text-center text-gray-700">${display}</td>`;
        });
        
        html += `</tr>`;
    });
    
    html += `
                </tbody>
            </table>
        </div>
        <p class="text-xs text-gray-400 mt-3 text-right">
            Última actualización: ${indicador.ultima_actualizacion || 'N/A'}
        </p>
    `;
    
    contenedor.innerHTML = html;
}
