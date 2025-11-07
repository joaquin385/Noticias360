"""
Script para normalizar fechas de todas las noticias extraídas.
Convierte las fechas a formato estándar y zona horaria local (UTC-3).
"""

import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from dateutil import parser
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Rutas
BASE_DIR = Path(__file__).parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
NORMALIZED_DIR = BASE_DIR / "data" / "normalized"

# Zona horaria de Argentina (UTC-3)
ARG_TIMEZONE = timezone(timedelta(hours=-3))


def parsear_fecha(fecha_str: str) -> datetime:
    """
    Parsea un string de fecha a objeto datetime.
    
    Args:
        fecha_str: String con la fecha en formato RSS o similar
    
    Returns:
        Objeto datetime con timezone
    """
    try:
        # dateutil.parser.parse puede manejar múltiples formatos
        dt = parser.parse(fecha_str)
        
        # Si no tiene timezone, asumir UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        return dt
    except Exception as e:
        logging.error(f"Error al parsear fecha '{fecha_str}': {str(e)}")
        # Retornar None en caso de error
        return None


def convertir_a_local(dt: datetime) -> datetime:
    """
    Convierte una fecha UTC a hora local de Argentina (UTC-3).
    
    Args:
        dt: Objeto datetime (debe tener timezone)
    
    Returns:
        Objeto datetime en zona horaria de Argentina
    """
    if dt is None:
        return None
    
    try:
        # Convertir a zona horaria de Argentina
        dt_local = dt.astimezone(ARG_TIMEZONE)
        return dt_local
    except Exception as e:
        logging.error(f"Error al convertir a hora local: {str(e)}")
        return None


def calcular_horas_atras(dt_local: datetime) -> float:
    """
    Calcula cuántas horas hace que se publicó la noticia.
    
    Args:
        dt_local: Fecha/hora local de la noticia
    
    Returns:
        Número de horas transcurridas (negativo si es futuro)
    """
    if dt_local is None:
        return None
    
    try:
        ahora_local = datetime.now(ARG_TIMEZONE)
        delta = ahora_local - dt_local
        horas_atras = delta.total_seconds() / 3600
        return round(horas_atras, 2)
    except Exception as e:
        logging.error(f"Error al calcular horas atrás: {str(e)}")
        return None


def normalizar_noticia(noticia: dict) -> dict:
    """
    Normaliza la fecha de una noticia individual.
    
    Args:
        noticia: Diccionario con datos de la noticia
    
    Returns:
        Diccionario con fechas normalizadas
    """
    # Copiar la noticia original
    noticia_normalizada = noticia.copy()
    
    # Leer fecha original
    fecha_original_str = noticia.get("fecha_original", "")
    
    if not fecha_original_str:
        logging.warning(f"Noticia sin fecha: {noticia.get('titulo', 'Sin título')[:50]}")
        noticia_normalizada["fecha_local"] = None
        noticia_normalizada["horas_atras"] = None
        return noticia_normalizada
    
    # Parsear fecha original
    dt = parsear_fecha(fecha_original_str)
    
    if dt is None:
        noticia_normalizada["fecha_local"] = None
        noticia_normalizada["horas_atras"] = None
        return noticia_normalizada
    
    # Convertir a hora local
    dt_local = convertir_a_local(dt)
    
    if dt_local is None:
        noticia_normalizada["fecha_local"] = None
        noticia_normalizada["horas_atras"] = None
        return noticia_normalizada
    
    # Guardar fecha en formato ISO string (fácil de leer)
    fecha_local_str = dt_local.strftime("%Y-%m-%d %H:%M:%S")
    
    # Calcular horas atrás
    horas_atras = calcular_horas_atras(dt_local)
    
    # Actualizar noticia
    noticia_normalizada["fecha_local"] = fecha_local_str
    noticia_normalizada["horas_atras"] = horas_atras
    
    return noticia_normalizada


def limpiar_carpeta_normalized():
    """
    Limpia todos los archivos JSON de la carpeta normalized para empezar una normalización limpia.
    """
    archivos_existentes = list(NORMALIZED_DIR.glob("*.json"))
    
    if archivos_existentes:
        logging.info(f"Limpiando {len(archivos_existentes)} archivos existentes en {NORMALIZED_DIR}")
        for archivo in archivos_existentes:
            try:
                archivo.unlink()
            except Exception as e:
                logging.error(f"Error al eliminar {archivo.name}: {str(e)}")
        logging.info("Carpeta normalized limpiada correctamente")
    else:
        logging.info("No hay archivos antiguos que limpiar")


def procesar_archivo(archivo_entrada: Path, archivo_salida: Path):
    """
    Procesa un archivo JSON de noticias y normaliza sus fechas.
    
    Args:
        archivo_entrada: Path del archivo de entrada (data/raw/)
        archivo_salida: Path del archivo de salida (data/normalized/)
    """
    try:
        logging.info(f"Procesando: {archivo_entrada.name}")
        
        # Leer archivo
        with open(archivo_entrada, "r", encoding="utf-8") as f:
            noticias = json.load(f)
        
        if not noticias:
            logging.warning(f"Archivo vacío: {archivo_entrada.name}")
            return
        
        # Normalizar cada noticia
        noticias_normalizadas = []
        for noticia in noticias:
            noticia_normalizada = normalizar_noticia(noticia)
            noticias_normalizadas.append(noticia_normalizada)
        
        # Guardar archivo normalizado
        with open(archivo_salida, "w", encoding="utf-8") as f:
            json.dump(noticias_normalizadas, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Guardado: {archivo_salida.name} ({len(noticias_normalizadas)} noticias)")
        
    except Exception as e:
        logging.error(f"Error al procesar {archivo_entrada.name}: {str(e)}")


def main():
    """
    Función principal que procesa todos los archivos raw.
    """
    logging.info("=" * 60)
    logging.info("NORMALIZACIÓN DE FECHAS")
    logging.info("=" * 60)
    
    # Crear directorio de salida si no existe
    NORMALIZED_DIR.mkdir(parents=True, exist_ok=True)
    
    # Limpiar archivos existentes para empezar limpio
    limpiar_carpeta_normalized()
    
    # Buscar todos los archivos JSON en data/raw/
    archivos_raw = list(RAW_DIR.glob("*.json"))
    
    if not archivos_raw:
        logging.warning(f"No se encontraron archivos en {RAW_DIR}")
        return
    
    logging.info(f"Procesando {len(archivos_raw)} archivos...")
    
    # Procesar cada archivo
    archivos_procesados = 0
    total_noticias = 0
    
    for archivo in archivos_raw:
        # Crear archivo de salida con el mismo nombre
        archivo_salida = NORMALIZED_DIR / archivo.name
        
        # Procesar archivo
        procesar_archivo(archivo, archivo_salida)
        
        archivos_procesados += 1
        
        # Contar noticias procesadas
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                noticias = json.load(f)
                total_noticias += len(noticias)
        except:
            pass
    
    # Resumen final
    logging.info("=" * 60)
    logging.info("RESUMEN DE NORMALIZACIÓN")
    logging.info(f"Archivos procesados: {archivos_procesados}/{len(archivos_raw)}")
    logging.info(f"Total de noticias normalizadas: {total_noticias}")
    logging.info(f"Archivos guardados en: {NORMALIZED_DIR}")
    logging.info("=" * 60)


if __name__ == "__main__":
    main()

