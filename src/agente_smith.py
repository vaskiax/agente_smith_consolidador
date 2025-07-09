# src/agente_smith.py

import pandas as pd
import os
from datetime import datetime
import glob

# --- Configuración del Agente ---
# Rutas relativas para que el script sea portable
INPUT_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'input')
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'output')
FILE_PATTERN = "*.csv" # Patrón para encontrar los archivos, puede ser *.xlsx

class AgenteSmithConsolidador:
    """
    Un agente IA diseñado para automatizar la consolidación y procesamiento
    de reportes de ventas.
    """
    def __init__(self, input_path, output_path, file_pattern):
        self.input_path = input_path
        self.output_path = output_path
        self.file_pattern = file_pattern
        self.log = []
        self.reporte_consolidado = None
        self._log_action("Agente Smith inicializado.")

    def _log_action(self, message):
        """Registra una acción para seguimiento y depuración."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log.append(f"[{timestamp}] {message}")
        print(f"[{timestamp}] {message}")

    def descubrir_y_leer_archivos(self):
        """
        ROL: Descubridor.
        Busca todos los archivos que coincidan con el patrón en la carpeta de entrada
        y los carga en una lista de DataFrames de Pandas.
        """
        self._log_action(f"Buscando archivos con el patrón '{self.file_pattern}' en '{self.input_path}'...")
        
        # glob.glob construye la ruta completa
        archivos_a_procesar = glob.glob(os.path.join(self.input_path, self.file_pattern))

        if not archivos_a_procesar:
            self._log_action("ADVERTENCIA: No se encontraron archivos para procesar. Abortando misión.")
            return []

        self._log_action(f"Se encontraron {len(archivos_a_procesar)} archivos: {', '.join([os.path.basename(f) for f in archivos_a_procesar])}")

        lista_de_dfs = []
        for archivo in archivos_a_procesar:
            try:
                # Añadimos una columna para saber el origen del dato
                df = pd.read_csv(archivo) # Usar pd.read_excel(archivo) para .xlsx
                df['Fuente'] = os.path.basename(archivo)
                lista_de_dfs.append(df)
                self._log_action(f"Archivo '{os.path.basename(archivo)}' leído y cargado exitosamente.")
            except Exception as e:
                self._log_action(f"ERROR: No se pudo leer el archivo '{os.path.basename(archivo)}'. Error: {e}")
        
        return lista_de_dfs

    def consolidar_y_procesar(self, lista_de_dfs):
        """
        ROL: Procesador.
        Toma la lista de DataFrames, los une, calcula nuevas columnas y
        realiza los análisis necesarios.
        """
        if not lista_de_dfs:
            self._log_action("No hay datos para procesar.")
            return None

        self._log_action("Consolidando todos los datos en un único reporte...")
        reporte_unificado = pd.concat(lista_de_dfs, ignore_index=True)
        self._log_action("Datos consolidados. Total de registros: " + str(len(reporte_unificado)))

        # Procesamiento: Calcular la columna de venta total
        self._log_action("Calculando la columna 'Total_Venta' (Cantidad * Precio_Unitario)...")
        reporte_unificado['Total_Venta'] = reporte_unificado['Cantidad'] * reporte_unificado['Precio_Unitario']
        
        # Agregación: Agrupar por producto
        self._log_action("Agrupando ventas por producto para generar resumen...")
        resumen_por_producto = reporte_unificado.groupby(['ID_Producto', 'Nombre_Producto']).agg(
            Cantidad_Total=('Cantidad', 'sum'),
            Venta_Total=('Total_Venta', 'sum')
        ).reset_index()
        
        self._log_action("Procesamiento y análisis completados.")
        self.reporte_consolidado = {"completo": reporte_unificado, "resumen": resumen_por_producto}

    def generar_reporte_final(self):
        """
        ROL: Generador/Publicador.
        Guarda los DataFrames procesados en un nuevo archivo Excel con múltiples hojas.
        """
        if self.reporte_consolidado is None:
            self._log_action("No hay reporte procesado para guardar.")
            return

        # Crear un nombre de archivo dinámico
        semana_actual = datetime.now().strftime('%Y_S%U')
        nombre_archivo_salida = f"reporte_consolidado_{semana_actual}.xlsx"
        ruta_salida = os.path.join(self.output_path, nombre_archivo_salida)

        self._log_action(f"Generando archivo de Excel en: {ruta_salida}")
        
        # Usar ExcelWriter para guardar en múltiples hojas
        with pd.ExcelWriter(ruta_salida, engine='openpyxl') as writer:
            self.reporte_consolidado['completo'].to_excel(writer, sheet_name='Datos_Completos', index=False)
            self.reporte_consolidado['resumen'].to_excel(writer, sheet_name='Resumen_por_Producto', index=False)
        
        self._log_action(f"¡Misión cumplida! Reporte generado exitosamente.")
        
    def ejecutar_mision(self):
        """
        ROL: Orquestador (MCP).
        Ejecuta la secuencia completa de la misión del agente.
        """
        self._log_action("--- INICIO DE MISIÓN: CONSOLIDACIÓN DE REPORTES ---")
        
        # Paso 1: Descubrir y leer
        datos_brutos = self.descubrir_y_leer_archivos()
        
        # Paso 2: Procesar
        if datos_brutos:
            self.consolidar_y_procesar(datos_brutos)
            
            # Paso 3: Generar
            self.generar_reporte_final()

        self._log_action("--- FIN DE MISIÓN ---")


if __name__ == '__main__':
    # --- Punto de Entrada del Script ---
    # Así es como un cliente (o un programador de tareas) ejecutaría al agente.
    agente = AgenteSmithConsolidador(INPUT_FOLDER, OUTPUT_FOLDER, FILE_PATTERN)
    agente.ejecutar_mision()