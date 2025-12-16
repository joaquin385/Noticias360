"""
Script unificado para generar JSONs de todos los indicadores desde la base de datos para el frontend.
Puede generar JSONs para un indicador específico o para todos los indicadores disponibles.
"""

import json
import os
import sys
import argparse
from datetime import datetime
from db import obtener_datos_indicador, obtener_indicadores_disponibles

# Configuración
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'data', 'indicadores')

# Países de comparación
PAISES_COMPARACION = ['ARG', 'BRA', 'CHL', 'URY', 'COL', 'MEX', 'USA', 'DEU', 'ESP']

# Rango de años por defecto
AÑO_INICIO = 2004
AÑO_FIN = 2024

# Mapeo de códigos de indicadores a nombres de archivo más legibles
MAPEO_NOMBRES_ARCHIVO = {
    'NY.GDP.MKTP.KD.ZG': 'pib_real_crecimiento.json',
    'NY.GDP.PCAP.PP.KD': 'pib_per_capita_ppa.json',
    # Agregar más mapeos aquí cuando se agreguen nuevos indicadores
}


def generar_nombre_archivo(codigo_indicador: str) -> str:
    """
    Genera un nombre de archivo para el JSON basado en el código del indicador.
    Si existe un mapeo, lo usa; si no, genera uno basado en el código.
    """
    if codigo_indicador in MAPEO_NOMBRES_ARCHIVO:
        return MAPEO_NOMBRES_ARCHIVO[codigo_indicador]
    
    # Generar nombre basado en el código (reemplazar puntos por guiones bajos)
    nombre_base = codigo_indicador.lower().replace('.', '_')
    return f'{nombre_base}.json'


def generar_json_para_indicador(codigo_indicador: str, año_inicio: int = AÑO_INICIO, año_fin: int = AÑO_FIN) -> bool:
    """
    Genera el JSON para un indicador específico.
    
    Returns:
        bool: True si se generó exitosamente, False en caso contrario
    """
    print(f"\n📊 Procesando indicador: {codigo_indicador}")
    
    # Obtener datos de la BD
    datos = obtener_datos_indicador(
        codigo_indicador=codigo_indicador,
        codigos_paises=PAISES_COMPARACION,
        año_inicio=año_inicio,
        año_fin=año_fin
    )
    
    if not datos:
        print(f"   ⚠️  No se encontraron datos para {codigo_indicador}")
        return False
    
    # Organizar datos por país
    datos_por_pais = {}
    indicador_info = None
    
    for dato in datos:
        codigo_pais = dato['codigo_iso']
        nombre_pais = dato['pais_nombre']
        año = dato['año']
        valor = dato['valor']
        
        # Guardar info del indicador (solo una vez)
        if not indicador_info:
            indicador_info = {
                'codigo_api': dato['codigo_api'],
                'nombre': dato['indicador_nombre'],
                'unidad': dato['unidad']
            }
        
        # Inicializar país si no existe
        if codigo_pais not in datos_por_pais:
            datos_por_pais[codigo_pais] = {
                'codigo': codigo_pais,
                'nombre': nombre_pais,
                'valores': {}
            }
        
        # Agregar valor (solo si no es None)
        if valor is not None:
            # Redondear a 2 decimales
            datos_por_pais[codigo_pais]['valores'][str(año)] = round(valor, 2)
    
    # Construir estructura final
    resultado = {
        'indicador': {
            'codigo_api': indicador_info['codigo_api'],
            'nombre': indicador_info['nombre'],
            'unidad': indicador_info['unidad'],
            'ultima_actualizacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'paises': list(datos_por_pais.values())
    }
    
    # Crear directorio si no existe
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Generar nombre de archivo
    nombre_archivo = generar_nombre_archivo(codigo_indicador)
    output_file = os.path.join(OUTPUT_DIR, nombre_archivo)
    
    # Guardar JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    
    # Mostrar resumen
    total_valores = sum(len(p['valores']) for p in resultado['paises'])
    print(f"   ✅ JSON generado: {output_file}")
    print(f"   📊 Países: {len(resultado['paises'])} | Valores: {total_valores}")
    
    return True


def generar_todos_los_json(año_inicio: int = AÑO_INICIO, año_fin: int = AÑO_FIN):
    """Genera JSONs para todos los indicadores disponibles en la base de datos."""
    print("🚀 Generando JSONs para todos los indicadores...")
    print(f"📅 Rango: {año_inicio} - {año_fin}")
    print(f"🌍 Países: {len(PAISES_COMPARACION)}\n")
    
    # Obtener todos los indicadores disponibles
    indicadores = obtener_indicadores_disponibles()
    
    if not indicadores:
        print("❌ No se encontraron indicadores en la base de datos.")
        print("   Ejecuta primero los scripts de ingesta (ingestar_pib.py, etc.)")
        return
    
    print(f"📋 Indicadores encontrados: {len(indicadores)}\n")
    
    exitosos = 0
    fallidos = 0
    
    # Procesar cada indicador
    for indicador in indicadores:
        codigo = indicador['codigo_api']
        nombre = indicador['nombre']
        print(f"📈 {nombre} ({codigo})")
        
        if generar_json_para_indicador(codigo, año_inicio, año_fin):
            exitosos += 1
        else:
            fallidos += 1
    
    # Resumen final
    print(f"\n🎉 Proceso completado!")
    print(f"   ✅ Exitosos: {exitosos}")
    if fallidos > 0:
        print(f"   ⚠️  Fallidos: {fallidos}")


def main():
    """Función principal con soporte para argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description='Genera JSONs de indicadores desde la base de datos para el frontend.'
    )
    parser.add_argument(
        '--indicador',
        '-i',
        type=str,
        help='Código del indicador específico a generar (ej: NY.GDP.MKTP.KD.ZG). Si no se especifica, genera todos.'
    )
    parser.add_argument(
        '--año-inicio',
        type=int,
        default=AÑO_INICIO,
        help=f'Año de inicio (default: {AÑO_INICIO})'
    )
    parser.add_argument(
        '--año-fin',
        type=int,
        default=AÑO_FIN,
        help=f'Año de fin (default: {AÑO_FIN})'
    )
    
    args = parser.parse_args()
    
    if args.indicador:
        # Generar solo un indicador
        print(f"🚀 Generando JSON para indicador: {args.indicador}")
        generar_json_para_indicador(args.indicador, args.año_inicio, args.año_fin)
    else:
        # Generar todos los indicadores
        generar_todos_los_json(args.año_inicio, args.año_fin)


if __name__ == '__main__':
    main()
