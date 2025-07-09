# Agente Smith: Consolidador de Reportes Automático con Python

Este proyecto demuestra cómo automatizar una tarea de oficina común y tediosa: consolidar múltiples reportes de ventas en un único archivo de resumen.

![GIF de Demostración](link_a_tu_gif_aqui.gif) <!-- pendiente -->

## El Problema: Horas Perdidas en Trabajo Manual

En muchas empresas, un gerente o analista invierte horas cada semana o mes en las siguientes tareas:
- Abrir múltiples archivos de Excel (ej: por región, por vendedor).
- Copiar y pegar los datos en una sola hoja.
- Realizar cálculos manuales (ej: `total = cantidad * precio`).
- Crear tablas dinámicas para resumir la información.
- Este proceso no solo consume tiempo valioso, sino que también es propenso a errores humanos.

**Antes: ~2 horas de trabajo manual. Después: ~1 segundo de ejecución de un script.**

## La Solución: Un Agente de Automatización

Este script de Python actúa como un "agente" que realiza todo el proceso de forma automática.

### Características
- **Descubrimiento Automático:** Encuentra todos los archivos `.csv` (o `.xlsx`) en una carpeta de entrada.
- **Consolidación Inteligente:** Une todos los datos y añade una columna `Fuente` para mantener la trazabilidad.
- **Procesamiento de Datos:** Calcula nuevas columnas (ej: `Total_Venta`).
- **Análisis y Resumen:** Genera un resumen agregado (ej: ventas totales por producto).
- **Reporte Final Profesional:** Guarda los resultados en un archivo Excel limpio y organizado con múltiples hojas:
    1.  `Datos_Completos`: Todos los datos unificados.
    2.  `Resumen_por_Producto`: Una vista agregada lista para el análisis.

## Tecnologías Utilizadas
- **Python:** Lenguaje de programación principal.
- **Pandas:** Para la manipulación y análisis de datos de alto rendimiento.
- **Openpyxl:** Para la escritura de archivos `.xlsx` complejos.

## Cómo Usarlo
1.  Clona este repositorio: `git clone https://github.com/tu-usuario/python-report-automation.git`
2.  Navega al directorio del proyecto: `cd python-report-automation`
3.  Instala las dependencias: `pip install -r requirements.txt` (primero crea un `requirements.txt` con `pip freeze > requirements.txt`).
4.  Coloca tus archivos de reporte (`.csv` o `.xlsx`) en la carpeta `input/`.
5.  Ejecuta el agente: `python src/agente_smith.py`
6.  ¡Encuentra tu reporte consolidado en la carpeta `output/`!