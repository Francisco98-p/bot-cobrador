from fastapi import FastAPI
# Importa la nueva función y la URL de pagos desde programa_traspaso
from programa_traspaso import extraer_datos_desde_url, formatear_para_prompt, extraer_deudores_vencidos_desde_url, URL_GOOGLE_SHEET_PAGOS
import uvicorn

app = FastAPI()

@app.get("/")
def home():
    # Mensaje actualizado para reflejar la nueva funcionalidad
    return {"status": "ok", "message": "API activa para leer horarios y deudores."}

@app.get("/turnos")
def get_turnos():
    url_csv = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRxvq7h8kghE7h1Hr8T0P6rFykWzyZq8WNc1YSqlbo6JubxFDHZ_9VNYZgTSAQcifOyGCVmKE876pcC/pub?gid=2085227179&single=true&output=csv"
    df = extraer_datos_desde_url(url_csv)
    if df is None or df.empty:
        return {"error": "No se encontraron datos válidos."}
    texto = formatear_para_prompt(df)
    return {"respuesta": texto}

# --- NUEVA RUTA PARA OBTENER DEUDORES VENCIDOS ---
@app.get("/deudores-vencidos")
def get_deudores_vencidos():
    """
    Endpoint para obtener la lista de clientes con pagos vencidos desde el Google Sheet de pagos.
    Utiliza la función extraer_deudores_vencidos_desde_url de programa_traspaso.py.
    """
    deudores = extraer_deudores_vencidos_desde_url(URL_GOOGLE_SHEET_PAGOS)
    if not deudores:
        # Si no se encuentran deudores o hay un error en la extracción
        return {"exito": False, "mensaje": "No se encontraron deudores vencidos o hubo un error al procesar el archivo."}
    return {"exito": True, "datos": deudores}

# OPCIONAL: Para ejecutar localmente si no usás Uvicorn directamente
# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
