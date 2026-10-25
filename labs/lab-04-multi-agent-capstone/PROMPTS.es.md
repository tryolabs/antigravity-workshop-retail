<p align="center">
  <img src="../../src/static/tryolabs-logo.png" alt="Tryolabs Logo" width="180" />
</p>

# Playbook de Prompts del Lab 04: Google ADK, Protocolo A2A, Enrutamiento Omnicanal y Despliegue en Gemini Enterprise

> **Idioma / Language:** [Español](./PROMPTS.es.md) | [English](./PROMPTS.md) • **Guía del Lab:** [README.es.md](./README.es.md) | [README.md](./README.md) • **PDF:** [ES](./LAB_04_INSTRUCTIONS_ES.pdf) | [EN](./LAB_04_INSTRUCTIONS_EN.pdf)

Copia y pega estos prompts en **Google Antigravity** mientras completas el Capstone del Lab 04. Cada fase incluye prompts tanto para el **Track Técnico** como para el **Track Comercial / Ejecutivo**.

---

## Fase 1: Descubrimiento y Planificación Multi-Agente (`/plan` y `/boost`)

### Prompt 1A — Track Técnico: Plan Arquitectónico para Enrutamiento + ADK + A2A (`/plan`)
```text
/plan Lee @src/services/fulfillment_router.py, @src/agents/adk_a2a_orchestrator.py, @adk_agents/retail_pulse/agent.py, @src/main.py y @tests/test_lab04_capstone.py.
Crea un plan de implementación paso a paso para completar nuestro Capstone del Lab 04:
1. En `src/services/fulfillment_router.py`, implementar `optimize_at_risk_order_routing` y `claim_vendor_otif_chargebacks` para clasificar los nodos elegibles (`true_atp >= qty`) por `(-post_shipping_margin_usd, 0 if location_type == 'DC' else 1, -true_atp)`, re-enrutar las 35 órdenes VIP `AT_RISK_STOCKOUT` a `REROUTED_SAVED` (protegiendo $749,300.00 en LTV VIP), y reclamar $98,250.00 en los 6 contratos OTIF en incumplimiento (`CHARGEBACK_CLAIMED`).
2. En `src/agents/adk_a2a_orchestrator.py`, implementar:
   - `WMSInventoryATPAgent.execute(task_payload)` (resumen de red True ATP + re-enrutamiento óptimo omnicanal + recomendación de handoff)
   - `MerchandisingMarginOTIFAgent.execute(task_payload, wms_routing_output)` (remediación del piso de margen bruto del 15% + recuperación de penalidades OTIF de proveedores)
   - `RetailPulseOrchestratorAgent.run_multi_agent_workflow(prompt, skill_id, metadata)` coordinando `WMSInventoryATPAgent` -> `MerchandisingMarginOTIFAgent` con metadatos de Google ADK
   - `get_a2a_agent_card(base_url)` y `handle_a2a_jsonrpc(payload, db_path)` para `GET /.well-known/agent.json` y `POST /api/v1/a2a/tasks/send` (`tasks/send`, `message/send` y `tasks/get`).
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
1. Ingeniero de Enrutamiento Omnicanal: Implementa `optimize_at_risk_order_routing` y `claim_vendor_otif_chargebacks` en @src/services/fulfillment_router.py para que las 35 órdenes VIP `AT_RISK_STOCKOUT` se re-enruten a `REROUTED_SAVED` ($749,300.00 LTV VIP protegido) y los 6 contratos de proveedores en incumplimiento pasen a `CHARGEBACK_CLAIMED` ($98,250.00 recuperados).
2. Arquitecto de Sistemas ADK y A2A: Implementa `WMSInventoryATPAgent`, `MerchandisingMarginOTIFAgent`, `RetailPulseOrchestratorAgent`, `get_a2a_agent_card` y `handle_a2a_jsonrpc` en @src/agents/adk_a2a_orchestrator.py.
3. Auditor de QA, ADK Web y Cloud Run: Ejecuta `./labs/lab-04-multi-agent-capstone/verify.sh` para validar las 20 pruebas de los Labs 01-04, verifica `./scripts/run_adk_web.sh --check` y `./labs/lab-04-multi-agent-capstone/deploy_gcp.sh --dry-run`, y genera una tabla ejecutiva con la recuperación financiera total.
```

---

## Fase 3: Edición en Línea (`Cmd+I` / `Ctrl+I`)

Abre `src/services/fulfillment_router.py`, selecciona `optimize_at_risk_order_routing` y `claim_vendor_otif_chargebacks`, presiona `Cmd+I` (macOS) o `Ctrl+I` (Windows/Linux) e ingresa:

```text
Implementa `optimize_at_risk_order_routing` usando `evaluate_location_atp` para filtrar nodos candidatos con `can_fulfill == True`, calcula `post_shipping_margin_usd = round((unit_price - unit_cost) * qty - shipping_cost, 2)`, ordena por `(-post_shipping_margin_usd, 0 if location_type == 'DC' else 1, -true_atp)` y actualiza `omnichannel_orders` (`status='REROUTED_SAVED'`) cuando `persist_changes=True`. Luego implementa `claim_vendor_otif_chargebacks` usando `audit_all_vendor_otif_contracts(only_breaching=True)` para cambiar el estado de los contratos en incumplimiento a `status='CHARGEBACK_CLAIMED'`.
```

---

## Fase 4: Pruebas Interactivas Locales con `adk web` y `/browser`

### Prompt 4A — Probar la Jerarquía Multi-Agente Localmente en ADK Web UI (`adk web`)
```text
Valida nuestra configuración local de Google ADK Development UI ejecutando `./scripts/run_adk_web.sh --check`, e inspecciona @adk_agents/retail_pulse/agent.py para confirmar cómo `root_agent` (`retail_pulse_orchestrator`) delega entre `wms_inventory_atp_agent` y `merchandising_margin_otif_agent`.
```

### Prompt 4B — Verificación Visual de Punta a Punta en el Navegador (`/browser`)
```text
/browser Inicia el servidor FastAPI (`./.venv/bin/uvicorn src.main:app --host 127.0.0.1 --port 8002`) si aún no está corriendo, abre `http://localhost:8002` y verifica:
1. El encabezado muestra el logo de Tryolabs ("Delivered by Tryolabs") y los KPIs del Retail Pulse Command Center.
2. Ejecuta las acciones de remediación (`POST /api/v1/remediate/margins`, `POST /api/v1/remediate/routing` o `POST /api/v1/a2a/tasks/send`).
3. Confirma que Margin Hold Orders = 0, VIP Stockout Risk = 0 ($749,300.00 LTV VIP protegido), y que los 6 contratos de proveedores en incumplimiento muestran `CHARGEBACK_CLAIMED` sumando $98,250.00.
4. Consulta también `http://localhost:8002/.well-known/agent.json` para inspeccionar la Agent Card A2A en vivo.
```

---

## Fase 5: Despliegue en Cloud Run + Terraform y Registro en Gemini Enterprise

### Prompt 5 — Validar Infraestructura Terraform y Registro A2A en Gemini Enterprise
```text
Lee @infra/terraform/main.tf, @deploy/deploy_gcp.sh y @deploy/register_gemini_enterprise_agent.sh.
Ejecuta `./labs/lab-04-multi-agent-capstone/deploy_gcp.sh --dry-run --project-id retail-pulse-prod --region us-central1 --gemini-app-id retail-pulse-ge-app` y explica cada paso del pipeline de despliegue:
1. Construcción de la imagen de contenedor con Cloud Build y Artifact Registry
2. Aprovisionamiento de Cloud Run v2, cuenta de servicio IAM de mínimo privilegio y permisos de Vertex AI con Terraform
3. Registro de la Agent Card A2A de Cloud Run (`/.well-known/agent.json` y `/api/v1/a2a/tasks/send`) en Gemini Enterprise (Discovery Engine).
```
