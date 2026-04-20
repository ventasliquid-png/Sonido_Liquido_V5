# INFORME TÉCNICO V5 — SESIÓN 2026-04-19
**Asunto**: Siembra de Contactos Person-Centric + Purga Total de PostgreSQL Externo.  
**Estado**: **NOMINAL GOLD**.  
**Protocolo**: Omega Closure (PIN 1974).  
**Agente**: Claude Code (Sonnet 4.6)  
**Entorno**: OF  

---

## 1. RESUMEN EJECUTIVO

Sesión de dos bloques. Primer bloque: diagnóstico y eliminación de referencias a bases de datos externas en la nube que impedían la ejecución de scripts locales. Segundo bloque: ejecución exitosa de la siembra masiva de 10 contactos bajo arquitectura Person-Centric con Genoma 64-bit.

El sistema emergió con soberanía total — sin dependencias a Google Cloud, PostgreSQL ni servicios externos. Los 10 contactos están en la DB local con trazabilidad completa en `notas_sistema`.

---

## 2. HITOS ALCANZADOS

### A. PURGA POSTGRESQL — SOBERANÍA LOCAL

**Diagnóstico forense de tres capas:**

| Capa | Fuente | URL |
|---|---|---|
| 1 (raíz) | Variable sistema Windows `HKCU\Environment` | `postgresql://...Spawn8559@34.95.172.190` |
| 2 | `backend/.env` | `postgresql://...SonidoV5_2025@104.197.57.226` |
| 3 | `backend/.env.bak`, `.env.postgres_fail` | Credenciales legacy |

La capa 1 era la causa raíz: cualquier proceso Python heredaba `DATABASE_URL` del sistema operativo, pisando `.env` y fallbacks de `database.py`. El script `import_contactos_bulk.py` se colgaba indefinidamente intentando conectar a `34.95.172.190` que ya no responde.

**Resolución:**
- Capa 1: `[System.Environment]::SetEnvironmentVariable('DATABASE_URL', $null, 'User')` — eliminada del registro
- Capa 2: `backend/.env` reescrito → solo `DATABASE_URL=sqlite:///./pilot_v5x.db`
- Capa 3: archivos eliminados

**Defensa instalada en `import_contactos_bulk.py`:**
```python
# Carga .env local, rechaza cualquier postgres
from dotenv import load_dotenv
load_dotenv(os.path.join(root_dir, ".env"), override=True)
if "postgresql" in os.environ.get("DATABASE_URL", ""):
    os.environ["DATABASE_URL"] = f"sqlite:///{sqlite_path}"
```
El script es ahora inmune a contaminación de entorno.

---

### B. REPARACIÓN DE MAPPERS SQLALCHEMY

Tres modelos tenían relaciones con `relationship("Clase")` (string) sin el import explícito de la clase referenciada. SQLAlchemy falla al inicializar el mapper si la clase no está en el registro ORM al momento de la primera query.

| Modelo | Import agregado | Relación resuelta |
|---|---|---|
| `backend/clientes/models.py` | `EmpresaTransporte` | `transporte_habitual` |
| `backend/clientes/models.py` | `Pedido` | `pedidos` |
| `backend/pedidos/models.py` | `Producto` | `PedidoItem.producto` |

**Fix adicional:** `backend/contactos/models.py` — campo `notas_sistema = Column(Text, nullable=True)` agregado para segregar notas de auditoría del script de notas operativas del usuario.

**Migración SQLite:**
```sql
ALTER TABLE personas ADD COLUMN notas_sistema TEXT DEFAULT NULL;
```

---

### C. SIEMBRA DE CONTACTOS PERSON-CENTRIC

**Archivo:** `contactos_siembra_gmail_20260419_01.json` — 10 registros extraídos vía Gemini de la cantera Gmail.

**Arquitectura Person-Centric aplicada:**
- Persona = entidad constante (identificada por email)
- Empresa = trayectoria (vínculo con `cliente_id`)
- Si la persona existe con otra empresa → nuevo vínculo + Bit 7 (VINCULO_HISTORICO) en el vínculo anterior

**Resultado de la ejecución:**

| Métrica | Valor |
|---|---|
| Personas nuevas | 10 |
| Vínculos creados | 7 |
| Exacto (100% fuzzy) | 2 |
| Probable (70-98%) | 5 |
| Sin vínculo (ENTIDAD_PENDIENTE) | 3 |
| Duplicados saltados | 0 |
| Errores | 0 |

**Genoma insertado:**

| Contacto | Empresa | flags_estado | Bits |
|---|---|---|---|
| María Emilia Garrido | PANALAB S A ARGENTINA | 16 | Bit5 |
| Joshua Sosa | PANALAB S A ARGENTINA | 16 | Bit5 |
| Marcelo Massel | LAVIMAR S A | 48 | Bit5+Bit6 |
| Agustina Verea | LAVIMAR S A | 48 | Bit5+Bit6 |
| Matias E. Castelo | ALFAJORES JORGITO S A | 48 | Bit5+Bit6 |
| Carolina Papatanasi | ALFAJORES JORGITO S A | 48 | Bit5+Bit6 |
| Vanesa Vinciguerra | ALFAJORES JORGITO S A | 48 | Bit5+Bit6 |
| Sebastián Fiorito | [ENTIDAD_PENDIENTE: Rizobacter] | 16 | Bit5 |
| Facundo Ardissone | [ENTIDAD_PENDIENTE: Rizobacter/Bioceres] | 16 | Bit5 |
| Ignacio Gonzalo | [ENTIDAD_PENDIENTE: Rizobacter/Bioceres Crops] | 16 | Bit5 |

**`notas_sistema` por registro** (ejemplo):
```
[ORIGEN: Siembra Digital 2026-04-19] [Fuzzy Match: 77% (Probable)] [Cargo Detectado: Compras] [EMPRESA: LAVIMAR S A]
```

---

### D. LIMPIEZA DE LASTRE

Eliminados scripts y archivos que dependían de Google Cloud y no tenían función local:

| Archivo | Motivo |
|---|---|
| `backend/scripts/ingest_memory.py` | Google Vertex AI + PostgreSQL |
| `backend/config.py` | Generado durante debugging de ingest_memory |
| `backend/data/fenix.txt`, `informe43.txt`, `clientes.txt`, `integridad.txt` | Doctrina placeholder sin función |
| `atenea_memory.db` | DB SQLite creada por ingest_memory |

---

## 3. MÉTRICAS DE SESIÓN

| Métrica | Valor |
|---|---|
| Archivos modificados (D) | 5 (`models.py` ×3, `.env`, `import_contactos_bulk.py`) |
| Archivos eliminados | 6 |
| Personas insertadas en DB | 10 |
| Vínculos insertados en DB | 7 |
| Variables de sistema limpiadas | 1 (Windows registry) |
| URLs postgres eliminadas | 3 (sistema + .env + .env.bak) |

---

## 4. ESTADO DEL SISTEMA AL CIERRE

```
DATABASE_URL activa:  sqlite:///C:\dev\Sonido_Liquido_V5\pilot_v5x.db
Conexiones externas:  NINGUNA
Dependencias nube:    NINGUNA
personas (CANTERA):   10 nuevas (flags & 16 > 0)
vinculos:             7 nuevos
ENTIDAD_PENDIENTE:    3 (Rizobacter*)
```

**Próximas acciones sugeridas:**
1. Crear empresa "Rizobacter / Bioceres" en el sistema → vincular 3 contactos pendientes
2. Verificar Canario ALFA en próxima sesión
3. Continuar siembra con próximos JSONs de la cantera Gmail

---

## 5. CONCLUSIÓN

La sesión resolvió un problema sistémico silencioso que venía de sesiones anteriores: el sistema nunca fue "local" en la práctica porque una variable de entorno de Windows saboteaba cada arranque. La purga fue quirúrgica — tres capas identificadas, tres capas eliminadas, una defensa instalada.

La siembra de contactos funcionó exactamente como fue diseñada: Person-Centric, con Genoma auditado, notas segregadas y listo para escalar.

---
*Informe generado por Claude Code (Sonnet 4.6) — OF — 2026-04-19*
