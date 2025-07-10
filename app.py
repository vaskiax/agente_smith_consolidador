# app.py

import streamlit as st
import os
import sys
from datetime import datetime

# Añadir la carpeta 'src' al path para poder importar AgenteSmith
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from agente_smith import AgenteSmithConsolidador

# --- Configuración de la App de Streamlit ---
st.set_page_config(page_title="Agente Smith v2.0", page_icon="🤖", layout="centered")

st.title("🤖 Agente Smith v2.0 (con OAuth)")
st.markdown("Tu asistente personal para automatizar la consolidación y envío de reportes.")

# --- Rutas y Archivos Clave ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, 'input')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'output')
TOKEN_FILE = os.path.join(BASE_DIR, 'token.json')
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.json')

# Asegurarse de que las carpetas existan
os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# --- VERIFICACIÓN DE CONFIGURACIÓN INICIAL ---
# Esta es la puerta de entrada. Si no hay autenticación, no se puede usar la app.
if not os.path.exists(CREDENTIALS_FILE):
    st.error(
        "Error de Configuración: Falta el archivo `credentials.json`."
        "Por favor, descárgalo desde tu proyecto de Google Cloud y colócalo en la raíz del proyecto."
    )
elif not os.path.exists(TOKEN_FILE):
    st.warning(
        "¡Acción Requerida! El agente aún no ha sido autorizado."
    )
    st.info(
        "Por favor, ejecuta el siguiente comando en tu terminal (una sola vez) "
        "para autorizar al Agente Smith a enviar correos en tu nombre:\n\n"
        "```\n"
        "python autenticar.py\n"
        "```\n\n"
        "Después de autorizarlo, refresca esta página."
    )
else:
    # --- Interfaz Principal de la App (Solo se muestra si la configuración es correcta) ---
    st.sidebar.header("Configuración de la Misión")
    st.sidebar.success("✅ Agente autorizado y listo para la misión.")

    uploaded_files = st.sidebar.file_uploader(
        "1. Sube tus archivos de reporte (CSV o Excel)",
        accept_multiple_files=True,
        type=['csv', 'xlsx']
    )

    if uploaded_files:
        # Limpiar la carpeta de input antes de guardar los nuevos archivos
        for file_name in os.listdir(INPUT_FOLDER):
            os.remove(os.path.join(INPUT_FOLDER, file_name))
            
        for uploaded_file in uploaded_files:
            with open(os.path.join(INPUT_FOLDER, uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.sidebar.success(f"Se cargaron {len(uploaded_files)} archivos en la carpeta 'input'.")

    if st.button("🚀 Ejecutar Misión de Consolidación y Envío"):
        if not os.listdir(INPUT_FOLDER):
            st.error("La carpeta 'input' está vacía. Por favor, sube archivos antes de ejecutar la misión.")
        else:
            with st.spinner("El Agente Smith está en una misión... Esto puede tardar un momento."):
                primer_archivo = os.listdir(INPUT_FOLDER)[0]
                extension = primer_archivo.split('.')[-1]
                file_pattern = f"*.{extension}"

                agente = AgenteSmithConsolidador(INPUT_FOLDER, OUTPUT_FOLDER, file_pattern)
                
                # Redirigir logs para mostrarlos en la UI
                from io import StringIO
                old_stdout = sys.stdout
                sys.stdout = captured_output = StringIO()
                
                # La nueva ejecución es mucho más simple. ¡La clase se encarga de todo!
                agente.ejecutar_mision()
                
                sys.stdout = old_stdout # Restaurar
                log_text = captured_output.getvalue()

                st.success("¡Misión completada con éxito!")
                
                with st.expander("Ver registro de la misión (Logs)"):
                    st.code(log_text, language='text')

                semana_actual = datetime.now().strftime('%Y_S%U')
                nombre_archivo_salida = f"reporte_consolidado_{semana_actual}.xlsx"
                ruta_salida = os.path.join(OUTPUT_FOLDER, nombre_archivo_salida)

                if os.path.exists(ruta_salida):
                    with open(ruta_salida, "rb") as file:
                        st.download_button(
                            label="📥 Descargar Reporte Consolidado",
                            data=file,
                            file_name=nombre_archivo_salida,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                else:
                    st.error("Algo salió mal, no se pudo generar el archivo de reporte para descargar.")

st.sidebar.info(
    "**Flujo de Trabajo:**\n"
    "1. Sube tus archivos.\n"
    "2. Haz clic en 'Ejecutar Misión'.\n"
    "3. El Agente generará el reporte, lo enviará por email (usando la autorización guardada) y te ofrecerá una copia para descargar."
)