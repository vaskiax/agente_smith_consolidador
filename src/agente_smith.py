# src/agente_smith.py

import pandas as pd
import os
from datetime import datetime
import glob
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- NUEVAS IMPORTACIONES PARA OAUTH 2.0 ---
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- Configuración del Agente ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, '..', 'input')
OUTPUT_FOLDER = os.path.join(BASE_DIR, '..', 'output')
FILE_PATTERN = "*.csv"

# --- CONFIGURACIÓN DE OAUTH 2.0 ---
# Si modificas estos SCOPES, borra el archivo token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
CREDENTIALS_FILE = os.path.join(BASE_DIR, '..', 'credentials.json')
TOKEN_FILE = os.path.join(BASE_DIR, '..', 'token.json')
# --- Lista de destinatarios del email ---
EMAIL_RECIPIENTS = ["agente.reportes.sasori@gmail.com"] # Modifica esto con los correos reales


class AgenteSmithConsolidador:
    """
    Un agente IA diseñado para automatizar la consolidación y notificación
    de reportes de ventas usando OAuth 2.0 para la autenticación.
    """
    def __init__(self, input_path, output_path, file_pattern):
        self.input_path = input_path
        self.output_path = output_path
        self.file_pattern = file_pattern
        self.log = []
        self.reporte_consolidado = None
        self._log_action("Agente Smith v2.0 (OAuth) inicializado.")

    def _log_action(self, message):
        """Registra una acción para seguimiento y depuración."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log.append(f"[{timestamp}] {message}")
        print(f"[{timestamp}] {message}")
        
    def _autenticar_y_obtener_servicio_gmail(self):
        """
        --- NUEVO ROL: Autenticador ---
        Gestiona el flujo de OAuth 2.0 y crea un objeto de servicio de Gmail.
        """
        creds = None
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self._log_action("Refrescando token de acceso...")
                creds.refresh(Request())
            else:
                self._log_action("Se necesita autorización. Abriendo navegador para consentimiento...")
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
            self._log_action("Credenciales guardadas en token.json.")
            
        try:
            service = build('gmail', 'v1', credentials=creds)
            self._log_action("Servicio de Gmail autenticado y listo.")
            return service
        except HttpError as error:
            self._log_action(f"Ocurrió un error al construir el servicio: {error}")
            return None

    # ... (descubrir_y_leer_archivos y consolidar_y_procesar permanecen EXACTAMENTE IGUAL) ...
    def descubrir_y_leer_archivos(self):
        self._log_action(f"Buscando archivos con el patrón '{self.file_pattern}' en '{self.input_path}'...")
        archivos_a_procesar = glob.glob(os.path.join(self.input_path, self.file_pattern))
        if not archivos_a_procesar:
            self._log_action("ADVERTENCIA: No se encontraron archivos para procesar.")
            return []
        self._log_action(f"Se encontraron {len(archivos_a_procesar)} archivos: {', '.join([os.path.basename(f) for f in archivos_a_procesar])}")
        lista_de_dfs = []
        for archivo in archivos_a_procesar:
            try:
                df = pd.read_csv(archivo)
                df['Fuente'] = os.path.basename(archivo)
                lista_de_dfs.append(df)
                self._log_action(f"Archivo '{os.path.basename(archivo)}' leído y cargado exitosamente.")
            except Exception as e:
                self._log_action(f"ERROR: No se pudo leer el archivo '{os.path.basename(archivo)}'. Error: {e}")
        return lista_de_dfs

    def consolidar_y_procesar(self, lista_de_dfs):
        if not lista_de_dfs:
            self._log_action("No hay datos para procesar.")
            return None
        self._log_action("Consolidando todos los datos en un único reporte...")
        reporte_unificado = pd.concat(lista_de_dfs, ignore_index=True)
        self._log_action("Datos consolidados. Total de registros: " + str(len(reporte_unificado)))
        self._log_action("Calculando la columna 'Total_Venta' (Cantidad * Precio_Unitario)...")
        reporte_unificado['Total_Venta'] = reporte_unificado['Cantidad'] * reporte_unificado['Precio_Unitario']
        self._log_action("Agrupando ventas por producto para generar resumen...")
        resumen_por_producto = reporte_unificado.groupby(['ID_Producto', 'Nombre_Producto']).agg(
            Cantidad_Total=('Cantidad', 'sum'),
            Venta_Total=('Total_Venta', 'sum')
        ).reset_index()
        self._log_action("Procesamiento y análisis completados.")
        self.reporte_consolidado = {"completo": reporte_unificado, "resumen": resumen_por_producto}
    
    # --- generar_reporte_final también permanece igual ---
    def generar_reporte_final(self):
        if self.reporte_consolidado is None:
            self._log_action("No hay reporte procesado para guardar.")
            return None
        semana_actual = datetime.now().strftime('%Y_S%U')
        nombre_archivo_salida = f"reporte_consolidado_{semana_actual}.xlsx"
        ruta_salida = os.path.join(self.output_path, nombre_archivo_salida)
        self._log_action(f"Generando archivo de Excel en: {ruta_salida}")
        with pd.ExcelWriter(ruta_salida, engine='openpyxl') as writer:
            self.reporte_consolidado['completo'].to_excel(writer, sheet_name='Datos_Completos', index=False)
            self.reporte_consolidado['resumen'].to_excel(writer, sheet_name='Resumen_por_Producto', index=False)
        self._log_action("¡Misión cumplida! Reporte generado exitosamente.")
        return ruta_salida
        
    def _crear_mensaje_con_adjunto(self, destinatarios, asunto, cuerpo, ruta_archivo):
        """Crea el objeto del mensaje de email."""
        msg = MIMEMultipart()
        msg['To'] = ", ".join(destinatarios)
        msg['Subject'] = asunto
        msg.attach(MIMEText(cuerpo, 'plain'))

        try:
            with open(ruta_archivo, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename= {os.path.basename(ruta_archivo)}")
            msg.attach(part)
            return {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}
        except Exception as e:
            self._log_action(f"ERROR al crear el adjunto: {e}")
            return None

    def enviar_reporte_por_email(self, service, ruta_archivo_adjunto):
        """
        --- ROL MODIFICADO: Notificador (vía OAuth) ---
        Envía el email usando el servicio de Gmail autenticado.
        """
        self._log_action(f"Preparando envío de email OAuth a: {', '.join(EMAIL_RECIPIENTS)}")
        asunto = f"Reporte de Ventas Consolidado - Semana {datetime.now().strftime('%U')}"
        cuerpo = "Hola equipo,\n\nAdjunto encontrarán el reporte de ventas consolidado.\n\nSaludos,\nAgente Smith"
        
        mensaje_creado = self._crear_mensaje_con_adjunto(EMAIL_RECIPIENTS, asunto, cuerpo, ruta_archivo_adjunto)

        if mensaje_creado:
            try:
                (service.users().messages().send(userId="me", body=mensaje_creado).execute())
                self._log_action("Email enviado exitosamente vía OAuth.")
            except HttpError as error:
                self._log_action(f"Ocurrió un error al enviar el email: {error}")

    def ejecutar_mision(self):
        """
        --- ROL MODIFICADO: Orquestador (MCP) ---
        Ejecuta la secuencia incluyendo la autenticación OAuth.
        """
        self._log_action("--- INICIO DE MISIÓN v2.0: CONSOLIDACIÓN Y NOTIFICACIÓN OAuth ---")
        
        # Paso 1: Autenticar
        servicio_gmail = self._autenticar_y_obtener_servicio_gmail()
        if not servicio_gmail:
            self._log_action("Fallo en la autenticación. Abortando misión.")
            return

        # Pasos 2, 3 y 4: Descubrir, Procesar, Generar
        datos_brutos = self.descubrir_y_leer_archivos()
        if datos_brutos:
            self.consolidar_y_procesar(datos_brutos)
            ruta_reporte_generado = self.generar_reporte_final()
            
            # Paso 5: Notificar
            if ruta_reporte_generado:
                self.enviar_reporte_por_email(servicio_gmail, ruta_reporte_generado)

        self._log_action("--- FIN DE MISIÓN ---")

if __name__ == '__main__':
    agente = AgenteSmithConsolidador(INPUT_FOLDER, OUTPUT_FOLDER, FILE_PATTERN)
    agente.ejecutar_mision()