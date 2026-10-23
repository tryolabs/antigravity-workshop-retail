<p align="center">
  <img src="../../src/static/tryolabs-logo.png" alt="Tryolabs Logo" width="180" />
</p>

# Playbook de Prompts del Lab 04: Google ADK, Protocolo A2A, Enrutamiento Omnicanal y Despliegue en Gemini Enterprise

Copia y pega estos prompts en **Google Antigravity** mientras completas el Capstone del Lab 04. Cada fase incluye prompts tanto para el **Track Técnico** como para el **Track Comercial / Ejecutivo**.

---

## Fase 1: Descubrimiento y Planificación Multi-Agente (`/plan` y `/boost`)

### Prompt 1A — Track Técnico: Plan Arquitectónico para Enrutamiento + ADK + A2A (`/plan`)
```text
/plan Lee @src/services/fulfillment_router.py, @src/agents/adk_a2a_orchestrator.py, @adk_agents/retail_pulse/agent.py, @src/main.py y @tests/test_lab04_capstone.py.
Crea un plan de implementación paso a paso para completar nuestro Capstone del Lab 04:
1. En `src/services/fulfillment_router.py`, implementar `evaluate_candidates` y `optimize_at_risk_orders` para clasificar los nodos con `true_atp >= qty` por `(-post_shipping_net_margin_usd, shipping_cost_usd, 0 if location_type == 'DC' else 1)` y re-enrutar las 35 órdenes VIP `AT_RISK_STOCKOUT` a `REROUTED_OPTIMAL`.
2. En `src/agents/adk_a2a_orchestrator.py`, implementar:
   - `WMSInventoryATPAgent.execute(conn, dry_run)` (auditoría True ATP + enrutamiento óptimo omnicanal + `A2AAgentHandoff` hacia `merchandising_margin_agent`)
   - `MerchandisingMarginOTIFAgent.execute(conn, wms_handoff, dry_run)` (aplicación del piso de margen bruto del 15% + recuperación de penalidades OTIF de proveedores)
   - `RetailPulseOrchestratorAgent.run_orchestration(conn, prompt, dry_run, session_id)` y `build_adk_agent_hierarchy()` usando `google.adk.agents.LlmAgent` y `SequentialAgent`
   - `build_a2a_agent_card(base_url)` y `handle_a2a_jsonrpc(conn, rpc_request, base_url)` para `GET /.well-known/agent.json` y `POST /api/v1/a2a` (`tasks/send` y `message/send`).
```

### Prompt 1B — Track Comercial / Operaciones: Análisis de Gobernanza Multi-Agente (`/boost`)
```text
/boost Lee @src/services/fulfillment_router.py, @src/agents/adk_a2a_orchestrator.py y @tests/test_lab04_capstone.py.
Desde una perspectiva de rentabilidad omnicanal retail, analiza por qué separar responsabilidades entre un agente técnico `WMSInventoryATPAgent` (True ATP y enrutamiento por margen neto post-envío priorizando Centros de Distribución `DC`) y un agente comercial `MerchandisingMarginOTIFAgent` (piso de margen bruto del 15% y notas de débito OTIF) conectados mediante el Protocolo A2A previene tanto la fuga de margen negativo como las cancelaciones de clientes VIP. Luego implementa ambos módulos para que pasen las 20 pruebas del taller.
```

---

## Fase 2: Ejecución Multi-Agente (`/teamwork` y Subagentes)

### Prompt 2A — Orquestación Paralela de Subagentes (`/teamwork`)
```text
/teamwork Coordina tres flujos de trabajo especializados para completar el Capstone del Lab 04:
1. Ingeniero de Enrutamiento Omnicanal: Implementa `evaluate_candidates` y `optimize_at_risk_orders` en @src/services/fulfillment_router.py para que las 35 órdenes VIP `AT_RISK_STOCKOUT` se re-enruten al nodo con mayor margen neto post-envío y suficiente True ATP.
2. Arquitecto de Sistemas ADK y A2A: Implementa `WMSInventoryATPAgent`, `MerchandisingMarginOTIFAgent`, `RetailPulseOrchestratorAgent`, `build_a2a_agent_card` y `handle_a2a_jsonrpc` en @src/agents/adk_a2a_orchestrator.py.
3. Auditor de QA, ADK Web y Cloud Run: Ejecuta `./labs/lab-04-multi-agent-capstone/verify.sh` para validar las 20 pruebas de los Labs 01-04, verifica `./scripts/run_adk_web.sh --dry-run` y `./labs/lab-04-multi-agent-capstone/deploy_gcp.sh --dry-run`, y genera una tabla ejecutiva con la recuperación financiera total.
```

---

## Fase 3: Edición en Línea (`Cmd+I` / `Ctrl+I`)

Abre `src/services/fulfillment_router.py`, selecciona `evaluate_candidates` y `optimize_at_risk_orders`, presiona `Cmd+I` (macOS) o `Ctrl+I` (Windows/Linux) e ingresa:

```text
Implement `evaluate_candidates` using `calculate_node_atp` to filter nodes with `true_atp >= qty`, compute `post_shipping_net_margin_usd = round((effective_unit_price_usd - unit_cost_usd) * qty - shipping_cost_usd, 2)`, and sort by `(-post_shipping_net_margin_usd, shipping_cost_usd, 0 if location_type == 'DC' else 1)`. Then implement `optimize_at_risk_orders` to reroute `AT_RISK_STOCKOUT` orders (ordered by `customer_ltv_usd DESC, order_id ASC`) to `candidates[0]`, updating `omnichannel_orders` (`status='REROUTED_OPTIMAL'`) and decrementing `wms_inventory.on_hand_qty` when `not dry_run`.
```

---

## Fase 4: Pruebas Interactivas Locales con `adk web` y `/browser`

### Prompt 4A — Probar la Jerarquía Multi-Agente Localmente en ADK Web UI (`adk web`)
```text
Valida nuestra configuración local de Google ADK Development UI ejecutando `./scripts/run_adk_web.sh --dry-run`, e inspecciona @adk_agents/retail_pulse/agent.py para confirmar cómo `root_agent` (`retail_pulse_root_agent`) delega entre `wms_inventory_agent`, `merchandising_margin_agent` y `a2a_bridge_agent`.
```

### Prompt 4B — Verificación Visual de Punta a Punta en el Navegador (`/browser`)
```text
/browser Inicia el servidor FastAPI (`uvicorn src.main:app --port 8000`) si aún no está corriendo, abre `http://127.0.0.1:8000` y verifica:
1. El encabezado muestra el logo de Tryolabs ("Delivered by Tryolabs") y los KPIs del Retail Pulse Command Center.
2. Haz clic en "1. Enforce 15% Margin Floor (Lab 01)", "2. Optimize Split-Shipment Routing (Lab 04)" y "3. Claim OTIF Chargebacks (Lab 02/04)".
3. Confirma que Margin Hold Orders = 0, VIP Stockout Risk = 0, y que los 6 contratos de proveedores en incumplimiento muestran `CHARGEBACK_CLAIMED` sumando $98,250.00.
4. Consulta también `http://127.0.0.1:8000/.well-known/agent.json` para inspeccionar la Agent Card A2A en vivo.
```

---

## Fase 5: Despliegue en Cloud Run + Terraform y Registro en Gemini Enterprise

### Prompt 5 — Validar Infraestructura Terraform y Registro A2A en Gemini Enterprise
```text
Lee @infra/terraform/main.tf, @deploy/deploy_gcp.sh y @deploy/register_gemini_enterprise_agent.sh.
Ejecuta `./labs/lab-04-multi-agent-capstone/deploy_gcp.sh --dry-run --project-id retail-pulse-prod --region us-central1 --gemini-app-id retail-pulse-ge-app` y explica cada paso del pipeline de despliegue:
1. Construcción de la imagen de contenedor con Cloud Build y Artifact Registry
2. Aprovisionamiento de Cloud Run v2, cuenta de servicio IAM de mínimo privilegio y permisos de Vertex AI con Terraform
3. Registro de la Agent Card A2A de Cloud Run (`/.well-known/agent.json` y `/api/v1/a2a`) en Gemini Enterprise (Discovery Engine).
```
