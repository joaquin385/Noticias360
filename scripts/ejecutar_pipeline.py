"""
Script maestro que ejecuta el pipeline completo de extracción, normalización e integración de noticias.
Ejecuta los scripts en el siguiente orden:
1. extraer_feeds.py - Extrae noticias crudas de todas las fuentes RSS
2. normalizar_fechas.py - Normaliza fechas a UTC-3 y calcula horas_atras
3. integrar_fuentes.py - Consolida todas las noticias en un dataset diario
"""

import sys
from pathlib import Path
from datetime import datetime
import logging

# Agregar el directorio actual al path para importar los módulos
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

# Importar los módulos de los scripts
import extraer_feeds
import normalizar_fechas
import integrar_fuentes
import clasificar_categorias_url
import generar_resumenes_gemini

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def ejecutar_pipeline_completo():
    """
    Ejecuta el pipeline completo de extracción, normalización, integración y clasificación de noticias.
    """
    inicio = datetime.now()
    
    logging.info("=" * 70)
    logging.info("PIPELINE COMPLETO DE NOTICIAS RSS")
    logging.info(f"Inicio: {inicio.strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("=" * 70)
    
    # PASO 1: Extraer feeds
    logging.info("\n" + "=" * 70)
    logging.info("PASO 1/5: EXTRACCIÓN DE NOTICIAS RSS")
    logging.info("=" * 70)
    try:
        extraer_feeds.main()
        logging.info("✓ Extracción completada exitosamente")
    except Exception as e:
        logging.error(f"✗ Error en la extracción: {str(e)}")
        logging.error("Pipeline detenido por error en extracción")
        return
    
    # PASO 2: Normalizar fechas
    logging.info("\n" + "=" * 70)
    logging.info("PASO 2/5: NORMALIZACIÓN DE FECHAS")
    logging.info("=" * 70)
    try:
        normalizar_fechas.main()
        logging.info("✓ Normalización completada exitosamente")
    except Exception as e:
        logging.error(f"✗ Error en la normalización: {str(e)}")
        logging.error("Pipeline detenido por error en normalización")
        return
    
    # PASO 3: Integrar fuentes
    logging.info("\n" + "=" * 70)
    logging.info("PASO 3/5: INTEGRACIÓN DE FUENTES")
    logging.info("=" * 70)
    try:
        integrar_fuentes.main()
        logging.info("✓ Integración completada exitosamente")
    except Exception as e:
        logging.error(f"✗ Error en la integración: {str(e)}")
        logging.error("Pipeline detenido por error en integración")
        return
    
    # PASO 4: Clasificar por URL
    logging.info("\n" + "=" * 70)
    logging.info("PASO 4/5: CLASIFICACIÓN POR URL")
    logging.info("=" * 70)
    try:
        clasificar_categorias_url.main()
        logging.info("✓ Clasificación completada exitosamente")
    except Exception as e:
        logging.error(f"✗ Error en la clasificación: {str(e)}")
        logging.error("Pipeline detenido por error en clasificación")
        return

    # PASO 5: Generar resúmenes con Gemini
    logging.info("\n" + "=" * 70)
    logging.info("PASO 5/5: GENERACIÓN DE RESÚMENES (Gemini)")
    logging.info("=" * 70)
    try:
        generar_resumenes_gemini.main()
        logging.info("✓ Resúmenes generados exitosamente")
    except Exception as e:
        logging.error(f"✗ Error al generar resúmenes: {str(e)}")
        logging.error("Pipeline detenido por error en resúmenes")
        return
    
    # Resumen final
    fin = datetime.now()
    duracion = fin - inicio
    
    logging.info("\n" + "=" * 70)
    logging.info("PIPELINE COMPLETADO EXITOSAMENTE")
    logging.info("=" * 70)
    logging.info(f"Inicio: {inicio.strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"Fin: {fin.strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"Duración total: {duracion.total_seconds():.2f} segundos")
    logging.info("=" * 70)
    
    logging.info("\nArchivos generados:")
    logging.info("  • data/raw/ - Noticias crudas por fuente")
    logging.info("  • data/normalized/ - Noticias con fechas normalizadas")
    logging.info("  • data/noticias_YYYY-MM-DD.json - Dataset final consolidado")
    logging.info("  • data/resumenes_YYYY-MM-DD.json - Resúmenes por categoría (también copiado a frontend/data)")


def main():
    """
    Función principal que ejecuta el pipeline completo.
    """
    try:
        ejecutar_pipeline_completo()
    except KeyboardInterrupt:
        logging.warning("\nPipeline interrumpido por el usuario")
    except Exception as e:
        logging.error(f"\nError fatal en el pipeline: {str(e)}")
        raise


if __name__ == "__main__":
    main()

