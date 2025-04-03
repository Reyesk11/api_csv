from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import unidecode
import re
from fastapi.responses import PlainTextResponse

app = FastAPI()

# ====================== MODELOS ======================
class CSVData(BaseModel):
    csv_content: str

# ====================== FUNCIONES ======================
def normalize_text(text: str) -> str:
    """Elimina tildes, espacios extras y convierte a mayúsculas"""
    if pd.isna(text):
        return ""
    text = str(text)
    text = unidecode.unidecode(text)  # Quita tildes
    text = re.sub(r'\s+', ' ', text).strip()  # Elimina espacios extras
    return text.upper()

# ====================== RUTAS ======================
@app.get("/")
def home():
    """Mensaje de bienvenida"""
    return {
        "message": "¡API de normalización CSV activa!",
        "endpoints": {
            "normalizar_csv": "POST /normalize-csv",
            "health_check": "GET /health"
        }
    }

@app.get("/health")
def health_check():
    """Verifica el estado de la API"""
    return {
        "status": "ok",
        "version": "1.0.0",
        "service": "CSV Normalizer"
    }

@app.post("/normalize-csv", response_class=PlainTextResponse)
async def normalize_csv(data: CSVData):
    """Normaliza un CSV: elimina tildes, espacios y normaliza formatos"""
    try:
        # Convertir CSV a DataFrame
        df = pd.read_csv(pd.compat.StringIO(data.csv_content))
        
        # Normalizar todas las columnas de texto
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].apply(normalize_text)
        
        # Normalizar teléfonos (si existe la columna)
        if "CONTACTO 1" in df.columns:
            df["CONTACTO 1"] = df["CONTACTO 1"].apply(lambda x: re.sub(r'[^0-9]', '', str(x)))
        
        return df.to_csv(index=False)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

# ====================== EXTRAS ======================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)