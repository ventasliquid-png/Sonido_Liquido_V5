
==================== REPORTE FORENSE ====================

De acuerdo con el manual proporcionado de Buenos Aires Software (BAS) Discovery Easy Soft, el análisis enfocado en la entidad "CLIENTES" y sus campos asociados nos permite construir la siguiente tabla comparativa:

| CAMPO DETECTADO (BAS) | ¿PARA QUÉ SERVÍA? | PROPUESTA MIGRACIÓN V5 (Tu sugerencia) |
|---|---|---|
| Código | Identificador único del cliente. | Mantener como identificador principal del cliente en V5. Considerar si es numérico o alfanumérico para definir el tipo de dato en V5. |
| Nombre | Nombre del cliente. | Campo "Nombre" en V5.  |
| Domicilio | Dirección física del cliente. | Desglosar en: Calle, Número, Piso, Departamento, Localidad, Código Postal. |
| Cód. Postal | Código postal del cliente. | Integrar dentro de los campos de "Domicilio" en V5. |
| Teléfonos | Números de teléfono del cliente. | Crear una tabla relacionada "TeléfonosCliente" para almacenar múltiples teléfonos (fijo, móvil, etc.) por cliente. |
| Contacto | Nombre de la persona de contacto dentro del cliente. | Campo "ContactoPrincipal" o "NombreContacto" en V5. |
| Entregac (En control de Calidad) |  Indicador de si las entregas al cliente están bajo control de calidad. | Campo booleano "RequiereControlCalidad" en V5. |
| Zona fiscal | Zona fiscal a la que pertenece el cliente. | Referencia a una tabla "ZonasFiscales" en V5.  |
| Nombre de Fantasia | Nombre comercial del cliente. | Campo "NombreComercial" en V5. |
| Categoría de IVA | Régimen fiscal del cliente (Responsable Inscripto, Monotributo, etc.). | Referencia a una tabla "RegimenesFiscales" en V5. |
| Id. Impositiva Tipo | Tipo de identificación impositiva (CUIT, DNI, etc.). |  Referencia a una tabla "TiposIdentificacion" en V5.  |
| Número | Número de identificación impositiva. | Campo "NroIdentificacion" en V5. |
| Otros Impuestos |  Otros impuestos a los que está sujeto el cliente. |  Tabla relacionada "ImpuestosCliente" para almacenar múltiples impuestos por cliente. |
| Ref. Contable ($) | Referencia contable en pesos. |  Campo "CuentaContablePesos" en V5, enlazado con el plan de cuentas. |
| Ref. Contable (U$S) | Referencia contable en dólares. | Campo "CuentaContableDolares" en V5, enlazado con el plan de cuentas. |
| Depósito | Depósito predeterminado para el cliente. | Referencia a una tabla "Depositos" en V5. |
| Condición de venta | Plazo de pago predeterminado (Contado, 30 días, etc.). | Referencia a una tabla "CondicionesDeVenta" en V5. |
| Tipo de cliente | Clasificación interna del tipo de cliente. | Referencia a una tabla "TiposCliente" en V5. |
| Descuento 1 (%) | Descuento porcentual predeterminado 1. | Campo "Descuento1" en V5. |
| Tipo de bonificación | Permite definir que tipos de descuentos tiene el cliente | Crear tabla relacionada "Bonificaciones" para almacenar los diferentes tipos de bonificaciones que el cliente puede tener. |
| Descuento 2 (%) | Descuento porcentual predeterminado 2. | Campo "Descuento2" en V5. |
| Vendedor | Vendedor asignado al cliente. | Referencia a una tabla "Vendedores" en V5. |
| Crédito máximo | Límite de crédito asignado al cliente. | Campo "LimiteCredito" en V5. |
| Cobrador | Cobrador asignado al cliente. | Referencia a una tabla "Cobradores" en V5. |
| Enviar FC | Indicador de si se le debe enviar factura al cliente. | Campo booleano "EnviarFactura" en V5. |
| Lista de precios | Lista de precios predeterminada para el cliente. | Referencia a una tabla "ListasDePrecios" en V5. |
| Transportista | Transportista predeterminado para el cliente. | Referencia a una tabla "Transportistas" en V5. |
| Mail facturación | Dirección de correo electrónico para el envío de facturas. | Campo "EmailFacturacion" en V5. |
| Activo |  Indicador de si el cliente está activo. | Campo booleano "Activo" en V5. |
| Motivo | Motivo por el que el cliente está inactivo. | Campo "MotivoInactivo" en V5. |
| Habilitado hasta | Fecha hasta la que está habilitado el cliente. |  Campo "FechaHabilitacionHasta" en V5. |

**Reglas de Negocio Implícitas:**

*   **Multiempresa:** El sistema soporta múltiples empresas. Esto implica que la información del cliente debe estar asociada a una empresa específica.
*   **Moneda Extranjera:** Las cuentas corrientes pueden administrarse en moneda local y extranjera. Esto sugiere que hay campos relacionados con el tipo de cambio.
*   **Control de Stock:** La información del cliente se utiliza para automatizar la labor del sector de facturación, lo que implica que el sistema debe interactuar con el módulo de stock.
*   **Comisiones:** Es posible liquidar comisiones a vendedores/cobradores basados en las ventas y cobranzas.
*   **Listas de Precios:**  Cada cliente tiene asignada una lista de precios.

**Consideraciones Adicionales:**

*   El manual proporciona una visión general, pero no una descripción exhaustiva de la estructura de datos.
*   La información de "Configuración de parámetros generales" podría contener datos cruciales sobre cómo se configuran y utilizan los clientes.
*   Es importante analizar la documentación de la base de datos (si existe) para obtener una comprensión completa de la estructura y relaciones.

Espero que esta información sea útil.
