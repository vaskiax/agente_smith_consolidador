# autenticar.py

import os
import sys

# Añadir la carpeta 'src' al path para poder importar AgenteSmith
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
# Importamos la clase, pero no necesitamos todo el archivo
from agente_smith import AgenteSmithConsolidador

def realizar_autenticacion_inicial():
    """
    Este script tiene un único propósito: ejecutar el flujo de autenticación
    OAuth 2.0 para generar el archivo 'token.json'.
    """
    print("--- INICIANDO PROCESO DE AUTENTICACIÓN INICIAL ---")
    print("Este proceso se debe realizar solo una vez por máquina/usuario.")
    
    # Creamos una instancia del agente solo para usar su método de autenticación
    # Los argumentos de input/output no importan aquí
    agente_dummy = AgenteSmithConsolidador(None, None, None)
    
    servicio_gmail = agente_dummy._autenticar_y_obtener_servicio_gmail()
    
    if servicio_gmail:
        print("\n¡Éxito! La autenticación se completó y el archivo 'token.json' ha sido creado.")
        print("Ahora puedes ejecutar la aplicación de Streamlit con 'streamlit run app.py'.")
    else:
        print("\nOcurrió un error durante la autenticación. Por favor, revisa los logs.")
    print("--- FIN DEL PROCESO DE AUTENTICACIÓN ---")


if __name__ == '__main__':
    # Antes de empezar, verificamos si las credenciales existen
    if not os.path.exists('credentials.json'):
         print("ERROR: No se encuentra el archivo 'credentials.json'.")
         print("Por favor, descárgalo desde la Consola de Google Cloud y colócalo en la raíz del proyecto.")
    else:
        realizar_autenticacion_inicial()