from fastapi import FastAPI
from programa_traspaso import extraer_datos_desde_url, formatear_para_prompt, extraer_deudores_vencidos_desde_url, URL_GOOGLE_SHEET_PAGOS
import uvicorn

app = FastAPI()

@app.get("/")
def home():
    """
    Endpoint principal que ahora devuelve la lista de clientes con pagos vencidos.
    """
    deudores = extraer_deudores_vencidos_desde_url(URL_GOOGLE_SHEET_PAGOS)
    if not deudores:
        return {"exito": False, "mensaje": "No se encontraron deudores vencidos o hubo un error al procesar el archivo."}
    return {"exito": True, "datos": deudores}

# Puedes mantener o eliminar el endpoint /deudores-vencidos si quieres.
# Si lo mantienes, ambas rutas devolverán lo mismo.
@app.get("/deudores-vencidos")
def get_deudores_vencidos():
    """
    Endpoint para obtener la lista de clientes con pagos vencidos desde el Google Sheet de pagos.
    Utiliza la función extraer_deudores_vencidos_desde_url de programa_traspaso.py.
    """
    deudores = extraer_deudores_vencidos_desde_url(URL_GOOGLE_SHEET_PAGOS)
    if not deudores:
        return {"exito": False, "mensaje": "No se encontraron deudores vencidos o hubo un error al procesar el archivo."}
    return {"exito": True, "datos": deudores}

# ... el resto de tu código (como @app.get("/turnos"))
