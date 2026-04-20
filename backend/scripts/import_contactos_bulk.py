#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT: import_contactos_bulk.py
PROPÓSITO: Importación masiva de contactos bajo Doctrina Soberana (Person-Centric)
AUTORIZACIÓN: PIN 1974
GENOMA: Bit 5 (CANTERA_NIKE), Bit 6 (VINCULO_DUDOSO), Bit 7 (VINCULO_HISTORICO)
NOTAS: Segregadas (notas_sistema vs notas_globales)
"""

import sys
import os
import json
import glob
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import uuid
import re
import shutil
import difflib

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Path resolution
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
backend_dir = os.path.join(root_dir, "backend")
sys.path.insert(0, root_dir)
sys.path.insert(0, backend_dir)

# [DOCTRINA SOBERANA] Cargar .env local y rechazar cualquier URL externa
try:
    from dotenv import load_dotenv as _load_dotenv
    _env_path = os.path.join(root_dir, ".env")
    if os.path.exists(_env_path):
        _load_dotenv(_env_path, override=True)
except ImportError:
    pass

_current_db_url = os.environ.get("DATABASE_URL", "")
if not _current_db_url or "postgresql" in _current_db_url or "postgres://" in _current_db_url:
    _sqlite_path = os.path.join(root_dir, "pilot_v5x.db")
    os.environ["DATABASE_URL"] = f"sqlite:///{_sqlite_path}"

from core.database import SessionLocal, engine, Base
from backend.contactos import models as contactos_models, service as contactos_service, schemas
from backend.clientes import models as clientes_models, service as clientes_service

# ============================================================================
# CONSTANTES
# ============================================================================

# Bits de Genoma (Mapa 64-bit)
CANTERA_NIKE = 16           # Bit 5: Origen importación
VINCULO_DUDOSO = 32         # Bit 6: Fuzzy match 70-98% (validación diferida)
VINCULO_HISTORICO = 64      # Bit 7: Vínculo anterior cuando hay nueva empresa

# Rutas
IMPORTS_DIR = os.path.join(root_dir, "scripts", "imports")
PROCESSED_DIR_GDrive = r"G:\Mi unidad\V5_Silo_Datos\Contactos_Procesados"
PROCESSED_DIR_LOCAL = os.path.join(root_dir, ".claude", "processed_imports")

# Umbral fuzzy
FUZZY_THRESHOLD = 0.70  # 70%

# ============================================================================
# FUNCIONES DE NORMALIZACIÓN (FUZZY MATCHING)
# ============================================================================

def normalizar_nombre(texto: str) -> str:
    """Normalizar nombre de empresa para fuzzy matching"""
    if not texto:
        return ""

    texto = texto.lower()
    texto = texto.replace(".", "")
    texto = texto.replace(",", "")

    terminos_legales = ["s.a.", "sa", "s.r.l.", "srl", "s.a.s", "sas", "ltda", "ltda.", "inc", "inc.", "corp", "corp.", "cia", "cia."]
    for termino in terminos_legales:
        texto = re.sub(rf"\b{termino}\b", "", texto)

    texto = re.sub(r'\s+', ' ', texto)
    texto = texto.strip()

    return texto

def buscar_cliente_fuzzy(db, empresa_nombre: str) -> Tuple[Optional[clientes_models.Cliente], str, int]:
    """
    Buscar cliente usando fuzzy matching con SequenceMatcher.
    Retorna: (cliente_obj, nivel, confidence_score)
      - nivel: "exacto" (100%), "probable" (70-98%), "huerfano" (<70%)
    """
    if not empresa_nombre:
        return (None, "huerfano", 0)

    # 1. Búsqueda exacta primero
    try:
        cliente = buscar_cliente(db, empresa_nombre)
        if cliente:
            return (cliente, "exacto", 100)
    except:
        pass

    # 2. Fuzzy match
    try:
        clientes_db = db.query(clientes_models.Cliente).all()
    except:
        return (None, "huerfano", 0)

    nombre_norm = normalizar_nombre(empresa_nombre)

    if not nombre_norm:
        return (None, "huerfano", 0)

    mejores_matches = []

    for cliente in clientes_db:
        cliente_norm = normalizar_nombre(cliente.razon_social) if cliente.razon_social else ""
        ratio = difflib.SequenceMatcher(None, nombre_norm, cliente_norm).ratio()

        if cliente.nombre_fantasia:
            fantasia_norm = normalizar_nombre(cliente.nombre_fantasia)
            ratio_fantasia = difflib.SequenceMatcher(None, nombre_norm, fantasia_norm).ratio()
            ratio = max(ratio, ratio_fantasia)

        if ratio >= FUZZY_THRESHOLD:
            mejores_matches.append((cliente, ratio))

    if not mejores_matches:
        return (None, "huerfano", 0)

    mejores_matches.sort(key=lambda x: x[1], reverse=True)
    mejor_cliente, mejor_ratio = mejores_matches[0]

    confidence = int(mejor_ratio * 100)

    if mejor_ratio == 1.0 or mejor_ratio >= 0.99:
        return (mejor_cliente, "exacto", confidence)
    elif mejor_ratio >= FUZZY_THRESHOLD:
        return (mejor_cliente, "probable", confidence)
    else:
        return (None, "huerfano", confidence)

# ============================================================================
# FUNCIONES DE AUDITORÍA (GENOMA)
# ============================================================================

def audit_genome(db) -> Tuple[bool, str]:
    """Auditoría de arquitectura: verificar flags_estado y notas_sistema"""
    try:
        if not hasattr(contactos_models.Persona, '__table__'):
            return False, "Tabla 'personas' no encontrada"

        tabla_cols = [c.name for c in contactos_models.Persona.__table__.columns]

        if 'flags_estado' not in tabla_cols:
            return False, "Columna 'flags_estado' no existe"

        if 'notas_sistema' not in tabla_cols:
            return False, "Columna 'notas_sistema' no existe (requiere migración)"

        flags_col = contactos_models.Persona.__table__.columns['flags_estado']
        col_type = str(flags_col.type)
        if 'BigInteger' not in col_type and 'BIGINT' not in col_type and 'INTEGER' not in col_type:
            return False, f"flags_estado tipo incorrecto: {col_type}"

        try:
            result = db.query(contactos_models.Persona).filter(
                (contactos_models.Persona.flags_estado & 8) > 0
            ).first()
            arch_version = "V15+ (Bit 3 detectado)" if result else "V5+ (Compatible)"
        except:
            arch_version = "V5+ (Tabla compatible)"

        return True, arch_version

    except Exception as e:
        return False, f"Error auditoría: {str(e)[:80]}"

# ============================================================================
# FUNCIONES DE BÚSQUEDA
# ============================================================================

def existe_email_en_db(db, email: str) -> bool:
    """Buscar email en canales_personales JSON"""
    if not email:
        return False

    try:
        personas = db.query(contactos_models.Persona).all()
        for persona in personas:
            if persona.canales_personales:
                if isinstance(persona.canales_personales, list):
                    for canal in persona.canales_personales:
                        if canal.get('valor') == email:
                            return True
                elif isinstance(persona.canales_personales, str):
                    if email in persona.canales_personales:
                        return True
        return False
    except:
        return False

def buscar_persona_por_email(db, email: str) -> Optional[contactos_models.Persona]:
    """
    PERSON-CENTRIC: Buscar Persona por email.
    Retorna: Persona object o None
    """
    if not email:
        return None

    try:
        personas = db.query(contactos_models.Persona).all()
        for persona in personas:
            if persona.canales_personales:
                if isinstance(persona.canales_personales, list):
                    for canal in persona.canales_personales:
                        if canal.get('valor') == email:
                            return persona
        return None
    except:
        return None

def buscar_vinculo_existente(db, persona_id: str, cliente_id: str) -> Optional[contactos_models.Vinculo]:
    """
    PERSON-CENTRIC: Buscar si Persona ya tiene vínculo con Cliente.
    Retorna: Vinculo object o None
    """
    if not persona_id or not cliente_id:
        return None

    try:
        vinculo = db.query(contactos_models.Vinculo).filter(
            (contactos_models.Vinculo.persona_id == persona_id) &
            (contactos_models.Vinculo.entidad_tipo == 'CLIENTE') &
            (contactos_models.Vinculo.entidad_id == cliente_id)
        ).first()
        return vinculo
    except:
        return None

def marcar_vinculo_historico(db, persona_id: str):
    """
    PERSON-CENTRIC: Marcar todos los vínculos activos como históricos (Bit 7).
    Cuando hay nueva empresa, el anterior se preserva con VINCULO_HISTORICO.
    """
    try:
        vinculos = db.query(contactos_models.Vinculo).filter(
            (contactos_models.Vinculo.persona_id == persona_id) &
            (contactos_models.Vinculo.activo == True)
        ).all()

        for vinculo in vinculos:
            vinculo.flags_estado |= VINCULO_HISTORICO
            vinculo.activo = False

        db.commit()
    except:
        pass

def buscar_cliente(db, empresa_nombre: str) -> Optional[clientes_models.Cliente]:
    """Buscar cliente por razon_social o nombre_fantasia (búsqueda exacta)"""
    if not empresa_nombre:
        return None

    try:
        cliente = db.query(clientes_models.Cliente).filter(
            clientes_models.Cliente.razon_social.ilike(f"%{empresa_nombre}%")
        ).first()

        if cliente:
            return cliente

        cliente = db.query(clientes_models.Cliente).filter(
            clientes_models.Cliente.nombre_fantasia.ilike(f"%{empresa_nombre}%")
        ).first()

        return cliente
    except:
        return None

# ============================================================================
# FUNCIONES DE PROCESAMIENTO
# ============================================================================

def construir_canales(email: str, telefono: str) -> List[Dict]:
    """Construir lista de canales desde email y telefono"""
    canales = []

    if email:
        canales.append({"tipo": "EMAIL", "valor": email, "etiqueta": "Principal"})

    if telefono:
        canales.append({"tipo": "WHATSAPP", "valor": telefono, "etiqueta": "Principal"})

    return canales

def construir_notas_sistema(match_nivel: str, match_score: int, empresa: str, cargo: str) -> str:
    """
    Construir notas_sistema (auditoría del script).
    Formato segregado: [ORIGEN], [Fuzzy Match], [Cargo], [ENTIDAD_PENDIENTE]
    """
    notas = []

    notas.append(f"[ORIGEN: Siembra Digital {datetime.now().strftime('%Y-%m-%d')}]")

    if match_nivel == "exacto":
        notas.append("[Fuzzy Match: 100% (Exacto)]")
    elif match_nivel == "probable":
        notas.append(f"[Fuzzy Match: {match_score}% (Probable)]")
    elif match_nivel == "huerfano":
        notas.append(f"[Fuzzy Match: {match_score}% (No encontrada)]")
        notas.append(f"[ENTIDAD_PENDIENTE: {empresa}]")

    if cargo:
        notas.append(f"[Cargo Detectado: {cargo}]")

    return " ".join(notas)

def construir_notas_usuario(tags: Optional[List[str]], extra_data: Dict) -> Optional[str]:
    """
    Construir notas_globales (visible para usuario).
    El script NO escribe datos críticos aquí.
    """
    notas = []

    if tags:
        notas.append(f"[TAGS: {', '.join(tags)}]")

    if extra_data:
        for key, value in extra_data.items():
            if value:
                notas.append(f"[{key.upper()}: {str(value)[:100]}]")

    return " ".join(notas) if notas else None

# ============================================================================
# DRY RUN
# ============================================================================

def dry_run(json_data: List[Dict], db) -> Dict:
    """Análisis sin commit de lo que se va a insertar (con fuzzy matching)"""
    stats = {
        "total": len(json_data),
        "validos": 0,
        "nuevos": 0,
        "duplicados": 0,
        "exacto": 0,
        "probable": 0,
        "huerfano": 0,
        "errores_parse": 0,
        "preview": [],
        "empresas_exactas": {},
        "empresas_probables": {},
        "empresas_pendientes": set()
    }

    for idx, record in enumerate(json_data):
        try:
            nombre = record.get("nombre", "").strip()
            if not nombre:
                stats["errores_parse"] += 1
                continue

            stats["validos"] += 1
            email = record.get("email", "").strip()
            empresa = record.get("empresa", "").strip()
            cargo = record.get("cargo", "").strip()

            if email and existe_email_en_db(db, email):
                stats["duplicados"] += 1
                continue
            else:
                stats["nuevos"] += 1

            match_nivel = "huerfano"
            match_score = 0
            cliente_obj = None

            if empresa:
                cliente_obj, match_nivel, match_score = buscar_cliente_fuzzy(db, empresa)

                if match_nivel == "exacto":
                    stats["exacto"] += 1
                    if cliente_obj:
                        stats["empresas_exactas"][empresa] = cliente_obj.id
                elif match_nivel == "probable":
                    stats["probable"] += 1
                    if cliente_obj:
                        stats["empresas_probables"][empresa] = (cliente_obj.id, match_score)
                else:
                    stats["huerfano"] += 1
                    stats["empresas_pendientes"].add(empresa)
            else:
                stats["huerfano"] += 1

            if len(stats["preview"]) < 3:
                estado = "OK" if not email or not existe_email_en_db(db, email) else "DUP"
                if match_nivel == "exacto":
                    vinculo = f"EXACTO (100%)"
                elif match_nivel == "probable":
                    vinculo = f"PROBABLE ({match_score}%)"
                else:
                    vinculo = "PENDIENTE" if empresa else "N/A"

                stats["preview"].append({
                    "nombre": nombre,
                    "email": email,
                    "empresa": empresa,
                    "cargo": cargo,
                    "estado": estado,
                    "vinculo": vinculo,
                    "match_nivel": match_nivel,
                    "match_score": match_score
                })

        except Exception as e:
            stats["errores_parse"] += 1

    return stats

# ============================================================================
# EJECUCIÓN REAL (PERSON-CENTRIC)
# ============================================================================

def ejecutar_import(json_data: List[Dict], archivo_nombre: str, db) -> Dict:
    """
    Ejecutar importación con lógica PERSON-CENTRIC.

    Flujo:
    1. Buscar persona por email
    2. Si existe + empresa distinta → marcar anterior como histórico
    3. Buscar cliente con fuzzy
    4. Inyectar bits según match
    5. Separar notas_sistema vs notas_globales
    """
    report = {
        "timestamp": datetime.now(),
        "archivo": archivo_nombre,
        "exitosos": 0,
        "duplicados_saltados": 0,
        "sin_vinculo": 0,
        "nuevas_personas": 0,
        "personas_existentes": 0,
        "errores": [],
        "empresas_pendientes": {}
    }

    for idx, record in enumerate(json_data):
        try:
            nombre = record.get("nombre", "").strip()
            if not nombre:
                report["errores"].append(f"Fila {idx + 1}: Falta 'nombre'")
                continue

            email = record.get("email", "").strip()
            telefono = record.get("telefono", "").strip()
            direccion = record.get("direccion", "").strip()
            empresa = record.get("empresa", "").strip()
            cargo = record.get("cargo", "").strip()
            tags = record.get("tags", [])
            apellido = record.get("apellido", "").strip()

            # PERSON-CENTRIC: Buscar persona existente por email
            persona_existente = buscar_persona_por_email(db, email) if email else None

            # Fuzzy match para cliente
            cliente = None
            cliente_id = None
            match_nivel = "huerfano"
            match_score = 0

            if empresa:
                cliente, match_nivel, match_score = buscar_cliente_fuzzy(db, empresa)
                if cliente:
                    cliente_id = cliente.id

            # LÓGICA PERSON-CENTRIC
            if persona_existente:
                # Email ya existe
                vinculo_existente = buscar_vinculo_existente(db, persona_existente.id, cliente_id) if cliente_id else None

                if vinculo_existente:
                    # MISMO EMAIL + MISMO CLIENTE = DUPLICADO
                    report["duplicados_saltados"] += 1
                    continue
                elif cliente_id:
                    # MISMO EMAIL + EMPRESA DISTINTA = Marcar anterior como histórico
                    marcar_vinculo_historico(db, persona_existente.id)
                    persona = persona_existente
                    report["personas_existentes"] += 1
                else:
                    # EMAIL EXISTE PERO SIN CLIENTE = Usar persona existente
                    persona = persona_existente
                    report["personas_existentes"] += 1
            else:
                # EMAIL NO EXISTE = CREAR PERSONA NUEVA
                if email and existe_email_en_db(db, email):
                    report["duplicados_saltados"] += 1
                    continue

                canales = construir_canales(email, telefono)
                extra_data = {}
                notas_usuario = construir_notas_usuario(tags, extra_data)

                contacto_create = schemas.ContactoCreate(
                    nombre=nombre,
                    apellido=apellido if apellido else None,
                    notas=notas_usuario,
                    domicilio_personal=direccion if direccion else None,
                    canales=canales if canales else None,
                    cliente_id=cliente_id,
                    puesto=cargo if cargo else None,
                    roles=[],
                    estado=True
                )

                persona = contactos_service.create_contacto(db, contacto_create)
                report["nuevas_personas"] += 1

            # INYECTAR BITS SEGÚN MATCH
            persona.flags_estado |= CANTERA_NIKE  # Bit 5 siempre
            if match_nivel == "probable":
                persona.flags_estado |= VINCULO_DUDOSO  # Bit 6

            # NOTAS SEGREGADAS
            notas_sistema = construir_notas_sistema(match_nivel, match_score, empresa, cargo)
            persona.notas_sistema = notas_sistema

            # Rastrear empresas pendientes
            if match_nivel == "huerfano" and empresa:
                if empresa not in report["empresas_pendientes"]:
                    report["empresas_pendientes"][empresa] = 0
                report["empresas_pendientes"][empresa] += 1

            # Crear vínculo si cliente existe
            if cliente_id:
                try:
                    vinculo_data = schemas.ContactoCreate(cliente_id=cliente_id)
                    contactos_service.add_vinculo(db, persona.id, vinculo_data)
                except:
                    pass
            else:
                report["sin_vinculo"] += 1

            db.commit()
            report["exitosos"] += 1

        except Exception as e:
            db.rollback()
            report["errores"].append(f"Fila {idx + 1}: {str(e)}")

    return report

# ============================================================================
# MANEJO DE ARCHIVOS
# ============================================================================

def mover_archivo(origen: str, nombre_archivo: str, timestamp: str) -> str:
    """Mover archivo a destino (GDrive o fallback local)"""
    nombre_base = os.path.splitext(nombre_archivo)[0]
    nombre_destino = f"{nombre_base}_PROCESSED_{timestamp}.json"

    if os.path.exists(PROCESSED_DIR_GDrive):
        try:
            destino_path = os.path.join(PROCESSED_DIR_GDrive, nombre_destino)
            shutil.move(origen, destino_path)
            return destino_path
        except Exception as e:
            print(f"[WARN] No se pudo mover a GDrive: {e}. Usando fallback local...")

    os.makedirs(PROCESSED_DIR_LOCAL, exist_ok=True)
    destino_path = os.path.join(PROCESSED_DIR_LOCAL, nombre_destino)
    try:
        shutil.move(origen, destino_path)
        return destino_path
    except Exception as e:
        return f"(Error moving file: {e})"

def generar_audit_log(report: Dict, archivo_nombre: str, timestamp: str) -> str:
    """Generar archivo .log de auditoría"""
    nombre_base = os.path.splitext(archivo_nombre)[0]
    nombre_log = f"{nombre_base}_AUDIT_{timestamp}.log"

    if os.path.exists(PROCESSED_DIR_GDrive):
        log_path = os.path.join(PROCESSED_DIR_GDrive, nombre_log)
    else:
        os.makedirs(PROCESSED_DIR_LOCAL, exist_ok=True)
        log_path = os.path.join(PROCESSED_DIR_LOCAL, nombre_log)

    log_content = f"""
=== AUDIT LOG: IMPORT_CONTACTOS_BULK (PERSON-CENTRIC) ===
Archivo: {report['archivo']}
Timestamp: {report['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}

RESULTADOS:
  Exitosos: {report['exitosos']}
  Nuevas Personas: {report['nuevas_personas']}
  Personas Existentes (nueva empresa): {report['personas_existentes']}
  Duplicados (saltados): {report['duplicados_saltados']}
  Sin vínculo (pendientes): {report['sin_vinculo']}
  Errores: {len(report['errores'])}

GENOMA INYECTADO:
  Bit 5 (CANTERA_NIKE=16): Todos los contactos importados
  Bit 6 (VINCULO_DUDOSO=32): Contactos con fuzzy match 70-98%
  Bit 7 (VINCULO_HISTORICO=64): Vínculos anteriores cuando hay nueva empresa

EMPRESAS NO ENCONTRADAS (ENTIDAD_PENDIENTE):
"""

    if report["empresas_pendientes"]:
        for empresa, count in sorted(report["empresas_pendientes"].items()):
            log_content += f"  - {empresa} ({count} contactos)\n"
    else:
        log_content += "  (Ninguna)\n"

    if report["errores"]:
        log_content += "\nDETALLES DE ERRORES:\n"
        for error in report["errores"]:
            log_content += f"  - {error}\n"

    log_content += "\n[NOTAS SEGREGADAS]\n"
    log_content += "  - notas_sistema: Auditoría del script (Origen, Fuzzy %, Cargo, ENTIDAD_PENDIENTE)\n"
    log_content += "  - notas_globales: Visible para usuario (TAGS, campos extra)\n"
    log_content += "\n[PERSON-CENTRIC]\n"
    log_content += "  - Persona es constante, empresa es trayectoria\n"
    log_content += "  - Vínculos anteriores preservados con Bit 7 (VINCULO_HISTORICO)\n"

    with open(log_path, "w", encoding="utf-8") as f:
        f.write(log_content)

    return log_path

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "="*70)
    print("IMPORT_CONTACTOS_BULK - DOCTRINA SOBERANA (PERSON-CENTRIC)")
    print("="*70)

    db = SessionLocal()

    try:
        # 1. AUDITORÍA DE GENOMA
        print("\n[1/5] Auditoria de Genoma...")
        ok, info = audit_genome(db)
        if not ok:
            print(f"[ERROR] FALLO: {info}")
            return
        print(f"[OK] Genoma OK: {info}")

        # 2. BUSCAR ARCHIVOS
        print("\n[2/5] Buscando archivos JSON en scripts/imports/...")
        os.makedirs(IMPORTS_DIR, exist_ok=True)
        json_files = glob.glob(os.path.join(IMPORTS_DIR, "*.json"))

        if not json_files:
            print("[WARN] No hay archivos JSON en scripts/imports/")
            return

        print(f"[OK] Encontrados {len(json_files)} archivo(s)")

        # 3. PROCESAR CADA ARCHIVO
        for json_file in json_files:
            print(f"\n{'='*70}")
            print(f"Procesando: {os.path.basename(json_file)}")
            print(f"{'='*70}")

            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                if not isinstance(json_data, list):
                    print("[ERROR] JSON debe ser un array")
                    continue
            except Exception as e:
                print(f"[ERROR] Error cargando JSON: {e}")
                continue

            # DRY RUN
            print(f"\n[3/5] DRY RUN...")
            stats = dry_run(json_data, db)

            print(f"\nAnalisis:")
            print(f"  Total registros: {stats['total']}")
            print(f"  Validos: {stats['validos']}")
            print(f"  Nuevos: {stats['nuevos']}")
            print(f"  Duplicados: {stats['duplicados']}")
            print(f"  Match exacto (100%): {stats['exacto']}")
            print(f"  Match probable (70-98%): {stats['probable']}")
            print(f"  Sin vinculo (huerfano): {stats['huerfano']}")
            print(f"  Errores: {stats['errores_parse']}")

            if stats['empresas_pendientes']:
                print(f"\nEmpresas no encontradas:")
                for empresa in sorted(stats['empresas_pendientes']):
                    print(f"  - {empresa}")

            if stats['preview']:
                print(f"\nPREVIEW (primeros 3):")
                for i, prev in enumerate(stats['preview'], 1):
                    print(f"  {i}. {prev['nombre']}")
                    if prev['email']:
                        print(f"     Email: {prev['email']} {prev['estado']}")
                    if prev['empresa']:
                        print(f"     Empresa: {prev['empresa']} {prev['vinculo']}")
                    if prev['cargo']:
                        print(f"     Cargo: {prev['cargo']}")

            # Pedir confirmación
            print(f"\n[4/5] Confirmacion...")
            print(f"Se insertaran:")
            print(f"  - {stats['nuevos']} contactos nuevos")
            print(f"  - {len(stats['empresas_pendientes'])} empresas pendientes")

            confirm = input("\nProceder? (s/n): ").strip().lower()
            if confirm != 's':
                print("[SKIP] Operacion cancelada")
                continue

            # Pedir PIN 1974
            print(f"\n[SECURITY] BLOQUEO DE SEGURIDAD")
            pin = input("Ingresa PIN 1974 para autorizar: ")
            if pin != "1974":
                print("[ERROR] PIN incorrecto. Operacion abortada.")
                continue

            print("[OK] PIN validado. Ejecutando insercion...")

            # Ejecutar
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report = ejecutar_import(json_data, os.path.basename(json_file), db)

            # Mover archivo
            print(f"\n[5/5] Finalizando...")
            archivo_movido = mover_archivo(json_file, os.path.basename(json_file), timestamp)

            # Generar audit log
            log_path = generar_audit_log(report, os.path.basename(json_file), timestamp)

            # Mostrar reporte
            print(f"\n{'='*70}")
            print("REPORTE FINAL")
            print(f"{'='*70}")
            print(f"Archivo: {report['archivo']}")
            print(f"Exitosos: {report['exitosos']}")
            print(f"  - Nuevas personas: {report['nuevas_personas']}")
            print(f"  - Personas existentes (nueva empresa): {report['personas_existentes']}")
            print(f"Duplicados saltados: {report['duplicados_saltados']}")
            print(f"Sin vinculo: {report['sin_vinculo']}")
            print(f"Errores: {len(report['errores'])}")

            if report['empresas_pendientes']:
                print(f"\nEmpresas pendientes de vinculo:")
                for empresa, count in sorted(report['empresas_pendientes'].items()):
                    print(f"  - {empresa}: {count} contacto(s)")

            print(f"\nArchivo procesado movido a:")
            print(f"  {archivo_movido}")
            print(f"\nAudit log generado en:")
            print(f"  {log_path}")
            print(f"\n[SUCCESS] IMPORT COMPLETADO")

    finally:
        db.close()

if __name__ == "__main__":
    main()
