"""
Script para detectar y agrupar temas relevantes en las noticias usando Gemini AI.
Versión MVP: Agrupación básica y generación de resúmenes por tema.
"""

import json
import os
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict
import logging
import re

try:
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
TEMAS_DIR = DATA_DIR / "temas"
FRONTEND_DIR = BASE_DIR / "frontend" / "data"
# Intentar usar noticias con contenido completo desde data/, fallback a frontend/data/
NOTICIAS_DIR = DATA_DIR

# Límites
MAX_NOTICIAS_ANALIZAR = 150  # Máximo de noticias para analizar
MAX_TEMAS_DETECTAR = 10      # Máximo de temas a detectar
MIN_FUENTES_POR_TEMA = 2     # Mínimo de fuentes diferentes por tema


def obtener_api_key() -> str:
    """
    Obtiene la API key de Gemini de la variable de entorno o archivo .env.
    
    Returns:
        API key de Gemini
    """
    api_key = os.getenv("GEMINI_API_KEY")
    
    if api_key:
        api_key = api_key.strip().strip('"').strip("'")
    
    if not api_key or api_key == "":
        env_file = BASE_DIR / ".env"
        if env_file.exists():
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY="):
                        api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    
    if not api_key or api_key == "":
        raise ValueError("GEMINI_API_KEY no está configurada")
    
    return api_key


def cargar_noticias_del_dia() -> Dict:
    """
    Intenta cargar noticias con contenido completo desde data/.
    Si no existe, usa las del frontend/ (sin contenido completo).
    
    Returns:
        Diccionario con los datos del JSON
    """
    # Intentar cargar archivo con contenido desde data/
    archivos_contenido = list(DATA_DIR.glob("noticias_contenido_*.json"))
    
    if archivos_contenido:
        archivo = max(archivos_contenido, key=lambda p: p.stat().st_mtime)
        logging.info(f"✓ Usando noticias CON contenido completo: {archivo.name}")
    else:
        # Fallback a archivo normal desde frontend/data/
        archivos = list(FRONTEND_DIR.glob("noticias_[0-9]*.json"))
        if not archivos:
            raise FileNotFoundError(f"No se encontró ningún archivo de noticias")
        archivo = max(archivos, key=lambda p: p.stat().st_mtime)
        logging.warning(f"⚠️  Usando noticias SIN contenido completo: {archivo.name}")
    
    with open(archivo, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return data


def inicializar_historico() -> Dict:
    """
    Crea estructura vacía de histórico.
    
    Returns:
        Diccionario vacío de histórico
    """
    return {
        'temas': {},
        'ultima_actualizacion': datetime.now().isoformat(),
        'total_temas_activos': 0,
        'total_temas_inactivos': 0,
        'total_temas_historicos': 0
    }


def cargar_historico() -> Dict:
    """
    Carga el archivo histórico de temas.
    Si no existe, retorna estructura vacía.
    
    Returns:
        Diccionario con histórico de temas
    """
    archivo_historico = TEMAS_DIR / "historico_temas.json"
    
    if not archivo_historico.exists():
        logging.info("📂 No existe histórico previo, creando nuevo")
        return inicializar_historico()
    
    try:
        with open(archivo_historico, "r", encoding="utf-8") as f:
            historico = json.load(f)
        logging.info(f"✓ Histórico cargado: {len(historico.get('temas', {}))} temas registrados")
        return historico
    except Exception as e:
        logging.error(f"Error al cargar histórico: {str(e)}")
        return inicializar_historico()


def guardar_historico(historico: Dict):
    """
    Guarda el histórico actualizado en data/temas/ y frontend/data/.
    
    Args:
        historico: Diccionario completo del histórico
    """
    # Actualizar timestamp
    historico['ultima_actualizacion'] = datetime.now().isoformat()
    
    # Recalcular contadores
    temas_activos = sum(1 for t in historico['temas'].values() if t.get('estado') == 'activo')
    temas_inactivos = sum(1 for t in historico['temas'].values() if t.get('estado') == 'inactivo')
    
    historico['total_temas_activos'] = temas_activos
    historico['total_temas_inactivos'] = temas_inactivos
    historico['total_temas_historicos'] = len(historico['temas'])
    
    # Guardar en data/temas/
    TEMAS_DIR.mkdir(parents=True, exist_ok=True)
    archivo_historico = TEMAS_DIR / "historico_temas.json"
    
    with open(archivo_historico, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)
    
    logging.info(f"✓ Histórico guardado: {archivo_historico.name}")
    
    # NOTA: NO se copia a frontend/data/ porque el frontend no lo usa
    # El histórico solo se mantiene en data/temas/ para tracking interno


def calcular_similitud_simple(texto1: str, texto2: str) -> float:
    """
    Calcula similitud básica entre dos textos (0.0 a 1.0).
    Usa comparación de palabras en común (Jaccard similarity).
    
    Args:
        texto1: Primer texto normalizado
        texto2: Segundo texto normalizado
        
    Returns:
        Valor de 0.0 (nada similar) a 1.0 (idéntico)
    """
    palabras1 = set(texto1.split())
    palabras2 = set(texto2.split())
    
    if not palabras1 or not palabras2:
        return 0.0
    
    comunes = palabras1.intersection(palabras2)
    union = palabras1.union(palabras2)
    
    return len(comunes) / len(union) if union else 0.0


def encontrar_tema_existente(nombre_tema: str, nombre_normalizado: str, historico: Dict, umbral: float = 0.75) -> str:
    """
    Busca si el tema ya existe en el histórico.
    
    Args:
        nombre_tema: Nombre original del tema
        nombre_normalizado: Nombre normalizado del tema
        historico: Diccionario con histórico de temas
        umbral: Umbral de similitud para match (default 0.75 = 75%)
        
    Returns:
        tema_id si existe, None si es nuevo
    """
    for tema_id, datos in historico.get('temas', {}).items():
        # 1. Match exacto por nombre normalizado
        if datos.get('tema_normalizado') == nombre_normalizado:
            logging.info(f"  🔗 Match exacto: '{nombre_tema}' = '{datos['tema']}'")
            return tema_id
        
        # 2. Match por alias
        if nombre_normalizado in datos.get('alias', []):
            logging.info(f"  🔗 Match por alias: '{nombre_tema}' = '{datos['tema']}'")
            return tema_id
        
        # 3. Match por similitud (palabras en común)
        similitud = calcular_similitud_simple(nombre_normalizado, datos.get('tema_normalizado', ''))
        if similitud >= umbral:
            logging.info(f"  🔗 Match por similitud ({int(similitud*100)}%): '{nombre_tema}' ≈ '{datos['tema']}'")
            return tema_id
    
    # No se encontró match
    logging.info(f"  ⭐ Tema NUEVO: '{nombre_tema}'")
    return None


def seleccionar_noticias_para_analisis(noticias: List[Dict], max_noticias: int = MAX_NOTICIAS_ANALIZAR) -> List[Dict]:
    """
    Selecciona las noticias más relevantes para análisis de temas.
    Prioriza noticias de categorías principales y más recientes.
    
    Args:
        noticias: Lista completa de noticias
        max_noticias: Máximo de noticias a incluir
        
    Returns:
        Lista filtrada de noticias
    """
    # Filtrar por categorías principales
    categorias_principales = ['internacional', 'politica', 'economia', 'sociedad']
    
    noticias_filtradas = [
        n for n in noticias 
        if n.get('categoria_url', '').lower() in categorias_principales
    ]
    
    # Si no hay suficientes, usar todas
    if len(noticias_filtradas) < max_noticias:
        noticias_filtradas = noticias
    
    # Ordenar por fecha (más recientes primero) y tomar las primeras max_noticias
    noticias_ordenadas = sorted(
        noticias_filtradas,
        key=lambda n: n.get('fecha_local', ''),
        reverse=True
    )
    
    return noticias_ordenadas[:max_noticias]


def calcular_tendencia(apariciones: List[Dict]) -> str:
    """
    Calcula la tendencia del tema basándose en las últimas apariciones.
    
    Args:
        apariciones: Lista de apariciones del tema
        
    Returns:
        "nuevo", "creciente", "estable", "decreciente"
    """
    if len(apariciones) < 2:
        return "nuevo"
    
    # Comparar últimas dos apariciones
    ultimas_dos = apariciones[-2:]
    cantidad_anterior = ultimas_dos[0].get('cantidad_noticias', 0)
    cantidad_actual = ultimas_dos[1].get('cantidad_noticias', 0)
    
    diff = cantidad_actual - cantidad_anterior
    
    if diff > 0:
        return "creciente"
    elif diff < 0:
        return "decreciente"
    else:
        return "estable"


def calcular_metricas(apariciones: List[Dict]) -> Dict:
    """
    Calcula métricas estadísticas del tema.
    
    Args:
        apariciones: Lista de apariciones del tema
        
    Returns:
        Diccionario con métricas
    """
    if not apariciones:
        return {
            'pico_noticias': 0,
            'minimo_noticias': 0,
            'promedio_noticias_dia': 0.0,
            'fuentes_unicas': []
        }
    
    cantidades = [a.get('cantidad_noticias', 0) for a in apariciones]
    todas_fuentes = set()
    for a in apariciones:
        todas_fuentes.update(a.get('fuentes', []))
    
    return {
        'pico_noticias': max(cantidades) if cantidades else 0,
        'minimo_noticias': min(cantidades) if cantidades else 0,
        'promedio_noticias_dia': round(sum(cantidades) / len(cantidades), 1) if cantidades else 0.0,
        'fuentes_unicas': sorted(list(todas_fuentes))
    }


def actualizar_estado_temas(historico: Dict, fecha_actual: str):
    """
    Actualiza el estado de todos los temas en el histórico.
    Marca como inactivos los que no aparecieron en los últimos 3 días.
    
    Args:
        historico: Diccionario del histórico
        fecha_actual: Fecha de hoy en formato YYYY-MM-DD
    """
    from datetime import datetime, timedelta
    
    fecha_hoy = datetime.strptime(fecha_actual, "%Y-%m-%d")
    
    for tema_id, datos in historico.get('temas', {}).items():
        fecha_ultima = datos.get('fecha_ultima_aparicion', fecha_actual)
        fecha_ultima_dt = datetime.strptime(fecha_ultima, "%Y-%m-%d")
        
        dias_sin_aparecer = (fecha_hoy - fecha_ultima_dt).days
        
        # Marcar como inactivo si no apareció por 3+ días
        if dias_sin_aparecer >= 3 and datos.get('estado') == 'activo':
            datos['estado'] = 'inactivo'
            datos['dias_inactivo'] = dias_sin_aparecer
            logging.info(f"  ⏸️  Tema inactivo: '{datos['tema']}' ({dias_sin_aparecer} días sin aparecer)")
        
        # Si reaparece después de estar inactivo, reactivar
        elif dias_sin_aparecer == 0 and datos.get('estado') == 'inactivo':
            datos['estado'] = 'reactivado'
            datos['dias_inactivo'] = 0
            logging.info(f"  ▶️  Tema reactivado: '{datos['tema']}'")


def limpiar_apariciones_antiguas(historico: Dict, max_dias: int = 30):
    """
    Limita el histórico a los últimos X días para cada tema.
    
    Args:
        historico: Diccionario del histórico
        max_dias: Máximo de días a mantener
    """
    for tema_id, datos in historico.get('temas', {}).items():
        apariciones = datos.get('apariciones', [])
        
        if len(apariciones) > max_dias:
            # Mantener solo las últimas max_dias apariciones
            antes = len(apariciones)
            datos['apariciones'] = apariciones[-max_dias:]
            logging.info(f"  🗑️  Limpiadas apariciones antiguas de '{datos['tema']}': {antes} → {len(datos['apariciones'])}")


def limpiar_html(texto: str) -> str:
    """Limpia HTML del texto."""
    if not texto:
        return ""
    texto = re.sub(r'<[^>]+>', '', texto)
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()


def crear_prompt_agrupacion(noticias: List[Dict]) -> str:
    """
    Crea el prompt para que Gemini agrupe las noticias por tema.
    
    Args:
        noticias: Lista de noticias a agrupar
        
    Returns:
        Prompt completo
    """
    # Construir lista de titulares numerados
    lista_titulares = ""
    for idx, noticia in enumerate(noticias, 1):
        titulo = noticia.get('titulo', 'Sin título')
        fuente = noticia.get('fuente', '')
        categoria = noticia.get('categoria_url', '')
        lista_titulares += f"{idx}. {titulo} [{fuente} - {categoria}]\n"
    
    prompt = f"""Analizá los siguientes {len(noticias)} titulares de noticias argentinas y agrupalos por tema ESPECÍFICO.

TITULARES:
{lista_titulares}

CRITERIOS DE AGRUPACIÓN:
1. Creá nombres de temas ESPECÍFICOS Y CONCRETOS, no genéricos
2. Identificá el evento, conflicto o situación PARTICULAR
3. Ejemplos de nombres CORRECTOS:
   ✓ "Operativo policial en Río de Janeiro contra narcotráfico"
   ✓ "Negociación salarial docente 2025"
   ✓ "Causa Cuadernos: nuevos testimonios"
   ✓ "Dólar paralelo: escalada noviembre"
   ✓ "Huracán Melissa: paso por el Caribe"
4. Ejemplos de nombres INCORRECTOS (demasiado genéricos):
   ✗ "Geopolítica y conflictos globales"
   ✗ "Economía argentina"
   ✗ "Política nacional"
   ✗ "Noticias internacionales"
5. Cada grupo debe tener al menos 2 titulares relacionados DE DIFERENTES FUENTES
6. Un titular puede pertenecer solo a UN tema
7. Máximo {MAX_TEMAS_DETECTAR} temas
8. Si un titular no encaja claramente en ningún grupo, no lo fuerces
9. Nombres de 3-8 palabras
10. Priorizá temas con mayor cobertura (más fuentes = más relevante)

FORMATO DE RESPUESTA (JSON únicamente, sin texto adicional):
{{
  "temas": [
    {{
      "tema": "Nombre específico del tema o evento",
      "indices_titulares": [1, 3, 5]
    }}
  ]
}}

Respondé SOLO con el JSON:"""
    
    return prompt


def crear_prompt_resumen(tema: str, noticias_relacionadas: List[Dict]) -> str:
    """
    Crea el prompt para generar el resumen de un tema NUEVO.
    Usa contenido completo si está disponible, sino usa el resumen RSS.
    
    Args:
        tema: Nombre del tema
        noticias_relacionadas: Lista de diccionarios con datos completos de las noticias
        
    Returns:
        Prompt completo
    """
    noticias_texto = ""
    
    for idx, noticia in enumerate(noticias_relacionadas, 1):
        titulo = noticia.get('titulo', 'Sin título')
        noticias_texto += f"{idx}. {titulo}\n"
        
        # Usar contenido completo si existe, sino usar resumen RSS
        if noticia.get('contenido_extraido') and noticia.get('contenido_completo'):
            # Limitar a primeras 500 palabras para no saturar prompt
            contenido = ' '.join(noticia['contenido_completo'].split()[:500])
            palabras = noticia.get('palabras_contenido', 0)
            noticias_texto += f"   [Contenido completo - {palabras} palabras]:\n"
            noticias_texto += f"   {contenido}...\n\n"
        else:
            # Fallback a resumen RSS
            resumen = noticia.get('resumen', 'Sin descripción')
            resumen_limpio = limpiar_html(resumen) if resumen else ""
            if resumen_limpio:
                noticias_texto += f"   [Resumen RSS]: {resumen_limpio[:200]}...\n\n"
            else:
                noticias_texto += f"   [Sin contenido disponible]\n\n"
    
    prompt = f"""Creá un resumen SIMPLE y DIDÁCTICO sobre este tema, fácil de leer y bien estructurado.

TEMA: {tema}

NOTICIAS RELACIONADAS:
{noticias_texto}

FORMATO REQUERIDO:
Usá esta estructura SIEMPRE (NO uses párrafos largos):

📌 **¿Qué está pasando?**
• [En 2-3 oraciones cortas, explicar el hecho principal]
• [Usar bullets, NO párrafos]

🔍 **Datos clave:**
• [Cifra/fecha/nombre importante #1]
• [Cifra/fecha/nombre importante #2]
• [Cifra/fecha/nombre importante #3]
• [Agregar más si hay información relevante]

⚡ **Desarrollo:**
• [Punto importante #1 del contexto]
• [Punto importante #2 de las causas o consecuencias]
• [Punto importante #3 sobre actores involucrados]
• [Continuar con más bullets según necesidad]

💡 **¿Por qué importa?**
• [Explicar en 1-2 bullets el impacto o relevancia]

REGLAS:
- Comenzá DIRECTO sin saludos
- Usá BULLETS (•), NO párrafos largos
- Máximo 2-3 oraciones por bullet
- Incluí TODOS los datos concretos: cifras, fechas, nombres
- Entre 300-400 palabras
- Tono claro, profesional y neutral

Resumen:"""
    
    return prompt


def crear_prompt_resumen_recurrente(tema: str, resumen_anterior: str, noticias_nuevas: List[Dict]) -> str:
    """
    Crea el prompt para actualizar el resumen de un tema RECURRENTE.
    Integra el resumen anterior con las novedades de hoy.
    
    Args:
        tema: Nombre del tema
        resumen_anterior: Resumen del día anterior
        noticias_nuevas: Noticias nuevas de hoy relacionadas al tema
        
    Returns:
        Prompt completo
    """
    # Construir lista de noticias nuevas
    noticias_texto = ""
    for idx, noticia in enumerate(noticias_nuevas, 1):
        titulo = noticia.get('titulo', 'Sin título')
        noticias_texto += f"{idx}. {titulo}\n"
        
        # Usar contenido completo si está disponible
        if noticia.get('contenido_extraido') and noticia.get('contenido_completo'):
            contenido = ' '.join(noticia['contenido_completo'].split()[:500])
            palabras = noticia.get('palabras_contenido', 0)
            noticias_texto += f"   [Contenido completo - {palabras} palabras]:\n"
            noticias_texto += f"   {contenido}...\n\n"
        else:
            resumen = noticia.get('resumen', 'Sin descripción')
            resumen_limpio = limpiar_html(resumen) if resumen else ""
            if resumen_limpio:
                noticias_texto += f"   [Resumen RSS]: {resumen_limpio[:200]}...\n\n"
    
    prompt = f"""Actualizá el resumen de este tema con las novedades de hoy. Mantené el formato SIMPLE y DIDÁCTICO.

TEMA: {tema}

RESUMEN ANTERIOR:
{resumen_anterior}

NOTICIAS NUEVAS DE HOY:
{noticias_texto}

FORMATO REQUERIDO:
Mantené la misma estructura (NO uses párrafos largos):

📌 **¿Qué está pasando?**
• [Actualizar con lo MÁS RECIENTE en 2-3 oraciones cortas]
• [Mantener contexto si sigue siendo relevante]

🔍 **Datos clave:**
• [ACTUALIZAR cifras/fechas si cambiaron]
• [Mantener datos relevantes del resumen anterior]
• [Agregar nuevos datos importantes de hoy]

⚡ **Desarrollo:**
• [INTEGRAR novedades de hoy con el contexto previo]
• [Conectar: ¿cómo evolucionó la situación?]
• [Eliminar información obsoleta o menos relevante]
• [Agregar puntos nuevos importantes]

💡 **¿Por qué importa?**
• [Actualizar el impacto o relevancia según novedades]

REGLAS:
- Comenzá DIRECTO sin saludos
- INTEGRÁ las novedades (no las agregues como anexo)
- Usá BULLETS (•), NO párrafos largos
- ACTUALIZÁ cifras y datos obsoletos
- Eliminá info que ya no es central
- Entre 300-400 palabras
- Tono claro, profesional y neutral

Resumen actualizado:"""
    
    return prompt


def llamar_gemini_con_retry(client, model: str, prompt: str, max_intentos: int = 3) -> str:
    """
    Llama a Gemini con reintentos automáticos si el servicio está sobrecargado.
    
    Args:
        client: Cliente de Gemini
        model: Nombre del modelo
        prompt: Prompt a enviar
        max_intentos: Número máximo de intentos
        
    Returns:
        Texto de la respuesta
    """
    
    for intento in range(max_intentos):
        try:
            response = client.models.generate_content(
                model=model,
                contents=[prompt]
            )
            return getattr(response, "text", "") or ""
            
        except Exception as e:
            error_msg = str(e)
            
            # Si es error 503 (sobrecarga) o 429 (rate limit), reintentar
            if "503" in error_msg or "429" in error_msg or "UNAVAILABLE" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                if intento < max_intentos - 1:
                    espera = (intento + 1) * 5  # 5, 10, 15 segundos (más tiempo para rate limit)
                    logging.warning(f"Servicio sobrecargado. Reintentando en {espera}s... (intento {intento + 1}/{max_intentos})")
                    time.sleep(espera)
                    continue
                else:
                    logging.error(f"Servicio sobrecargado después de {max_intentos} intentos")
                    raise
            else:
                # Otro tipo de error, no reintentar
                raise
    
    raise Exception("No se pudo completar la solicitud después de múltiples intentos")


def agrupar_con_gemini(noticias: List[Dict], api_key: str) -> Dict:
    """
    Llama a Gemini para agrupar noticias por tema.
    
    Args:
        noticias: Lista de noticias
        api_key: API key de Gemini
        
    Returns:
        Diccionario con temas y sus índices
    """
    prompt = crear_prompt_agrupacion(noticias)
    
    try:
        client = genai.Client(api_key=api_key)
        
        # Usar gemini-2.5-flash
        texto_respuesta = llamar_gemini_con_retry(client, "gemini-2.5-flash", prompt)
        
        # Limpiar la respuesta para extraer solo el JSON
        if "```json" in texto_respuesta:
            texto_respuesta = texto_respuesta.split("```json")[1].split("```")[0]
        elif "```" in texto_respuesta:
            texto_respuesta = texto_respuesta.split("```")[1].split("```")[0]
        
        # Parsear JSON
        resultado = json.loads(texto_respuesta.strip())
        return resultado
        
    except json.JSONDecodeError as e:
        logging.error(f"Error al parsear JSON de Gemini: {str(e)}")
        logging.error(f"Respuesta recibida: {texto_respuesta[:500]}")
        raise
    except Exception as e:
        logging.error(f"Error al llamar a Gemini para agrupación: {str(e)}")
        raise


def generar_resumen_tema(tema: str, noticias_relacionadas: List[Dict], api_key: str, resumen_anterior: str = None) -> str:
    """
    Genera o actualiza el resumen de un tema usando Gemini.
    
    Args:
        tema: Nombre del tema
        noticias_relacionadas: Lista de noticias completas relacionadas al tema
        api_key: API key de Gemini
        resumen_anterior: Si existe, integra las novedades. Si es None, genera desde cero
        
    Returns:
        Resumen generado o actualizado
    """
    # Decidir qué prompt usar según si es tema nuevo o recurrente
    if resumen_anterior:
        logging.info(f"  🔄 Integrando resumen recurrente...")
        prompt = crear_prompt_resumen_recurrente(tema, resumen_anterior, noticias_relacionadas)
    else:
        logging.info(f"  ✨ Generando resumen nuevo...")
        prompt = crear_prompt_resumen(tema, noticias_relacionadas)
    
    try:
        client = genai.Client(api_key=api_key)
        
        # Usar gemini-2.5-flash con retry
        texto_respuesta = llamar_gemini_con_retry(client, "gemini-2.5-flash", prompt)
        
        return texto_respuesta.strip()
        
    except Exception as e:
        logging.error(f"Error al generar resumen para '{tema}': {str(e)}")
        return f"No se pudo generar resumen debido a sobrecarga del servicio. Por favor, intente más tarde."


def normalizar_nombre_tema(nombre: str) -> str:
    """
    Normaliza el nombre de un tema para comparaciones y generación de IDs.
    
    Args:
        nombre: Nombre original del tema
        
    Returns:
        Nombre normalizado
    """
    # Minúsculas
    norm = nombre.lower()
    
    # Remover artículos
    norm = re.sub(r'\b(el|la|los|las|un|una|unos|unas)\b', '', norm)
    
    # Remover acentos
    acentos = {'á':'a', 'é':'e', 'í':'i', 'ó':'o', 'ú':'u', 'ñ':'n'}
    for acento, sin_acento in acentos.items():
        norm = norm.replace(acento, sin_acento)
    
    # Limpiar espacios múltiples
    norm = re.sub(r'\s+', ' ', norm).strip()
    
    return norm


def generar_tema_id(nombre_normalizado: str, fecha: str) -> str:
    """
    Genera un ID único para el tema.
    
    Args:
        nombre_normalizado: Nombre normalizado del tema
        fecha: Fecha de detección
        
    Returns:
        ID del tema
    """
    # Tomar primeras palabras del nombre normalizado
    palabras = nombre_normalizado.split()[:3]
    base = '_'.join(palabras)
    
    # Agregar fecha para unicidad
    fecha_corta = fecha.replace('-', '')
    
    return f"{base}_{fecha_corta}"


def main():
    """
    Función principal que detecta y agrupa temas.
    """
    logging.info("=" * 70)
    logging.info("DETECCIÓN Y AGRUPACIÓN DE TEMAS CON IA")
    logging.info("=" * 70)
    
    # 1. Obtener API key
    try:
        api_key = obtener_api_key()
        logging.info("✓ API key de Gemini configurada")
    except ValueError as e:
        logging.error(str(e))
        return
    
    # 2. Cargar noticias del día
    try:
        data = cargar_noticias_del_dia()
        noticias = data.get("noticias", [])
        fecha_consolidacion = data.get("fecha_consolidacion", datetime.now().strftime("%Y-%m-%d"))
        logging.info(f"✓ Cargadas {len(noticias)} noticias del {fecha_consolidacion}")
    except Exception as e:
        logging.error(f"Error al cargar noticias: {str(e)}")
        return
    
    # 3. Cargar histórico de temas
    logging.info("\n" + "=" * 70)
    logging.info("CARGANDO HISTÓRICO DE TEMAS")
    logging.info("=" * 70)
    historico = cargar_historico()
    
    # 4. Actualizar estados de temas existentes (marcar inactivos)
    actualizar_estado_temas(historico, fecha_consolidacion)
    
    # 5. Seleccionar noticias para análisis
    noticias_seleccionadas = seleccionar_noticias_para_analisis(noticias)
    logging.info(f"Seleccionadas {len(noticias_seleccionadas)} noticias para análisis de temas")
    
    # 6. Agrupar noticias por tema con Gemini
    logging.info("\n" + "=" * 70)
    logging.info("AGRUPACIÓN POR TEMAS (Gemini AI)")
    logging.info("=" * 70)
    
    try:
        resultado_agrupacion = agrupar_con_gemini(noticias_seleccionadas, api_key)
        temas_detectados = resultado_agrupacion.get("temas", [])
        logging.info(f"✓ Detectados {len(temas_detectados)} temas")
        
        for tema_data in temas_detectados:
            logging.info(f"  • {tema_data['tema']}: {len(tema_data['indices_titulares'])} noticias")
            
    except Exception as e:
        logging.error(f"Error en agrupación: {str(e)}")
        logging.warning("No se pudieron detectar temas nuevos por sobrecarga de la API")
        logging.warning("Intentá ejecutar 'python scripts/agrupar_temas.py' más tarde")
        
        # Aunque falle la agrupación, copiar último temas_latest si existe
        import shutil
        FRONTEND_DIR.mkdir(parents=True, exist_ok=True)
        
        # Copiar último temas_latest si existe (el histórico NO se copia)
        archivos_temas = sorted(TEMAS_DIR.glob("temas_*.json"))
        if archivos_temas:
            try:
                ultimo_temas = archivos_temas[-1]
                archivo_frontend_temas = FRONTEND_DIR / "temas_latest.json"
                shutil.copy2(ultimo_temas, archivo_frontend_temas)
                logging.info(f"✓ Último archivo de temas copiado a frontend: {ultimo_temas.name}")
            except Exception as copy_error:
                logging.error(f"Error al copiar temas: {str(copy_error)}")
        
        return
    
    # 5. Generar resúmenes por cada tema
    logging.info("\n" + "=" * 70)
    logging.info("GENERACIÓN DE RESÚMENES")
    logging.info("=" * 70)
    
    # Pequeño delay después de la agrupación para respetar rate limit
    logging.info("⏳ Esperando 3s antes de comenzar generación de resúmenes...")
    time.sleep(3)
    
    temas_completos = []
    temas_pendientes = list(enumerate(temas_detectados, 1))  # (idx, tema_data)
    max_ciclos_reintento = 2
    ciclo = 0
    
    while temas_pendientes and ciclo <= max_ciclos_reintento:
        if ciclo > 0:
            logging.info("\n" + "=" * 70)
            logging.info(f"REINTENTANDO TEMAS FALLIDOS (Ciclo {ciclo})")
            logging.info("=" * 70)
            logging.info(f"⏳ Esperando 30s para resetear rate limit...")
            time.sleep(30)
        
        temas_para_siguiente_ciclo = []
        
        for idx_tema, tema_data in temas_pendientes:
            nombre_tema = tema_data['tema']
            indices = tema_data['indices_titulares']
            
            logging.info(f"\nProcesando tema {idx_tema}/{len(temas_detectados)}: {nombre_tema}")
            
            # Extraer noticias completas relacionadas (para usar contenido completo si está disponible)
            noticias_completas_relacionadas = []
            noticias_para_guardar = []
            fuentes_unicas = set()
            
            for idx in indices:
                if 0 <= idx - 1 < len(noticias_seleccionadas):  # indices son 1-based
                    noticia = noticias_seleccionadas[idx - 1]
                    fuente = noticia.get('fuente', '')
                    if fuente:
                        fuentes_unicas.add(fuente)
                    
                    # Guardar noticia completa para generar resumen (incluye contenido_completo si existe)
                    noticias_completas_relacionadas.append(noticia)
                    
                    # Guardar solo campos necesarios para el JSON final
                    noticias_para_guardar.append({
                        'titulo': noticia.get('titulo', ''),
                        'link': noticia.get('link', ''),
                        'fuente': fuente,
                        'fecha': noticia.get('fecha_local', '')
                    })
            
            # Validar que tenga al menos MIN_FUENTES_POR_TEMA fuentes diferentes
            if len(fuentes_unicas) < MIN_FUENTES_POR_TEMA:
                logging.warning(f"⚠️  Tema '{nombre_tema}' tiene solo {len(fuentes_unicas)} fuente(s). Requiere mínimo {MIN_FUENTES_POR_TEMA}. Saltando...")
                continue
            
            # Normalizar nombre del tema
            nombre_normalizado = normalizar_nombre_tema(nombre_tema)
            
            # Buscar si el tema ya existe en el histórico
            tema_id_existente = encontrar_tema_existente(nombre_tema, nombre_normalizado, historico)
            
            # Generar resumen con Gemini (nuevo o integrado según si existe)
            resumen_exitoso = False
            resumen_anterior = None
            es_tema_nuevo = True
            es_tema_recurrente = False
            dias_activo = 1
            
            if tema_id_existente:
                # Tema RECURRENTE: integrar con resumen anterior
                tema_historico = historico['temas'][tema_id_existente]
                resumen_anterior = tema_historico.get('resumen_actual', '')
                es_tema_nuevo = False
                es_tema_recurrente = True
                tema_id = tema_id_existente
            else:
                # Tema NUEVO: generar ID nuevo
                tema_id = generar_tema_id(nombre_normalizado, fecha_consolidacion)
            
            try:
                resumen = generar_resumen_tema(
                    nombre_tema, 
                    noticias_completas_relacionadas, 
                    api_key,
                    resumen_anterior=resumen_anterior
                )
                
                # Verificar que el resumen no sea un mensaje de error
                if not resumen.startswith("No se pudo generar resumen") and not resumen.startswith("Error al generar"):
                    logging.info(f"✓ Resumen generado ({len(resumen)} caracteres)")
                    
                    # Determinar categoría principal (la más frecuente, usando categoria_url)
                    categorias = []
                    for idx in indices:
                        if 0 <= idx - 1 < len(noticias_seleccionadas):
                            cat = noticias_seleccionadas[idx - 1].get('categoria_url', 'otros')
                            if cat and cat.strip():
                                categorias.append(cat.lower().strip())
                            else:
                                categorias.append('otros')
                    
                    categoria_principal = max(set(categorias), key=categorias.count) if categorias else 'otros'
                    fuentes_lista = list(set([n['fuente'] for n in noticias_para_guardar if n.get('fuente')]))
                    
                    # ACTUALIZAR O CREAR ENTRADA EN HISTÓRICO
                    if es_tema_recurrente:
                        # Actualizar tema existente en histórico
                        tema_historico = historico['temas'][tema_id]
                        tema_historico['fecha_ultima_aparicion'] = fecha_consolidacion
                        tema_historico['dias_activo'] = tema_historico.get('dias_activo', 0) + 1
                        tema_historico['resumen_actual'] = resumen
                        tema_historico['categoria_principal'] = categoria_principal
                        tema_historico['estado'] = 'activo'
                        
                        # Agregar aparición de hoy
                        tema_historico['apariciones'].append({
                            'fecha': fecha_consolidacion,
                            'cantidad_noticias': len(noticias_para_guardar),
                            'resumen': resumen,
                            'fuentes': fuentes_lista,
                            'categoria_principal': categoria_principal
                        })
                        
                        # Calcular tendencia y métricas
                        tema_historico['tendencia'] = calcular_tendencia(tema_historico['apariciones'])
                        tema_historico['metricas'] = calcular_metricas(tema_historico['apariciones'])
                        tema_historico['total_noticias_acumuladas'] = sum(a.get('cantidad_noticias', 0) for a in tema_historico['apariciones'])
                        
                        dias_activo = tema_historico['dias_activo']
                        
                    else:
                        # Crear nuevo tema en histórico
                        historico['temas'][tema_id] = {
                            'tema_id': tema_id,
                            'tema': nombre_tema,
                            'tema_normalizado': nombre_normalizado,
                            'alias': [],
                            'fecha_primer_deteccion': fecha_consolidacion,
                            'fecha_ultima_aparicion': fecha_consolidacion,
                            'dias_activo': 1,
                            'dias_consecutivos': 1,
                            'dias_inactivo': 0,
                            'apariciones': [{
                                'fecha': fecha_consolidacion,
                                'cantidad_noticias': len(noticias_para_guardar),
                                'resumen': resumen,
                                'fuentes': fuentes_lista,
                                'categoria_principal': categoria_principal
                            }],
                            'resumen_actual': resumen,
                            'categoria_principal': categoria_principal,
                            'total_noticias_acumuladas': len(noticias_para_guardar),
                            'estado': 'activo',
                            'tendencia': 'nuevo',
                            'metricas': calcular_metricas([{
                                'cantidad_noticias': len(noticias_para_guardar),
                                'fuentes': fuentes_lista
                            }])
                        }
                    
                    # Construir objeto de tema para el JSON del día
                    tema_completo = {
                        'tema_id': tema_id,
                        'tema': nombre_tema,
                        'tema_normalizado': nombre_normalizado,
                        'resumen': resumen,
                        'cantidad_noticias': len(noticias_para_guardar),
                        'noticias': noticias_para_guardar,
                        'categoria_principal': categoria_principal,
                        'fecha_deteccion': fecha_consolidacion,
                        'fuentes': fuentes_lista,
                        'es_tema_nuevo': es_tema_nuevo,
                        'es_tema_recurrente': es_tema_recurrente,
                        'dias_activo': dias_activo,
                        'tendencia': historico['temas'][tema_id].get('tendencia', 'nuevo')
                    }
                    
                    temas_completos.append(tema_completo)
                    resumen_exitoso = True
                else:
                    # Resumen falló, agregar a pendientes para reintentar
                    logging.warning(f"⚠️  Resumen falló, se reintentará después")
                    temas_para_siguiente_ciclo.append((idx_tema, tema_data))
                
            except Exception as e:
                logging.error(f"✗ Error al generar resumen: {str(e)}")
                temas_para_siguiente_ciclo.append((idx_tema, tema_data))
            
            # Delay entre resúmenes para respetar rate limit de Gemini (15 RPM)
            # Solo si fue exitoso y no es el último tema de este ciclo
            if resumen_exitoso and (idx_tema, tema_data) != temas_pendientes[-1]:
                delay = 5  # 5 segundos entre cada resumen
                logging.info(f"⏳ Esperando {delay}s antes del siguiente tema (rate limit)...")
                time.sleep(delay)
        
        # Actualizar pendientes para el próximo ciclo
        temas_pendientes = temas_para_siguiente_ciclo
        ciclo += 1
    
    # Resumen de procesamiento
    if temas_pendientes:
        logging.warning("\n" + "=" * 70)
        logging.warning(f"⚠️  {len(temas_pendientes)} TEMAS NO PUDIERON PROCESARSE")
        logging.warning("=" * 70)
        for idx, tema_data in temas_pendientes:
            logging.warning(f"  • {tema_data['tema']}")
        logging.warning("Intenta ejecutar el script nuevamente más tarde cuando la API esté menos cargada.")
        logging.warning("=" * 70)
    
    # NUEVO: Limpiar apariciones antiguas del histórico (mantener últimas 30)
    limpiar_apariciones_antiguas(historico, max_dias=30)
    
    # NUEVO: Guardar histórico actualizado
    logging.info("\n" + "=" * 70)
    logging.info("ACTUALIZANDO HISTÓRICO")
    logging.info("=" * 70)
    guardar_historico(historico)
    
    # 6. Guardar resultados del día
    logging.info("\n" + "=" * 70)
    logging.info("GUARDANDO RESULTADOS")
    logging.info("=" * 70)
    
    # Crear directorio de temas si no existe
    TEMAS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Estructura final
    resultado_final = {
        'fecha': fecha_consolidacion,
        'fecha_generacion': datetime.now().isoformat(),
        'total_temas': len(temas_completos),
        'temas': temas_completos
    }
    
    # Guardar en data/temas/
    nombre_archivo = f"temas_{fecha_consolidacion}.json"
    archivo_salida = TEMAS_DIR / nombre_archivo
    
    try:
        with open(archivo_salida, "w", encoding="utf-8") as f:
            json.dump(resultado_final, f, ensure_ascii=False, indent=2)
        
        logging.info(f"✓ Archivo guardado: {archivo_salida}")
        
        # Copiar también a frontend/data/ como "latest"
        try:
            FRONTEND_DIR.mkdir(parents=True, exist_ok=True)
            import shutil
            
            archivo_frontend = FRONTEND_DIR / "temas_latest.json"
            shutil.copy2(archivo_salida, archivo_frontend)
            logging.info(f"✓ Copiado a frontend: {archivo_frontend}")
            
        except Exception as e:
            logging.error(f"Error al copiar a frontend: {str(e)}")
        
        # Mostrar resumen
        logging.info("\n" + "=" * 70)
        logging.info("RESUMEN DE TEMAS DETECTADOS")
        logging.info("=" * 70)
        logging.info(f"Total detectados: {len(temas_detectados)}")
        logging.info(f"Procesados exitosamente: {len(temas_completos)}")
        logging.info(f"Fallidos: {len(temas_detectados) - len(temas_completos)}")
        
        # Estadísticas de nuevos vs recurrentes
        temas_nuevos = sum(1 for t in temas_completos if t.get('es_tema_nuevo'))
        temas_recurrentes = sum(1 for t in temas_completos if t.get('es_tema_recurrente'))
        logging.info(f"Temas NUEVOS: {temas_nuevos} ⭐")
        logging.info(f"Temas RECURRENTES: {temas_recurrentes} 🔄")
        logging.info("=" * 70)
        
        for tema in temas_completos:
            tipo = "⭐ NUEVO" if tema.get('es_tema_nuevo') else f"🔄 {tema.get('dias_activo', 1)} días"
            tendencia_emoji = {
                'nuevo': '✨',
                'creciente': '↑',
                'estable': '→',
                'decreciente': '↓'
            }.get(tema.get('tendencia', 'nuevo'), '')
            
            logging.info(f"• {tema['tema']} [{tipo}] {tendencia_emoji}")
            logging.info(f"  - {tema['cantidad_noticias']} noticias")
            logging.info(f"  - Categoría: {tema['categoria_principal']}")
            logging.info(f"  - Fuentes: {', '.join(tema['fuentes'][:3])}")
        
        logging.info("=" * 70)
        
    except Exception as e:
        logging.error(f"Error al guardar resultados: {str(e)}")


if __name__ == "__main__":
    main()

