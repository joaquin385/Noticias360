"""
Script de prueba para verificar que la API key de Gemini esté configurada correctamente.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

def cargar_api_key_desde_envfile() -> str:
    """Intenta leer GEMINI_API_KEY desde un archivo .env en la raíz."""
    env_file = BASE_DIR / ".env"
    if not env_file.exists():
        return ""
    try:
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("GEMINI_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except Exception:
        return ""
    return ""

def verificar_api_key():
    """Verifica que la API key esté configurada (env var o .env)."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        api_key = cargar_api_key_desde_envfile()

    if api_key:
        api_key = api_key.strip().strip('"').strip("'")
        print(f"✓ GEMINI_API_KEY encontrada")
        print(f"  Longitud: {len(api_key)} caracteres")
        print(f"  Vista parcial: {api_key[:10]}...{api_key[-5:]}")
    else:
        print("✗ GEMINI_API_KEY no encontrada ni en variables de entorno ni en .env")
        print("\nConfigúrala con:")
        print("  PowerShell: $env:GEMINI_API_KEY='tu-api-key'")
        print("  CMD:        set GEMINI_API_KEY=tu-api-key")
        print("  .env (raíz): GEMINI_API_KEY=tu-api-key")
        return False
    
    # Intentar importar e inicializar Gemini
    try:
        # Nuevo SDK oficial
        from google import genai
        client = genai.Client(api_key=api_key)
        # Prueba simple
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=["Responde solo con OK"]
        )
        print(f"\n✓ Conexión con Gemini AI exitosa")
        print(f"  Respuesta de prueba: {getattr(response, 'text', '')[:50]}")
        return True
        
    except ImportError:
        print("\n✗ google-genai no está instalado")
        print("  Instálalo con: pip install google-genai")
        return False
    except Exception as e:
        print(f"\n✗ Error al conectar con Gemini: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("PRUEBA DE CONFIGURACIÓN GEMINI API")
    print("=" * 60)
    verificar_api_key()
    print("=" * 60)

