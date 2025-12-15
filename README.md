# 📰 Noticias360 - Agregador de Noticias RSS

Sistema automatizado que:
- ✅ Extrae noticias de 8 medios argentinos (RSS)
- ✅ Normaliza fechas y consolida noticias en un único JSON diario
- ✅ Clasifica automáticamente por categorías (heurísticas por URL / RSS)

## 🛠️ Stack

**Backend:** Python 3.11+ • feedparser • python-dateutil  
**Frontend:** HTML5 • Tailwind CSS • JavaScript  
**Deploy:** Vercel + GitHub Actions

## 📁 Estructura Simplificada

```
├── data/                               # Backend (ignorado en Git)
│   ├── raw/                            # Noticias RSS crudas
│   ├── normalized/                     # Fechas normalizadas
│   ├── noticias_*.json                 # Consolidado diario
│   ├── noticias_contenido_*.json       # Con contenido completo (scraping - opcional/legacy)
│   └── temas/                          # Datos de temas IA (legacy, opcional)
│       ├── temas_*.json                # Temas detectados por día
│       └── historico_temas.json        # Evolución temporal de temas
│
├── frontend/data/                      # Para el sitio web (EN Git)
│   └── noticias_YYYY-MM-DD.json        # Noticias del día (por fecha)
│
├── scripts/                            # 4 pasos principales (+ scripts legacy IA)
│   ├── ejecutar_pipeline.py            # ← EJECUTAR ESTE (modo sin IA)
│   ├── extraer_feeds.py
│   ├── normalizar_fechas.py
│   ├── integrar_fuentes.py
│   ├── clasificar_categorias_url.py
│   ├── extraer_contenido.py            # Scraping (opcional / legacy IA)
│   ├── generar_resumenes_gemini.py     # Resúmenes con IA (legacy, desactivado del pipeline)
│   └── agrupar_temas.py                # Temas con IA (legacy, desactivado del pipeline)
│
└── feeds_config.json                   # Configuración RSS
```

## ⚙️ Instalación Rápida (modo sin IA)

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar pipeline (modo sin IA)
python scripts/ejecutar_pipeline.py

# 3. Ver en navegador
python server.py
# Abre: http://localhost:8000
```

## 🔄 Pipeline Completo (4 Pasos activos)

```
┌─────────────────────────────────────────────────────────────────┐
│  python scripts/ejecutar_pipeline.py      # Modo sin IA         │
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
  • Guarda: data/noticias_YYYY-MM-DD.json

PASO 4: clasificar_categorias_url.py (~5s)
  • Clasifica por URL (Internacional, Política, Economía, etc.)
  • Limpia frontend/data/ (noticias viejas)
  • Copia: frontend/data/noticias_YYYY-MM-DD.json ← FRONTEND

PASOS 5-7 (scraping + IA) están desactivados en el pipeline actual.

───────────────────────────────────────────────────────────────
TIEMPO TOTAL: ~4-6 minutos (modo sin IA)
```

## 📋 Archivos que DEBE tener `frontend/data/`

**Archivo principal que usa el frontend:**

```
frontend/data/
└── noticias_YYYY-MM-DD.json      # Noticias del día
```

**Cómo lo busca el frontend:**
- Calcula fecha actual (UTC-3 Argentina) → busca `noticias_YYYY-MM-DD.json`

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

## 🎨 Frontend

**Vista Noticias:**
- Navegación: Internacional, Política, Economía, Sociedad
- Tarjetas intercaladas por fuente

---

## ⚠️ Solución de Problemas

### Acelerar el pipeline
En modo sin IA no es necesario configurar API keys ni scraping extra; el pipeline ya corre con los 4 pasos básicos.

---

## 📊 Fuentes Configuradas

Clarín • La Nación • Infobae • Página 12 • Ámbito • Perfil • Minuto1 • iProfesional

Editá `feeds_config.json` para agregar más.

---

## 🤖 GitHub Actions (Automatización, modo sin IA)

El workflow `.github/workflows/update_news.yml` ejecuta el pipeline **cada 3 horas automáticamente** en modo sin IA.

### **Configuración (si aún no lo hiciste):**

1. **Subir cambios al repositorio**
   ```bash
   git add .
   git commit -m "Update: nuevos scripts y workflow mejorado"
   git push
   ```

2. **Probar el workflow manualmente**
   - Ir a: `Actions` → `Actualizar noticias cada 3h`
   - Click en `Run workflow` → `Run workflow`
   - Esperar 8-12 minutos y revisar logs

### **Qué hace el workflow:**
- ✅ Ejecuta `ejecutar_pipeline.py` (sin IA)
- ✅ Limpia archivos antiguos de `frontend/data/`
- ✅ Commitea solo archivos del día actual (`noticias_YYYY-MM-DD.json`)
- ✅ Push automático a `main` con `[ci skip]` para evitar loops

---

**Última actualización:** Noviembre 2025

