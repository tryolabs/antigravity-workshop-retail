# Playbook de Prompts del Laboratorio 04: Enrutamiento Omnicanal Multi-Agente y Centro de Comando Ejecutivo

Copia y pega estos prompts en **Google Antigravity** a medida que completas el Capstone del Laboratorio 04. Cada fase incluye prompts tanto para el **Track Técnico** como para el **Track Comercial / Ejecutivo**.

---

## Fase 1: Descubrimiento y Planificación Multi-Agente (`/plan` y `/boost`)

### Prompt 1A — Track Técnico: Plan Arquitectónico Profundo (`/plan`)
```text
/plan Lee @src/services/fulfillment_router.py, @src/services/inventory_atp.py, @src/main.py y @tests/test_lab04_capstone.py.
Crea un plan de implementación paso a paso para `evaluate_candidates` y `optimize_at_risk_orders` en `src/services/fulfillment_router.py`:
1. Filtrar los nodos de `wms_inventory` donde `calculate_node_atp(dict(row)) >= qty`.
2. Calcular `gross_margin_usd = (effective_unit_price_usd - unit_cost_usd) * qty` y `post_shipping_net_margin_usd = round(gross_margin_usd - shipping_cost_usd, 2)`.
3. Ordenar los candidatos elegibles por `(-post_shipping_net_margin_usd, shipping_cost_usd, 0 if location_type == 'DC' else 1)`.
4. En `optimize_at_risk_orders(conn, dry_run=False)`, iterar sobre todos los pedidos `AT_RISK_STOCKOUT` ordenados por `customer_ltv_usd DESC, order_id ASC`, re-enrutar cada uno al mejor candidato (`status = 'REROUTED_OPTIMAL'`), descontar `on_hand_qty` en el nodo ganador cuando `not dry_run` y devolver las métricas resumen esperadas por `tests/test_lab04_capstone.py`.
```

### Prompt 1B — Track Comercial / Operaciones: Análisis de Trade-Offs (`/boost`)
```text
/boost Lee @src/services/fulfillment_router.py y @tests/test_lab04_capstone.py.
Desde una perspectiva de rentabilidad omnicanal en retail, analiza por qué clasificar los nodos de cumplimiento por Margen Neto Post-Envío (`gross_margin_usd - shipping_zone_cost_usd`) con un criterio de desempate a favor de los Centros de Distribución regionales (`DC`) sobre el envío desde tienda (`STORE`) protege tanto la economía unitaria como la disponibilidad de inventario en tiendas insignia. Luego implementa el motor de enrutamiento en `src/services/fulfillment_router.py`.
```

---

## Fase 2: Ejecución Multi-Agente (`/teamwork` y Subagentes)

### Prompt 2A — Orquestación de Subagentes en Paralelo (`/teamwork`)
```text
/teamwork Coordina dos flujos de trabajo especializados para completar nuestro Capstone del Laboratorio 04:
1. Ingeniero de Enrutamiento Omnicanal: Implementa `evaluate_candidates` y `optimize_at_risk_orders` en @src/services/fulfillment_router.py para que los 35 pedidos VIP en `AT_RISK_STOCKOUT` sean re-enrutados al nodo con mayor margen neto post-envío y suficiente True ATP.
2. Auditor de QA y Finanzas Comerciales: Ejecuta `./labs/lab-04-multi-agent-capstone/verify.sh` para validar las 16 pruebas de los Laboratorios 01-04 y genera una tabla ejecutiva de resumen mostrando:
   - Fuga total de margen eliminada (Laboratorio 01)
   - LTV total de clientes VIP salvado y Margen Neto Post-Envío preservado en los 35 pedidos VIP re-enrutados (Laboratorio 04)
   - Chargebacks OTIF de proveedores recuperados en los 6 proveedores en incumplimiento (Laboratorio 02/04)
```

---

## Fase 3: Edición en Línea (`Cmd+I` / `Ctrl+I`)

Abre `src/services/fulfillment_router.py`, selecciona `evaluate_candidates` y `optimize_at_risk_orders`, presiona `Cmd+I` (macOS) o `Ctrl+I` (Windows/Linux) e ingresa:

```text
Implementa `evaluate_candidates` usando `calculate_node_atp` para filtrar nodos con `true_atp >= qty`, calcula `post_shipping_net_margin_usd = round((effective_unit_price_usd - unit_cost_usd) * qty - shipping_cost_usd, 2)` y ordena por `(-post_shipping_net_margin_usd, shipping_cost_usd, 0 if location_type == 'DC' else 1)`. Luego implementa `optimize_at_risk_orders` para re-enrutar pedidos `AT_RISK_STOCKOUT` (ordenados por `customer_ltv_usd DESC, order_id ASC`) hacia `candidates[0]`, actualizando `omnichannel_orders` (`status='REROUTED_OPTIMAL'`) y descontando `wms_inventory.on_hand_qty` cuando `not dry_run`.
```

---

## Fase 4: Verificación Visual del Centro de Comando (`/browser`)

### Prompt 4 — Verificación de Extremo a Extremo en el Navegador del Centro de Comando de Retail Pulse
```text
/browser Inicia el servidor FastAPI (`uvicorn src.main:app --port 8000`) si aún no está corriendo, abre `http://127.0.0.1:8000` y verifica:
1. El encabezado muestra el logo de Tryolabs ("Delivered by Tryolabs") y los KPIs del Centro de Comando de Retail Pulse.
2. Haz clic en "1. Enforce 15% Margin Floor (Lab 01)", "2. Optimize Split-Shipment Routing (Lab 04)" y "3. Claim OTIF Chargebacks (Lab 02/04)".
3. Confirma que Margin Hold Orders = 0, VIP Stockout Risk = 0 y que los 6 contratos de proveedores en incumplimiento muestran `CHARGEBACK_CLAIMED` sumando $98,250.00.
```

---

## Fase 5: Desafío Adicional — Cumplimiento Dividido entre Múltiples Nodos

### Prompt 5 — Diseñar Envíos Divididos Multi-Nodo cuando Ningún Nodo Único Tiene la Cantidad Completa
```text
¿Qué sucede si un pedido VIP de alto volumen (por ejemplo, 25 unidades) no puede ser surtido por ningún DC o Tienda individualmente, pero sí dividiéndolo entre dos nodos (por ejemplo, 15 unidades desde `DC-EAST-01` + 10 unidades desde `DC-CENTRAL-02`)?
Propón una función auxiliar compatible `evaluate_split_shipment_pair(conn, sku, qty, effective_unit_price_usd)` que encuentre la combinación de 2 nodos con mayor margen neto cuando `evaluate_candidates` devuelva una lista vacía, asegurando que los costos de envío combinados no incumplan nuestro piso mínimo de margen del 15%.
```
