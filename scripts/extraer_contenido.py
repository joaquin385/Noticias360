"""
Script para extraer el contenido completo de las noticias mediante web scraping.
Lee noticias desde frontend/data/ y genera un nuevo JSON con contenido completo.
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
import logging

try:
    from newspaper import Article
    NEWSPAPER_DISPONIBLE = True
except ImportError:
    NEWSPAPER_DISPONIBLE = False
    logging.warning("newspaper3k no está instalado")

try:
    import trafilatura
    TRAFILATURA_DISPONIBLE = True
except ImportError:
    TRAFILATURA_DISPONIBLE = False
    logging.warning("trafilatura no está instalado")

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Rutas
BASE_DIR = Path(__file__).parent.parent
FRONTEND_DIR = BASE_DIR / "frontend" / "data"  # Para leer noticias
DATA_DIR = BASE_DIR / "data"  # Para guardar contenido

# Parámetros
CATEGORIAS_PROCESAR = ['internacional', 'politica', 'economia']  # Solo estas categorías
MAX_NOTICIAS_EXTRAER = 150  # Límite total después de filtrar
DELAY_ENTRE_REQUESTS = 1.5  # Segundos entre cada extracción
TIMEOUT = 10  # Segundos para timeout


def extraer_con_newspaper(url: str, idioma: str = 'es') -> Optional[str]:
    """
    Extrae contenido usando Newspaper3k.
    """
    if not NEWSPAPER_DISPONIBLE:
        return None
    
    try:
        article = Article(url, language=idioma)
        article.download()
        article.parse()
        
        if article.text and len(article.text) > 100:
            return article.text
        return None
        
    except Exception as e:
        logging.debug(f"Newspaper falló para {url}: {str(e)}")
        return None


def extraer_con_trafilatura(url: str) -> Optional[str]:
    """
    Extrae contenido usando Trafilatura.
    """
    if not TRAFILATURA_DISPONIBLE:
        return None
    
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return None
        
        contenido = trafilatura.extract(downloaded, include_comments=False)
        
        if contenido and len(contenido) > 100:
            return contenido
        return None
        
    except Exception as e:
        logging.debug(f"Trafilatura falló para {url}: {str(e)}")
        return None


def extraer_contenido_noticia(noticia: Dict) -> Dict:
    """
    Extrae el contenido completo de una noticia.
    Retorna una COPIA de la noticia con campos adicionales.
    """
    # Crear copia para no modificar original
    noticia_con_contenido = noticia.copy()
    
    url = noticia.get('link', '')
    
    if not url:
        noticia_con_contenido['contenido_extraido'] = False
        noticia_con_contenido['metodo_extraccion'] = "sin_link"
        return noticia_con_contenido
    
    contenido = None
    metodo = None
    
    # Intentar con Newspaper3k
    contenido = extraer_con_newspaper(url)
    if contenido:
        metodo = "newspaper3k"
    
    # Si falla, intentar con Trafilatura
    if not contenido:
        contenido = extraer_con_trafilatura(url)
        if contenido:
            metodo = "trafilatura"
    
    # Agregar campos
    if contenido:
        noticia_con_contenido['contenido_completo'] = contenido
        noticia_con_contenido['contenido_extraido'] = True
        noticia_con_contenido['metodo_extraccion'] = metodo
        noticia_con_contenido['palabras_contenido'] = len(contenido.split())
        logging.info(f"  ✓ {metodo}: {noticia.get('titulo', '')[:50]}... ({noticia_con_contenido['palabras_contenido']} palabras)")
    else:
        noticia_con_contenido['contenido_extraido'] = False
        noticia_con_contenido['metodo_extraccion'] = "rss_only"
        logging.debug(f"  ✗ No extraído: {noticia.get('titulo', '')[:50]}...")
    
    return noticia_con_contenido


def main():
    logging.info("=" * 70)
    logging.info("EXTRACCIÓN DE CONTENIDO COMPLETO")
    logging.info("=" * 70)
    
    # 1. Cargar archivo de noticias más reciente
    archivos = list(FRONTEND_DIR.glob("noticias_[0-9]*.json"))
    if not archivos:
        logging.error("No se encontraron archivos de noticias en frontend/data/")
        return
    
    archivo_entrada = max(archivos, key=lambda p: p.stat().st_mtime)
    logging.info(f"Leyendo: {archivo_entrada.name}")
    
    with open(archivo_entrada, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    fecha_consolidacion = data.get('fecha_consolidacion', datetime.now().strftime('%Y-%m-%d'))
    noticias_originales = data.get('noticias', [])
    
    # 2. Filtrar solo categorías de interés: Internacional, Política, Economía
    noticias_filtradas = [
        n for n in noticias_originales 
        if n.get('categoria_url', '').lower() in CATEGORIAS_PROCESAR
    ]
    
    logging.info(f"Total de noticias: {len(noticias_originales)}")
    logging.info(f"Noticias filtradas (Internacional/Política/Economía): {len(noticias_filtradas)}")
    
    # 3. Limitar a MAX_NOTICIAS_EXTRAER
    noticias_a_procesar = noticias_filtradas[:MAX_NOTICIAS_EXTRAER]
    total = len(noticias_a_procesar)
    
    logging.info(f"Noticias a procesar con scraping: {total}")
    logging.info(f"Categorías: {', '.join(CATEGORIAS_PROCESAR)}")
    logging.info(f"Delay entre requests: {DELAY_ENTRE_REQUESTS}s")
    logging.info(f"Tiempo estimado: ~{int(total * DELAY_ENTRE_REQUESTS / 60)} minutos\n")
    
    # 4. Extraer contenido de cada noticia
    noticias_con_contenido = []
    exitosas = 0
    fallidas = 0
    
    for idx, noticia in enumerate(noticias_a_procesar, 1):
        if idx % 20 == 0:
            logging.info(f"Progreso: {idx}/{total} ({int(idx/total*100)}%) - Exitosas: {exitosas}, Fallidas: {fallidas}")
        
        noticia_procesada = extraer_contenido_noticia(noticia)
        noticias_con_contenido.append(noticia_procesada)
        
        if noticia_procesada.get('contenido_extraido'):
            exitosas += 1
        else:
            fallidas += 1
        
        # Delay entre requests para no sobrecargar servidores
        time.sleep(DELAY_ENTRE_REQUESTS)
    
    # 5. Crear nuevo archivo con contenido completo
    nombre_archivo = f"noticias_contenido_{fecha_consolidacion}.json"
    archivo_salida = DATA_DIR / nombre_archivo
    
    resultado = {
        'fecha_consolidacion': fecha_consolidacion,
        'fecha_scraping': datetime.now().isoformat(),
        'categorias_procesadas': CATEGORIAS_PROCESAR,
        'total_noticias': len(noticias_con_contenido),
        'noticias_con_contenido': exitosas,
        'noticias_sin_contenido': fallidas,
        'tasa_exito': round(exitosas / total * 100, 2) if total > 0 else 0,
        'noticias': noticias_con_contenido
    }
    
    # Asegurar que existe el directorio data/
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Guardar archivo principal
    with open(archivo_salida, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    
    # Copiar también como "latest"
    import shutil
    archivo_latest = DATA_DIR / "noticias_contenido_latest.json"
    shutil.copy2(archivo_salida, archivo_latest)
    
    # 6. Resumen final
    logging.info("\n" + "=" * 70)
    logging.info("EXTRACCIÓN COMPLETADA")
    logging.info("=" * 70)
    logging.info(f"✓ Contenido extraído: {exitosas}/{total} ({resultado['tasa_exito']}%)")
    logging.info(f"✗ Fallidas: {fallidas}")
    logging.info(f"📁 Archivo guardado en: data/{nombre_archivo}")
    logging.info(f"📁 Archivo latest: data/noticias_contenido_latest.json")
    
    # Estadísticas por método
    metodos = {}
    for n in noticias_con_contenido:
        metodo = n.get('metodo_extraccion', 'desconocido')
        metodos[metodo] = metodos.get(metodo, 0) + 1
    
    logging.info("\nMétodos de extracción:")
    for metodo, cantidad in metodos.items():
        logging.info(f"  {metodo}: {cantidad}")
    
    logging.info("=" * 70)


if __name__ == "__main__":
    main()

