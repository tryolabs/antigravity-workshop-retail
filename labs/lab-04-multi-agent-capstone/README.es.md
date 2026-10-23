# Laboratorio 04: Capstone Multi-Agente — Enrutamiento Inteligente de Envíos Divididos y Centro de Comando Ejecutivo

**Duración**: 45 Minutos | **Perfil**: Track Técnico y Comercial | **Prerrequisitos**: Laboratorios 01, 02 y 03 Completados

---

## 1. Escenario de Retail y Contexto de Negocio

En los Laboratorios 01–03, tu equipo estabilizó los pisos de margen promocional, reparó el cálculo de inventario True ATP, codificó los estándares de cumplimiento de retail (`GEMINI.md`, `.agents/rules/retail-standards.md`, `.agents/skills/retail-otif-margin-auditor/SKILL.md`) y conectó Antigravity a `retail_pulse.db` mediante FastMCP y hooks deterministas `PreToolUse`.

Sin embargo, **35 pedidos VIP (niveles de lealtad `DIAMOND` y `GOLD`)** que representan **más de $250,000 en Customer Lifetime Value (LTV)** siguen retenidos en estado `AT_RISK_STOCKOUT` porque su tienda insignia original carecía de suficiente inventario True ATP.

Anteriormente, el OMS heredado simplemente cancelaba cualquier pedido cuyo nodo primario no pudiera surtirlo. Tu misión en este proyecto integrador (Capstone) es utilizar la **Orquestación Multi-Agente de Antigravity** (`/plan`, `/boost`, `/teamwork`, subagentes y `/browser`) para construir el **Motor Inteligente de Re-enrutamiento y Envíos Omnicanal** (`src/services/fulfillment_router.py`), exponerlo mediante `/api/v1/fulfillment/optimize-routing` y verificar la recuperación ejecutiva de KPIs en vivo en el **Centro de Comando de Retail Pulse**.

---

## 2. Objetivos de Aprendizaje

En este laboratorio Capstone lograrás:
1. Utilizar `/plan` y `/boost` (o subagentes paralelos con `/teamwork`) para diseñar e implementar `evaluate_candidates` y `optimize_at_risk_orders` en `src/services/fulfillment_router.py`.
2. Clasificar los nodos candidatos de cumplimiento (`DC` y `STORE`) donde `true_atp >= order_qty` según el mayor **Margen Neto Post-Envío en USD** (utilizando `shipping_zone_cost_usd` del nodo y desempatando por menor costo de envío / prioridad de `DC`).
3. Re-enrutar automáticamente los 35 pedidos VIP en `AT_RISK_STOCKOUT` al estado `REROUTED_OPTIMAL`, descontando `on_hand_qty` en el nodo ganador y preservando `$14,774.00` en margen neto post-envío.
4. Verificar la recuperación de extremo a extremo mediante `pytest` (`./labs/lab-04-multi-agent-capstone/verify.sh`) e inspeccionar visualmente el **Centro de Comando de Retail Pulse** (`http://127.0.0.1:8000`) usando `/browser`.

---

## 3. Instrucciones Paso a Paso

### Paso 1: Inicializar el Estado Inicial del Laboratorio 04

Ejecuta el instalador del Laboratorio 04 para asegurar que las soluciones de los Laboratorios 01, 02 y 03 estén aplicadas y cargar el stub inicial de `src/services/fulfillment_router.py`:

```bash
./labs/lab-04-multi-agent-capstone/install.sh
```

Ejecuta el script de verificación para observar las pruebas fallidas del Capstone (`NotImplementedError` en `evaluate_candidates` y `optimize_at_risk_orders`):

```bash
./labs/lab-04-multi-agent-capstone/verify.sh
```

---

### Paso 2: Inspeccionar los Requerimientos del Capstone

Abre `src/services/fulfillment_router.py` y `tests/test_lab04_capstone.py`.
Revisa la lógica de negocio requerida para las dos funciones en `src/services/fulfillment_router.py`:

1. **`evaluate_candidates(conn, sku, qty, effective_unit_price_usd)`**:
   - Consultar `wms_inventory` para todos los nodos que tienen el `sku`.
   - Calcular `true_atp` usando `calculate_node_atp(dict(row))` de `src.services.inventory_atp`.
   - Filtrar únicamente los nodos elegibles donde `true_atp >= qty`.
   - Para cada nodo elegible, calcular:
     - `shipping_cost_usd = round(float(row["shipping_zone_cost_usd"]), 2)`
     - `gross_margin_usd = (effective_unit_price_usd - unit_cost_usd) * qty`
     - `post_shipping_net_margin_usd = round(gross_margin_usd - shipping_cost_usd, 2)`
   - Ordenar los candidatos elegibles por:
     1. Mayor `post_shipping_net_margin_usd` (`-c["post_shipping_net_margin_usd"]`)
     2. Menor `shipping_cost_usd` (`c["shipping_cost_usd"]`)
     3. Preferencia por Centro de Distribución (`0 if c["location_type"] == "DC" else 1`)

2. **`optimize_at_risk_orders(conn, dry_run=False)`**:
   - Consultar `omnichannel_orders` donde `status = 'AT_RISK_STOCKOUT'` ordenado por `customer_ltv_usd DESC, order_id ASC`.
   - Para cada pedido, invocar `evaluate_candidates(conn, sku, qty, effective_unit_price_usd)`:
     - Seleccionar el mejor candidato (`best = candidates[0]`).
     - Si `not dry_run`:
       - Actualizar `omnichannel_orders` asignando `assigned_node_id = best["location_id"]`, `status = 'REROUTED_OPTIMAL'` y `fulfillment_notes` con una nota de auditoría clara que incluya `best["location_id"]` y `best["post_shipping_net_margin_usd"]`.
       - Descontar `on_hand_qty = on_hand_qty - qty` en `wms_inventory` para `(sku, best["location_id"])`.
   - Hacer commit si `not dry_run` y devolver el diccionario resumen (`total_at_risk_evaluated`, `rerouted_count`, `unfulfillable_count`, `vip_ltv_saved_usd`, `total_post_shipping_net_margin_usd`, `decisions`).

---

### Paso 3: Orquestar la Implementación Multi-Agente (`/plan`, `/boost`, `/teamwork`)

Abre `labs/lab-04-multi-agent-capstone/PROMPTS.es.md` y ejecuta los **Prompts Multi-Agente del Capstone**:
- Comienza con `/plan` o `/boost` para diseñar la evaluación de candidatos y la transacción de reserva de inventario.
- O utiliza `/teamwork` para coordinar subagentes en paralelo:
  - **Subagente 1 (Ingeniero de Enrutamiento Omnicanal)**: Implementa `evaluate_candidates` y `optimize_at_risk_orders` en `src/services/fulfillment_router.py`.
  - **Subagente 2 (Auditor de QA y Finanzas)**: Ejecuta `pytest tests/test_lab04_capstone.py` y verifica que los 35 pedidos VIP sean re-enrutados (`+$250,000` LTV salvado, `$14,774.00` margen neto post-envío) y que `/api/v1/vendors/claim-chargebacks` recupere `$98,250.00` en los 6 proveedores en incumplimiento.

---

### Paso 4: Verificar vía CLI y Dashboard Web en Vivo (`/browser`)

1. Ejecuta el script completo de verificación del Capstone (que corre las 16 pruebas de los Laboratorios 01–04):
   ```bash
   ./labs/lab-04-multi-agent-capstone/verify.sh
   ```
2. Inicia el servidor FastAPI y abre `http://127.0.0.1:8000` (o pídele a Antigravity que lo inspeccione usando `/browser`):
   ```bash
   .venv/bin/uvicorn src.main:app --reload --port 8000
   ```
3. En el **Centro de Comando de Retail Pulse**, haz clic en:
   - **"1. Enforce 15% Margin Floor (Lab 01)"** -> Observa cómo los pedidos en Margin Hold bajan de `30` (`-$35,113.25` de fuga) a `0` (`$0.00` de fuga).
   - **"2. Optimize Split-Shipment Routing (Lab 04)"** -> Observa cómo los `35` pedidos VIP en riesgo se re-enrutan a DCs/Tiendas óptimos (`0` pedidos en riesgo restantes, `$14,774.00` de margen neto post-envío preservado).
   - **"3. Claim OTIF Chargebacks (Lab 02/04)"** -> Observa cómo los `6` contratos de proveedores en incumplimiento pasan a `CHARGEBACK_CLAIMED` (`$98,250.00` recuperados).

---

## 4. Lista de Verificación

- [ ] `./labs/lab-04-multi-agent-capstone/verify.sh` pasa las **16/16 pruebas automatizadas** en `test_lab01_triage.py`, `test_lab02_rules_skills.py`, `test_lab03_mcp_hooks.py` y `test_lab04_capstone.py`.
- [ ] Los 35 pedidos VIP en `AT_RISK_STOCKOUT` pasan a `REROUTED_OPTIMAL` con `$14,774.00` de margen neto post-envío total.
- [ ] Los 6 contratos de proveedores en incumplimiento pasan a `CHARGEBACK_CLAIMED` con `$98,250.00` en penalizaciones reclamadas.

> ¿Necesitas aplicar directamente la solución verificada del Capstone? Ejecuta `./labs/lab-04-multi-agent-capstone/apply_solution.sh`.
