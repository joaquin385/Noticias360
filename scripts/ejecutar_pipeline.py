"""
Script maestro que ejecuta el pipeline completo de extracción, normalización, integración y análisis de noticias.
Ejecuta los scripts en el siguiente orden:
1. extraer_feeds.py - Extrae noticias crudas de todas las fuentes RSS
2. normalizar_fechas.py - Normaliza fechas a UTC-3 y calcula horas_atras
3. integrar_fuentes.py - Consolida todas las noticias en un dataset diario
4. clasificar_categorias_url.py - Clasifica noticias y copia a frontend
5. extraer_contenido.py - Extrae contenido completo (opcional, lento)
6. generar_resumenes_gemini.py - Genera resúmenes por categoría con IA
7. agrupar_temas.py - Detecta temas relevantes y mantiene histórico
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
import extraer_contenido
import generar_resumenes_gemini
import agrupar_temas

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
    logging.info("PASO 1/7: EXTRACCIÓN DE NOTICIAS RSS")
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
    logging.info("PASO 2/7: NORMALIZACIÓN DE FECHAS")
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
    logging.info("PASO 3/7: INTEGRACIÓN DE FUENTES")
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
    logging.info("PASO 4/7: CLASIFICACIÓN POR URL")
    logging.info("=" * 70)
    try:
        clasificar_categorias_url.main()
        logging.info("✓ Clasificación completada exitosamente")
    except Exception as e:
        logging.error(f"✗ Error en la clasificación: {str(e)}")
        logging.error("Pipeline detenido por error en clasificación")
        return

    # PASO 5: Extraer contenido completo (OPCIONAL - toma ~4-5 minutos)
    # Puedes comentar este bloque si quieres acelerar el pipeline
    # Los temas funcionarán igual pero con menos detalle en los resúmenes
    logging.info("\n" + "=" * 70)
    logging.info("PASO 5/7: EXTRACCIÓN DE CONTENIDO COMPLETO (Web Scraping - OPCIONAL)")
    logging.info("=" * 70)
    try:
        extraer_contenido.main()
        logging.info("✓ Contenido extraído exitosamente")
    except Exception as e:
        logging.error(f"✗ Error al extraer contenido: {str(e)}")
        logging.warning("Continuando pipeline sin contenido completo...")
        # No detener el pipeline, es opcional

    # PASO 6: Generar resúmenes con Gemini
    logging.info("\n" + "=" * 70)
    logging.info("PASO 6/7: GENERACIÓN DE RESÚMENES POR CATEGORÍA (Gemini)")
    logging.info("=" * 70)
    try:
        generar_resumenes_gemini.main()
        logging.info("✓ Resúmenes generados exitosamente")
    except Exception as e:
        logging.error(f"✗ Error al generar resúmenes: {str(e)}")
        logging.warning("Continuando pipeline sin resúmenes de categoría...")
        # No detener el pipeline, es opcional
    
    # PASO 7: Detectar y agrupar temas con IA
    logging.info("\n" + "=" * 70)
    logging.info("PASO 7/7: DETECCIÓN Y AGRUPACIÓN DE TEMAS (Gemini)")
    logging.info("=" * 70)
    try:
        agrupar_temas.main()
        logging.info("✓ Temas detectados y guardados exitosamente")
    except Exception as e:
        logging.error(f"✗ Error al detectar temas: {str(e)}")
        logging.warning("Pipeline completado sin detección de temas")
        # No detener el pipeline, es opcional
    
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
    logging.info("  Backend (data/):")
    logging.info("    • data/raw/ - Noticias crudas por fuente")
    logging.info("    • data/normalized/ - Noticias con fechas normalizadas")
    logging.info("    • data/noticias_YYYY-MM-DD.json - Dataset consolidado")
    logging.info("    • data/noticias_contenido_YYYY-MM-DD.json - Noticias con contenido completo")
    logging.info("    • data/resumenes_YYYY-MM-DD.json - Resúmenes por categoría")
    logging.info("    • data/temas/temas_YYYY-MM-DD.json - Temas detectados del día")
    logging.info("    • data/temas/historico_temas.json - Histórico completo de temas")
    logging.info("\n  Frontend (frontend/data/):")
    logging.info("    • noticias_YYYY-MM-DD.json - Noticias clasificadas (por fecha)")
    logging.info("    • resumenes_YYYY-MM-DD.json - Resúmenes de categorías (por fecha)")
    logging.info("    • temas_latest.json - Temas detectados del día")
    logging.info("\n  Nota: historico_temas.json solo en data/temas/ (no se copia a frontend)")


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

