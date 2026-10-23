<div align="center">
  <img src="src/static/tryolabs-logo.png" alt="Tryolabs Logo" height="44" />
  <h1>Guía Maestra del Instructor y Guion de Demostración en Vivo</h1>
  <p><strong>Taller de la Industria Retail de Google Antigravity — Impartido por Tryolabs</strong></p>
  <p><a href="INSTRUCTOR_DEMO_GUIDE.md"><strong>English</strong></a> | <a href="INSTRUCTOR_DEMO_GUIDE.es.md"><strong>Español</strong></a> | <a href="README.es.md"><strong>README Principal</strong></a></p>
</div>

---

## 1. Lista de Verificación Pre-Vuelo (15 Minutos Antes de Iniciar el Taller)

1. **Inicializar y Restaurar al Estado Inicial del Lab 01**:
   ```bash
   ./install.sh
   ```
2. **Iniciar el Retail Pulse Command Center (Pestaña de Terminal 1 en Segundo Plano)**:
   ```bash
   .venv/bin/uvicorn src.main:app --reload --port 8002
   ```
3. **Abrir `http://127.0.0.1:8002` en Chrome**:
   - Verifica que el **logo de Tryolabs ("Delivered by Tryolabs")** aparezca en el encabezado superior.
   - Verifica que los 3 KPIs de crisis se muestren en rojo/ámbar:
     - **Margin Hold Orders**: `30` (`-$35,113.25` de fuga de margen)
     - **VIP Stockout Risk**: `35` órdenes VIP (`>$250,000` de LTV expuesto)
     - **OTIF Chargeback Recovery**: `6` proveedores en incumplimiento (`$98,250.00` sin reclamar)
4. **Comandos de Recuperación Instantánea**:
   Si tú o cualquier asistente necesitan saltar limpiamente al estado inicial o a la solución de cualquier laboratorio:
   ```bash
   # Restaurar al estado inicial del Lab X:
   ./labs/lab-01-margin-inventory-triage/install.sh
   ./labs/lab-02-rules-and-skills/install.sh
   ./labs/lab-03-mcp-and-hooks/install.sh
   ./labs/lab-04-multi-agent-capstone/install.sh

   # Aplicar solución del Lab X y verificar:
   ./labs/lab-01-margin-inventory-triage/apply_solution.sh && ./labs/lab-01-margin-inventory-triage/verify.sh
   ./labs/lab-02-rules-and-skills/apply_solution.sh       && ./labs/lab-02-rules-and-skills/verify.sh
   ./labs/lab-03-mcp-and-hooks/apply_solution.sh          && ./labs/lab-03-mcp-and-hooks/verify.sh
   ./labs/lab-04-multi-agent-capstone/apply_solution.sh   && ./labs/lab-04-multi-agent-capstone/verify.sh
   ```

---

## 2. Guion de Demostración en Vivo Módulo por Módulo (4 Horas)

### Módulo 0: Briefing Ejecutivo y Tour de la Crisis (`00:00 - 00:30`)

#### Puntos Clave
- Da la bienvenida en nombre de **Tryolabs**. Explica que el taller une a **Ingenieros de Plataforma/Software** y **Líderes Comerciales/Merchandising/Supply Chain** alrededor de una crisis omnicanal realista de Black Friday (**Retail Pulse**).
- Muestra `http://127.0.0.1:8002`. Señala que la plataforma está perdiendo `-$35,113.25` en 30 órdenes con descuentos apilados, dejando 35 órdenes VIP `DIAMOND`/`GOLD` (`>$250K` LTV) en riesgo de quiebre de stock por inventario BOPIS fantasma, y dejando `$98,250.00` en penalidades OTIF de proveedores sin reclamar.
- Contrasta **Editor View** (para ediciones en línea síncronas con `Cmd+I` / `Ctrl+I`) con **Agent Manager (`Cmd+E` / `Ctrl+E`)** (para planificación asíncrona, ejecución de pruebas y delegación en subagentes).

---

### Módulo 1: Lab 01 — Triage Omnicanal en Flash-Sale (`00:30 - 01:15`)

#### Capacidades Demostradas
- Menciones de contexto `@` (`@src/services/promo_pricing.py`, `@data/exports/omnichannel_orders.csv`)
- Planificación interactiva con `/plan`
- Edición en Línea (`Cmd+I` / `Ctrl+I`)
- Verificación autónoma guiada por pruebas (`pytest`)

#### Pasos de Demostración en Vivo
1. Ejecuta `./labs/lab-01-margin-inventory-triage/verify.sh` en la terminal para mostrar las pruebas que fallan inicialmente.
2. Pega el **Prompt 1A** (Técnico) o **Prompt 1B** (Comercial) de `labs/lab-01-margin-inventory-triage/PROMPTS.es.md` para diagnosticar el Bug #1A y el Bug #1B.
3. Pega el **Prompt 2** (`/plan`) para generar el artefacto del plan de implementación.
4. Selecciona `calculate_stacked_promo_price` en `src/services/promo_pricing.py`, presiona `Cmd+I` / `Ctrl+I` y aplica el piso de margen del 15% (`unit_cost_usd / (1.0 - minimum_margin_pct)`).
5. Corrige `calculate_node_atp` en `src/services/inventory_atp.py` y ejecuta `./labs/lab-01-margin-inventory-triage/verify.sh` (`6/6` aprobadas).
6. En el navegador (`http://127.0.0.1:8002`), haz clic en **"1. Enforce 15% Margin Floor (Lab 01)"** y muestra cómo las órdenes retenidas por margen bajan de `30` a `0` (`$0.00` de pérdida).

---

### Módulo 2: Lab 02 — Personalizaciones (`GEMINI.md`, Rules y Skills) (`01:15 - 02:00`)

#### Capacidades Demostradas
- Memoria del Workspace (`GEMINI.md`)
- Reglas de Dominio (`.agents/rules/retail-standards.md`)
- Skills Reutilizables con YAML Frontmatter + Scripts Auxiliares (`.agents/skills/margin-otif-audit/SKILL.md` + `scripts/run_otif_margin_audit.py`)
- Comando Slash `/learn`

#### Pasos de Demostración en Vivo
1. Ejecuta `./labs/lab-02-rules-and-skills/install.sh` y `./labs/lab-02-rules-and-skills/verify.sh`.
2. Explica la **Jerarquía de Personalización de Antigravity**:
   - **Memoria permanente del workspace**: `GEMINI.md`
   - **Guardrails de dominio**: `.agents/rules/retail-standards.md` (validación GS1 Módulo-10 GTIN-14, piso de margen del 15%, tramos de penalidad OTIF)
   - **Flujos procedimentales bajo demanda**: `.agents/skills/margin-otif-audit/SKILL.md`
3. Ejecuta el **Prompt 4A** de `labs/lab-02-rules-and-skills/PROMPTS.es.md` (o usa `/learn`) para generar los tres archivos.
4. Ejecuta `./labs/lab-02-rules-and-skills/verify.sh` y luego activa el skill con el **Prompt 5B** para mostrar los **6 proveedores en incumplimiento** y los **$98,250.00 en penalidades recuperables**.

---

### Módulo 3: Lab 03 — Servidor FastMCP, Hooks Deterministas y Seguridad Empresarial (`02:00 - 02:55`)

#### Capacidades Demostradas
- Servidor FastMCP (`mcp_server/retail_mcp.py` y `.agents/mcp_config.json`)
- Hooks Deterministas de Ciclo de Vida (`.agents/hooks.json` y `scripts/margin_guard_hook.py` -> `data/logs/hook_compliance_audit.jsonl`)
- **Deep-Dive de Gobernanza Empresarial**: Google Cloud IAM / Cloud Audit Logs / VPC-SC + Sandbox y Controles de Permisos del Cliente Antigravity

#### Pasos de Demostración en Vivo
1. Ejecuta `./labs/lab-03-mcp-and-hooks/install.sh` y `./labs/lab-03-mcp-and-hooks/verify.sh`.
2. Abre `mcp_server/retail_mcp.py` (donde `query_true_atp_inventory` ya está implementada y faltan `audit_vendor_otif_contracts`, `simulate_promo_margin_guard` y `list_at_risk_vip_orders`) y completa las herramientas MCP junto con `.agents/mcp_config.json` y `.agents/hooks.json`.
3. **Demostración Adversarial en Vivo del Hook**:
   ```bash
   echo '{"toolCall":{"name":"edit_file","args":{"Path":"src/services/promo_pricing.py","Replacement":"enforce_floor=False"}}}' | .venv/bin/python scripts/margin_guard_hook.py --event PreToolUse
   ```
   Muestra la respuesta determinista en JSON (`{"decision": "deny", "reason": "Blocked by Retail Compliance Hook (SOX 404 / Gross Margin Protection)..."}`), inspecciona `data/logs/hook_compliance_audit.jsonl` y ejecuta `./labs/lab-03-mcp-and-hooks/verify.sh` (**13/13 pruebas acumuladas aprobadas**).
4. Recorre las dos capas de seguridad empresarial documentadas en `labs/lab-03-mcp-and-hooks/README.es.md` (Google Cloud IAM + Cloud Audit Logs + VPC-SC + Controles Locales del Cliente Antigravity).

---

### Módulo 4: Lab 04 — Capstone Multi-Agente: Google ADK, Protocolo A2A, `adk web` y Cloud Run / Gemini Enterprise (`02:55 - 03:45`)

#### Capacidades Demostradas
- `/plan`, `/boost` y `/teamwork` para arquitectura multi-agente y optimización de enrutamiento
- Jerarquía multi-agente con **Google ADK (`google-adk`)** (`WMSInventoryATPAgent` + `MerchandisingMarginOTIFAgent` + `RetailPulseOrchestratorAgent`)
- Interoperabilidad con **Protocolo A2A (`/.well-known/agent.json` y `POST /api/v1/a2a`)** vía JSON-RPC 2.0
- **Interfaz Local ADK Development UI (`adk web`)** mediante `./scripts/run_adk_web.sh`
- **Despliegue en Cloud Run con Terraform y Registro en Gemini Enterprise** mediante `./labs/lab-04-multi-agent-capstone/deploy_gcp.sh`

#### Pasos de Demostración en Vivo
1. Ejecuta `./labs/lab-04-multi-agent-capstone/install.sh` y `./labs/lab-04-multi-agent-capstone/verify.sh`.
2. Muestra `src/services/fulfillment_router.py` y `src/agents/adk_a2a_orchestrator.py` donde los métodos iniciales lanzan `NotImplementedError`.
3. Pega el **Prompt 1A (`/plan`)** o **Prompt 2A (`/teamwork`)** de `labs/lab-04-multi-agent-capstone/PROMPTS.es.md` (o ejecuta `./labs/lab-04-multi-agent-capstone/apply_solution.sh`) para implementar el motor de enrutamiento y el orquestador multi-agente ADK + A2A.
4. Ejecuta `./labs/lab-04-multi-agent-capstone/verify.sh` y celebra las **20/20 pruebas aprobadas** en los Labs 01, 02, 03 y 04.
5. **Demostración en Vivo de `adk web` (ADK Development UI Local)**:
   ```bash
   ./scripts/run_adk_web.sh --dry-run
   # Opcionalmente iniciar en vivo en el puerto 8080:
   ./scripts/run_adk_web.sh --port 8080
   ```
6. **Demostración en Vivo de la Agent Card A2A y Handoff JSON-RPC 2.0**:
   ```bash
   curl -s http://127.0.0.1:8002/.well-known/agent.json | python3 -m json.tool
   ```
7. **Demostración en Vivo de Cloud Run + Terraform + Registro en Gemini Enterprise**:
   ```bash
   ./labs/lab-04-multi-agent-capstone/deploy_gcp.sh --dry-run --project-id retail-pulse-enterprise --region us-central1 --gemini-app-id retail-pulse-ge-app
   ```
8. Regresa a `http://127.0.0.1:8002` (o invoca el **Prompt 4B (`/browser`)**):
   - Haz clic en **"1. Enforce 15% Margin Floor (Lab 01)"** -> `0` órdenes retenidas por margen (`$0.00` de fuga).
   - Haz clic en **"2. Optimize Split-Shipment Routing (Lab 04)"** -> Las `35` órdenes VIP re-enrutadas (`$250,000+` LTV salvado, `$14,774.00` de margen neto post-envío preservado).
   - Haz clic en **"3. Claim OTIF Chargebacks (Lab 02/04)"** -> Los `6` contratos en incumplimiento marcados como `CHARGEBACK_CLAIMED` (`$98,250.00` recuperados).

---

## 3. Resumen de Métricas Financieras y Operativas Verificadas

Utiliza esta tabla de referencia durante la sesión de Q&A ejecutivo para explicar las cifras deterministas de `data/seed_retail_data.py`:

| Métrica | Estado Inicial de Crisis (Starter) | Estado Post-Remediación (Solución) | Verificado Por |
| :--- | :--- | :--- | :--- |
| **Órdenes Retenidas por Margen (`MARGIN_HOLD`)** | `30` órdenes (`-$35,113.25` de fuga de margen negativo) | `0` órdenes (`$0.00` de fuga; ajustadas al piso de margen bruto `>= 15%`) | `tests/test_lab01_triage.py` |
| **Órdenes VIP en Riesgo (`AT_RISK_STOCKOUT`)** | `35` órdenes VIP (`DIAMOND`/`GOLD`) (`>$250,000` de LTV expuesto) | `0` órdenes en riesgo (`35` re-enrutadas a `REROUTED_OPTIMAL` con `$14,774.00` de margen neto post-envío) | `tests/test_lab04_capstone.py` |
| **Incumplimientos OTIF (`BREACH_DETECTED`)** | `6` contratos en incumplimiento (`$98,250.00` en penalidades no reclamadas) | `6` contratos actualizados a `CHARGEBACK_CLAIMED` (`$98,250.00` recuperados) | `tests/test_lab02_rules_skills.py` y `tests/test_lab04_capstone.py` |
| **Auditoría del Hook `PreToolUse`** | Desprotegido ante ediciones `enforce_floor=False` | Bloqueo determinista JSON `"decision": "deny"` + bitácora JSONL en `data/logs/hook_compliance_audit.jsonl` | `tests/test_lab03_mcp_hooks.py` |
| **Sistema Multi-Agente Google ADK + A2A** | Flujos técnicos y comerciales desconectados | Handoff A2A `WMSInventoryATPAgent` -> `MerchandisingMarginOTIFAgent` + Terraform Cloud Run + Registro en Gemini Enterprise | `tests/test_lab04_capstone.py` (`20/20` pruebas en total) |
