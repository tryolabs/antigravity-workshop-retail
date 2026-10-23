# Playbook de Prompts del Laboratorio 03: Servidor MCP de Retail y Hooks Deterministas de Margen

Copia y pega estos prompts en **Google Antigravity** a medida que avanzas en el Laboratorio 03. Cada sección incluye prompts diseñados tanto para el **Track Técnico** como para el **Track Comercial / Merchandising**.

---

## Fase 1: Descubrimiento e Inspección de Arquitectura

### Prompt 1A — Track Técnico: Inspeccionar el Servidor MCP Inicial y el Script del Hook
```text
Lee @mcp_server/retail_mcp.py, @scripts/margin_guard_hook.py y @tests/test_lab03_mcp_hooks.py.
Resume:
1. Cómo las dos herramientas MCP existentes (`query_true_atp_inventory` y `audit_vendor_otif_contracts`) se conectan a `data/retail_pulse.db` y a nuestra capa de servicios.
2. Qué campos JSON exactos deben devolver `simulate_promo_margin_guard` y `list_at_risk_vip_orders` para pasar `tests/test_lab03_mcp_hooks.py`.
3. Cómo `scripts/margin_guard_hook.py` inspecciona los payloads `PreToolUse` en stdin y escribe eventos de cumplimiento en `data/logs/hook_compliance_audit.jsonl`.
```

### Prompt 1B — Track Comercial / Operaciones: Comprender MCP en Vivo vs. Hooks Deterministas
```text
Lee @mcp_server/retail_mcp.py y @scripts/margin_guard_hook.py. Explica en términos comerciales de retail:
1. Cómo las 4 herramientas MCP permiten a un gerente de Merchandising o Supply Chain consultar en vivo el stock True ATP, los contratos OTIF en incumplimiento, el impacto promocional en márgenes y los pedidos VIP en riesgo sin escribir SQL.
2. Por qué combinamos nuestras directrices en `.agents/rules/retail-standards.md` con un hook determinista `PreToolUse` (`scripts/margin_guard_hook.py`) que bloquea cualquier intento de desactivar el piso de margen del 15%.
```

---

## Fase 2: Planificación (`/plan`)

### Prompt 2 — Crear un Plan de Implementación para Herramientas MCP y Hooks de Ciclo de Vida
```text
/plan Diseña la implementación del Laboratorio 03 para que pasen las 5 pruebas en @tests/test_lab03_mcp_hooks.py:
1. Implementar `simulate_promo_margin_guard(promo_code: str, category: str = "", loyalty_tier: str = "SILVER") -> str` y `list_at_risk_vip_orders(loyalty_tier: str = "DIAMOND", limit: int = 20) -> str` en @mcp_server/retail_mcp.py.
2. Crear `.agents/mcp_config.json` registrando `retail-pulse-mcp` usando `.venv/bin/python -m mcp_server.retail_mcp`.
3. Crear `.agents/hooks.json` registrando `.venv/bin/python scripts/margin_guard_hook.py` como un hook `PreToolUse` para `write_file|edit_file|replace_file_content`.
```

---

## Fase 3: Edición en Línea (`Cmd+I` / `Ctrl+I`)

Abre `mcp_server/retail_mcp.py`, selecciona las funciones stub `simulate_promo_margin_guard` y `list_at_risk_vip_orders`, presiona `Cmd+I` (macOS) o `Ctrl+I` (Windows/Linux) e ingresa:

```text
Implementa `simulate_promo_margin_guard` usando `evaluate_sku_promo` de `src.services.promo_pricing` (con `enforce_floor=True`) para que devuelva JSON con `promo_code`, `loyalty_tier`, `category_filter`, `total_skus_evaluated`, `floor_violations_count`, `requires_vp_merchandising_override` y `skus`. Luego implementa `list_at_risk_vip_orders` consultando `omnichannel_orders` donde `status = 'AT_RISK_STOCKOUT'` ordenado por `customer_ltv_usd DESC`, devolviendo JSON con `loyalty_tier_filter`, `count`, `total_ltv_exposed_usd` y `orders`.
```

---

## Fase 4: Prompts de Implementación Completa

### Prompt 4A — Implementar `mcp_server/retail_mcp.py`, `.agents/mcp_config.json` y `.agents/hooks.json`
```text
Completa el Laboratorio 03 realizando los siguientes cambios:
1. En @mcp_server/retail_mcp.py:
   - Implementa `simulate_promo_margin_guard(promo_code: str, category: str = "", loyalty_tier: str = "SILVER") -> str` consultando `wms_inventory` para los SKUs distintos (filtrados por `category` si se proporciona), llamando a `evaluate_sku_promo(conn, sku, promo_code=promo_code, loyalty_tier=loyalty_tier, enforce_floor=True)` y devolviendo JSON con `promo_code`, `loyalty_tier`, `category_filter`, `total_skus_evaluated`, `floor_violations_count`, `requires_vp_merchandising_override` y `skus`.
   - Implementa `list_at_risk_vip_orders(loyalty_tier: str = "DIAMOND", limit: int = 20) -> str` consultando `omnichannel_orders` donde `status = 'AT_RISK_STOCKOUT'` (y `customer_loyalty_tier = ?` a menos que `loyalty_tier.upper() == "ALL"`), ordenado por `customer_ltv_usd DESC LIMIT ?`, y devolviendo JSON con `loyalty_tier_filter`, `count`, `total_ltv_exposed_usd` y `orders`.
2. Crea `.agents/mcp_config.json` con una entrada `mcpServers` para `retail-pulse-mcp` ejecutando `.venv/bin/python -m mcp_server.retail_mcp`.
3. Crea `.agents/hooks.json` con un hook `PreToolUse` que coincida con `write_file|edit_file|replace_file_content` y ejecute `.venv/bin/python scripts/margin_guard_hook.py`.
```

---

## Fase 5: Verificación y Consultas MCP en Vivo

### Prompt 5A — Ejecutar la Verificación Automatizada (`verify.sh`)
```text
Ejecuta `./labs/lab-03-mcp-and-hooks/verify.sh`, confirma que las 5 pruebas en `tests/test_lab03_mcp_hooks.py` pasen y muestra la última entrada en `data/logs/hook_compliance_audit.jsonl`.
```

### Prompt 5B — Track Comercial: Consultar las Herramientas MCP de Retail para Insights Ejecutivos
```text
Usando las funciones en @mcp_server/retail_mcp.py, responde estas tres preguntas comerciales:
1. Si acumulamos la promoción `VIP-EXTRA-15` para miembros `DIAMOND` en la categoría `Electronics`, ¿cuántos SKUs activan el límite del piso de margen del 15%?
2. ¿Cuántos pedidos VIP `DIAMOND` están actualmente en estado `AT_RISK_STOCKOUT` y cuál es el Customer LTV total expuesto?
3. ¿Qué proveedores en incumplimiento tienen un puntaje OTIF inferior al 85% y cuál es su penalización combinada por chargeback en USD?
```

---

## Fase 6: Desafío Adicional — Probar el Hook de Margen ante Prompts Adversarios

### Prompt 6 — Intentar Evadir el Piso de Margen del 15% (Observar el Bloqueo del Hook)
```text
Simula una solicitud no autorizada: prueba ejecutar `scripts/margin_guard_hook.py` contra un payload que intente editar `src/services/promo_pricing.py` con `enforce_floor=False`, y otro payload que intente establecer `"minimum_margin_pct": 0.05`. Muestra los códigos de salida del hook, los mensajes en stderr y las entradas registradas en `data/logs/hook_compliance_audit.jsonl`.
```
