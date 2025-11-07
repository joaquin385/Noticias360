# 📰 Frontend - Noticias360

## 📁 Estructura del Proyecto

```
frontend/
├── index.html          # Página principal HTML
├── css/
│   └── estilos.css     # Estilos personalizados adicionales
├── js/
│   └── app.js          # Lógica de la aplicación
├── data/               # Datos JSON de noticias
│   └── noticias_*.json
├── assets/             # Recursos (imágenes, íconos, etc.)
└── README.md           # Este archivo
```

## 🎨 Características Implementadas

### ✅ Navegación por Categorías
- Barra de navegación horizontal con botones de categorías
- Filtrado dinámico de noticias por categoría
- Botón "Todas" para mostrar todas las noticias

### ✅ Navegación por Fuentes
- Sub-bar de navegación con fuentes disponibles
- Filtrado por fuente dentro de la categoría seleccionada
- Fuentes se adaptan según la categoría elegida

### ✅ Tarjetas de Noticias
- Diseño tipo card con shadow y hover effects
- Información de fuente, categoría y fecha
- Descripción/resumen de la noticia
- Enlace para leer la noticia completa (abre en nueva pestaña)
- Indicador de horas atrás

### ✅ Header
- Logo/Nombre del sitio (Noticias360)
- Fecha de última actualización
- Botón de actualización manual

### ✅ Diseño Responsive
- Mobile-first approach
- Grid adaptativo (1 columna en mobile, 2 en tablet, 3 en desktop)
- Navegación con scroll horizontal en móviles

## 🚀 Uso

### Abrir la página
Abre `index.html` en un navegador web.

### Actualizar datos
1. Ejecuta el pipeline de backend en `scripts/ejecutar_pipeline.py`
2. Copia el archivo JSON generado de `data/noticias_YYYY-MM-DD.json` a `frontend/data/`
3. Recarga la página o haz clic en el botón "Actualizar"

## 🔧 Tecnologías Usadas

- **HTML5**: Estructura semántica
- **Tailwind CSS**: Framework CSS utility-first (via CDN)
- **JavaScript Vanilla**: Sin frameworks adicionales
- **Font Awesome**: Íconos (via HTML entities)

## 📋 Próximas Mejoras

- [ ] Buscador de noticias por palabra clave
- [ ] Modo oscuro/claro
- [ ] Favoritos guardados en localStorage
- [ ] Resumen automático con IA
- [ ] Ranking de temas más frecuentes
- [ ] Paginación para noticias

