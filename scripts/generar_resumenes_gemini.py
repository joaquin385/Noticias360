"""
Script para generar resúmenes de noticias usando Gemini AI.
Toma las primeras 30 noticias por categoría (como se muestran en el frontend)
y genera un resumen consolidado usando la API de Gemini.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import logging

try:
    # Nuevo SDK oficial
    from google import genai
except ImportError:
    logging.error("Error: google-genai no está instalado.")
    logging.error("Instálalo con: pip install google-genai")
    exit(1)

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Rutas
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
FRONTEND_DIR = BASE_DIR / "frontend" / "data"
OUTPUT_DIR = BASE_DIR / "data"

# Categorías a procesar (en el mismo orden que el frontend)
CATEGORIAS = ["internacional", "politica", "economia", "sociedad"]

# Número de noticias por categoría
NUM_NOTICIAS = 30


def obtener_api_key() -> str:
    """
    Obtiene la API key de Gemini de la variable de entorno.
    
    Returns:
        API key de Gemini
        
    Raises:
        ValueError: Si la API key no está configurada
    """
    # Intentar obtener de variable de entorno (funciona en PowerShell con $env: y en CMD con set)
    api_key = os.getenv("GEMINI_API_KEY")
    
    # Si tiene comillas, removerlas
    if api_key:
        api_key = api_key.strip().strip('"').strip("'")
    
    if not api_key or api_key == "":
        # Intentar leer de un archivo .env si existe
        env_file = BASE_DIR / ".env"
        if env_file.exists():
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY="):
                        api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    
    if not api_key or api_key == "":
        raise ValueError(
            "❌ GEMINI_API_KEY no está configurada.\n\n"
            "Para configurarla en PowerShell:\n"
            "  $env:GEMINI_API_KEY='tu-api-key'\n\n"
            "Para configurarla en CMD:\n"
            "  set GEMINI_API_KEY=tu-api-key\n\n"
            "O crea un archivo .env en la raíz del proyecto con:\n"
            "  GEMINI_API_KEY=tu-api-key"
        )
    
    return api_key


def intercalar_por_fuente(noticias: List[Dict]) -> List[Dict]:
    """
    Intercala noticias por fuente para evitar noticias consecutivas de la misma fuente.
    Replica la lógica del frontend.
    
    Args:
        noticias: Lista de noticias ya ordenadas por fecha
        
    Returns:
        Lista de noticias intercaladas por fuente
    """
    # 1. Agrupar noticias por fuente
    noticias_por_fuente = {}
    for noticia in noticias:
        fuente = noticia.get("fuente", "Sin fuente")
        if fuente not in noticias_por_fuente:
            noticias_por_fuente[fuente] = []
        noticias_por_fuente[fuente].append(noticia)
    
    # 2. Cada grupo ya está ordenado por fecha (más recientes primero)
    # 3. Intercalar usando algoritmo round-robin
    resultado = []
    fuentes = list(noticias_por_fuente.keys())
    indices = {fuente: 0 for fuente in fuentes}
    
    hay_mas_noticias = True
    while hay_mas_noticias:
        hay_mas_noticias = False
        
        # Agregar una noticia de cada fuente en orden
        for fuente in fuentes:
            cola_fuente = noticias_por_fuente[fuente]
            if indices[fuente] < len(cola_fuente):
                resultado.append(cola_fuente[indices[fuente]])
                indices[fuente] += 1
                hay_mas_noticias = True
    
    return resultado


def filtrar_y_ordenar_noticias(noticias: List[Dict], categoria: str, excluir_infobae: bool = False) -> List[Dict]:
    """
    Filtra noticias por categoría y las ordena como en el frontend.
    
    Args:
        noticias: Lista completa de noticias
        categoria: Categoría a filtrar
        excluir_infobae: Si True, excluye Infobae de la categoría internacional
        
    Returns:
        Lista de noticias filtradas y ordenadas
    """
    # Filtrar por categoría
    noticias_filtradas = []
    for noticia in noticias:
        categoria_noticia = noticia.get("categoria_url", "").lower().strip()
        
        # Si no tiene categoria_url, usar categoria como fallback
        if not categoria_noticia or categoria_noticia == "":
            categoria_noticia = noticia.get("categoria", "").lower().strip()
            if categoria_noticia == "no categorizada" or categoria_noticia == "":
                categoria_noticia = "otros"
        
        # Verificar si cumple la categoría
        cumple_categoria = categoria_noticia == categoria.lower()
        
        # Excluir Infobae de internacional
        if categoria.lower() == "internacional" and excluir_infobae:
            if noticia.get("fuente") == "Infobae":
                cumple_categoria = False
        
        if cumple_categoria:
            noticias_filtradas.append(noticia)
    
    # Ordenar por fecha descendente
    def obtener_fecha_sort(noticia: Dict) -> str:
        fecha_local = noticia.get("fecha_local", "")
        if fecha_local:
            return fecha_local
        return noticia.get("fecha_original", "")
    
    noticias_ordenadas = sorted(
        noticias_filtradas,
        key=obtener_fecha_sort,
        reverse=True
    )
    
    # Intercalar por fuente
    noticias_intercaladas = intercalar_por_fuente(noticias_ordenadas)
    
    # Tomar solo las primeras NUM_NOTICIAS
    return noticias_intercaladas[:NUM_NOTICIAS]


def limpiar_html(texto: str) -> str:
    """
    Limpia HTML del texto.
    """
    if not texto:
        return ""
    
    # Remover etiquetas HTML básicas
    import re
    texto = re.sub(r'<[^>]+>', '', texto)
    # Limpiar espacios múltiples
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()


def crear_prompt_resumen(noticias: List[Dict], categoria: str) -> str:
    """
    Crea el prompt para Gemini con las noticias a resumir.
    
    Args:
        noticias: Lista de noticias de la categoría
        categoria: Nombre de la categoría
        
    Returns:
        Prompt completo para Gemini
    """
    # Mapear nombres de categorías para el prompt
    nombres_categoria = {
        "internacional": "Internacional",
        "politica": "Política",
        "economia": "Economía",
        "sociedad": "Sociedad"
    }
    
    nombre_cat = nombres_categoria.get(categoria.lower(), categoria.capitalize())
    
    # Construir el texto con todas las noticias
    texto_noticias = f"Noticias de la categoría '{nombre_cat}':\n\n"
    
    for idx, noticia in enumerate(noticias, 1):
        titulo = noticia.get("titulo", "Sin título")
        resumen = limpiar_html(noticia.get("resumen", "Sin descripción"))
        fuente = noticia.get("fuente", "Sin fuente")
        fecha = noticia.get("fecha_local", noticia.get("fecha_original", ""))
        
        texto_noticias += f"{idx}. {titulo}\n"
        texto_noticias += f"   Fuente: {fuente}\n"
        if fecha:
            texto_noticias += f"   Fecha: {fecha}\n"
        if resumen:
            texto_noticias += f"   Resumen: {resumen}\n"
        texto_noticias += "\n"
    
    prompt = f"""Analiza las siguientes {len(noticias)} noticias de la categoría '{nombre_cat}' y crea un resumen ejecutivo consolidado.

El resumen debe:
1. COMENZAR DIRECTAMENTE con el contenido, sin introducciones ni saludos.
2. Identificar los temas principales y agrupar noticias relacionadas.
3. ESTRUCTURAR el contenido en párrafos separados por tema/área, cada uno con un punto clave al inicio cuando sea relevante.
4. Destacar los eventos más importantes de forma concisa.
5. Máximo 300 palabras.
6. Tono profesional, objetivo y periodístico. Sin lenguaje coloquial ni expresiones informales.
7. Usar puntos y aparte (saltos de línea) para separar temas distintos y mejorar la legibilidad.

EJEMPLO DE ESTRUCTURA DESEADA:
- Párrafo 1: Tema principal A con sus desarrollos
- Párrafo 2: Tema principal B con sus desarrollos
- Párrafo 3: Tema principal C con sus desarrollos

{texto_noticias}

Resumen ejecutivo:"""
    
    return prompt


def generar_resumen_gemini(texto: str, api_key: str) -> str:
    """
    Genera un resumen usando Gemini AI.
    
    Args:
        texto: Prompt con las noticias a resumir
        api_key: API key de Gemini
        
    Returns:
        Resumen generado por Gemini
    """
    try:
        # Cliente del nuevo SDK
        client = genai.Client(api_key=api_key)
        # Modelo recomendado para resúmenes rápidos y baratos
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[texto]
        )
        # El SDK expone .text con el texto agregado
        return getattr(response, "text", "") or ""
        
    except Exception as e:
        logging.error(f"Error al generar resumen con Gemini: {str(e)}")
        raise


def cargar_json_noticias(fecha: str = None) -> Dict:
    """
    Carga el archivo JSON de noticias consolidado.
    
    Args:
        fecha: Fecha en formato YYYY-MM-DD. Si es None, usa el archivo más reciente.
        
    Returns:
        Diccionario con los datos del JSON
    """
    # Siempre buscar el archivo más reciente para evitar problemas de zona horaria
    archivos = list(DATA_DIR.glob("noticias_*.json"))
    if not archivos:
        raise FileNotFoundError(f"No se encontró ningún archivo de noticias en {DATA_DIR}")
    
    # Ordenar por fecha de modificación y tomar el más reciente
    archivo = max(archivos, key=lambda p: p.stat().st_mtime)
    
    logging.info(f"Cargando noticias desde: {archivo.name}")
    
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise FileNotFoundError(f"Error al cargar {archivo}: {str(e)}")


def main():
    """
    Función principal que genera los resúmenes por categoría.
    """
    logging.info("=" * 70)
    logging.info("GENERACIÓN DE RESUMENES CON GEMINI AI")
    logging.info("=" * 70)
    
    # 1. Obtener API key
    try:
        api_key = obtener_api_key()
        logging.info("✓ API key de Gemini configurada")
    except ValueError as e:
        logging.error(str(e))
        return
    
    # 2. Cargar noticias
    try:
        data = cargar_json_noticias()
        noticias = data.get("noticias", [])
        fecha_consolidacion = data.get("fecha_consolidacion", datetime.now().strftime("%Y-%m-%d"))
        logging.info(f"✓ Cargadas {len(noticias)} noticias")
    except Exception as e:
        logging.error(f"Error al cargar noticias: {str(e)}")
        return
    
    # 3. Generar resúmenes por categoría
    resumenes = {}
    
    for categoria in CATEGORIAS:
        logging.info("\n" + "=" * 70)
        logging.info(f"Procesando categoría: {categoria.upper()}")
        logging.info("=" * 70)
        
        # Filtrar y ordenar noticias (excluir Infobae de internacional)
        excluir_infobae = (categoria.lower() == "internacional")
        noticias_categoria = filtrar_y_ordenar_noticias(
            noticias, 
            categoria, 
            excluir_infobae=excluir_infobae
        )
        
        if not noticias_categoria:
            logging.warning(f"No se encontraron noticias para la categoría: {categoria}")
            resumenes[categoria] = {
                "resumen": "No hay noticias disponibles para esta categoría.",
                "cantidad_noticias": 0,
                "fecha_generacion": datetime.now().isoformat()
            }
            continue
        
        logging.info(f"Filtradas {len(noticias_categoria)} noticias de {categoria}")
        
        # Crear prompt
        prompt = crear_prompt_resumen(noticias_categoria, categoria)
        
        # Generar resumen con Gemini
        try:
            logging.info("Generando resumen con Gemini AI...")
            resumen_texto = generar_resumen_gemini(prompt, api_key)
            
            resumenes[categoria] = {
                "resumen": resumen_texto,
                "cantidad_noticias": len(noticias_categoria),
                "fecha_generacion": datetime.now().isoformat(),
                "categoria": categoria
            }
            
            logging.info(f"✓ Resumen generado para {categoria} ({len(resumen_texto)} caracteres)")
            
        except Exception as e:
            logging.error(f"Error al generar resumen para {categoria}: {str(e)}")
            resumenes[categoria] = {
                "resumen": f"Error al generar resumen: {str(e)}",
                "cantidad_noticias": len(noticias_categoria),
                "fecha_generacion": datetime.now().isoformat(),
                "categoria": categoria
            }
    
    # 4. Guardar resúmenes
    nombre_archivo = f"resumenes_{fecha_consolidacion}.json"
    archivo_salida = OUTPUT_DIR / nombre_archivo
    
    resultado = {
        "fecha_consolidacion": fecha_consolidacion,
        "fecha_generacion": datetime.now().isoformat(),
        "resumenes": resumenes
    }
    
    try:
        with open(archivo_salida, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        # Copiar también a frontend/data para consumo directo del frontend
        try:
            FRONTEND_DIR.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.copy2(archivo_salida, FRONTEND_DIR / nombre_archivo)
            logging.info(f"Copiado a frontend/data: {FRONTEND_DIR / nombre_archivo}")
        except Exception as e:
            logging.error(f"No se pudo copiar a frontend/data: {str(e)}")
        
        logging.info("\n" + "=" * 70)
        logging.info("RESUMENES GUARDADOS")
        logging.info("=" * 70)
        logging.info(f"Archivo: {archivo_salida}")
        
        for categoria, datos in resumenes.items():
            logging.info(f"  {categoria.upper()}: {datos['cantidad_noticias']} noticias resumidas")
        
        logging.info("=" * 70)
        
    except Exception as e:
        logging.error(f"Error al guardar resúmenes: {str(e)}")


if __name__ == "__main__":
    main()

