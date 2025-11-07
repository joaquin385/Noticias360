# Resumen de Noticias Diarias

Agregador de noticias RSS para Argentina que consolida información de múltiples fuentes periodísticas, normaliza los datos, clasifica automáticamente por categorías y genera resúmenes inteligentes usando IA (Google Gemini).

## 📋 Descripción

Esta aplicación automatiza la recopilación diaria de noticias desde múltiples fuentes RSS de medios argentinos, las procesa, clasifica y presenta en una interfaz web moderna. Además, utiliza inteligencia artificial para generar resúmenes ejecutivos por categoría de las noticias más relevantes.

## 🚀 Tecnologías Utilizadas

### Backend
- **Python 3.11+**: Lenguaje principal para los scripts de procesamiento
- **feedparser**: Biblioteca para parsear feeds RSS/Atom
- **python-dateutil**: Manejo y conversión de fechas y zonas horarias
- **google-genai**: SDK oficial de Google para interactuar con Gemini AI
- **json**: Manejo de datos estructurados
- **pathlib**: Gestión de archivos y rutas multiplataforma
- **logging**: Sistema de registro de eventos y errores

### Frontend
- **HTML5**: Estructura de la página
- **CSS3 con Tailwind CSS**: Framework de estilos utilitarios para diseño responsivo
- **JavaScript (ES6+)**: Lógica del cliente
  - Fetch API: Carga asíncrona de datos JSON
  - DOM API: Manipulación dinámica del contenido
  - Event Listeners: Interactividad del usuario

### Despliegue
- **Vercel**: Hosting de archivos estáticos y frontend
- **Git**: Control de versiones

## 📁 Estructura de Carpetas

```
Resumen de Noticias Diarias/
│
├── data/                          # Datos procesados (NO en Git)
│   ├── raw/                       # Noticias crudas extraídas de RSS
│   ├── normalized/                # Noticias con fechas normalizadas
│   ├── noticias_YYYY-MM-DD.json  # Dataset consolidado diario
│   └── resumenes_YYYY-MM-DD.json # Resúmenes generados por Gemini
│
├── frontend/                      # Aplicación web
│   ├── css/
│   │   └── estilos.css           # Estilos personalizados
│   ├── js/
│   │   └── app.js                # Lógica del frontend
│   ├── data/                     # Datos para consumo del frontend (NO en Git)
│   │   ├── noticias_YYYY-MM-DD.json
│   │   └── resumenes_YYYY-MM-DD.json
│   ├── assets/                   # Recursos estáticos
│   └── index.html                # Página principal
│
├── scripts/                       # Scripts de procesamiento
│   ├── extraer_feeds.py          # Extracción de RSS
│   ├── normalizar_fechas.py      # Normalización de fechas
│   ├── integrar_fuentes.py       # Consolidación de datos
│   ├── clasificar_categorias_url.py  # Clasificación por URL
│   ├── generar_resumenes_gemini.py   # Generación de resúmenes IA
│   ├── ejecutar_pipeline.py      # Script maestro
│   └── test_gemini_api.py        # Prueba de API de Gemini
│
├── .env                          # Variables de entorno (NO en Git)
├── .gitignore                    # Archivos ignorados por Git
├── feeds_config.json             # Configuración de fuentes RSS
├── requirements.txt              # Dependencias de Python
├── vercel.json                   # Configuración de Vercel
└── README.md                     # Esta documentación
```

## 🔧 Instalación y Configuración Local

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd "Resumen de Noticias Diarias"
```

### 2. Instalar dependencias de Python

```bash
pip install -r requirements.txt
```

### 3. Configurar API de Gemini

Crea un archivo `.env` en la raíz del proyecto:

```env
GEMINI_API_KEY=tu-api-key-aqui
```

Puedes obtener una API key gratuita en: https://aistudio.google.com/apikey

### 4. Ejecutar el pipeline de datos

```bash
python scripts/ejecutar_pipeline.py
```

Este comando:
1. Extrae noticias de RSS
2. Normaliza fechas a UTC-3
3. Consolida todas las fuentes
4. Clasifica por categoría
5. Genera resúmenes con IA

### 5. Visualizar el frontend localmente

**Opción A - Servidor HTTP de Python (incluido)**:
```bash
python server.py
```
Abre: `http://localhost:8000`

**Opción B - Cualquier servidor HTTP**:
```bash
# Con Python
cd frontend && python -m http.server 8000

# Con Node.js
cd frontend && npx serve
```

## 🌐 Despliegue en Vercel

### Configuración Inicial

1. **Instala Vercel CLI** (opcional):
```bash
npm install -g vercel
```

2. **Conecta el repositorio a Vercel**:
   - Ve a [vercel.com](https://vercel.com)
   - Importa tu repositorio de GitHub/GitLab/Bitbucket
   - Vercel detectará automáticamente la configuración de `vercel.json`

3. **Configuración en Vercel**:
   - **Framework Preset**: Other
   - **Root Directory**: `./`
   - **Build Command**: (vacío)
   - **Output Directory**: `frontend`

### Actualización de Datos en Producción

Los archivos JSON (noticias y resúmenes) se generan localmente y deben subirse manualmente o mediante CI/CD:

**Opción 1 - Manual**:
```bash
# Generar datos localmente
python scripts/ejecutar_pipeline.py

# Subir frontend/data/ a Vercel
# (Puedes usar Vercel CLI o GitHub Actions)
```

**Opción 2 - GitHub Actions** (recomendado):

Crea `.github/workflows/update-news.yml`:

```yaml
name: Update News Daily

on:
  schedule:
    - cron: '0 12 * * *'  # Ejecuta diariamente a las 12:00 UTC
  workflow_dispatch:  # Permite ejecución manual

jobs:
  update-news:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run pipeline
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: python scripts/ejecutar_pipeline.py
      
      - name: Commit and push if changed
        run: |
          git config --global user.name 'GitHub Action'
          git config --global user.email 'action@github.com'
          git add frontend/data/
          git diff --quiet && git diff --staged --quiet || (git commit -m "Update news data" && git push)
```

**Configurar secreto en GitHub**:
1. Ve a tu repositorio > Settings > Secrets and variables > Actions
2. Crea un nuevo secret: `GEMINI_API_KEY` con tu API key

### Nota Importante sobre Vercel
- Vercel es ideal para el **frontend estático**
- Los scripts de Python **NO se ejecutan** en Vercel
- Los datos deben generarse localmente o mediante CI/CD y pushearse al repositorio
- El frontend lee los archivos JSON estáticos

## 📊 Scripts y Funcionalidades

### Pipeline Completo
```bash
python scripts/ejecutar_pipeline.py
```

Ejecuta en orden:
1. **Extracción**: Descarga noticias de RSS
2. **Normalización**: Convierte fechas a UTC-3
3. **Integración**: Consolida y elimina duplicados
4. **Clasificación**: Categoriza por URL
5. **Resúmenes IA**: Genera resúmenes con Gemini

### Scripts Individuales

```bash
# Solo extraer noticias
python scripts/extraer_feeds.py

# Solo normalizar fechas
python scripts/normalizar_fechas.py

# Solo integrar fuentes
python scripts/integrar_fuentes.py

# Solo clasificar
python scripts/clasificar_categorias_url.py

# Solo generar resúmenes
python scripts/generar_resumenes_gemini.py

# Probar API de Gemini
python scripts/test_gemini_api.py
```

## 🎨 Funcionalidades del Frontend

- **Navegación por categorías**: Internacional, Política, Economía, Sociedad
- **Filtro por fuente**: Filtra por medio periodístico
- **Resumen desplegable**: Resumen ejecutivo generado por IA
- **Grid responsivo**: Adaptable a móviles, tablets y desktop
- **Ordenamiento inteligente**: Intercala noticias de diferentes fuentes
- **Actualización dinámica**: Carga datos del día actual automáticamente

## 🔍 Fuentes de Noticias Configuradas

- Clarín
- La Nación
- Infobae
- Página 12
- Ámbito Financiero
- Perfil
- Minuto1
- iProfesional

Las fuentes se configuran en `feeds_config.json`.

## 🛠️ Configuración de Fuentes RSS

Edita `feeds_config.json`:

```json
[
  {
    "fuente": "Nombre del medio",
    "url": "https://ejemplo.com/rss",
    "categoria": "Categoría del feed",
    "zona_horaria": "UTC-3"
  }
]
```

## 📝 Formato de Datos

### Noticia Individual
```json
{
  "titulo": "Título de la noticia",
  "link": "https://...",
  "fecha_local": "2025-10-29 12:23:30",
  "horas_atras": 2.5,
  "resumen": "Descripción...",
  "fuente": "Clarín",
  "categoria_url": "politica"
}
```

### Resumen por Categoría
```json
{
  "fecha_consolidacion": "2025-10-29",
  "resumenes": {
    "internacional": {
      "resumen": "Texto del resumen...",
      "cantidad_noticias": 30
    }
  }
}
```

## 🐛 Solución de Problemas

### Error: "GEMINI_API_KEY no está configurada"
```bash
# Crea archivo .env con:
GEMINI_API_KEY=tu-api-key

# O configura variable de entorno:
export GEMINI_API_KEY='tu-api-key'  # Linux/Mac
$env:GEMINI_API_KEY='tu-api-key'   # PowerShell
```

### Frontend no muestra noticias
- Ejecuta el pipeline primero: `python scripts/ejecutar_pipeline.py`
- Verifica que existan archivos en `frontend/data/`
- Revisa la consola del navegador para errores

### Resúmenes no aparecen
- Verifica que la API key de Gemini sea válida
- Ejecuta: `python scripts/test_gemini_api.py`

## 📄 Licencia

Este proyecto es de uso personal/educacional.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

**Desarrollado con ❤️ para mantener informados a los argentinos**

**Última actualización**: Octubre 2025

