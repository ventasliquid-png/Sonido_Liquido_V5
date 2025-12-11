from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import os

router = APIRouter(prefix="/data_intel", tags=["Data Intelligence"])

# Configuración de rutas (debe coincidir con harvest_excel.py)
DATA_DIR = r"c:\dev\Sonido_Liquido_V5\BUILD_PILOTO\data"

class CleanItem(BaseModel):
    nombre_original: str
    nombre_final: Optional[str] = None
    alias: Optional[str] = None
    cuit: Optional[str] = None
    frecuencia: int
    estado: str = "PENDIENTE" # PENDIENTE, IMPORTAR, IGNORAR

class CleanPayload(BaseModel):
    items: List[CleanItem]

@router.get("/candidates/{type}")
def get_candidates(type: str):
    """
    Lee el CSV correspondiente y devuelve los datos.
    Type: 'clientes' o 'productos'
    """
    if type not in ["clientes", "productos"]:
        raise HTTPException(status_code=400, detail="Tipo inválido")
    
    # Priorizar archivo 'limpios' si existe, sino el 'candidatos' (raw)
    filename_raw = f"{type}_candidatos.csv"
    filename_clean = f"{type}_limpios.csv"
    
    path_clean = os.path.join(DATA_DIR, filename_clean)
    path_raw = os.path.join(DATA_DIR, filename_raw)
    
    target_path = path_clean if os.path.exists(path_clean) else path_raw
    print(f"DEBUG: Loading candidates from {target_path}")
    
    if not os.path.exists(target_path):
        print(f"DEBUG: File not found {target_path}")
        return {"items": []} # Archivo no existe aun
        
    try:
        df = pd.read_csv(target_path)
        print(f"DEBUG: Loaded DF Columns: {df.columns}")
        
        # Normalizar columnas para el frontend
        if "nombre" in df.columns: # Formato RAW
            df["nombre_original"] = df["nombre"]
            df["nombre_final"] = df["nombre"] # Por defecto igual
            df["estado"] = "PENDIENTE"
            if "alias" not in df.columns: df["alias"] = ""
        
        # Eliminar NaNs
        df = df.fillna("")
        
        items = df.to_dict(orient="records")
        print(f"DEBUG: Returning {len(items)} items")
        return {"items": items}
        
    except Exception as e:
        print(f"❌ ERROR reading CSV: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error leyendo datos: {str(e)}")

@router.post("/candidates/{type}")
def save_candidates(type: str, payload: CleanPayload):
    """
    Guarda el progreso en el archivo CSV 'limpios'.
    """
    if type not in ["clientes", "productos"]:
        raise HTTPException(status_code=400, detail="Tipo inválido")
        
    filename_clean = f"{type}_limpios.csv"
    path_clean = os.path.join(DATA_DIR, filename_clean)
    
    try:
        # Convertir items a DataFrame
        data = [item.dict() for item in payload.items]
        df = pd.DataFrame(data)
        
        # Asegurar directorio
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            
        df.to_csv(path_clean, index=False, encoding='utf-8-sig')
        return {"status": "ok", "message": f"Guardado en {filename_clean}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
from fastapi import Depends
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.clientes.models import Cliente
from backend.productos.models import Producto, Rubro

@router.post("/commit/{type}")
def commit_candidates(type: str, db: Session = Depends(get_db)):
    """
    Toma los items marcados como IMPORTAR en el archivo 'limpios' y los inserta en la BD real.
    """
    if type not in ["clientes", "productos"]:
        raise HTTPException(status_code=400, detail="Tipo inválido")
        
    filename_clean = f"{type}_limpios.csv"
    path_clean = os.path.join(DATA_DIR, filename_clean)
    
    if not os.path.exists(path_clean):
        raise HTTPException(status_code=404, detail="No hay datos para commitear (archivo no existe)")
        
    try:
        df = pd.read_csv(path_clean)
        # Filtrar solo IMPORTAR
        if "estado" not in df.columns:
             return {"message": "No hay columna estado"}
             
        df_import = df[df["estado"] == "IMPORTAR"]
        
        count = 0
        errores = []
        
        if type == "clientes":
            for _, row in df_import.iterrows():
                try:
                    cuit_limpio = str(row.get("cuit", "")).replace("-", "").replace("/", "").strip()
                    nombre = row.get("nombre_final", row.get("nombre_original"))
                    # Alias ignorado por ahora en modelo Cliente simple, o podria ir en observaciones
                    
                    # Chequear duplicado por CUIT si existe
                    if cuit_limpio:
                        exists = db.query(Cliente).filter(Cliente.cuit == cuit_limpio).first()
                        if exists:
                            errores.append(f"Cliente {nombre} ya existe (CUIT {cuit_limpio})")
                            continue
                    
                    nuevo_cliente = Cliente(
                        razon_social=nombre,
                        cuit=cuit_limpio,
                        # email="importado@data-cleaner.local", # Removed: field does not exist in model
                        activo=True
                    )
                    db.add(nuevo_cliente)
                    count += 1
                except Exception as e:
                    errores.append(f"Error importando {row.get('nombre_original')}: {e}")
                    
        elif type == "productos":
             # Lógica simplificada para productos
             # Asumimos Rubro "GENERAL" por defecto si no existe hay que crearlo
             rubro_default = db.query(Rubro).filter(Rubro.nombre == "GENERAL").first()
             if not rubro_default:
                 rubro_default = Rubro(nombre="GENERAL", codigo="GEN")
                 db.add(rubro_default)
                 db.commit()
                 db.refresh(rubro_default)
                 
             for _, row in df_import.iterrows():
                try:
                    nombre = row.get("nombre_final", row.get("nombre_original"))
                    # Check duplicado nombre
                    exists = db.query(Producto).filter(Producto.nombre == nombre).first()
                    if exists: continue

                    nuevo_prod = Producto(
                        nombre=nombre,
                        rubro_id=rubro_default.id,
                        activo=True,
                        sku=None # Dejar que sea null o generar uno
                    )
                    db.add(nuevo_prod)
                    count += 1
                except Exception as ex:
                    errores.append(f"Error prod {row.get('nombre')}: {ex}")

        db.commit()
        return {
            "status": "ok", 
            "imported_count": count, 
            "errors": errores
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ COMMIT ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
