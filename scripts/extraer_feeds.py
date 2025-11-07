"""
Script para extraer noticias de todas las fuentes RSS configuradas.
Descarga los datos crudos y los guarda en archivos JSON separados por fuente.
"""

import feedparser
import json
import os
from pathlib import Path
from datetime import datetime
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Rutas
BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE = BASE_DIR / "feeds_config.json"
OUTPUT_DIR = BASE_DIR / "data" / "raw"


def generar_nombre_archivo(fuente: str, categoria: str) -> str:
    """
    Genera un nombre de archivo válido basado en fuente y categoría.
    Ejemplo: "Clarín" + "Economía" -> "clarin_economia.json"
    """
    # Normaliza para crear nombre de archivo válido
    fuente_norm = fuente.lower().replace(" ", "_").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    categoria_norm = categoria.lower().replace(" ", "_").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    
    # Limpia caracteres especiales
    fuente_norm = "".join(c for c in fuente_norm if c.isalnum() or c == "_")
    categoria_norm = "".join(c for c in categoria_norm if c.isalnum() or c == "_")
    
    return f"{fuente_norm}_{categoria_norm}.json"


def extraer_noticias_feed(feed_config: dict) -> list:
    """
    Extrae noticias de un feed RSS específico.
    
    Args:
        feed_config: Diccionario con configuración del feed (fuente, url, categoria, zona_horaria)
    
    Returns:
        Lista de diccionarios con las noticias extraídas
    """
    url = feed_config["url"]
    fuente = feed_config["fuente"]
    categoria = feed_config["categoria"]
    
    try:
        logging.info(f"Descargando feed: {fuente} - {categoria}")
        logging.info(f"URL: {url}")
        
        # Descargar y parsear el feed
        feed = feedparser.parse(url)
        
        if feed.bozo:
            logging.warning(f"Feed puede tener errores de parsing: {feed.bozo_exception}")
        
        logging.info(f"Noticias encontradas: {len(feed.entries)}")
        
        noticias = []
        for entry in feed.entries:
            noticia = {
                "titulo": entry.get("title", ""),
                "link": entry.get("link", ""),
                "fecha_original": entry.get("published", entry.get("updated", "")),
                "resumen": entry.get("summary", entry.get("description", "")).strip(),
                "fuente": fuente,
                "categoria": categoria,
                "url_feed": url
            }
            
            # Agregar campos adicionales si están disponibles
            if hasattr(entry, "author") and entry.author:
                noticia["autor"] = entry.author
            
            if hasattr(entry, "tags") and entry.tags:
                noticia["tags"] = [tag.term for tag in entry.tags]
            
            noticias.append(noticia)
        
        return noticias
        
    except Exception as e:
        logging.error(f"Error al procesar feed {fuente} - {categoria}: {str(e)}")
        return []


def limpiar_carpeta_raw():
    """
    Limpia todos los archivos JSON de la carpeta raw para empezar una extracción limpia.
    """
    archivos_existentes = list(OUTPUT_DIR.glob("*.json"))
    
    if archivos_existentes:
        logging.info(f"Limpiando {len(archivos_existentes)} archivos existentes en {OUTPUT_DIR}")
        for archivo in archivos_existentes:
            try:
                archivo.unlink()
            except Exception as e:
                logging.error(f"Error al eliminar {archivo.name}: {str(e)}")
        logging.info("Carpeta raw limpiada correctamente")
    else:
        logging.info("No hay archivos antiguos que limpiar")


def guardar_noticias(noticias: list, nombre_archivo: str):
    """
    Guarda las noticias en un archivo JSON.
    Sobrescribe el archivo si ya existe.
    
    Args:
        noticias: Lista de diccionarios con noticias
        nombre_archivo: Nombre del archivo de salida
    """
    archivo_completo = OUTPUT_DIR / nombre_archivo
    
    try:
        # Abrir en modo 'w' que sobrescribe automáticamente
        with open(archivo_completo, "w", encoding="utf-8") as f:
            json.dump(noticias, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Archivo guardado: {archivo_completo.name} ({len(noticias)} noticias)")
            
    except Exception as e:
        logging.error(f"Error al guardar archivo {nombre_archivo}: {str(e)}")


def main():
    """
    Función principal que lee la configuración y procesa todos los feeds.
    """
    logging.info("=" * 60)
    logging.info("EXTRACCIÓN DE NOTICIAS RSS")
    logging.info("=" * 60)
    
    # Crear directorio de salida si no existe
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Limpiar archivos existentes para empezar limpio
    limpiar_carpeta_raw()
    
    # Leer configuración
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            feeds_config = json.load(f)
    except Exception as e:
        logging.error(f"Error al leer archivo de configuración: {str(e)}")
        return
    
    logging.info(f"Procesando {len(feeds_config)} feeds...")
    
    # Procesar cada feed
    total_noticias = 0
    feeds_exitosos = 0
    
    for feed_config in feeds_config:
        noticias = extraer_noticias_feed(feed_config)
        
        if noticias:
            # Generar nombre de archivo
            nombre_archivo = generar_nombre_archivo(
                feed_config["fuente"],
                feed_config["categoria"]
            )
            
            # Guardar noticias
            guardar_noticias(noticias, nombre_archivo)
            
            total_noticias += len(noticias)
            feeds_exitosos += 1
    
    # Resumen final
    logging.info("=" * 60)
    logging.info("RESUMEN DE EXTRACCIÓN")
    logging.info(f"Feeds procesados exitosamente: {feeds_exitosos}/{len(feeds_config)}")
    logging.info(f"Total de noticias extraídas: {total_noticias}")
    logging.info(f"Archivos guardados en: {OUTPUT_DIR}")
    logging.info("=" * 60)


if __name__ == "__main__":
    main()

