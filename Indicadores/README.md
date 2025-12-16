# 📊 Sistema de Indicadores - Banco Mundial

Sistema para obtener, almacenar y generar indicadores económicos desde la API del Banco Mundial.

## Estructura

- **`db.py`**: Módulo para manejar la base de datos SQLite
- **`ingestar_pib.py`**: Script para consultar la API y guardar datos del PIB Real (crecimiento anual %)
- **`ingestar_pib_per_capita.py`**: Script para consultar la API y guardar datos del PIB per Cápita (PPA)
- **`generar_json.py`**: Script unificado para generar JSONs de todos los indicadores desde la BD para el frontend
- **`indicadores.db`**: Base de datos SQLite (se crea automáticamente)

## Instalación

```bash
pip install requests
```

## Uso

### 1. Inicializar la base de datos

```bash
python db.py
```

### 2. Ingestar datos de indicadores

#### PIB Real (crecimiento anual %)

```bash
python ingestar_pib.py
```

#### PIB per Cápita (PPA)

```bash
python ingestar_pib_per_capita.py
```

Estos scripts:
- Consultan la API del Banco Mundial para 9 países
- Guardan los datos en SQLite
- Rango de años: 2004-2024

### 3. Generar JSONs para el frontend

El script `generar_json.py` es unificado y puede generar JSONs para todos los indicadores o uno específico.

#### Generar todos los indicadores

```bash
python generar_json.py
```

Genera JSONs para todos los indicadores disponibles en la base de datos.

#### Generar un indicador específico

```bash
python generar_json.py --indicador NY.GDP.MKTP.KD.ZG
```

O con el nombre corto:

```bash
python generar_json.py -i NY.GDP.PCAP.PP.KD
```

#### Opciones adicionales

```bash
# Especificar rango de años
python generar_json.py --año-inicio 2010 --año-fin 2020

# Combinar opciones
python generar_json.py -i NY.GDP.MKTP.KD.ZG --año-inicio 2015 --año-fin 2024
```

Los JSONs se guardan en `frontend/data/indicadores/` con nombres descriptivos:
- `pib_real_crecimiento.json` (NY.GDP.MKTP.KD.ZG)
- `pib_per_capita_ppa.json` (NY.GDP.PCAP.PP.KD)

## Países de comparación

- 🇦🇷 Argentina (ARG)
- 🇧🇷 Brasil (BRA)
- 🇨🇱 Chile (CHL)
- 🇺🇾 Uruguay (URY)
- 🇨🇴 Colombia (COL)
- 🇲🇽 México (MEX)
- 🇺🇸 Estados Unidos (USA)
- 🇩🇪 Alemania (DEU)
- 🇪🇸 España (ESP)

## Indicadores disponibles

### 1. Variación del PIB Real (anual %)

- **Código API**: `NY.GDP.MKTP.KD.ZG`
- **Nombre**: Variación del PIB Real (anual %)
- **Descripción**: El estándar de oro. Mide el crecimiento de la producción descontando el efecto de la inflación.
- **Unidad**: %
- **Script ingesta**: `ingestar_pib.py`
- **Archivo JSON**: `pib_real_crecimiento.json`

### 2. PIB per Cápita (PPA)

- **Código API**: `NY.GDP.PCAP.PP.KD`
- **Nombre**: PIB per Cápita (PPA)
- **Descripción**: Utiliza la Paridad de Poder Adquisitivo (PPA) para comparar el nivel de vida real entre países, eliminando las distorsiones de los tipos de cambio.
- **Unidad**: USD constantes 2017
- **Script ingesta**: `ingestar_pib_per_capita.py`
- **Archivo JSON**: `pib_per_capita_ppa.json`

## Estructura de la base de datos

### Tabla `paises`
- `id`: ID único
- `codigo_iso`: Código ISO del país (ej: ARG)
- `nombre`: Nombre del país
- `region`: Región (opcional)
- `grupo_ingreso`: Grupo de ingreso (opcional)

### Tabla `indicadores`
- `id`: ID único
- `codigo_api`: Código del indicador en la API (ej: NY.GDP.MKTP.KD.ZG)
- `nombre`: Nombre del indicador
- `descripcion`: Descripción
- `tema`: Tema/categoría
- `unidad`: Unidad de medida

### Tabla `datos`
- `id`: ID único
- `pais_id`: ID del país
- `indicador_id`: ID del indicador
- `año`: Año del dato
- `valor`: Valor numérico
- `fecha_actualizacion`: Timestamp de última actualización

## Formato del JSON generado

```json
{
  "indicador": {
    "codigo_api": "NY.GDP.MKTP.KD.ZG",
    "nombre": "Variación del PIB Real (anual %)",
    "unidad": "%",
    "ultima_actualizacion": "2025-01-15 16:30:00"
  },
  "paises": [
    {
      "codigo": "ARG",
      "nombre": "Argentina",
      "valores": {
        "2020": -9.9,
        "2021": 10.4,
        "2022": 5.0
      }
    }
  ]
}
```

## Próximos pasos

- [ ] Agregar más indicadores del Plan
- [ ] Automatizar con GitHub Actions
- [ ] Agregar validación de datos
- [ ] Implementar comparaciones en el frontend

