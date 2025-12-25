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
                htmlParts.push(`<p style="color: var(--color-tinta-alt); margin-bottom: 1rem; line-height: 1.7;">${parrafoActual.join(' ')}</p>`);
                parrafoActual = [];
            }
            continue;
        }
        
        // Detectar títulos (empiezan con número y punto)
        if (/^\d+\.\s/.test(linea)) {
            if (parrafoActual.length > 0) {
                htmlParts.push(`<p style="color: var(--color-tinta-alt); margin-bottom: 1rem; line-height: 1.7;">${parrafoActual.join(' ')}</p>`);
                parrafoActual = [];
            }
            htmlParts.push(`<h3 style="font-size: 1.2rem; font-weight: 400; color: var(--color-tinta); margin-top: 1.5rem; margin-bottom: 0.75rem; font-family: var(--font-serif);">${linea}</h3>`);
        } else {
            parrafoActual.push(linea);
        }
    }
    
    if (parrafoActual.length > 0) {
        htmlParts.push(`<p style="color: var(--color-tinta-alt); margin-bottom: 1rem; line-height: 1.7;">${parrafoActual.join(' ')}</p>`);
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
            ? `<p style="color: var(--color-tinta-alt); margin-top: 1rem; max-width: 65ch; line-height: 1.7;">${subareaData.descripcion}</p>`
            : (subareaData.descripcion_detallada
                ? `<div style="margin-top: 1rem; max-width: 75ch; background-color: var(--color-papel); border: 1px solid var(--color-borde-suave); border-radius: 2px; padding: 2rem;">${formatearDescripcionDetallada(subareaData.descripcion_detallada)}</div>`
                : `<p style="color: var(--color-tinta-alt); margin-top: 1rem; max-width: 65ch; line-height: 1.7;">${subareaData.descripcion}</p>`);
        
        header.innerHTML = `
            <div class="flex items-center gap-3 mb-2">
                <span class="text-3xl">${areaData.icono || '📊'}</span>
                <div>
                    <h1 style="font-size: 2rem; font-weight: 400; color: var(--color-tinta); font-family: var(--font-serif);">${subareaData.nombre}</h1>
                    <p style="font-size: 0.875rem; color: var(--color-texto-secundario); margin-top: 0.5rem;">${areaData.nombre}</p>
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
                    class="pilar-btn"
                    data-pilar-id="${pilar.id}">
                    <h3>${pilar.nombre}</h3>
                    <p>${pilar.descripcion.substring(0, 100)}...</p>
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
                    b.classList.remove('active');
                });
                e.currentTarget.classList.add('active');
                
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
        <h2>${pilar.nombre}</h2>
        <p style="color: var(--color-tinta-alt); line-height: 1.7; margin-bottom: 2rem;">${pilar.descripcion}</p>
        
        ${indicadoresDelPilar.length > 0 ? `
            <div style="margin-top: 2rem;">
                <h3>Indicadores</h3>
                ${renderizarIndicadoresHTML(indicadoresDelPilar)}
            </div>
        ` : `
            <div style="text-align: center; padding: 3rem 0; color: var(--color-texto-secundario);">
                <p>No hay indicadores disponibles aún para este pilar.</p>
                <p style="font-size: 0.875rem; color: var(--color-texto-terciario); margin-top: 0.5rem;">Los indicadores se agregarán próximamente.</p>
            </div>
        `}
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
        <article class="indicador-card">
            <h3>${ind.nombre}</h3>
            <p>${ind.descripcion}</p>
            <div style="display: flex; align-items: center; gap: 1.5rem; font-size: 0.875rem; color: var(--color-texto-secundario); margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--color-borde-suave);">
                <span><strong>Código:</strong> <code>${ind.codigo}</code></span>
                <span><strong>Unidad:</strong> ${ind.unidad}</span>
            </div>
            
            <!-- Contenedor para gráfico -->
            <div id="grafico-${ind.codigo}" data-archivo-json="${ind.archivo_json}" data-codigo="${ind.codigo}">
                <div style="text-align: center; color: var(--color-texto-secundario); padding: 2rem 0;">
                    <p style="font-size: 0.875rem;">Cargando datos del indicador...</p>
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
            <div style="text-align: center; color: var(--color-texto-secundario); padding: 2rem 0;">
                <p style="font-size: 0.875rem;">⚠️ No se pudieron cargar los datos del indicador.</p>
                <p style="font-size: 0.75rem; color: var(--color-texto-terciario); margin-top: 0.5rem;">${error.message}</p>
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
            <div style="text-align: center; color: var(--color-texto-secundario); padding: 2rem 0;">
                <p style="font-size: 0.875rem;">No hay datos disponibles para este indicador.</p>
            </div>
        `;
        return;
    }
    
    // Crear tabla con los datos
    let html = `
        <div style="margin-bottom: 1.5rem;">
            <h4 style="font-size: 0.9375rem; font-weight: 400; color: var(--color-tinta); margin-bottom: 0.5rem; font-family: var(--font-serif);">${indicador.nombre}</h4>
            <p style="font-size: 0.75rem; color: var(--color-texto-secundario);">Unidad: ${indicador.unidad}</p>
        </div>
        <div style="overflow-x: auto;">
            <table>
                <thead>
                    <tr>
                        <th>País</th>
    `;
    
    // Obtener todos los años únicos
    const años = new Set();
    paises.forEach(pais => {
        Object.keys(pais.valores || {}).forEach(año => años.add(año));
    });
    const añosOrdenados = Array.from(años).sort();
    
    // Encabezados de años
    añosOrdenados.forEach(año => {
        html += `<th style="text-align: center;">${año}</th>`;
    });
    
    html += `
                    </tr>
                </thead>
                <tbody>
    `;
    
    // Filas de países
    paises.forEach((pais) => {
        html += `
            <tr>
                <td style="font-weight: 400; color: var(--color-tinta);">${pais.nombre}</td>
        `;
        
        añosOrdenados.forEach(año => {
            const valor = pais.valores[año];
            const display = valor !== undefined && valor !== null 
                ? valor.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
                : '-';
            html += `<td style="text-align: center; color: var(--color-tinta-alt);">${display}</td>`;
        });
        
        html += `</tr>`;
    });
    
    html += `
                </tbody>
            </table>
        </div>
        <p style="font-size: 0.75rem; color: var(--color-texto-terciario); margin-top: 1rem; text-align: right;">
            Última actualización: ${indicador.ultima_actualizacion || 'N/A'}
        </p>
    `;
    
    contenedor.innerHTML = html;
}
