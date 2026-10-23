<div align="center">
  <img src="src/static/tryolabs-logo.png" alt="Tryolabs Logo" height="44" />
  <h1>Guía Maestra del Instructor y Guion de Demo en Vivo</h1>
  <p><strong>Workshop de la Industria Retail de Google Antigravity — Impartido por Tryolabs</strong></p>
  <p><a href="INSTRUCTOR_DEMO_GUIDE.md"><strong>English</strong></a> | <a href="INSTRUCTOR_DEMO_GUIDE.es.md"><strong>Español</strong></a> | <a href="README.es.md"><strong>README Principal</strong></a></p>
</div>

---

## 1. Lista de Verificación Previa (15 Minutos Antes de Iniciar el Workshop)

1. **Inicializar y Restablecer al Estado Inicial del Laboratorio 01**:
   ```bash
   ./install.sh
   ```
2. **Iniciar el Centro de Comando de Retail Pulse (Pestaña de Terminal 1 en Segundo Plano)**:
   ```bash
   .venv/bin/uvicorn src.main:app --reload --port 8000
   ```
3. **Abrir `http://127.0.0.1:8000` en Chrome**:
   - Verificar que el **logo de Tryolabs ("Delivered by Tryolabs")** aparezca en el encabezado superior.
   - Verificar que los 3 KPIs de crisis se muestren en rojo/ámbar:
     - **Margin Hold Orders**: `30` (`-$35,113.25` de Fuga de Margen)
     - **VIP Stockout Risk**: `35` Pedidos VIP (`>$250,000` de LTV Expuesto)
     - **OTIF Chargeback Recovery**: `6` Proveedores en Incumplimiento (`$98,250.00` Sin Reclamar)
4. **Comandos de Recuperación Instantánea**:
   Si tú o algún participante necesitan saltar limpiamente al inicio o a la solución de cualquier laboratorio:
   ```bash
   # Restablecer al estado inicial del Laboratorio X:
   ./labs/lab-01-margin-inventory-triage/install.sh
   ./labs/lab-02-rules-and-skills/install.sh
   ./labs/lab-03-mcp-and-hooks/install.sh
   ./labs/lab-04-multi-agent-capstone/install.sh

   # Aplicar la solución del Laboratorio X y verificar:
   ./labs/lab-01-margin-inventory-triage/apply_solution.sh && ./labs/lab-01-margin-inventory-triage/verify.sh
   ./labs/lab-02-rules-and-skills/apply_solution.sh       && ./labs/lab-02-rules-and-skills/verify.sh
   ./labs/lab-03-mcp-and-hooks/apply_solution.sh          && ./labs/lab-03-mcp-and-hooks/verify.sh
   ./labs/lab-04-multi-agent-capstone/apply_solution.sh   && ./labs/lab-04-multi-agent-capstone/verify.sh
   ```

---

## 2. Guion de Demo en Vivo Módulo por Módulo (4 Horas)

### Módulo 0: Introducción Ejecutiva y Recorrido por la Crisis (`00:00 - 00:30`)

#### Puntos Clave de Presentación
- Dar la bienvenida en nombre de **Tryolabs**. Explicar que el workshop reúne a **Ingenieros de Plataforma/Software** y **Gerentes Comerciales/Merchandising/Supply Chain** en torno a una crisis omnicanal realista de Black Friday (**Retail Pulse**).
- Mostrar `http://127.0.0.1:8000`. Señalar que la plataforma está perdiendo `-$35,113.25` en 30 pedidos con promociones acumuladas, dejando 35 pedidos VIP `DIAMOND`/`GOLD` (`>$250K` LTV) en riesgo por inventario fantasma BOPIS, y dejando `$98,250.00` en penalizaciones OTIF de proveedores sin reclamar.
- Contrastar la **Vista de Editor** (para ediciones rápidas en línea con `Cmd+I` / `Ctrl+I`) con el **Agent Manager (`Cmd+E` / `Ctrl+E`)** (para planificación asíncrona multipaso, ejecución de pruebas y delegación en subagentes).

---

### Módulo 1: Laboratorio 01 — Triaje Omnicanal de Flash-Sale (`00:30 - 01:15`)

#### Capacidades Demostradas
- Menciones de Contexto `@` (`@src/services/promo_pricing.py`, `@data/exports/omnichannel_orders.csv`)
- Planificación Interactiva con Artefactos (`/plan`)
- Edición en Línea (`Cmd+I` / `Ctrl+I`)
- Verificación Autónoma Guiada por Pruebas (`pytest`)

#### Pasos de la Demo en Vivo
1. Ejecutar `./labs/lab-01-margin-inventory-triage/verify.sh` en la terminal para mostrar las 2 pruebas fallidas (`test_promo_pricing_enforces_minimum_margin_floor` y `test_true_atp_deducts_bopis_damaged_and_safety_stock`).
2. Pegar el **Prompt 1A** (Técnico) o **Prompt 1B** (Comercial) de `labs/lab-01-margin-inventory-triage/PROMPTS.es.md` para diagnosticar el Bug #1A y el Bug #1B.
3. Pegar el **Prompt 2** (`/plan`) para generar un artefacto estructurado de plan de implementación.
4. Seleccionar `calculate_stacked_promo_price` en `src/services/promo_pricing.py`, presionar `Cmd+I` / `Ctrl+I` y aplicar el piso de margen del 15% (`unit_cost_usd / (1.0 - minimum_margin_pct)`).
5. Pedir a Antigravity que corrija `calculate_node_atp` en `src/services/inventory_atp.py` (`max(0, on_hand - reserved_bopis - damaged_hold - safety_stock)`) y ejecute `./labs/lab-01-margin-inventory-triage/verify.sh`.
6. En el navegador (`http://127.0.0.1:8000`), hacer clic en **"1. Enforce 15% Margin Floor (Lab 01)"** y mostrar cómo los pedidos en Margin Hold bajan de `30` a `0` (`$0.00` de fuga).

---

### Módulo 2: Laboratorio 02 — Personalizaciones (`GEMINI.md`, Reglas y Skills) (`01:15 - 02:00`)

#### Capacidades Demostradas
- Memoria del Workspace (`GEMINI.md`)
- Reglas de Dominio (`.agents/rules/retail-standards.md`)
- Skills Reutilizables con Frontmatter YAML + Scripts Auxiliares (`.agents/skills/retail-otif-margin-auditor/SKILL.md` + `scripts/run_otif_margin_audit.py`)
- Comando Slash `/learn`

#### Pasos de la Demo en Vivo
1. Ejecutar `./labs/lab-02-rules-and-skills/install.sh` y `./labs/lab-02-rules-and-skills/verify.sh`.
2. Explicar la **Jerarquía de Personalización de Antigravity**:
   - **Memoria permanente del workspace**: `GEMINI.md`
   - **Guardrails específicos de dominio**: `.agents/rules/retail-standards.md` (validación GS1 Módulo-10 GTIN-14, piso de margen del 15%, niveles de penalización OTIF: 85%–89.99% -> 3%, 80%–84.99% -> 5%, <80% -> 8%)
   - **Flujos procedimentales bajo demanda**: `.agents/skills/retail-otif-margin-auditor/SKILL.md`
3. Ejecutar el **Prompt 4A** de `labs/lab-02-rules-and-skills/PROMPTS.es.md` (o usar `/learn`) para generar los tres archivos.
4. Ejecutar `./labs/lab-02-rules-and-skills/verify.sh` y luego invocar la skill con el **Prompt 5B**:
   - Mostrar la tabla ejecutiva en Markdown identificando **6 proveedores en incumplimiento** y **$98,250.00 en chargebacks recuperables** (`VND-APEX-01`: `$31,200`, `VND-LUXE-02`: `$14,250`, `VND-SOLAR-04`: `$24,800`, `VND-VELO-05`: `$7,600`, `VND-KINETIC-07`: `$9,900`, `VND-OMNI-09`: `$10,500`).

---

### Módulo 3: Laboratorio 03 — Servidor FastMCP, Hooks Deterministas y Seguridad Empresarial (`02:00 - 02:55`)

#### Capacidades Demostradas
- Servidor FastMCP (`mcp_server/retail_mcp.py` y `.agents/mcp_config.json`)
- Hooks Deterministas de Ciclo de Vida (`.agents/hooks.json` y `scripts/margin_guard_hook.py` -> `data/logs/hook_compliance_audit.jsonl`)
- **Inmersión Profunda en Gobernanza Empresarial**: Google Cloud IAM / Cloud Audit Logs / VPC-SC + Controles de Sandbox y Permisos del Cliente Antigravity

#### Pasos de la Demo en Vivo (Parte A — MCP y Hooks)
1. Ejecutar `./labs/lab-03-mcp-and-hooks/install.sh` y `./labs/lab-03-mcp-and-hooks/verify.sh`.
2. Abrir `mcp_server/retail_mcp.py` y mostrar las 2 herramientas implementadas (`query_true_atp_inventory`, `audit_vendor_otif_contracts`) y los 2 stubs (`simulate_promo_margin_guard`, `list_at_risk_vip_orders`).
3. Ejecutar el **Prompt 4A** de `labs/lab-03-mcp-and-hooks/PROMPTS.es.md` para implementar ambas herramientas MCP y crear `.agents/mcp_config.json` y `.agents/hooks.json`.
4. **Demo en Vivo de Bloqueo por Hook ante Intento Adversario**:
   Ejecutar el siguiente comando en la terminal para simular que un agente o usuario intenta desactivar el piso de margen del 15% (`enforce_floor=False`):
   ```bash
   echo '{"tool_name":"edit_file","tool_input":{"Path":"src/services/promo_pricing.py","Replacement":"enforce_floor=False"}}' | .venv/bin/python scripts/margin_guard_hook.py
   ```
   Mostrar el mensaje `[MARGIN_GUARD_HOOK BLOCKED]` (código de salida `2`) e inspeccionar el log inmutable de cumplimiento:
   ```bash
   cat data/logs/hook_compliance_audit.jsonl
   ```
5. Ejecutar `./labs/lab-03-mcp-and-hooks/verify.sh` para confirmar que pasan las 5/5 pruebas.

#### Pasos de la Demo en Vivo (Parte B — Recorrido de Seguridad y Gobernanza Empresarial)
Guiar a la audiencia a través de las dos capas de gobernanza empresarial documentadas en `labs/lab-03-mcp-and-hooks/README.es.md`:

1. **Capa 1: Plano de Administración en Google Cloud & Gemini Enterprise**:
   - **Identidad y Gestión de Licencias**: Mostrar cómo los administradores empresariales asignan `roles/cloudaicompanion.user` en Google Cloud IAM vinculado a grupos de Cloud Identity / Okta / Entra ID (`retail-engineering@`, `retail-merchandising@`).
   - **Cloud Audit Logging (`cloudaicompanion.googleapis.com`)**: Compartir este filtro exacto de Google Cloud Logging que los equipos SecOps utilizan para auditar la actividad de Gemini Enterprise en BigQuery / Chronicle SIEM:
     ```text
     protoPayload.serviceName="cloudaicompanion.googleapis.com"
     AND logName=("projects/YOUR_GCP_PROJECT/logs/cloudaudit.googleapis.com%2Factivity"
       OR "projects/YOUR_GCP_PROJECT/logs/cloudaudit.googleapis.com%2Fdata_access")
     ```
   - **Cero Retención de Datos y Sin Entrenamiento de Modelos Fundacionales**: Enfatizar que los costos mayoristas, contratos SLA de proveedores y código fuente propietario jamás se retienen ni se usan para entrenar modelos de Google.
   - **VPC Service Controls (VPC-SC) y Endpoints Regionales**: Explicar cómo `cloudaicompanion.googleapis.com` opera dentro de un perímetro VPC-SC junto con BigQuery y Cloud SQL.

2. **Capa 2: Controles de Seguridad del Cliente y Workspace de Antigravity**:
   - Abrir el panel de Configuración de Antigravity y demostrar:
     - **Política de Ejecución de Herramientas**: `strict`, `request-review`, `proceed-in-sandbox`, `always-proceed`.
     - **Sandbox de Terminal y Aislamiento de Red**: Sandboxing a nivel de SO e interruptor de red saliente.
     - **Acceso a Archivos Fuera del Workspace**: Bloqueo de lecturas/escrituras fuera de `/antigravity-workshop-retail`.
     - **Lista Blanca / Negra de Comandos y Lista Blanca del Navegador**: Permitir `.venv/bin/python -m pytest` y restringir `/browser` a `http://127.0.0.1:8000`.
     - **Hooks Deterministas (`.agents/hooks.json`)**: Aplicación de políticas antes de ejecutar herramientas registrando cada evento en `data/logs/hook_compliance_audit.jsonl`.

---

### Módulo 4: Laboratorio 04 — Capstone Multi-Agente: Enrutamiento Inteligente Omnicanal (`02:55 - 03:45`)

#### Capacidades Demostradas
- `/plan` y `/boost` para diseño de optimización multi-restricción
- `/teamwork` y Orquestación de Subagentes (`invoke_subagent`)
- Verificación Visual en Vivo con `/browser`

#### Pasos de la Demo en Vivo
1. Ejecutar `./labs/lab-04-multi-agent-capstone/install.sh` y `./labs/lab-04-multi-agent-capstone/verify.sh`.
2. Mostrar `src/services/fulfillment_router.py` donde `evaluate_candidates` y `optimize_at_risk_orders` lanzan `NotImplementedError`.
3. Pegar el **Prompt 1A (`/plan`)** o el **Prompt 2A (`/teamwork`)** de `labs/lab-04-multi-agent-capstone/PROMPTS.es.md` para implementar el motor de enrutamiento y ejecutar la suite completa de pruebas.
4. Ejecutar `./labs/lab-04-multi-agent-capstone/verify.sh` y celebrar las **16/16 pruebas aprobadas** en los Laboratorios 01, 02, 03 y 04.
5. Volver a `http://127.0.0.1:8000` (o invocar el **Prompt 4 (`/browser`)**):
   - Hacer clic en **"1. Enforce 15% Margin Floor (Lab 01)"** -> `0` pedidos en Margin Hold (`$0.00` de fuga).
   - Hacer clic en **"2. Optimize Split-Shipment Routing (Lab 04)"** -> Los `35` pedidos VIP en riesgo son re-enrutados (`+$250,000` LTV salvado, `$14,774.00` de margen neto post-envío preservado).
   - Hacer clic en **"3. Claim OTIF Chargebacks (Lab 02/04)"** -> Los `6` contratos de proveedores en incumplimiento pasan a `CHARGEBACK_CLAIMED` (`$98,250.00` recuperados).

---

## 3. Resumen de Métricas Financieras y Operativas Verificadas

Utiliza esta tabla de referencia durante la sesión de preguntas y respuestas ejecutivas para explicar las cifras deterministas en `data/seed_retail_data.py`:

| Métrica | Estado Inicial de Crisis (Starter) | Estado Post-Remediación (Solution) | Verificado Por |
| :--- | :--- | :--- | :--- |
| **Pedidos en Margin Hold (`MARGIN_HOLD`)** | `30` pedidos (`-$35,113.25` de fuga de margen negativo) | `0` pedidos (`$0.00` de fuga; ajustados al piso de margen bruto `>= 15%`) | `tests/test_lab01_triage.py` |
| **Pedidos VIP en Riesgo (`AT_RISK_STOCKOUT`)** | `35` pedidos VIP (`DIAMOND`/`GOLD`) (`>$250,000` Customer LTV expuesto) | `0` pedidos en riesgo (`35` re-enrutados a `REROUTED_OPTIMAL` con `$14,774.00` de margen neto post-envío) | `tests/test_lab04_capstone.py` |
| **Incumplimientos OTIF (`BREACH_DETECTED`)** | `6` contratos en incumplimiento (`$98,250.00` en penalizaciones sin reclamar entre `10` proveedores) | `6` contratos actualizados a `CHARGEBACK_CLAIMED` (`$98,250.00` recuperados) | `tests/test_lab02_rules_skills.py` y `tests/test_lab04_capstone.py` |
| **Auditoría de Cumplimiento del Hook PreToolUse** | Desprotegido ante ediciones `enforce_floor=False` | Bloqueo determinista con código `2` + log JSONL en `data/logs/hook_compliance_audit.jsonl` | `tests/test_lab03_mcp_hooks.py` |
