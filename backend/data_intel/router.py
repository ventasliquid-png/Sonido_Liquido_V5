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
    # Priorizar archivo 'limpios' si existe, sino el 'raw' original
    filename_raw = f"{type}_raw.csv"
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
from sqlalchemy import func
from backend.core.database import get_db
from backend.clientes.models import Cliente
from backend.clientes.models import Cliente, Domicilio
from backend.productos.models import Producto, Rubro, ProductoCosto
from decimal import Decimal

@router.post("/commit/{type}")
def commit_candidates(type: str, db: Session = Depends(get_db)):
    # ... (existing check code) ...
    if type not in ["clientes", "productos"]:
        raise HTTPException(status_code=400, detail="Tipo inválido")
        
    filename_clean = f"{type}_limpios.csv"
    path_clean = os.path.join(DATA_DIR, filename_clean)
    
    if not os.path.exists(path_clean):
        raise HTTPException(status_code=404, detail="No hay datos para commitear")
        
    try:
        df = pd.read_csv(path_clean)
        # Filtrar solo IMPORTAR
        if "estado" not in df.columns:
             return {"message": "No hay columna estado"}
             
        df_import = df[df["estado"] == "IMPORTAR"]
        
        count = 0
        errores = []
        
        if type == "clientes":
            filename_master = "clientes_master.csv"
            path_master = os.path.join(DATA_DIR, filename_master)
            master_rows = []

            for index, row in df_import.iterrows():
                try:
                    cuit_limpio = str(row.get("cuit", "")).replace("-", "").replace("/", "").strip()
                    nombre = row.get("nombre_final", row.get("nombre_original"))
                    
                    if cuit_limpio:
                        exists = db.query(Cliente).filter(Cliente.cuit == cuit_limpio).first()
                        if exists:
                            # [SMART UPDATE]
                            # Si es 100% igual, "chilla" (Marca EXISTENTE).
                            # Si es diferente, actualiza.
                            if exists.razon_social == nombre:
                                df.at[index, 'estado'] = 'EXISTENTE'
                                errores.append(f"Cliente {nombre} ya existe idéntico. (Skip)")
                                continue
                            else:
                                # Update existing
                                old_name = exists.razon_social
                                exists.razon_social = nombre
                                db.add(exists)
                                
                                # Add to Master (New Version)
                                master_rows.append({
                                    "id_legacy": row.get("id", ""), 
                                    "razon_social": nombre,
                                    "cuit": cuit_limpio,
                                    "fecha_importacion": pd.Timestamp.now().isoformat()
                                })
                                
                                df.at[index, 'estado'] = 'ACTUALIZADO'
                                count += 1
                                continue
                    
                    nuevo_cliente = Cliente(
                        razon_social=nombre,
                        cuit=cuit_limpio,
                        activo=True
                    )
                    db.add(nuevo_cliente)
                    db.flush() # Get ID for Domicilio

                    # [FIX CONSISTENCY] Create Default Address
                    dom_def = Domicilio(
                        cliente_id=nuevo_cliente.id,
                        calle="A DEFINIR",
                        numero="0",
                        localidad="CABA", # Default safe
                        cp="0000",
                        es_fiscal=True,
                        activo=True
                    )
                    db.add(dom_def)
                    
                    # Add to Master List
                    master_rows.append({
                        "id_legacy": row.get("id", ""), 
                        "razon_social": nombre,
                        "cuit": cuit_limpio,
                        "fecha_importacion": pd.Timestamp.now().isoformat()
                    })
                    
                    # Update status
                    df.at[index, 'estado'] = 'IMPORTADO'
                    count += 1
                except Exception as e:
                    errores.append(f"Error importando {row.get('nombre_original')}: {e}")
            
            # Append to Master CSV
            if master_rows:
                df_master_new = pd.DataFrame(master_rows)
                header = not os.path.exists(path_master)
                df_master_new.to_csv(path_master, mode='a', header=header, index=False, encoding='utf-8-sig')

        elif type == "productos":
             filename_master = "productos_master.csv"
             path_master = os.path.join(DATA_DIR, filename_master)
             master_rows = []

             rubro_default = db.query(Rubro).filter(Rubro.nombre == "GENERAL").first()
             if not rubro_default:
                 rubro_default = Rubro(nombre="GENERAL", codigo="GEN")
                 db.add(rubro_default)
                 db.commit()
                 db.refresh(rubro_default)
            
             next_sku_counter = None
                 
             for index, row in df_import.iterrows():
                try:
                    nombre = row.get("nombre_final", row.get("nombre_original"))
                    exists = db.query(Producto).filter(Producto.nombre == nombre).first()
                    if exists: 
                        df.at[index, 'estado'] = 'EXISTENTE'
                        continue
                        
                    # [AUTO SKU] Generate Next SKU
                    # Buscamos el max SKU actual en la DB (solo la primera vez del loop es ineficiente, 
                    # pero seguro. Idealmente cachear fuera del loop si son muchos).
                    # Para seguridad transaccional simple en piloto:
                    max_sku_db = db.query(func.max(Producto.sku)).scalar() or 9999
                    # Si acabamos de agregar un producto en este commit (pero no flush commit total), 
                    # el SKU podria chocar si no lo incrementamos localmente.
                    # Pero como hacemos db.add() y db.flush(), el item ya está en la sesión?
                    # No, el flush manda el ID, pero el commit final asegura la persistencia.
                    # Mejor estrategia simple: Buscar max, sumar 1 + index loop (pero index es relativo a df).
                    # Mas seguro: Query real-time o un contador manual. 
                    # Usaremos contador manual iniciado fuera del loop.
                    
                    if next_sku_counter is None:
                         next_sku_counter = max_sku_db + 1
                    else:
                         next_sku_counter += 1

                    nuevo_prod = Producto(
                        nombre=nombre,
                        rubro_id=rubro_default.id,
                        activo=True,
                        sku=next_sku_counter,
                        tipo_producto='VENTA' 
                    )
                    db.add(nuevo_prod)
                    db.flush() # ID for Costo

                    # [FIX CONSISTENCY] Create Default Cost
                    costo_def = ProductoCosto(
                        producto_id=nuevo_prod.id,
                        costo_reposicion=Decimal(0),
                        rentabilidad_target=Decimal(30),
                        iva_alicuota=Decimal(21)
                    )
                    db.add(costo_def)
                    
                    master_rows.append({
                        "nombre": nombre,
                        "rubro": "GENERAL",
                        "fecha_importacion": pd.Timestamp.now().isoformat()
                    })
                    count += 1
                except Exception as ex:
                    errores.append(f"Error prod {row.get('nombre')}: {ex}")

             if master_rows:
                df_master_new = pd.DataFrame(master_rows)
                header = not os.path.exists(path_master)
                df_master_new.to_csv(path_master, mode='a', header=header, index=False, encoding='utf-8-sig')

        db.commit()
        
        # Save updated Clean CSV with new statuses
        df.to_csv(path_clean, index=False, encoding='utf-8-sig')

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
