# script_extraccion_google_sheet.py
import re
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURACIÓN ---
# ¡IMPORTANTE! Reemplaza esta URL con la URL de TU GOOGLE SHEET PUBLICADO EN LA WEB EN FORMATO CSV.
# Esta es la URL para los turnos, la mantendremos.
URL_GOOGLE_SHEET_TURNOS = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRxvq7h8kghE7h1Hr8T0P6rFykWzyZq8WNc1YSqlbo6JubxFDHZ_9VNYZgTSAQcifOyGCVmKE876pcC/pub?gid=2085227179&single=true&output=csv'

# --- NUEVA URL PARA LOS PAGOS/DEUDORES ---
# ¡IMPORTANTE! REEMPLAZA ESTA URL con la URL de TU GOOGLE SHEET PUBLICADO EN LA WEB EN FORMATO CSV
# que contenga la información de los pagos y vencimientos.
# Asegúrate de que tenga columnas como 'Nombre Cliente', 'Monto Adeudado', 'Fecha Vencimiento', 'Telefono', 'Estado'.
URL_GOOGLE_SHEET_PAGOS = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRxvq7h8kghE7h1Hr8T0P6rFykWzyZq8WNc1YSqlbo6JubxFDHZ_9VNYZgTSAQcifOyGCVmKE876pcC/pub?gid=0&single=true&output=csv' # <--- ¡ESTA ES LA URL QUE HAS PROPORCIONADO!

# Ruta completa donde se guardará el archivo .txt.
RUTA_ARCHIVO_PROMPT_TXT = r'C:\Users\User\Desktop\chatia\cobrador\info.txt'


# --- FUNCIONES EXISTENTES (PARA TURNOS) ---

def extraer_datos_desde_url(url):
    """
    Extrae datos de un archivo CSV desde una URL.
    (Función existente para los turnos, sin cambios significativos aquí)
    """
    try:
        if 'output=csv' in url or 'format=csv' in url:
            print(f"[{datetime.now()}] Intentando leer CSV desde: {url}")
            df = pd.read_csv(url, header=None)

            print(f"[{datetime.now()}] CSV leído (sin header). Filas iniciales: {len(df)}, Columnas iniciales: {len(df.columns)}")

            header_row_index = -1
            if not df.empty and len(df) > 1:
                row_as_str_index_1 = df.iloc[1].astype(str).str.upper().fillna('')
                if row_as_str_index_1.str.contains('CUENTA DE CLIENTE').any() or row_as_str_index_1.str.contains('HORA').any():
                    header_row_index = 1
                    print(f"[{datetime.now()}] Encabezados detectados en la fila con índice {header_row_index}.")
                elif df.iloc[0].astype(str).str.upper().fillna('').str.contains('CUENTA DE CLIENTE').any() or df.iloc[0].astype(str).str.upper().fillna('').str.contains('HORA').any():
                    header_row_index = 0
                    print(f"[{datetime.now()}] Encabezados detectados en la fila con índice {header_row_index}.")

            if header_row_index != -1:
                new_header = df.iloc[header_row_index]
                df = df[header_row_index+1:]
                df.columns = new_header
                df.reset_index(drop=True, inplace=True)
                df.dropna(axis=1, how='all', inplace=True)
                df.dropna(axis=0, how='all', inplace=True)
                print(f"[{datetime.now()}] DataFrame reestructurado. Filas: {len(df)}, Columnas: {len(df.columns)}")
            else:
                print(f"[{datetime.now()}] ADVERTENCIA: No se pudo detectar la fila de encabezados automáticamente. El DataFrame puede no estar estructurado correctamente. Se procesará el DataFrame crudo. (Esto es para la hoja de turnos)")

        else:
            print(f"[{datetime.now()}] ERROR: URL no reconocida como CSV. Debe terminar en '?output=csv' o contener 'format=csv'.")
            return None

        cols_to_drop = [col for col in df.columns if 'unnamed' in str(col).lower()]
        if cols_to_drop:
            print(f"[{datetime.now()}] Eliminando columnas 'Unnamed': {cols_to_drop}")
            df.drop(columns=cols_to_drop, inplace=True)

        new_columns = []
        counts = {}
        for col_name in df.columns:
            base_name = str(col_name).strip()
            cleaned_name = re.sub(r'(\.\d+|\_\d+|\s+\d+|\s+\(\d+\))$', '', base_name).strip()

            if cleaned_name in counts:
                counts[cleaned_name] += 1
                new_columns.append(f"{cleaned_name}_{counts[cleaned_name]}")
            else:
                counts[cleaned_name] = 0
                new_columns.append(cleaned_name)
        df.columns = new_columns

        df.dropna(axis=1, how='all', inplace=True)
        df.dropna(axis=0, how='all', inplace=True)

        if df.empty:
            print(f"[{datetime.now()}] Advertencia: El DataFrame resultante está vacío después de la extracción y limpieza. Verifique el contenido de la fuente y los pasos de detección de encabezados.")

        return df
    except Exception as e:
        print(f"[{datetime.now()}] ERROR al extraer datos de la URL '{url}': {e}")
        return None

def formatear_para_prompt(dataframe):
    """
    Formatea los datos del DataFrame en un string adecuado para un prompt de chatbot.
    Esta versión está adaptada para hojas con patrones de columnas repetidos como 'HORA', 'CUENTA DE CLIENTE'.
    """
    if dataframe is None or dataframe.empty:
        return f"[{datetime.now()}] No se encontraron datos para el prompt. El DataFrame está vacío."

    prompt_text = f"[{datetime.now()}] Horarios de clientes disponibles:\n\n"

    column_names = dataframe.columns.tolist()

    block_info = []
    i = 0
    while i < len(column_names):
        col_name_i = str(column_names[i]).strip().upper()

        if col_name_i.startswith('HORA'):
            found_cliente_col = None
            for j in range(i + 1, len(column_names)):
                col_name_j = str(column_names[j]).strip().upper()
                if col_name_j.startswith('CUENTA DE CLIENTE'):
                    found_cliente_col = column_names[j]
                    break

            if found_cliente_col:
                day_suffix = str(column_names[i]).strip().upper().replace('HORA', '').replace(' ', '').replace('.', '').replace('_', '')
                day_label = ""
                if not day_suffix:
                    day_label = "Lunes"
                elif day_suffix == 'M':
                    day_label = "Martes"
                elif day_suffix == 'MI':
                    day_label = "Miércoles"
                elif day_suffix == 'J':
                    day_label = "Jueves"
                elif day_suffix == 'V':
                    day_label = "Viernes"
                elif day_suffix == 'S':
                    day_label = "Sábado"
                elif day_suffix == 'D':
                    day_label = "Domingo"
                else:
                    day_label = f"Día (Columna: {column_names[i]})"

                block_info.append((column_names[i], found_cliente_col, day_label))
                i = j
            else:
                i += 1
        else:
            i += 1

    if not block_info:
        prompt_text += "ADVERTENCIA: No se pudieron identificar los pares de columnas 'HORA' y 'CUENTA DE CLIENTE' con los patrones esperados.\n"
        prompt_text += "Columnas encontradas en el DataFrame: " + ", ".join([str(c) for c in column_names]) + "\n"
        prompt_text += "Por favor, verifica los encabezados en tu Google Sheet y la lógica del script.\n"
        prompt_text += "Datos brutos (primeras 10 filas):\n"
        prompt_text += dataframe.head(10).to_string()
        return prompt_text


    for hora_col_original, cliente_col_original, day_label in block_info:
        prompt_text += f"**--- Horarios para el {day_label} ---**\n"

        for index, row in dataframe.iterrows():
            hora = row.get(hora_col_original)
            cuenta_cliente = row.get(cliente_col_original)

            is_hora_empty = pd.isna(hora) or (isinstance(hora, str) and str(hora).strip() == '')
            is_cliente_empty = pd.isna(cuenta_cliente) or (isinstance(cuenta_cliente, str) and str(cuenta_cliente).strip() == '')

            if is_hora_empty and is_cliente_empty:
                continue

            formatted_hora = str(hora).strip() if not is_hora_empty else "N/A"
            formatted_cliente = str(cuenta_cliente).strip() if not is_cliente_empty else "Sin Cliente Asignado"

            prompt_text += (
                f"  - Hora: {formatted_hora}\n"
                f"    Clientes: {formatted_cliente}\n"
            )
        prompt_text += f"\n"

    print(f"[{datetime.now()}] Datos formateados para el prompt.")
    return prompt_text

def guardar_prompt_en_txt(texto_prompt, ruta_archivo_txt):
    """
    Guarda el texto formateado del prompt en un archivo .txt.
    Crea el directorio si no existe.
    """
    try:
        directorio = os.path.dirname(ruta_archivo_txt)
        if not os.path.exists(directorio):
            os.makedirs(directorio)
            print(f"[{datetime.now()}] Directorio '{directorio}' creado.")

        with open(ruta_archivo_txt, 'w', encoding='utf-8') as f:
            f.write(texto_prompt)
        print(f"[{datetime.now()}] Prompt guardado exitosamente en: '{ruta_archivo_txt}'")
    except Exception as e:
        print(f"[{datetime.now()}] ERROR al guardar el archivo .txt: {e}")


# --- NUEVA FUNCIÓN PARA EXTRAER DEUDORES VENCIDOS ---
def extraer_deudores_vencidos_desde_url(url_pagos):
    """
    Extrae datos de pagos desde una URL CSV, filtra los vencidos SOLAMENTE por la columna 'Estado'
    y devuelve la información relevante (nombre, vencimiento, estado y observaciones completas).
    """
    try:
        print(f"[{datetime.now()}] Intentando leer CSV de pagos desde: {url_pagos}")
        
        # Leer el CSV asumiendo que los encabezados están en la fila 3 (índice 2)
        df_pagos = pd.read_csv(url_pagos, header=2)
        print(f"[{datetime.now()}] CSV de pagos leído. Filas: {len(df_pagos)}, Columnas: {len(df_pagos.columns)}")

        # Normalizar nombres de columnas para facilitar el acceso
        df_pagos.columns = [
            re.sub(r'[^a-z0-9_]', '', col.strip().lower().replace(' ', '_'))
            for col in df_pagos.columns
        ]

        # Columnas requeridas para la salida y el filtro
        col_nombre = 'cliente'       # Mapea a 'cliente'
        col_vencimiento = 'vence'    # Mapea a 'vence'
        col_estado = 'estado'        # Mapea a 'estado' (columna principal para filtrar)
        col_observaciones = 'observaciones' # Mapea a 'observaciones'

        # Verificar que las columnas REQUERIDAS existan después de la normalización
        required_cols = [col_nombre, col_vencimiento, col_estado, col_observaciones] 

        existing_cols_in_df = df_pagos.columns.tolist()
        missing_required_cols = [col for col in required_cols if col not in existing_cols_in_df]

        if missing_required_cols:
            print(f"[{datetime.now()}] ERROR: Faltan columnas REQUERIDAS en el CSV de pagos: {missing_required_cols}")
            print(f"Columnas disponibles (normalizadas): {existing_cols_in_df}")
            return []
        
        # Asegurarse de que solo trabajamos con las columnas existentes y requeridas para el filtrado inicial
        df_pagos_filtered = df_pagos[existing_cols_in_df].copy()

        # Eliminar filas donde todas las columnas críticas son NaN (para limpiar filas vacías)
        df_pagos_filtered.dropna(subset=[col_nombre, col_vencimiento, col_estado], how='all', inplace=True)

        # Convertir la columna de fecha de vencimiento a formato datetime
        if col_vencimiento in df_pagos_filtered.columns:
            df_pagos_filtered[col_vencimiento] = pd.to_datetime(df_pagos_filtered[col_vencimiento], errors='coerce', dayfirst=True) 
            df_pagos_filtered.dropna(subset=[col_vencimiento], inplace=True) # Eliminar filas con fechas no parseables


        # Filtrar los deudores vencidos: SOLAMENTE por la columna 'estado'
        deudores_vencidos_df = df_pagos_filtered[
            df_pagos_filtered[col_estado].astype(str).str.lower() == 'vencido'
        ]

        print(f"[{datetime.now()}] Deudores vencidos encontrados: {len(deudores_vencidos_df)}.")

        # Seleccionar y formatear los datos para la respuesta de la API
        lista_deudores = []
        for index, row in deudores_vencidos_df.iterrows():
            observaciones_completas = "N/A" # Campo para el texto completo de observaciones

            if col_observaciones in row and pd.notna(row.get(col_observaciones)):
                observaciones_completas = str(row[col_observaciones]).strip() # Guarda el texto completo

            deudor_info = {
                "nombre": row[col_nombre] if pd.notna(row.get(col_nombre)) else "N/A",
                "fecha_vencimiento": row[col_vencimiento].strftime('%Y-%m-%d') if pd.notna(row.get(col_vencimiento)) else "N/A",
                "estado_pago": row[col_estado] if pd.notna(row.get(col_estado)) else "N/A",
                "observaciones_completas": observaciones_completas, # <--- Texto completo de Observaciones
            }
            lista_deudores.append(deudor_info)

        return lista_deudores

    except Exception as e:
        print(f"[{datetime.now()}] ERROR al extraer deudores vencidos de la URL '{url_pagos}': {e}")
        return []

# --- LÓGICA PRINCIPAL (EXISTENTE) ---
if __name__ == "__main__":
    print(f"[{datetime.now()}] --- Iniciando proceso de automatización de Google Sheet a TXT ---")

    # 1. Extraer datos de turnos del Google Sheet desde la URL
    datos_turnos = extraer_datos_desde_url(URL_GOOGLE_SHEET_TURNOS)

    # 2. Formatear los datos de turnos para el prompt
    prompt_final_turnos = formatear_para_prompt(datos_turnos)

    # 3. Guardar el prompt de turnos en un archivo .txt
    guardar_prompt_en_txt(prompt_final_turnos, RUTA_ARCHIVO_PROMPT_TXT)

    # --- Ejemplo de uso de la nueva función de deudores (solo para prueba local) ---
    print(f"\n[{datetime.now()}] --- Probando extracción de deudores vencidos ---")
    # Asegúrate de que URL_GOOGLE_SHEET_PAGOS esté configurada con una URL válida para pruebas
    deudores_test = extraer_deudores_vencidos_desde_url(URL_GOOGLE_SHEET_PAGOS)
    if deudores_test:
        print(f"[{datetime.now()}] Deudores vencidos (prueba):")
        for deudor in deudores_test:
            # Imprime solo los campos solicitados
            nombre = deudor.get('nombre', 'N/A')
            vencimiento = deudor.get('fecha_vencimiento', 'N/A')
            estado = deudor.get('estado_pago', 'N/A')
            observaciones = deudor.get('observaciones_completas', 'N/A') 
            print(f"  - Nombre: {nombre} - Vencimiento: {vencimiento} - Estado: {estado} - Observaciones: {observaciones}")
    else:
        print(f"[{datetime.now()}] No se encontraron deudores vencidos en la prueba o hubo un error.")

    print(f"[{datetime.now()}] --- Proceso completado ---")
