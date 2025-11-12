# 📰 Noticias360 - Agregador Inteligente de Noticias

Sistema automatizado que:
- ✅ Extrae noticias de 8 medios argentinos (RSS)
- ✅ Clasifica automáticamente por categorías
- ✅ Genera resúmenes con IA (Gemini)
- ✅ Detecta temas relevantes y su evolución temporal
- ✅ Extrae contenido completo de artículos (web scraping)

## 🛠️ Stack

**Backend:** Python 3.11+ • feedparser • google-genai • newspaper3k • trafilatura  
**Frontend:** HTML5 • Tailwind CSS • JavaScript  
**Deploy:** Vercel + GitHub Actions

## 📁 Estructura Simplificada

```
├── data/                               # Backend (ignorado en Git)
│   ├── raw/                            # Noticias RSS crudas
│   ├── normalized/                     # Fechas normalizadas
│   ├── noticias_*.json                 # Consolidado diario
│   ├── noticias_contenido_*.json       # Con contenido completo (scraping)
│   └── temas/
│       ├── temas_*.json                # Temas detectados por día
│       └── historico_temas.json        # Evolución temporal de temas
│
├── frontend/data/                      # Para el sitio web (EN Git)
│   ├── noticias_YYYY-MM-DD.json        # Noticias del día (por fecha)
│   ├── resumenes_YYYY-MM-DD.json       # Resúmenes por categoría (por fecha)
│   └── temas_latest.json               # Temas del día (se sobrescribe)
│
├── scripts/                            # 7 scripts del pipeline
│   ├── ejecutar_pipeline.py            # ← EJECUTAR ESTE
│   ├── extraer_feeds.py
│   ├── normalizar_fechas.py
│   ├── integrar_fuentes.py
│   ├── clasificar_categorias_url.py
│   ├── extraer_contenido.py            # Scraping (nuevo)
│   ├── generar_resumenes_gemini.py
│   └── agrupar_temas.py                # Detección de temas (nuevo)
│
└── feeds_config.json                   # Configuración RSS
```

## ⚙️ Instalación Rápida

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar API de Gemini (crear archivo .env)
echo "GEMINI_API_KEY=tu-api-key" > .env

# 3. Ejecutar pipeline completo
python scripts/ejecutar_pipeline.py

# 4. Ver en navegador
python server.py
# Abre: http://localhost:8000
```

**Obtener API key gratuita:** https://aistudio.google.com/apikey

## 🔄 Pipeline Completo (7 Pasos)

```
┌─────────────────────────────────────────────────────────────────┐
│  python scripts/ejecutar_pipeline.py                           │
└─────────────────────────────────────────────────────────────────┘

PASO 1: extraer_feeds.py (~30s)
  • Descarga RSS de 8 fuentes (Clarín, La Nación, Infobae, etc.)
  • Guarda: data/raw/*.json

PASO 2: normalizar_fechas.py (~5s)
  • Convierte fechas a UTC-3 (Argentina)
  • Calcula horas_atras
  • Guarda: data/normalized/*.json

PASO 3: integrar_fuentes.py (~5s)
  • Consolida todas las fuentes en un archivo
  • Elimina duplicados
  • Guarda: data/noticias_2025-11-12.json

PASO 4: clasificar_categorias_url.py (~5s)
  • Clasifica por URL (Internacional, Política, Economía, etc.)
  • Limpia frontend/data/ (solo noticias/resúmenes viejos, NO temas)
  • Copia: frontend/data/noticias_2025-11-12.json ← FRONTEND

PASO 5: extraer_contenido.py (~4-5 min) [OPCIONAL]
  • Web scraping de 150 noticias (Internacional, Política, Economía)
  • Usa Newspaper3k + Trafilatura
  • Guarda: data/noticias_contenido_latest.json ← PARA IA

PASO 6: generar_resumenes_gemini.py (~30s)
  • Genera resúmenes de 4 categorías con Gemini
  • Guarda: data/resumenes_2025-11-12.json
  • Copia: frontend/data/resumenes_2025-11-12.json ← FRONTEND

PASO 7: agrupar_temas.py (~2-3 min)
  • Detecta 10 temas relevantes con Gemini
  • Identifica NUEVOS vs RECURRENTES (histórico)
  • Integra resúmenes para temas recurrentes
  • Calcula tendencias y métricas
  • Guarda:
    ├─ data/temas/historico_temas.json (tracking interno)
    ├─ data/temas/temas_2025-11-12.json (backup)
    └─ frontend/data/temas_latest.json ← FRONTEND

───────────────────────────────────────────────────────────────
TIEMPO TOTAL: ~8-12 minutos (con scraping)
              ~4-6 minutos (sin scraping - comentar PASO 5)
```

## 📋 Archivos que DEBE tener `frontend/data/`

**Solo 3 archivos** (el frontend busca por fecha):

```
frontend/data/
├── noticias_2025-11-12.json      # Noticias del día
├── resumenes_2025-11-12.json     # Resúmenes por categoría
└── temas_latest.json             # Temas del día
```

**Cómo los busca el frontend:**
- `noticias_*.json`: Calcula fecha actual (UTC-3 Argentina) → busca `noticias_YYYY-MM-DD.json`
- `resumenes_*.json`: Calcula fecha actual → busca `resumenes_YYYY-MM-DD.json`
- `temas_latest.json`: Siempre busca este nombre fijo

**Nota:** El histórico de temas (`historico_temas.json`) solo se guarda en `data/temas/` para tracking interno, el frontend no lo usa.

---

## 🎯 Scripts Individuales (para debugging)

```bash
# Extraer contenido completo (solo si necesitas regenerarlo)
python scripts/extraer_contenido.py

# Detectar temas (solo si falló en el pipeline)
python scripts/agrupar_temas.py

# Probar conexión con Gemini
python scripts/test_gemini_api.py
```

## 🧠 Sistema de Temas (Fase 2 - Con Histórico)

### **Qué hace:**
- Detecta **10 temas relevantes** por día usando IA
- Identifica si son **NUEVOS** ⭐ o **RECURRENTES** 🔄
- Para temas recurrentes: **integra** el resumen anterior + noticias nuevas
- Calcula **tendencias** (creciente ↑, estable →, decreciente ↓)
- Mantiene **histórico completo** de evolución día a día

### **Ejemplo de evolución:**

**Día 1 (10/11):** 
- "Cotizaciones del Dólar" ⭐ NUEVO
- Resumen generado desde cero

**Día 2 (11/11):**
- "Cotizaciones del Dólar" 🔄 2 días, ↑ CRECIENTE
- Resumen integrado (mantiene contexto + agrega novedades)

**Día 5 (14/11):**
- "Cotizaciones del Dólar" 🔥 5 días, → ESTABLE
- Si no aparece por 3+ días → marca como "inactivo"

### **Archivos generados:**
- `frontend/data/temas_latest.json`: Temas de HOY para el frontend (10 temas con resúmenes)
- `data/temas/historico_temas.json`: Tracking interno con todas las apariciones (NO se copia a frontend)

---

## 🎨 Frontend

**Vista Noticias:**
- Navegación: Internacional, Política, Economía, Sociedad
- Resumen colapsable por categoría (IA)
- Tarjetas intercaladas por fuente

**Vista Temas:**
- Filtrado por categoría (igual que noticias)
- Badges: ⭐ NUEVO, ↑ EN ALZA, 🔥 X días
- Resumen completo expandible

---

## ⚠️ Solución de Problemas

### Error 503 en Gemini (servicio sobrecargado)
```bash
# Esperar 1-2 minutos y reintentar solo el paso que falló:
python scripts/generar_resumenes_gemini.py  # Si falló PASO 6
python scripts/agrupar_temas.py             # Si falló PASO 7
```

### Falta `temas_latest.json` en frontend/
```bash
# Ejecutar solo detección de temas:
python scripts/agrupar_temas.py
```

### Acelerar el pipeline
Comentar PASO 5 en `ejecutar_pipeline.py` (líneas 97-109) para saltear el scraping.
Los temas funcionarán igual pero con menos detalle.

---

## 📊 Fuentes Configuradas

Clarín • La Nación • Infobae • Página 12 • Ámbito • Perfil • Minuto1 • iProfesional

Editá `feeds_config.json` para agregar más.

---

## 🤖 GitHub Actions (Automatización)

El workflow `.github/workflows/update_news.yml` ejecuta el pipeline **cada 3 horas automáticamente**.

### **Configuración (si aún no lo hiciste):**

1. **Configurar GEMINI_API_KEY en GitHub Secrets**
   - Ir a: `Settings` → `Secrets and variables` → `Actions`
   - Click en `New repository secret`
   - Name: `GEMINI_API_KEY`
   - Secret: Tu API key de Gemini
   - Click en `Add secret`

2. **Subir cambios al repositorio**
   ```bash
   git add .
   git commit -m "Update: nuevos scripts y workflow mejorado"
   git push
   ```

3. **Probar el workflow manualmente**
   - Ir a: `Actions` → `Actualizar noticias cada 3h`
   - Click en `Run workflow` → `Run workflow`
   - Esperar 8-12 minutos y revisar logs

### **Qué hace el workflow:**
- ✅ Ejecuta `ejecutar_pipeline.py` completo
- ✅ Limpia archivos antiguos de `frontend/data/`
- ✅ Commitea solo archivos del día actual
- ✅ Push automático a `main` con `[ci skip]` para evitar loops

### **Archivos que se commitean:**
```
frontend/data/
├── noticias_2025-11-12.json    (se sobrescribe cada 3h)
├── resumenes_2025-11-12.json   (se sobrescribe cada 3h)
└── temas_latest.json           (se sobrescribe cada 3h)
```

---

**Última actualización:** Noviembre 2025

