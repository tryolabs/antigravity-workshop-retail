<p align="center">
  <img src="../../src/static/tryolabs-logo.png" alt="Tryolabs Logo" width="180" />
</p>

# Playbook de Prompts del Laboratorio 03: Servidor MCP de Retail y Hooks Deterministas de Margen

> **Idioma / Language:** [Español](./PROMPTS.es.md) | [English](./PROMPTS.md) • **Guía del Lab:** [README.es.md](./README.es.md) | [README.md](./README.md) • **PDF:** [ES](./LAB_03_INSTRUCTIONS_ES.pdf) | [EN](./LAB_03_INSTRUCTIONS_EN.pdf)

Copia y pega estos prompts en **Google Antigravity** a medida que avanzas en el Laboratorio 03. Cada sección incluye prompts diseñados tanto para el **Track Técnico** como para el **Track Comercial / Merchandising**.

---

## Fase 1: Descubrimiento e Inspección de Arquitectura

### Prompt 1A — Track Técnico: Inspeccionar el Servidor MCP Inicial y el Script del Hook
```text
Lee @mcp_server/retail_mcp.py, @scripts/margin_guard_hook.py y @tests/test_lab03_mcp_hooks.py.
Resume:
1. Cómo la herramienta MCP inicial (`query_true_atp_inventory`) se conecta a `data/retail_pulse.db` y a nuestra capa de servicios.
2. Qué campos JSON exactos deben devolver `audit_vendor_otif_contracts`, `simulate_promo_margin_guard` y `list_at_risk_vip_orders` para pasar `tests/test_lab03_mcp_hooks.py`.
3. Cómo `scripts/margin_guard_hook.py` inspecciona los payloads `--phase pre` (`PreToolUse`) y `--phase post` (`PostToolUse`) en stdin y escribe eventos de cumplimiento en `data/logs/hook_compliance_audit.jsonl`.
```

### Prompt 1B — Track Comercial / Operaciones: Comprender MCP en Vivo vs. Hooks Deterministas
```text
Lee @mcp_server/retail_mcp.py y @scripts/margin_guard_hook.py. Explica en términos comerciales de retail:
1. Cómo las 4 herramientas MCP permiten a un gerente de Merchandising o Supply Chain consultar en vivo el stock True ATP, los contratos OTIF en incumplimiento, el impacto promocional en márgenes y los pedidos VIP en riesgo sin escribir SQL.
2. Por qué combinamos nuestras directrices en `.agents/rules/retail-standards.md` con un hook determinista `PreToolUse` (`scripts/margin_guard_hook.py`) que bloquea cualquier intento de desactivar el piso de margen del 15% o ejecutar SQL destructivo sobre `wms_inventory` y `omnichannel_orders`.
```

---

## Fase 2: Planificación (`/plan`)

### Prompt 2 — Crear un Plan de Implementación para Herramientas MCP y Hooks de Ciclo de Vida
```text
/plan Diseña la implementación del Laboratorio 03 para que pasen todas las pruebas en @tests/test_lab03_mcp_hooks.py:
1. Implementar `audit_vendor_otif_contracts(only_breaching: bool = True) -> str`, `simulate_promo_margin_guard(sku: str, qty: int = 1, promo_codes_csv: str = "") -> str` y `list_at_risk_vip_orders(loyalty_tier: str = "DIAMOND") -> str` en @mcp_server/retail_mcp.py.
2. Actualizar `.agents/mcp_config.json` registrando `retail-pulse-mcp` usando `"command": "./.venv/bin/python"` y `"args": ["mcp_server/retail_mcp.py"]`.
3. Actualizar `.agents/hooks.json` registrando `./.venv/bin/python scripts/margin_guard_hook.py --phase pre` en `PreToolUse` (`run_command|execute_command|bash|write_file|edit_file`) y `./.venv/bin/python scripts/margin_guard_hook.py --phase post` en `PostToolUse`.
```

---

## Fase 3: Edición en Línea (`Cmd+I` / `Ctrl+I`)

Abre `mcp_server/retail_mcp.py`, selecciona las funciones stub `audit_vendor_otif_contracts`, `simulate_promo_margin_guard` y `list_at_risk_vip_orders`, presiona `Cmd+I` (macOS) o `Ctrl+I` (Windows/Linux) e ingresa:

```text
Implementa `audit_vendor_otif_contracts` usando `audit_all_vendor_otif_contracts(only_breaching=only_breaching)`. Implementa `simulate_promo_margin_guard` separando `promo_codes_csv` en una lista de códigos en mayúsculas y llamando a `calculate_promotional_order_pricing(sku=sku, qty=qty, promo_codes=codes)`. Implementa `list_at_risk_vip_orders` uniendo `omnichannel_orders`, `wms_inventory` y `sku_catalog`, evaluando `evaluate_location_atp` para cada pedido y devolviendo JSON con `loyalty_tier_filter`, `at_risk_order_count`, `total_vip_ltv_at_risk_usd` y `orders`.
```

---

## Fase 4: Prompts de Implementación Completa

### Prompt 4A — Implementar `mcp_server/retail_mcp.py`, `.agents/mcp_config.json` y `.agents/hooks.json`
```text
Completa el Laboratorio 03 realizando los siguientes cambios:
1. En @mcp_server/retail_mcp.py:
   - Implementa `audit_vendor_otif_contracts(only_breaching: bool = True) -> str` devolviendo `json.dumps(audit_all_vendor_otif_contracts(only_breaching=only_breaching), indent=2)`.
   - Implementa `simulate_promo_margin_guard(sku: str, qty: int = 1, promo_codes_csv: str = "") -> str` separando `promo_codes_csv` en códigos en mayúsculas y devolviendo `json.dumps(calculate_promotional_order_pricing(sku=sku, qty=qty, promo_codes=codes), indent=2)`.
   - Implementa `list_at_risk_vip_orders(loyalty_tier: str = "DIAMOND") -> str` consultando `omnichannel_orders` unido con `wms_inventory` y `sku_catalog`, filtrando los pedidos donde `evaluate_location_atp(..., required_qty=int(row["qty"]))["oversell_risk"]` sea True (o `status == 'AT_RISK_STOCKOUT'`), y devolviendo JSON con `loyalty_tier_filter`, `at_risk_order_count`, `total_vip_ltv_at_risk_usd` y `orders`.
2. Actualiza `.agents/mcp_config.json` con una entrada `mcpServers` para `retail-pulse-mcp` ejecutando `"command": "./.venv/bin/python"` y `"args": ["mcp_server/retail_mcp.py"]`.
3. Actualiza `.agents/hooks.json` con `PreToolUse` (`./.venv/bin/python scripts/margin_guard_hook.py --phase pre`) y `PostToolUse` (`./.venv/bin/python scripts/margin_guard_hook.py --phase post`).
```

---

## Fase 5: Verificación y Consultas MCP en Vivo

### Prompt 5A — Ejecutar la Verificación Automatizada (`verify.sh`)
```text
Ejecuta `./labs/lab-03-mcp-and-hooks/verify.sh`, confirma que las 13 pruebas acumuladas de los Labs 01-03 pasen (incluyendo las 3 pruebas en `tests/test_lab03_mcp_hooks.py`) y muestra la última entrada en `data/logs/hook_compliance_audit.jsonl`.
```

### Prompt 5B — Track Comercial: Consultar las Herramientas MCP de Retail para Insights Ejecutivos
```text
Usando las funciones en @mcp_server/retail_mcp.py, responde estas tres preguntas comerciales:
1. Si acumulamos las promociones `VIP20,FLASH15,CLEARANCE10` sobre `SKU-OLED-65` (qty=1), ¿se activa el límite del piso de margen del 15% (`margin_floor_clamped`) y cuál es el precio unitario ajustado?
2. ¿Cuántos pedidos VIP `DIAMOND` están actualmente en riesgo de quiebre de stock y cuál es el Customer LTV total expuesto (`total_vip_ltv_at_risk_usd`)?
3. ¿Qué 6 proveedores en incumplimiento no alcanzan su SLA OTIF contratado y cuál es su penalización combinada por chargeback en USD (`total_chargeback_usd`)?
```

---

## Fase 6: Desafío Adicional — Probar el Hook de Margen ante Prompts Adversarios

### Prompt 6 — Intentar Evadir el Piso de Margen del 15% (Observar el Bloqueo del Hook)
```text
Simula una solicitud no autorizada: prueba ejecutar `scripts/margin_guard_hook.py --phase pre` contra un payload que intente editar `src/services/promo_pricing.py` con `margin_floor_pct = 0.0 # DISABLE_MARGIN_FLOOR`, y otro payload que intente ejecutar `DROP TABLE wms_inventory;`. Muestra los códigos de salida (`2`), las decisiones JSON `deny` y las entradas registradas en `data/logs/hook_compliance_audit.jsonl`.
```
