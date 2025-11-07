"""
Script para integrar todas las fuentes de noticias en un único dataset diario.
Combina todos los archivos de data/normalized/, elimina duplicados y ordena por fecha.
"""

import json
from pathlib import Path
from datetime import datetime
import logging
from typing import List, Dict

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Rutas
BASE_DIR = Path(__file__).parent.parent
NORMALIZED_DIR = BASE_DIR / "data" / "normalized"
OUTPUT_DIR = BASE_DIR / "data"
FRONTEND_DIR = BASE_DIR / "frontend" / "data"


def leer_todas_las_noticias() -> List[Dict]:
    """
    Lee todos los archivos JSON de data/normalized/ y retorna una lista única.
    
    Returns:
        Lista con todas las noticias de todas las fuentes
    """
    todas_las_noticias = []
    
    # Buscar todos los archivos JSON
    archivos_json = list(NORMALIZED_DIR.glob("*.json"))
    
    if not archivos_json:
        logging.warning(f"No se encontraron archivos en {NORMALIZED_DIR}")
        return []
    
    logging.info(f"Leyendo {len(archivos_json)} archivos...")
    
    # Leer cada archivo y agregar las noticias
    for archivo in archivos_json:
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                noticias = json.load(f)
                todas_las_noticias.extend(noticias)
                logging.info(f"  {archivo.name}: {len(noticias)} noticias")
        except Exception as e:
            logging.error(f"Error al leer {archivo.name}: {str(e)}")
    
    return todas_las_noticias


def eliminar_duplicados(noticias: List[Dict]) -> List[Dict]:
    """
    Elimina noticias duplicadas basándose en el campo 'link'.
    
    Args:
        noticias: Lista de noticias
    
    Returns:
        Lista sin duplicados
    """
    total_inicial = len(noticias)
    
    # Usar un set para trackear links únicos
    links_vistos = set()
    noticias_unicas = []
    
    for noticia in noticias:
        link = noticia.get("link", "")
        
        # Si el link está vacío o ya fue visto, saltar
        if not link or link in links_vistos:
            continue
        
        # Marcar como visto y agregar
        links_vistos.add(link)
        noticias_unicas.append(noticia)
    
    duplicados_eliminados = total_inicial - len(noticias_unicas)
    
    if duplicados_eliminados > 0:
        logging.info(f"Eliminados {duplicados_eliminados} duplicados")
    else:
        logging.info("No se encontraron duplicados")
    
    return noticias_unicas


def ordenar_por_fecha(noticias: List[Dict]) -> List[Dict]:
    """
    Ordena las noticias por fecha descendente (más recientes primero).
    
    Args:
        noticias: Lista de noticias
    
    Returns:
        Lista ordenada por fecha_descendente
    """
    def obtener_fecha_sort(noticia: Dict) -> str:
        """
        Obtiene la fecha para ordenamiento.
        Usa fecha_local si está disponible, si no fecha_original.
        """
        fecha_local = noticia.get("fecha_local")
        if fecha_local:
            return fecha_local
        
        fecha_original = noticia.get("fecha_original", "")
        return fecha_original
    
    try:
        # Ordenar por fecha_local o fecha_original, descendente
        noticias_ordenadas = sorted(
            noticias,
            key=obtener_fecha_sort,
            reverse=True
        )
        
        logging.info("Noticias ordenadas por fecha (más recientes primero)")
        return noticias_ordenadas
        
    except Exception as e:
        logging.error(f"Error al ordenar noticias: {str(e)}")
        return noticias


def guardar_dataset(noticias: List[Dict], fecha_str: str):
    """
    Guarda el dataset final en un archivo JSON con nombre incluyendo la fecha.
    
    Args:
        noticias: Lista de noticias consolidadas
        fecha_str: Fecha en formato YYYY-MM-DD
    """
    nombre_archivo = f"noticias_{fecha_str}.json"
    archivo_completo = OUTPUT_DIR / nombre_archivo
    
    try:
        # Agregar metadata al inicio del JSON
        dataset = {
            "fecha_consolidacion": fecha_str,
            "total_noticias": len(noticias),
            "noticias": noticias
        }
        
        with open(archivo_completo, "w", encoding="utf-8") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Dataset guardado: {archivo_completo}")
        logging.info(f"Total de noticias consolidadas: {len(noticias)}")
        
    except Exception as e:
        logging.error(f"Error al guardar dataset: {str(e)}")


def copiar_a_frontend(nombre_archivo: str, fecha_str: str):
    """
    Copia el archivo JSON consolidado a la carpeta frontend/data/.
    Sobrescribe el archivo si ya existe.
    
    Args:
        nombre_archivo: Nombre del archivo fuente
        fecha_str: Fecha en formato YYYY-MM-DD
    """
    # Crear directorio frontend/data/ si no existe
    FRONTEND_DIR.mkdir(parents=True, exist_ok=True)
    
    archivo_fuente = OUTPUT_DIR / nombre_archivo
    archivo_destino = FRONTEND_DIR / nombre_archivo
    
    try:
        # Copiar archivo
        import shutil
        shutil.copy2(archivo_fuente, archivo_destino)
        logging.info(f"Archivo copiado a frontend: {archivo_destino}")
    except Exception as e:
        logging.error(f"Error al copiar a frontend: {str(e)}")


def generar_resumen_por_categoria(noticias: List[Dict]) -> Dict:
    """
    Genera un resumen de noticias por categoría.
    
    Args:
        noticias: Lista de noticias
    
    Returns:
        Diccionario con conteo por categoría
    """
    resumen = {}
    
    for noticia in noticias:
        categoria = noticia.get("categoria", "Sin categoría")
        fuente = noticia.get("fuente", "Sin fuente")
        
        # Crear clave compuesta: categoría-fuente
        clave = f"{categoria} ({fuente})"
        
        resumen[clave] = resumen.get(clave, 0) + 1
    
    return resumen


def main():
    """
    Función principal que integra todas las fuentes.
    """
    # Fecha actual para el nombre del archivo
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    
    logging.info("=" * 60)
    logging.info("INTEGRACIÓN DE FUENTES RSS")
    logging.info(f"Fecha: {fecha_actual}")
    logging.info("=" * 60)
    
    # 1. Leer todas las noticias de archivos normalizados
    todas_las_noticias = leer_todas_las_noticias()
    
    if not todas_las_noticias:
        logging.warning("No se encontraron noticias para procesar")
        return
    
    logging.info(f"Total de noticias leídas: {len(todas_las_noticias)}")
    
    # 2. Eliminar duplicados
    noticias_unicas = eliminar_duplicados(todas_las_noticias)
    
    # 3. Ordenar por fecha descendente
    noticias_ordenadas = ordenar_por_fecha(noticias_unicas)
    
    # 4. Guardar dataset
    nombre_archivo = f"noticias_{fecha_actual}.json"
    guardar_dataset(noticias_ordenadas, fecha_actual)
    
    # 5. Copiar a frontend
    copiar_a_frontend(nombre_archivo, fecha_actual)
    
    # 6. Mostrar resumen por categoría
    resumen = generar_resumen_por_categoria(noticias_ordenadas)
    
    logging.info("=" * 60)
    logging.info("RESUMEN POR CATEGORÍA")
    logging.info("=" * 60)
    
    # Ordenar por cantidad de noticias (descendente)
    resumen_ordenado = sorted(resumen.items(), key=lambda x: x[1], reverse=True)
    
    for categoria, cantidad in resumen_ordenado[:15]:  # Mostrar top 15
        logging.info(f"  {categoria}: {cantidad} noticias")
    
    logging.info("=" * 60)


if __name__ == "__main__":
    main()

