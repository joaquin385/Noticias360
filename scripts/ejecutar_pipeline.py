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
# NOTA: Estos módulos quedan disponibles pero
# se han desactivado del pipeline principal
# import extraer_contenido
# import generar_resumenes_gemini
# import agrupar_temas

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

    # PASO 5-7: Funcionalidades avanzadas (scraping + IA) DESACTIVADAS
    # ----------------------------------------------------------------
    # Los siguientes pasos quedan documentados pero fuera del flujo:
    # 5. extraer_contenido.py      - Scraping de contenido completo
    # 6. generar_resumenes_gemini.py - Resúmenes por categoría con Gemini
    # 7. agrupar_temas.py            - Detección y agrupación de temas con Gemini
    #
    # Si en el futuro se desea reactivar estas funciones, se pueden
    # descomentar los bloques anteriores y las importaciones.
    logging.info("\n" + "=" * 70)
    logging.info("PASOS 5-7 DESACTIVADOS: scraping y módulos de IA no se ejecutan en este pipeline")
    logging.info("=" * 70)
    
    # Resumen final
    fin = datetime.now()
    duracion = fin - inicio
    
    logging.info("\n" + "=" * 70)
    logging.info("PIPELINE COMPLETADO (MODO SIN IA)")
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
    logging.info("\n  Nota: módulos de IA y temas están desactivados en este modo")


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

