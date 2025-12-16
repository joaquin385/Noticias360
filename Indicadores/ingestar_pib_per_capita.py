"""
Script para consultar la API del Banco Mundial y guardar datos del PIB per Cápita (PPA).
"""

import requests
from db import (
    init_database,
    obtener_o_crear_pais,
    obtener_o_crear_indicador,
    guardar_dato
)

# Configuración
INDICADOR_CODIGO = 'NY.GDP.PCAP.PP.KD'  # GDP per capita, PPP (constant 2017 international $)
INDICADOR_NOMBRE = 'PIB per Cápita (PPA)'
INDICADOR_DESCRIPCION = 'Utiliza la Paridad de Poder Adquisitivo (PPA) para comparar el nivel de vida real entre países, eliminando las distorsiones de los tipos de cambio.'
INDICADOR_UNIDAD = 'USD constantes 2017'

# Países de comparación
PAISES_COMPARACION = [
    {'codigo': 'ARG', 'nombre': 'Argentina'},
    {'codigo': 'BRA', 'nombre': 'Brasil'},
    {'codigo': 'CHL', 'nombre': 'Chile'},
    {'codigo': 'URY', 'nombre': 'Uruguay'},
    {'codigo': 'COL', 'nombre': 'Colombia'},
    {'codigo': 'MEX', 'nombre': 'México'},
    {'codigo': 'USA', 'nombre': 'Estados Unidos'},
    {'codigo': 'DEU', 'nombre': 'Alemania'},
    {'codigo': 'ESP', 'nombre': 'España'},
]

# Rango de años (últimos 20 años)
AÑO_INICIO = 2004
AÑO_FIN = 2024


def consultar_api_banco_mundial(codigo_pais: str, codigo_indicador: str, año_inicio: int, año_fin: int):
    """
    Consulta la API del Banco Mundial para un país e indicador específico.
    
    Returns:
        list: Lista de diccionarios con los datos obtenidos
    """
    url = f'https://api.worldbank.org/v2/es/country/{codigo_pais}/indicator/{codigo_indicador}'
    params = {
        'format': 'json',
        'date': f'{año_inicio}:{año_fin}',
        'per_page': 1000
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if len(data) < 2 or not data[1]:
            print(f"⚠️  No se encontraron datos para {codigo_pais}")
            return []
        
        return data[1]  # El segundo elemento contiene los datos
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al consultar API para {codigo_pais}: {e}")
        return []


def procesar_y_guardar_datos():
    """Procesa y guarda los datos del PIB per Cápita (PPA) en la base de datos."""
    print("🚀 Iniciando ingesta de datos del PIB per Cápita (PPA)...")
    print(f"📊 Indicador: {INDICADOR_NOMBRE} ({INDICADOR_CODIGO})")
    print(f"🌍 Países: {len(PAISES_COMPARACION)}")
    print(f"📅 Rango: {AÑO_INICIO} - {AÑO_FIN}\n")
    
    # Inicializar BD
    init_database()
    
    # Obtener o crear el indicador
    indicador_id = obtener_o_crear_indicador(
        codigo_api=INDICADOR_CODIGO,
        nombre=INDICADOR_NOMBRE,
        descripcion=INDICADOR_DESCRIPCION,
        tema='Desarrollo económico y empleo',
        unidad=INDICADOR_UNIDAD
    )
    print(f"✅ Indicador registrado (ID: {indicador_id})")
    
    total_datos = 0
    total_paises_exitosos = 0
    
    # Procesar cada país
    for pais_info in PAISES_COMPARACION:
        codigo = pais_info['codigo']
        nombre = pais_info['nombre']
        
        print(f"\n📥 Consultando datos para {nombre} ({codigo})...")
        
        # Consultar API
        datos_api = consultar_api_banco_mundial(
            codigo_pais=codigo,
            codigo_indicador=INDICADOR_CODIGO,
            año_inicio=AÑO_INICIO,
            año_fin=AÑO_FIN
        )
        
        if not datos_api:
            print(f"   ⚠️  Sin datos para {nombre}")
            continue
        
        # Obtener o crear el país
        pais_id = obtener_o_crear_pais(
            codigo_iso=codigo,
            nombre=nombre
        )
        
        # Guardar cada dato
        datos_guardados = 0
        for entrada in datos_api:
            año = int(entrada.get('date', 0))
            valor = entrada.get('value')
            
            # Solo guardar si hay valor válido
            if valor is not None:
                guardar_dato(pais_id, indicador_id, año, float(valor))
                datos_guardados += 1
        
        total_datos += datos_guardados
        total_paises_exitosos += 1
        print(f"   ✅ {datos_guardados} datos guardados para {nombre}")
    
    print(f"\n🎉 Proceso completado!")
    print(f"   📊 Países procesados: {total_paises_exitosos}/{len(PAISES_COMPARACION)}")
    print(f"   📈 Total de datos guardados: {total_datos}")


if __name__ == '__main__':
    procesar_y_guardar_datos()

