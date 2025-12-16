"""
Módulo para manejar la base de datos SQLite de indicadores.
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), 'indicadores.db')


def get_connection():
    """Obtiene una conexión a la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acceso por nombre de columna
    return conn


def init_database():
    """Inicializa la base de datos con las tablas necesarias."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabla de países
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS paises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_iso TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            region TEXT,
            grupo_ingreso TEXT,
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de indicadores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS indicadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_api TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            tema TEXT,
            unidad TEXT,
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de datos (valores de indicadores por país y año)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS datos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pais_id INTEGER NOT NULL,
            indicador_id INTEGER NOT NULL,
            año INTEGER NOT NULL,
            valor REAL,
            fecha_actualizacion TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pais_id) REFERENCES paises(id),
            FOREIGN KEY (indicador_id) REFERENCES indicadores(id),
            UNIQUE(pais_id, indicador_id, año)
        )
    ''')
    
    # Índices para mejorar performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_datos_pais ON datos(pais_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_datos_indicador ON datos(indicador_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_datos_año ON datos(año)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_datos_pais_indicador_año ON datos(pais_id, indicador_id, año)')
    
    conn.commit()
    conn.close()
    print("✅ Base de datos inicializada correctamente.")


def obtener_o_crear_pais(codigo_iso: str, nombre: str, region: Optional[str] = None, grupo_ingreso: Optional[str] = None) -> int:
    """Obtiene el ID de un país, o lo crea si no existe."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Buscar si existe
    cursor.execute('SELECT id FROM paises WHERE codigo_iso = ?', (codigo_iso,))
    row = cursor.fetchone()
    
    if row:
        pais_id = row['id']
    else:
        # Crear nuevo país
        cursor.execute('''
            INSERT INTO paises (codigo_iso, nombre, region, grupo_ingreso)
            VALUES (?, ?, ?, ?)
        ''', (codigo_iso, nombre, region, grupo_ingreso))
        pais_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    return pais_id


def obtener_o_crear_indicador(codigo_api: str, nombre: str, descripcion: Optional[str] = None, tema: Optional[str] = None, unidad: Optional[str] = None) -> int:
    """Obtiene el ID de un indicador, o lo crea si no existe."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Buscar si existe
    cursor.execute('SELECT id FROM indicadores WHERE codigo_api = ?', (codigo_api,))
    row = cursor.fetchone()
    
    if row:
        indicador_id = row['id']
    else:
        # Crear nuevo indicador
        cursor.execute('''
            INSERT INTO indicadores (codigo_api, nombre, descripcion, tema, unidad)
            VALUES (?, ?, ?, ?, ?)
        ''', (codigo_api, nombre, descripcion, tema, unidad))
        indicador_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    return indicador_id


def guardar_dato(pais_id: int, indicador_id: int, año: int, valor: Optional[float]):
    """Guarda o actualiza un dato de indicador."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO datos (pais_id, indicador_id, año, valor, fecha_actualizacion)
        VALUES (?, ?, ?, ?, ?)
    ''', (pais_id, indicador_id, año, valor, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()


def obtener_indicadores_disponibles() -> List[Dict[str, Any]]:
    """Obtiene todos los indicadores disponibles en la base de datos."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT
            i.codigo_api,
            i.nombre,
            i.unidad
        FROM indicadores i
        INNER JOIN datos d ON i.id = d.indicador_id
        ORDER BY i.nombre
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def obtener_datos_indicador(codigo_indicador: str, codigos_paises: List[str], año_inicio: Optional[int] = None, año_fin: Optional[int] = None) -> List[Dict[str, Any]]:
    """Obtiene datos de un indicador para varios países."""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT 
            p.codigo_iso,
            p.nombre as pais_nombre,
            i.codigo_api,
            i.nombre as indicador_nombre,
            i.unidad,
            d.año,
            d.valor
        FROM datos d
        JOIN paises p ON d.pais_id = p.id
        JOIN indicadores i ON d.indicador_id = i.id
        WHERE i.codigo_api = ?
        AND p.codigo_iso IN ({})
    '''.format(','.join(['?'] * len(codigos_paises)))
    
    params = [codigo_indicador] + codigos_paises
    
    if año_inicio:
        query += ' AND d.año >= ?'
        params.append(año_inicio)
    
    if año_fin:
        query += ' AND d.año <= ?'
        params.append(año_fin)
    
    query += ' ORDER BY p.codigo_iso, d.año'
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    conn.close()
    
    # Convertir a lista de diccionarios
    return [dict(row) for row in rows]


if __name__ == '__main__':
    # Inicializar BD si se ejecuta directamente
    init_database()

