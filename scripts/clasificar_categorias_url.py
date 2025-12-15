"""
Script para clasificar noticias por categoría basándose únicamente en la URL.
Usa patrones heurísticos para inferir la categoría sin analizar el contenido.
"""

import json
import re
from pathlib import Path
import shutil
from datetime import datetime
from typing import Dict, List
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Rutas
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
FRONTEND_DIR = BASE_DIR / "frontend" / "data"

# Categorías disponibles
CATEGORIAS = [
    "politica",
    "economia",
    "sociedad",
    "deportes",
    "cultura",
    "espectaculos",
    "tecnologia",
    "internacional",
    "salud",
    "ciencia",
    "otros"
]

# Patrones por categoría (ordenados por prioridad/orden jerárquico)
PATRONES_CATEGORIAS = {
    "politica": [
        r'/politica/',
        r'/politico/',
        r'/elecciones',
        r'/votacion',
        r'/congreso',
        r'/senado',
        r'/diputados',
        r'/gobierno',
        r'/presidente',
        r'/presidencial',
        r'/campana',
        r'/partido',
        r'/oposicion',
        r'/jefe-de-gobierno',
        r'/intendente',
        r'/rss/secciones/el-pais/notas',  # Página 12
    ],
    "economia": [
        r'/economia/',
        r'/economico/',
        r'/finanzas/',
        r'/financiero/',
        r'/mercados/',
        r'/dolar',
        r'/rss/secciones/economia/notas',  # Página 12
        r'/peso',
        r'/inflacion',
        r'/desempleo',
        r'/empleo',
        r'/bcra',
        r'/banco-central',
        r'/reservas',
        r'/bonos',
        r'/acciones',
        r'/bolsa',
        r'/cotizacion',
        r'/tipo-de-cambio',
        r'/comercio-exterior',
        r'/exportacion',
        r'/importacion',
        r'/pbi',
        r'/producto-bruto',
        r'/impuestos',
        r'/tributos',
        r'/afip',
        r'/presupuesto',
    ],
    "deportes": [
        r'/deportes/',
        r'/deporte/',
        r'/futbol/',
        r'/futbolistico/',
        r'/tenis',
        r'/basquet',
        r'/basket',
        r'/rugby',
        r'/boxeo',
        r'/automovilismo',
        r'/formula-1',
        r'/f1',
        r'/voley',
        r'/voleibol',
        r'/hockey',
        r'/natacion',
        r'/atletismo',
        r'/ciclismo',
        r'/golf',
        r'/motociclismo',
        r'/olimpicos',
        r'/olimpico',
    ],
    "salud": [
        r'/salud/',
        r'/medicina/',
        r'/medico/',
        r'/medicos/',
        r'/hospital',
        r'/clinica',
        r'/vacuna',
        r'/vacunacion',
        r'/enfermedad',
        r'/tratamiento',
        r'/operacion',
        r'/cirugia',
        r'/epidemia',
        r'/pandemia',
        r'/contagio',
        r'/pandemia',
        r'/nutricion',
        r'/dieta',
        r'/bienestar',
    ],
    "tecnologia": [
        r'/tecnologia/',
        r'/tecnologico/',
        r'/tech/',
        r'/informatica',
        r'/computacion',
        r'/software',
        r'/hardware',
        r'/internet',
        r'/redes-sociales',
        r'/smartphone',
        r'/iphone',
        r'/android',
        r'/apple',
        r'/google',
        r'/microsoft',
        r'/facebook',
        r'/instagram',
        r'/twitter',
        r'/x\.com',
        r'/tiktok',
        r'/youtube',
        r'/app',
        r'/aplicacion',
        r'/digital',
        r'/inteligencia-artificial',
        r'/ia/',
        r'/ai/',
        r'/chatgpt',
        r'/robotica',
    ],
    "internacional": [
        r'/internacional/',
        r'/mundo/',
        r'/el-mundo/',
        r'/rss/secciones/el-mundo/notas',  # Página 12
        r'/mundial/',
        r'/global/',
        r'/exterior/',
        r'/extranjero',
        r'/estados-unidos',
        r'/usa',
        r'/eeuu',
        r'/ee\.uu\.',
        r'/brasil',
        r'/chile',
        r'/uruguay',
        r'/paraguay',
        r'/bolivia',
        r'/colombia',
        r'/mexico',
        r'/españa',
        r'/europa',
        r'/unión-europea',
        r'/ue/',
        r'/china',
        r'/rusia',
        r'/onu',
        r'/naciones-unidas',
        r'/g20',
        r'/mercosur',
    ],
    "ciencia": [
        r'/ciencia/',
        r'/cientifico/',
        r'/investigacion/',
        r'/investigador/',
        r'/universidad',
        r'/universitario',
        r'/estudio',
        r'/descubrimiento',
        r'/nasa',
        r'/espacio',
        r'/astronomia',
        r'/fisica',
        r'/quimica',
        r'/biologia',
        r'/genetica',
        r'/clima',
        r'/medio-ambiente',
        r'/medioambiente',
        r'/ecologia',
        r'/sustentabilidad',
    ],
    "sociedad": [
        r'/sociedad/',
        r'/social/',
        r'/comunidad',
        r'/barrio',
        r'/vecinos',
        r'/seguridad',
        r'/policia',
        r'/robo',
        r'/crimen',
        r'/delito',
        r'/violencia',
        r'/accidente',
        r'/siniestro',
        r'/educacion/',
        r'/educativo/',
        r'/escuela',
        r'/colegio',
        r'/universidad',
        r'/trabajo',
        r'/empleo',
        r'/desempleo',
        r'/vivienda',
        r'/inmobiliaria',
        r'/transporte',
        r'/metro',
        r'/subte',
        r'/colectivo',
        r'/tren',
        r'/rss/secciones/sociedad/notas',  # Página 12
    ],
    "cultura": [
        r'/cultura/',
        r'/cultural/',
        r'/arte/',
        r'/artistico/',
        r'/museo',
        r'/literatura',
        r'/libro',
        r'/escritor',
        r'/poesia',
        r'/teatro',
        r'/danza',
        r'/fotografia',
        r'/pintura',
        r'/escultura',
        r'/historia',
        r'/historico',
        r'/patrimonio',
    ],
    "espectaculos": [
        r'/espectaculos/',
        r'/espectaculo/',
        r'/entretenimiento',
        r'/show',
        r'/tv/',
        r'/television',
        r'/tele',
        r'/actor',
        r'/actriz',
        r'/pelicula',
        r'/cine',
        r'/cinematografico',
        r'/serie',
        r'/netflix',
        r'/streaming',
        r'/youtube',
        r'/musica',
        r'/musical',
        r'/cantante',
        r'/banda',
        r'/concierto',
        r'/recital',
        r'/festival',
        r'/comedia',
        r'/humor',
    ],
}


def categorizar_por_url(url: str, url_feed: str = None) -> str:
    """
    Clasifica una noticia por categoría basándose en su URL o URL del feed.
    
    Args:
        url: URL de la noticia
        url_feed: URL del feed RSS (opcional, usado cuando la URL no contiene la categoría)
    
    Returns:
        Categoría detectada (string)
    
    Reglas jerárquicas:
    1. Primero intenta clasificar usando url_feed si está disponible
    2. Si url_feed no tiene categoría, usa la url
    3. Si cumple múltiples patrones, retorna el primero encontrado según el orden de PATRONES_CATEGORIAS
    4. Si no cumple ningún patrón, retorna "otros"
    """
    # Lista de URLs a analizar (prioridad: url_feed primero, luego url)
    urls_a_analizar = []
    
    if url_feed:
        urls_a_analizar.append(url_feed.lower())
    if url:
        urls_a_analizar.append(url.lower())
    
    if not urls_a_analizar:
        return "otros"
    
    # Verificar cada categoría en orden (determina la jerarquía)
    for categoria, patrones in PATRONES_CATEGORIAS.items():
        for patron in patrones:
            # Buscar el patrón en todas las URLs
            for url_analizar in urls_a_analizar:
                if re.search(patron, url_analizar, re.IGNORECASE):
                    return categoria
    
    # Si no coincide con ningún patrón, retorna "otros"
    return "otros"


def procesar_json(archivo_entrada: Path, archivo_salida: Path = None):
    """
    Procesa un archivo JSON y agrega la columna categoria_url.
    
    Args:
        archivo_entrada: Path del archivo JSON de entrada
        archivo_salida: Path del archivo JSON de salida (si es None, sobrescribe el de entrada)
    """
    if archivo_salida is None:
        archivo_salida = archivo_entrada
    
    try:
        # Leer JSON
        with open(archivo_entrada, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        noticias = data.get("noticias", [])
        if not noticias:
            logging.warning(f"No hay noticias en {archivo_entrada.name}")
            return
        
        logging.info(f"Procesando {len(noticias)} noticias...")
        
        # Contadores por categoría
        contadores = {cat: 0 for cat in CATEGORIAS}
        
        # Procesar cada noticia
        for noticia in noticias:
            link = noticia.get("link", "")
            url_feed = noticia.get("url_feed", "")
            categoria_url = categorizar_por_url(link, url_feed)
            noticia["categoria_url"] = categoria_url
            contadores[categoria_url] = contadores.get(categoria_url, 0) + 1
        
        # Guardar JSON actualizado
        with open(archivo_salida, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Archivo guardado: {archivo_salida.name}")
        
        # Mostrar resumen
        logging.info("=" * 60)
        logging.info("RESUMEN DE CLASIFICACIÓN POR URL")
        logging.info("=" * 60)
        for categoria, cantidad in sorted(contadores.items(), key=lambda x: x[1], reverse=True):
            if cantidad > 0:
                logging.info(f"  {categoria}: {cantidad} noticias")
        logging.info("=" * 60)
        
    except Exception as e:
        logging.error(f"Error al procesar {archivo_entrada.name}: {str(e)}")


def limpiar_frontend_data(fecha_actual: str):
    """
    Limpia archivos antiguos en frontend/data/ para evitar acumulación.

    Reglas:
    - Mantener solo:
      - noticias_YYYY-MM-DD.json de la fecha_actual
      - resumenes_YYYY-MM-DD.json de la fecha_actual
      - temas_latest.json (no se toca)
    - Eliminar cualquier otro archivo noticias_*.json o resumenes_*.json
    """
    try:
        FRONTEND_DIR.mkdir(parents=True, exist_ok=True)

        patron_noticias_hoy = f"noticias_{fecha_actual}.json"
        patron_resumenes_hoy = f"resumenes_{fecha_actual}.json"

        # Eliminar noticias_*.json antiguos
        for archivo in FRONTEND_DIR.glob("noticias_*.json"):
            if archivo.name != patron_noticias_hoy:
                try:
                    archivo.unlink()
                    logging.info(f"Eliminado archivo antiguo de noticias: {archivo.name}")
                except Exception as e:
                    logging.warning(f"No se pudo eliminar {archivo}: {str(e)}")

        # Eliminar resumenes_*.json antiguos
        for archivo in FRONTEND_DIR.glob("resumenes_*.json"):
            if archivo.name != patron_resumenes_hoy:
                try:
                    archivo.unlink()
                    logging.info(f"Eliminado archivo antiguo de resúmenes: {archivo.name}")
                except Exception as e:
                    logging.warning(f"No se pudo eliminar {archivo}: {str(e)}")

    except Exception as e:
        logging.error(f"Error al limpiar frontend/data: {str(e)}")


def main():
    """
    Función principal que procesa el archivo JSON más reciente.
    """
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    nombre_archivo_noticias = f"noticias_{fecha_actual}.json"

    archivo_data = DATA_DIR / nombre_archivo_noticias
    archivo_frontend = FRONTEND_DIR / nombre_archivo_noticias
    
    logging.info("=" * 60)
    logging.info("CLASIFICACIÓN DE NOTICIAS POR URL")
    logging.info(f"Fecha: {fecha_actual}")
    logging.info("=" * 60)
    
    # Procesar archivo en data/
    if archivo_data.exists():
        logging.info(f"Procesando: {archivo_data.name}")
        procesar_json(archivo_data)

        # Antes de copiar, limpiar archivos antiguos del frontend
        limpiar_frontend_data(fecha_actual)

        # Copiar a frontend (sobrescribiendo el archivo del día si existe)
        try:
            FRONTEND_DIR.mkdir(parents=True, exist_ok=True)
            shutil.copy2(archivo_data, archivo_frontend)
            logging.info(f"Copiado a frontend: {archivo_frontend.name}")

            # Volver a procesar en el archivo de frontend para asegurar que tenga categoria_url
            procesar_json(archivo_frontend, archivo_frontend)
        except Exception as e:
            logging.error(f"No se pudo copiar a frontend/data: {str(e)}")
    else:
        logging.warning(f"No se encontró el archivo: {archivo_data}")
        logging.info("Buscando archivos disponibles...")
        
        # Buscar archivos disponibles
        archivos_disponibles = sorted(DATA_DIR.glob("noticias_*.json"))
        if archivos_disponibles:
            ultimo_archivo = archivos_disponibles[-1]
            logging.info(f"Procesando último archivo disponible: {ultimo_archivo.name}")
            procesar_json(ultimo_archivo)
        else:
            logging.error("No se encontraron archivos de noticias para procesar")


if __name__ == "__main__":
    main()

