# Laboratorio 03: Servidor MCP de Retail, Hooks Deterministas de Margen y Gobernanza de Seguridad Empresarial

**Duración**: 45 Minutos | **Perfil**: Track Técnico y Comercial | **Prerrequisitos**: Laboratorio 02 Completado

---

## 1. Escenario de Retail y Contexto de Negocio

Incluso después de codificar reglas y skills (Laboratorio 02), persisten dos grandes desafíos operativos en una organización empresarial de retail:

1. **Conexión en Vivo a Sistemas mediante Model Context Protocol (MCP)**:
   Ni los ingenieros ni los gerentes comerciales de categoría desean copiar y pegar consultas SQL o archivos CSV en ventanas de chat. En su lugar, Antigravity debe consultar directamente la base de datos en vivo `data/retail_pulse.db` mediante herramientas estructuradas de **Model Context Protocol (MCP)** para inspeccionar el True ATP por nodo, auditar contratos OTIF de proveedores en incumplimiento, simular márgenes promocionales antes de su lanzamiento y listar pedidos VIP en riesgo de quiebre de stock.
2. **Guardrails Deterministas y Gobernanza Empresarial**:
   Las instrucciones en `.agents/rules/` guían el razonamiento del LLM, pero el cumplimiento de misión crítica —como bloquear que alguien desactive `enforce_floor=False` en `src/services/promo_pricing.py` o codifique `minimum_margin_pct` por debajo de `0.15` (`15%`)— requiere **ejecución determinista** fuera de la salida probabilística del LLM, junto con **gobernanza en Google Cloud / Gemini Enterprise** y **controles de Sandbox y Permisos del cliente Antigravity**.

---

## 2. Objetivos de Aprendizaje

En este laboratorio lograrás:
1. Completar el **Servidor FastMCP de Retail Pulse** (`mcp_server/retail_mcp.py`) implementando dos herramientas MCP de alto impacto:
   - `simulate_promo_margin_guard`: Simula la aplicación acumulada de una campaña promocional sobre un SKU o categoría e informa si algún SKU incumple su piso mínimo de margen.
   - `list_at_risk_vip_orders`: Consulta `omnichannel_orders` para pedidos `AT_RISK_STOCKOUT` filtrados por nivel de lealtad (`DIAMOND`, `GOLD`) y los ordena por Customer Lifetime Value (`customer_ltv_usd`).
2. Registrar el servidor MCP local en `.agents/mcp_config.json` para que Antigravity descubra e invoque automáticamente las 4 herramientas MCP de retail.
3. Configurar un hook determinista de ciclo de vida `PreToolUse` en `.agents/hooks.json` respaldado por `scripts/margin_guard_hook.py` que intercepta cualquier llamada a `write_file` / `edit_file` que viole el piso de margen del 15% y escribe un registro de auditoría inmutable en `data/logs/hook_compliance_audit.jsonl`.
4. Recorrer la arquitectura de **Gobernanza de Google Cloud & Gemini Enterprise** y los **Controles de Seguridad del Cliente y Workspace de Antigravity** para despliegues empresariales de retail.

---

## 3. Instrucciones Paso a Paso

### Paso 1: Inicializar el Estado Inicial del Laboratorio 03

Ejecuta el instalador del Laboratorio 03 para asegurar que las soluciones de los Laboratorios 01 y 02 estén activas y cargar los archivos iniciales del Laboratorio 03:

```bash
./labs/lab-03-mcp-and-hooks/install.sh
```

Verifica que la suite de pruebas del Laboratorio 03 falle inicialmente en las herramientas MCP aún no implementadas y los archivos faltantes `.agents/mcp_config.json` / `.agents/hooks.json`:

```bash
./labs/lab-03-mcp-and-hooks/verify.sh
```

---

### Paso 2: Inspeccionar el Servidor MCP Inicial (`mcp_server/retail_mcp.py`)

Abre `mcp_server/retail_mcp.py`. Observa que dos herramientas MCP ya están implementadas:
- `query_true_atp_inventory(sku: str = "", category: str = "") -> str`
- `audit_vendor_otif_contracts(only_breaching: bool = True) -> str`

Sin embargo, dos herramientas son actualmente stubs que devuelven `{"status": "NOT_IMPLEMENTED"}`:
- `simulate_promo_margin_guard(promo_code: str, category: str = "", loyalty_tier: str = "SILVER") -> str`
- `list_at_risk_vip_orders(loyalty_tier: str = "DIAMOND", limit: int = 20) -> str`

---

### Paso 3: Implementar las Herramientas MCP Restantes y Registrar `.agents/mcp_config.json`

Abre `labs/lab-03-mcp-and-hooks/PROMPTS.es.md` y utiliza los **Prompts de Implementación** (o **Edición en Línea `Cmd+I` / `Ctrl+I`**) para:
1. Implementar `simulate_promo_margin_guard` en `mcp_server/retail_mcp.py` para que evalúe todos los SKUs de la categoría solicitada contra el `promo_code` y `loyalty_tier` usando `evaluate_sku_promo()`, devolviendo `total_skus_evaluated`, `floor_violations_count`, `requires_vp_merchandising_override` y el detalle por SKU (`sku`, `product_name`, `unit_cost_usd`, `msrp_usd`, `effective_price_usd`, `margin_pct`, `minimum_margin_pct`, `floor_clamped`).
2. Implementar `list_at_risk_vip_orders` en `mcp_server/retail_mcp.py` para que consulte `omnichannel_orders` donde `status = 'AT_RISK_STOCKOUT'` y `customer_loyalty_tier = loyalty_tier` (o todos los niveles si `loyalty_tier == "ALL"`), ordenados por `customer_ltv_usd DESC`, devolviendo `count`, `total_ltv_exposed_usd` y `orders`.
3. Crear `.agents/mcp_config.json` registrando el servidor `retail-pulse-mcp` mediante `.venv/bin/python -m mcp_server.retail_mcp`.

---

### Paso 4: Configurar el Hook Determinista `PreToolUse` de Protección de Margen (`.agents/hooks.json`)

Inspecciona `scripts/margin_guard_hook.py`. Este script lee el payload de la llamada a herramienta desde `stdin` antes de que ocurra cualquier modificación de archivo:
- Si una llamada a herramienta intenta establecer `enforce_floor=False` o `enforce_floor = False` dentro de `src/services/promo_pricing.py`, o establece `"minimum_margin_pct"` por debajo de `0.15`, el hook finaliza con código de salida `2` (`BLOCKED`) e imprime un mensaje claro de incumplimiento en `stderr`.
- Cada evaluación del hook (`ALLOW` o `BLOCK`) se agrega como un evento JSON estructurado en `data/logs/hook_compliance_audit.jsonl`.

Crea `.agents/hooks.json` para conectar `scripts/margin_guard_hook.py` al evento de ciclo de vida `PreToolUse` para `write_file`, `edit_file` y `replace_file_content`.

Prueba el hook directamente desde la terminal para verificar tanto el bloqueo como el registro en el log de auditoría:

```bash
echo '{"tool_name":"edit_file","tool_input":{"Path":"src/services/promo_pricing.py","Replacement":"enforce_floor=False"}}' | .venv/bin/python scripts/margin_guard_hook.py
cat data/logs/hook_compliance_audit.jsonl
```

---

## 4. Inmersión Profunda en Seguridad, Privacidad y Gobernanza Empresarial

Al desplegar Antigravity en una empresa de retail (merchandising, cadena de suministro, operaciones en tienda e ingeniería de plataforma), los arquitectos de seguridad gobiernan la plataforma en **dos capas complementarias**:

```
+-----------------------------------------------------------------------------------+
| CAPA 1: Gobernanza en Google Cloud & Gemini Enterprise (Plano de Admin Cloud)     |
|  - IAM e Identidad: roles/cloudaicompanion.user vía Cloud Identity / SSO Corp     |
|  - Cloud Audit Logs: cloudaicompanion.googleapis.com en Google Cloud Logging      |
|  - Privacidad: Cero Retención de Datos y Sin Entrenamiento con prompts/código     |
|  - Perímetro de Red: VPC Service Controls (VPC-SC) y Endpoints Regionales         |
|  - Protección IP: Indemnización de Google Cloud y Filtros de Citación             |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| CAPA 2: Controles de Seguridad del Cliente y Workspace Antigravity (Plano Local)  |
|  - Política de Ejecución: strict | request-review | proceed-in-sandbox            |
|  - Sandbox de Terminal y Aislamiento de Red: Sandboxing a nivel de SO             |
|  - Acceso a Archivos Fuera del Workspace: Restricción estricta al repositorio     |
|  - Lista Blanca/Negra de Comandos y Lista Blanca del Navegador                    |
|  - Hooks Deterministas de Ciclo de Vida: .agents/hooks.json -> auditoría JSONL    |
+-----------------------------------------------------------------------------------+
```

### Capa 1: Gobernanza en Google Cloud & Gemini Enterprise

| Área de Control | Capacidad en Google Cloud / Gemini Enterprise | Caso de Uso en Retail Empresarial |
| :--- | :--- | :--- |
| **IAM y Gestión de Licencias** | Asignar `roles/cloudaicompanion.user` mediante Google Cloud IAM integrado con grupos SSO de **Cloud Identity / Okta / Azure AD (Entra ID)**. | Otorgar acceso diferenciado a `retail-platform-eng@` y `retail-commercial-ops@` con alta/baja centralizada. |
| **Cloud Audit Logging** | Habilitar logs de auditoría **Admin Activity** y **Data Access** para `cloudaicompanion.googleapis.com` en **Google Cloud Logging**, y enrutarlos mediante Log Sinks a BigQuery o Chronicle SIEM. | Mantener una pista de auditoría empresarial inmutable de quién invocó Gemini Enterprise, desde qué IP/dispositivo y cuándo. |
| **Privacidad de Datos y Cero Entrenamiento** | Los prompts de clientes, contexto del workspace, esquemas SQL y código generado **nunca se utilizan para entrenar modelos fundacionales compartidos** y cumplen garantías de cero retención fuera de tu tenant. | Analizar de forma segura contratos confidenciales de proveedores (`data/exports/vendor_contracts.csv`), costos unitarios mayoristas y LTV de clientes VIP. |
| **VPC Service Controls (VPC-SC)** | Ubicar `cloudaicompanion.googleapis.com` dentro de un **perímetro de VPC Service Controls** junto con BigQuery, Cloud SQL y Secret Manager, con fijación de endpoints regionales. | Prevenir la exfiltración de datos desde estaciones de trabajo corporativas o redes externas no autorizadas. |

### Capa 2: Controles de Seguridad del Cliente y Workspace de Antigravity

| Configuración / Hook del Cliente | Opciones de Configuración | Configuración Recomendada en Producción Retail |
| :--- | :--- | :--- |
| **Política de Ejecución de Herramientas** | `strict`, `request-review`, `proceed-in-sandbox`, `always-proceed` | Usar `proceed-in-sandbox` o `request-review` para que los comandos mutantes requieran sandboxing del SO o aprobación humana. |
| **Sandbox de Terminal y Política de Red** | Sandbox a nivel de SO (`sandbox-exec` en macOS / namespaces en Linux) + Interruptor de Acceso a Internet | Habilitar el Sandbox de Terminal y restringir llamadas de red externas para alcanzar solo endpoints internos aprobados. |
| **Acceso a Archivos Fuera del Workspace** | Bloquear o requerir confirmación para lecturas/escrituras fuera de la raíz del workspace | **Bloquear** el acceso fuera del workspace para impedir lecturas de `~/.ssh`, `~/.aws` u otros directorios del host. |
| **Lista Blanca / Negra de Comandos** | Lista blanca de prefijos (`pytest`, `.venv/bin/python`) y lista negra (`rm -rf`, `curl`, `nc`) | Permitir `.venv/bin/python -m pytest` para TDD autónomo bloqueando comandos destructivos o de exfiltración. |
| **Lista Blanca del Navegador** | Lista blanca de dominios para el subagente `/browser` | Restringir `/browser` estrictamente a `http://127.0.0.1:8000` y dashboards internos aprobados. |
| **Hooks Deterministas de Ciclo de Vida** | `.agents/hooks.json` (`PreToolUse`, `PostToolUse`) | Hacer cumplir invariantes comerciales y de seguridad (como `scripts/margin_guard_hook.py`) y registrar cada verificación en `data/logs/hook_compliance_audit.jsonl`. |

---

## 5. Lista de Verificación

Ejecuta el script de verificación del Laboratorio 03 para confirmar que tus herramientas MCP, `.agents/mcp_config.json` y `.agents/hooks.json` pasan todas las pruebas automatizadas:

```bash
./labs/lab-03-mcp-and-hooks/verify.sh
```

Resultado esperado:
- `tests/test_lab03_mcp_hooks.py` pasa **5/5 pruebas**:
  - `test_mcp_query_true_atp_inventory`
  - `test_mcp_audit_vendor_otif_contracts`
  - `test_mcp_simulate_promo_margin_guard`
  - `test_mcp_list_at_risk_vip_orders`
  - `test_mcp_config_and_margin_guard_hook`

> ¿Necesitas saltar directamente al estado verificado? Ejecuta `./labs/lab-03-mcp-and-hooks/apply_solution.sh`.
