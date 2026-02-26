# 🦅 INFORME TÉCNICO: ESTABILIZACIÓN AFIP DUAL & IDENTIDAD (V14.6)

**Fecha:** 2026-02-26
**Sistema:** RAR_V1 + V5 Bridge
**Estado:** OPERATIVO GOLD

## 1. EL INCIDENTE (DN Mismatch)
Se detectó un bloqueo crítico en el acceso al Padrón A13 de AFIP. El sistema reportaba `Fault: DN del Source invalido`.

### Análisis Forense:
AFIP realiza una validación lexicográfica exacta de la firma digital. El error se producía por dos discrepancias:
1. **CUIT Cruzado:** Se intentaba firmar un pedido con el CUIT de la Empresa usando un certificado emitido para el CUIT Personal del usuario.
2. **Case Sensitivity:** El certificado personal está registrado con el alias `RAR_V5` (Mayúsculas), mientras que el de empresa usa `rar_v5` (Minúsculas). El código forzaba minúsculas para ambos, rompiendo la firma del certificado personal.

## 2. LA SOLUCIÓN (Identidad Dual)
Se implementó una arquitectura de conmutación de identidades en `Conexion_Blindada.py`.

* **Identidad Padrón (Usuario):** CUIT `20132967572`. Cert: `certificado_06_02_2026.crt`. Alias: `RAR_V5`.
* **Identidad Fiscal (Empresa):** CUIT `30715603973`. Cert: `certificado.crt`. Alias: `rar_v5`.

El sistema ahora detecta el servicio solicitado (Padrón vs WSMTXCA) y selecciona automáticamente el par (CUIT + Cert + Alias) correcto, asegurando una firma válida en todos los escenarios.

## 3. VERIFICACIÓN
Se ejecutaron handshakes exitosos para ambos servicios:
1. **Padrón A13:** Autorizado (CUIT 20...). Consulta exitosa de "LAVIMAR S.A.".
2. **WSMTXCA:** Autorizado (CUIT 30...). Token obtenido satisfactoriamente.

## 4. CONCLUSIÓN
El puente AFIP queda estabilizado. Se recomienda no alterar los nombres de los archivos en la carpeta `certs` para mantener la integridad de este mapping.

---
**Firma:** Agente Antigravity / Gy V14
