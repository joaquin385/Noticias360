Quiero rediseñar la pagina web.

El objetivo NO es modernidad ni impacto visual, sino transmitir tranquilidad, reflexión y lectura lenta, como un diario físico o revista cultural impresa.

La estética debe:

Recordar al papel ligeramente gastado

Usar colores suaves (beige, gris, tinta)

Evitar blanco puro y negro puro

Usar tipografías serif editoriales

Tener mucho espacio en blanco

Separadores delicados (líneas finas, símbolos editoriales)

Nada invasivo, nada ruidoso




Necesito propuestas concretas de:

Paleta de colores

Tipografías (titulares y cuerpo)

Layout (anchos, columnas, márgenes)

Estilo de separadores

Ritmo visual

Detalles sutiles que refuercen la sensación de diario impreso

Pensar la experiencia como un espacio de lectura serena, no como un portal de noticias tradicional.


Es importante que no busco esa captacion moderna de atencion. Sino que busco romper un poco con esa dinamica.

---

## PLANIFICACIÓN DEL REDISEÑO

### 1. PALETA DE COLORES

**Fondo principal (papel gastado):**
- `#faf8f5` - Beige muy claro, como papel envejecido
- Alternativa: `#f7f5f2` - Un poco más cálido

**Fondo secundario:**
- `#f5f3f0` - Para secciones diferenciadas
- `#f0ede8` - Para cards/tarjetas

**Texto principal (tinta):**
- `#2c2416` - Marrón oscuro, como tinta de imprenta (no negro puro)
- Alternativa: `#3d3528` - Un poco más claro

**Texto secundario:**
- `#6b6458` - Gris cálido para metadatos
- `#8b8579` - Gris más claro para elementos menos importantes

**Acentos sutiles:**
- `#8b7355` - Marrón medio para enlaces y elementos interactivos
- `#a8997a` - Marrón claro para hover states (muy sutil)

**Bordes y separadores:**
- `#e8e4df` - Líneas muy suaves, casi imperceptibles
- `#d4cfc7` - Un poco más visible cuando se necesita

**Evitar completamente:**
- Blanco puro (`#ffffff`)
- Negro puro (`#000000`)
- Colores brillantes (azules, rojos, verdes saturados)
- Sombras duras o contrastes fuertes

---

### 2. TIPOGRAFÍAS

**Titulares principales (H1, H2):**
- **Google Fonts:** `Crimson Text` o `Lora` o `Playfair Display`
- **Fallback:** `Georgia, serif`
- **Tamaños:** 
  - H1: `2.5rem` (40px) - máximo, con mucho espacio arriba
  - H2: `1.75rem` (28px)
  - H3: `1.35rem` (22px)
- **Peso:** `400` (regular) o `600` (semi-bold) para énfasis, nunca `700` o más
- **Interlineado:** `1.4` - `1.5` para legibilidad serena

**Cuerpo de texto:**
- **Google Fonts:** `Crimson Text` o `Lora` (misma familia que titulares para coherencia)
- **Fallback:** `Georgia, serif`
- **Tamaño:** `1.125rem` (18px) - más grande que lo estándar para lectura cómoda
- **Interlineado:** `1.7` - `1.8` - mucho espacio entre líneas
- **Peso:** `400` (regular)

**Metadatos y elementos pequeños:**
- **Fuente:** Misma serif pero más pequeña
- **Tamaño:** `0.875rem` (14px) o `0.9375rem` (15px)
- **Color:** `#6b6458` (gris cálido)

**Código y datos técnicos:**
- Mantener `monospace` pero con color suave: `#6b6458`

---

### 3. LAYOUT Y ESTRUCTURA

**Ancho máximo del contenido:**
- **Desktop:** `65ch` - `75ch` (medido en caracteres, no píxeles)
- **Tablet:** `90%` del viewport, máximo `65ch`
- **Mobile:** `95%` del viewport, padding lateral `1.5rem`

**Márgenes y espaciado:**
- **Márgenes verticales entre secciones:** `4rem` - `5rem` (64px - 80px)
- **Márgenes verticales entre elementos:** `2rem` - `3rem` (32px - 48px)
- **Padding lateral:** `2rem` - `3rem` (32px - 48px)
- **Espacio entre párrafos:** `1.5rem` (24px)

**Sistema de columnas:**
- **Noticias:** Una sola columna vertical (no grid mosaico)
- **Cada noticia:** Ocupa todo el ancho disponible, con mucho espacio vertical
- **Indicadores:** También una columna, sin cards apiladas

**Header:**
- Altura reducida: `4rem` (64px) máximo
- Fondo: `#faf8f5` (mismo que el body)
- Borde inferior: Línea muy sutil `1px solid #e8e4df`
- Sin sombras, sin sticky (o sticky muy discreto)

**Footer:**
- Mismo fondo que body
- Borde superior: Línea sutil
- Texto pequeño y discreto
- Márgenes verticales generosos

---

### 4. ESTILO DE SEPARADORES

**Entre noticias/artículos:**
- Línea horizontal muy fina: `1px solid #e8e4df`
- Espacio arriba: `3rem` (48px)
- Espacio abajo: `2rem` (32px)
- Opcional: Símbolo editorial discreto (• o —) centrado sobre la línea

**Entre secciones principales:**
- Línea más visible pero aún suave: `1px solid #d4cfc7`
- Espacio vertical: `5rem` (80px)
- Opcional: Número de sección o fecha en tipografía pequeña

**En el header:**
- Línea inferior: `1px solid #e8e4df`
- Sin sombras ni efectos

**En cards/tarjetas (si se mantienen):**
- Borde: `1px solid #e8e4df`
- Sin bordes redondeados excesivos: `border-radius: 2px` máximo
- Sin sombras o sombras muy sutiles: `box-shadow: 0 1px 3px rgba(0,0,0,0.05)`

---

### 5. RITMO VISUAL

**Jerarquía tipográfica clara pero sutil:**
- Tamaños diferenciados pero no agresivos
- Espaciado generoso entre niveles
- Uso de mayúsculas pequeñas (`text-transform: uppercase`, `font-size: 0.75rem`, `letter-spacing: 0.1em`) para etiquetas

**Espaciado vertical rítmico:**
- Múltiplos de `1rem` (16px): `1rem`, `1.5rem`, `2rem`, `3rem`, `4rem`, `5rem`
- Consistencia en todo el sitio

**Imágenes:**
- Bordes muy sutiles: `1px solid #e8e4df`
- Sin bordes redondeados o muy mínimos
- Espacio generoso alrededor
- Opcional: Efecto sutil de papel (muy ligero, casi imperceptible)

**Enlaces:**
- Color: `#8b7355` (marrón medio)
- Sin subrayado por defecto
- Subrayado sutil al hover: `text-decoration: underline`, `text-decoration-color: #a8997a`
- Sin cambios de color bruscos

---

### 6. DETALLES SUTILES DE DIARIO IMPRESO

**Efecto de papel (opcional, muy sutil):**
- `background-image: url('data:image/svg+xml,...')` con textura de papel muy ligera
- Opacidad: `0.02` - `0.03` (casi imperceptible)

**Numeración de páginas (footer):**
- Estilo discreto, como en revista

**Fechas y metadatos:**
- Tipografía pequeña, color gris cálido
- Formato: "15 de diciembre de 2025" (no "15/12/2025")
- Separador: "•" o "—" entre elementos

**Badges y etiquetas:**
- Fondo: `#f0ede8` (beige muy claro)
- Borde: `1px solid #e8e4df`
- Texto: `#6b6458`
- Sin bordes redondeados o mínimos: `border-radius: 2px`
- Padding: `0.25rem 0.5rem`

**Botones:**
- Fondo: `#f5f3f0`
- Borde: `1px solid #d4cfc7`
- Texto: `#2c2416`
- Hover: Fondo `#f0ede8`, borde `#c9c4bb`
- Sin transformaciones ni sombras en hover
- Transición muy suave: `transition: all 0.2s ease`

**Cards de noticias:**
- Fondo: `#faf8f5` (mismo que body) o `#f5f3f0` (muy sutil)
- Borde: `1px solid #e8e4df`
- Padding: `2rem` (32px)
- Márgenes verticales: `2.5rem` (40px)
- Sin sombras o sombra muy sutil
- Sin efectos hover agresivos

**Grid de noticias:**
- Eliminar el grid mosaico moderno
- Lista vertical simple, una noticia debajo de otra
- Cada noticia con título, metadatos, imagen (opcional), resumen, enlace

---

### 7. ELEMENTOS A ELIMINAR O SUAVIZAR

**Eliminar:**
- Grid mosaico con tamaños variables
- Sombras pronunciadas (`box-shadow` fuerte)
- Bordes redondeados excesivos (`border-radius: 0.75rem` o más)
- Colores brillantes (azules `#2563eb`, etc.)
- Efectos hover agresivos (transform, scale)
- Animaciones llamativas
- Emojis en el header (o reemplazarlos por texto simple)
- Sticky header con sombra

**Suavizar:**
- Transiciones: De `0.3s` a `0.2s`, más sutiles
- Hover states: Cambios de color muy leves
- Focus states: Outline suave, no el default del navegador

---

### 8. IMPLEMENTACIÓN TÉCNICA

**Orden de trabajo:**
1. Actualizar paleta de colores en CSS
2. Cambiar tipografías (importar Google Fonts, actualizar `font-family`)
3. Ajustar layout (anchos máximos, márgenes, espaciado)
4. Rediseñar cards de noticias (de grid mosaico a lista vertical)
5. Actualizar separadores y bordes
6. Ajustar header y footer
7. Refinar detalles (badges, botones, enlaces)
8. Aplicar a todas las páginas (index.html, indicadores.html, subarea.html)

**Archivos a modificar:**
- `frontend/css/estilos.css` - Estilos principales
- `frontend/index.html` - Estructura y clases
- `frontend/indicadores.html` - Aplicar mismo estilo
- `frontend/indicadores/subarea.html` - Aplicar mismo estilo
- `frontend/js/app.js` - Ajustar generación de HTML de noticias si es necesario

**Consideraciones:**
- Mantener funcionalidad existente
- Asegurar legibilidad (contraste suficiente aunque suave)
- Responsive design manteniendo la estética
- Performance: Cargar tipografías de forma eficiente

---

### 9. REFERENCIAS DE INSPIRACIÓN

**Estética objetivo:**
- The New York Times (versión impresa, no digital)
- The Guardian (estilo editorial clásico)
- Medium (en su versión más minimalista)
- Revistas culturales impresas (Letras Libres, The New Yorker)

**Principios:**
- Menos es más
- El contenido es el rey
- La tipografía es la protagonista
- El espacio en blanco es diseño
- La calma es un valor

---

## PLAN DE IMPLEMENTACIÓN EN FASES

### FASE 1: FUNDACIÓN (Base visual)
**Objetivo:** Establecer la base visual del rediseño sin romper funcionalidad.

**Tareas:**
1. **Actualizar paleta de colores en CSS**
   - Definir variables CSS para todos los colores de la paleta
   - Reemplazar colores hardcodeados por variables
   - Archivo: `frontend/css/estilos.css`

2. **Cambiar tipografías**
   - Importar Google Fonts (Crimson Text o Lora)
   - Actualizar `font-family` en body y elementos base
   - Ajustar tamaños de fuente según especificación
   - Archivos: `frontend/index.html` (head), `frontend/css/estilos.css`

3. **Ajustar fondo y colores base**
   - Cambiar `bg-gray-50` por color beige (`#faf8f5`)
   - Actualizar colores de texto principales
   - Archivos: `frontend/index.html`, `frontend/indicadores.html`, `frontend/indicadores/subarea.html`

**Criterios de éxito:**
- La página carga con nueva paleta y tipografía
- No hay errores de consola
- El contenido sigue siendo legible

**Tiempo estimado:** 2-3 horas

---

### FASE 2: LAYOUT Y ESPACIADO
**Objetivo:** Reestructurar el layout para lectura serena.

**Tareas:**
1. **Ajustar ancho máximo del contenido**
   - Implementar `max-width: 65ch` - `75ch` en contenedores principales
   - Centrar contenido con márgenes automáticos
   - Archivos: `frontend/css/estilos.css`

2. **Rediseñar header**
   - Reducir altura a máximo 4rem
   - Cambiar fondo a beige
   - Agregar borde inferior sutil
   - Eliminar sombras
   - Simplificar diseño (quitar emojis o reemplazar por texto)
   - Archivos: `frontend/index.html`, `frontend/indicadores.html`, `frontend/indicadores/subarea.html`, `frontend/css/estilos.css`

3. **Ajustar márgenes y espaciado vertical**
   - Implementar sistema de espaciado rítmico (múltiplos de 1rem)
   - Aumentar márgenes entre secciones (4rem - 5rem)
   - Aumentar padding lateral (2rem - 3rem)
   - Archivos: `frontend/css/estilos.css`

4. **Rediseñar footer**
   - Cambiar fondo a beige
   - Agregar borde superior sutil
   - Ajustar tipografía y espaciado
   - Archivos: Todos los HTML, `frontend/css/estilos.css`

**Criterios de éxito:**
- El contenido está centrado y tiene ancho cómodo para lectura
- Hay mucho espacio en blanco alrededor
- El header y footer son discretos

**Tiempo estimado:** 3-4 horas

---

### FASE 3: NOTICIAS (Transformación principal)
**Objetivo:** Convertir grid mosaico en lista vertical serena.

**Tareas:**
1. **Eliminar grid mosaico**
   - Remover `.mosaic-grid` y sus estilos
   - Cambiar a layout de lista vertical simple
   - Archivos: `frontend/css/estilos.css`, `frontend/js/app.js`

2. **Rediseñar cards de noticias**
   - Eliminar clases de tamaño variable (hero, large, standard)
   - Crear estilo único y uniforme para todas las noticias
   - Cambiar fondo a beige claro o mantener fondo del body
   - Agregar borde sutil (`1px solid #e8e4df`)
   - Reducir `border-radius` a 2px máximo
   - Eliminar sombras o hacerlas muy sutiles
   - Aumentar padding interno (2rem)
   - Aumentar márgenes verticales entre noticias (2.5rem)
   - Archivos: `frontend/css/estilos.css`

3. **Ajustar elementos internos de noticias**
   - Rediseñar títulos (tipografía serif, tamaño adecuado)
   - Ajustar metadatos (color gris cálido, tipografía pequeña)
   - Rediseñar badges (fondo beige, borde sutil, sin bordes redondeados)
   - Ajustar imágenes (borde sutil, espacio generoso)
   - Rediseñar enlaces (color marrón, hover sutil)
   - Archivos: `frontend/css/estilos.css`, `frontend/js/app.js` (si genera HTML)

4. **Eliminar efectos hover agresivos**
   - Quitar `transform: translateY()` y escalados
   - Cambiar a hover muy sutil (cambio de color de borde o fondo mínimo)
   - Archivos: `frontend/css/estilos.css`

**Criterios de éxito:**
- Las noticias se muestran en lista vertical
- Todas las noticias tienen el mismo estilo
- No hay efectos visuales agresivos
- La lectura es cómoda y serena


Homepage = 90% lista vertical

Podés permitir:

1 bloque editorial arriba (muy sobrio)
1 separador temático ocasional
**Tiempo estimado:** 4-5 horas

---

### FASE 4: NAVEGACIÓN Y FILTROS
**Objetivo:** Suavizar elementos de navegación y filtros.

**Tareas:**
1. **Rediseñar navegación de categorías**
   - Cambiar fondo a beige claro
   - Rediseñar botones (fondo beige, borde sutil, sin bordes redondeados)
   - Ajustar estados hover y active (muy sutiles)
   - Archivos: `frontend/index.html`, `frontend/css/estilos.css`

2. **Rediseñar botones generales**
   - Aplicar estilo consistente a todos los botones
   - Fondo beige, borde sutil, sin efectos agresivos
   - Archivos: `frontend/css/estilos.css`

3. **Ajustar separadores**
   - Implementar líneas finas entre noticias
   - Agregar separadores entre secciones principales
   - Usar colores suaves (#e8e4df, #d4cfc7)
   - Archivos: `frontend/css/estilos.css`, posiblemente `frontend/js/app.js`

**Criterios de éxito:**
- La navegación es discreta y funcional
- Los botones tienen estilo consistente y sutil
- Los separadores son elegantes y no invasivos

**Tiempo estimado:** 2-3 horas

---

### FASE 5: PÁGINA DE INDICADORES
**Objetivo:** Aplicar mismo estilo a la sección de indicadores.

**Tareas:**
1. **Actualizar `indicadores.html`**
   - Aplicar nueva paleta y tipografía
   - Ajustar layout y espaciado
   - Rediseñar header y footer
   - Archivos: `frontend/indicadores.html`, `frontend/css/estilos.css`

2. **Rediseñar botones de áreas**
   - Cambiar estilo a "tags" más sutiles
   - Fondo beige claro, borde sutil
   - Ajustar grid para que se vean uniformes
   - Archivos: `frontend/css/estilos.css`

3. **Rediseñar cards de subáreas**
   - Aplicar mismo estilo que cards de noticias
   - Fondo beige, borde sutil, espaciado generoso
   - Eliminar efectos hover agresivos
   - Archivos: `frontend/css/estilos.css`

**Criterios de éxito:**
- La página de indicadores tiene el mismo estilo que noticias
- La experiencia es consistente en todo el sitio

**Tiempo estimado:** 2-3 horas

---

### FASE 6: PÁGINA DE SUBÁREA
**Objetivo:** Completar el rediseño en todas las páginas.

**Tareas:**
1. **Actualizar `subarea.html`**
   - Aplicar nueva paleta y tipografía
   - Ajustar layout y espaciado
   - Rediseñar header y footer
   - Archivos: `frontend/indicadores/subarea.html`, `frontend/css/estilos.css`

2. **Rediseñar elementos de indicadores**
   - Cards de indicadores con estilo beige y bordes sutiles
   - Gráficos con estilo discreto (colores suaves)
   - Tablas con estilo editorial
   - Archivos: `frontend/css/estilos.css`, posiblemente `frontend/js/subarea.js`

3. **Rediseñar navegación de pilares**
   - Botones con estilo consistente
   - Estados hover y active sutiles
   - Archivos: `frontend/css/estilos.css`

**Criterios de éxito:**
- Todas las páginas tienen estilo consistente
- La experiencia de lectura es serena en todo el sitio

**Tiempo estimado:** 2-3 horas

---

### FASE 7: DETALLES Y REFINAMIENTO
**Objetivo:** Agregar toques finales y pulir la experiencia.

**Tareas:**
1. **Efectos sutiles de papel (opcional)**
   - Agregar textura de papel muy sutil si se desea
   - Archivos: `frontend/css/estilos.css`

2. **Ajustar formato de fechas y metadatos**
   - Cambiar formato a "15 de diciembre de 2025"
   - Usar separadores elegantes (• o —)
   - Archivos: `frontend/js/app.js`, posiblemente otros JS

3. **Refinar badges y etiquetas**
   - Asegurar estilo consistente
   - Colores suaves, bordes sutiles
   - Archivos: `frontend/css/estilos.css`

4. **Ajustar responsive design**
   - Verificar que el diseño funciona bien en mobile
   - Ajustar espaciados para pantallas pequeñas
   - Archivos: `frontend/css/estilos.css` (media queries)

5. **Optimizar tipografías**
   - Verificar carga eficiente de Google Fonts
   - Asegurar fallbacks apropiados
   - Archivos: `frontend/index.html` (head)

6. **Revisión final de accesibilidad**
   - Verificar contraste de colores (aunque suaves, deben ser legibles)
   - Asegurar que focus states sean visibles pero sutiles
   - Archivos: Todos

**Criterios de éxito:**
- El sitio tiene un aspecto pulido y profesional
- Todos los detalles están cuidados
- La experiencia es consistente y serena

**Tiempo estimado:** 3-4 horas

---

### FASE 8: TESTING Y AJUSTES FINALES
**Objetivo:** Asegurar que todo funciona correctamente.

**Tareas:**
1. **Testing funcional**
   - Verificar que todas las funcionalidades siguen trabajando
   - Probar navegación entre páginas
   - Verificar carga de datos (noticias, indicadores)
   - Probar filtros y búsquedas

2. **Testing visual**
   - Revisar en diferentes navegadores (Chrome, Firefox, Safari, Edge)
   - Revisar en diferentes tamaños de pantalla
   - Verificar que no hay elementos rotos o mal alineados

3. **Testing de rendimiento**
   - Verificar tiempos de carga
   - Optimizar si es necesario

4. **Ajustes finales basados en feedback**
   - Hacer ajustes menores según necesidad
   - Pulir detalles que puedan haberse pasado por alto

**Criterios de éxito:**
- Todo funciona correctamente
- No hay errores de consola
- La experiencia es fluida y serena
- El diseño cumple con los objetivos establecidos

**Tiempo estimado:** 2-3 horas

---

## RESUMEN DE FASES

| Fase | Descripción | Tiempo Estimado | Prioridad |
|------|-------------|-----------------|------------|
| 1 | Fundación (colores, tipografías) | 2-3h | Alta |
| 2 | Layout y espaciado | 3-4h | Alta |
| 3 | Noticias (transformación principal) | 4-5h | Crítica |
| 4 | Navegación y filtros | 2-3h | Media |
| 5 | Página de indicadores | 2-3h | Media |
| 6 | Página de subárea | 2-3h | Media |
| 7 | Detalles y refinamiento | 3-4h | Baja |
| 8 | Testing y ajustes finales | 2-3h | Alta |

**Tiempo total estimado:** 20-28 horas

**Orden recomendado:** Secuencial (1 → 2 → 3 → 4 → 5 → 6 → 7 → 8)

**Notas importantes:**
- Cada fase debe completarse antes de pasar a la siguiente para evitar conflictos
- Se puede hacer commit después de cada fase para tener puntos de control
- La Fase 3 es la más crítica y transformadora
- Las fases 5 y 6 pueden hacerse en paralelo si hay tiempo
- La Fase 7 puede hacerse de forma iterativa mientras se trabaja en otras fases