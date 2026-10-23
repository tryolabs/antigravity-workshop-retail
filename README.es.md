<div align="center">
  <img src="src/static/tryolabs-logo.png" alt="Tryolabs Logo" height="48" />
  <h1>Retail Pulse — Taller Práctico de Google Antigravity</h1>
  <p><strong>Plataforma de Inteligencia Omnicanal de Órdenes, Sincronización de Inventario, Margen Comercial y Contratos de Proveedores</strong></p>
  <p><em>Impartido por <strong>Tryolabs</strong> | Taller Empresarial de 4 Horas para Retail y Comercio Omnicanal</em></p>
  <p><a href="README.md"><strong>English</strong></a> | <a href="README.es.md"><strong>Español</strong></a> | <a href="INSTRUCTOR_DEMO_GUIDE.md"><strong>Instructor Demo Guide (EN)</strong></a> | <a href="INSTRUCTOR_DEMO_GUIDE.es.md"><strong>Guía del Instructor (ES)</strong></a></p>
</div>

---

## 1. Resumen Ejecutivo y Diseño de Doble Track

Bienvenido al **Taller de la Industria Retail de Google Antigravity**, diseñado e impartido por **Tryolabs**.

Durante eventos estacionales pico (Flash Sales / Black Friday), las empresas retail enfrentan una crisis simultánea entre **Ingeniería de Plataforma** y **Operaciones Comerciales / Merchandising**:
1. **Apilamiento Descontrolado de Descuentos Promocionales (`-$35,113.25` de Fuga de Margen)**: Los códigos promocionales se apilan multiplicativamente con descuentos de lealtad sin aplicar el piso de margen bruto del 15% (`minimum_margin_pct`), vendiendo productos insignia por debajo del costo mayorista.
2. **Inventario Fantasma y Riesgo de Quiebre de Stock (`$250,000+` de LTV VIP Expuesto)**: El motor Available-to-Promise (`ATP`) consulta `on_hand_qty` bruto ignorando `reserved_bopis_qty`, `damaged_hold_qty` y `safety_stock_qty`, dejando **35 órdenes VIP (`DIAMOND`/`GOLD`)** bloqueadas en `AT_RISK_STOCKOUT`.
3. **Penalidades OTIF de Proveedores No Reclamadas (`$98,250.00` en Chargebacks Recuperables)**: 6 de los 10 proveedores estratégicos incumplen sus SLAs contractuales On-Time In-Full (`OTIF`) (`actual_otif_pct < contracted_otif_pct`), dejando casi `$100K` en notas de débito sin reclamar.

Este repositorio soporta **tanto a Ingenieros Técnicos como a Líderes Comerciales/Operaciones** trabajando en equipo:
- **Track Técnico (Ingenieros de Software, Datos y Plataforma)**: Depuran microservicios Python/FastAPI, escriben pruebas `pytest`, construyen herramientas FastMCP (`mcp_server/retail_mcp.py`), aplican hooks deterministas `PreToolUse` (`scripts/margin_guard_hook.py`), orquestan sistemas multi-agente con **Google ADK (Agent Development Kit)** y **A2A (Agent2Agent Protocol)** (`src/agents/adk_a2a_orchestrator.py`), prueban interactivamente con **`adk web`** (`scripts/run_adk_web.sh`), y despliegan en **Google Cloud Run + Gemini Enterprise** usando **Terraform** (`infra/terraform/`).
- **Track Comercial (Merchandising, Category Management y Supply Chain)**: Auditan exportaciones CSV (`data/exports/`), codifican reglas corporativas de margen y OTIF (`GEMINI.md`, `.agents/rules/retail-standards.md`), crean skills ejecutivos reutilizables (`.agents/skills/`), consultan bases de datos retail en lenguaje natural vía MCP, y validan KPIs en el **Retail Pulse Command Center** (`http://127.0.0.1:8000`) y **ADK Web UI** (`http://127.0.0.1:8080`).

---

## 2. Arquitectura del Sistema (Antigravity + FastMCP + Google ADK + A2A + Cloud Run)

```text
+---------------------------------------------------------------------------------------------------+
|                           GOOGLE ANTIGRAVITY IDE & AGENT RUNTIME                                  |
|  - Comandos Slash: /plan, /boost, /teamwork, /browser, /learn, /compact, /goal                    |
|  - Personalizaciones: GEMINI.md | .agents/rules/ | .agents/skills/ | .agents/hooks.json           |
+------------------+-----------------------------------+-----------------------------------+--------+
                   |                                   |                                   |
     Stdio FastMCP |                      HTTP / REST  |                 A2A JSON-RPC 2.0  |
                   v                                   v                                   v
+------------------+-------------------+ +-------------+--------------------+ +------------+--------+
| MCP SERVER (mcp_server/retail_mcp.py)| | FASTAPI COMMAND CENTER (main.py) | | GOOGLE ADK & A2A    |
| - query_true_atp_inventory           | | - Web UI: src/static/index.html  | | - /.well-known/     |
| - audit_vendor_otif_contracts        | | - promo_pricing.py (Lab 01)      | |   agent.json        |
| - simulate_promo_margin_guard        | | - inventory_atp.py (Lab 01)      | | - POST /api/v1/a2a  |
| - list_at_risk_vip_orders            | | - fulfillment_router.py (Lab 04) | | - adk web (:8080)   |
+------------------+-------------------+ +-------------+--------------------+ +------------+--------+
                   |                                   |                                   |
                   +-----------------------------------+-----------------------------------+
                                                       |
                                                       v
+---------------------------------------------------------------------------------------------------+
|                CAPA DE DATOS DETERMINISTA (data/) Y DESPLIEGUE CLOUD (infra/ + deploy/)           |
|  - SQLite DB: data/retail_pulse.db | Exportaciones CSV: data/exports/ | Logs: data/logs/          |
|  - Terraform IaC: infra/terraform/ (Cloud Run v2 + Artifact Registry + Vertex AI + IAM)           |
|  - Registro en Gemini Enterprise: deploy/register_gemini_enterprise_agent.sh                      |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. Currículo de 4 Horas y Matriz de Laboratorios

| Módulo | Duración | Área de Enfoque y Capacidades de Antigravity | Guía del Lab y Playbook de Prompts | Scripts de Automatización |
| :--- | :--- | :--- | :--- | :--- |
| **Setup y Briefing** | `00:00 - 00:30` | Configuración del entorno, tour por el Retail Pulse Command Center, vista general de Antigravity IDE + Agent Manager | [Guía del Instructor (ES)](INSTRUCTOR_DEMO_GUIDE.es.md) / [EN](INSTRUCTOR_DEMO_GUIDE.md) | `./install.sh` (o `./install.ps1`) |
| **Lab 01** | `00:30 - 01:15` | **Triage Omnicanal en Flash-Sale**: Menciones `@`, `/plan`, Edición en Línea (`Cmd+I`), corrección de Apilamiento Promocional (Bug #1A) e Inventario Fantasma True ATP (Bug #1B) | [Guía Lab 01 (ES)](labs/lab-01-margin-inventory-triage/README.es.md) \| [EN](labs/lab-01-margin-inventory-triage/README.md)<br>[Prompts (ES)](labs/lab-01-margin-inventory-triage/PROMPTS.es.md) \| [EN](labs/lab-01-margin-inventory-triage/PROMPTS.md) | `labs/lab-01-margin-inventory-triage/{install.sh,verify.sh,apply_solution.sh,deploy_gcp.sh}` |
| **Lab 02** | `01:15 - 02:00` | **Personalizaciones (`GEMINI.md`, Rules y Skills)**: Codificación de GS1 GTIN-14, piso de margen del 15% y estándares OTIF en `.agents/rules/retail-standards.md` y creación de `.agents/skills/margin-otif-audit/SKILL.md` | [Guía Lab 02 (ES)](labs/lab-02-rules-and-skills/README.es.md) \| [EN](labs/lab-02-rules-and-skills/README.md)<br>[Prompts (ES)](labs/lab-02-rules-and-skills/PROMPTS.es.md) \| [EN](labs/lab-02-rules-and-skills/PROMPTS.md) | `labs/lab-02-rules-and-skills/{install.sh,verify.sh,apply_solution.sh,deploy_gcp.sh}` |
| **Lab 03** | `02:00 - 02:55` | **Servidor FastMCP, Hooks Deterministas y Gobernanza Empresarial**: Construcción de `mcp_server/retail_mcp.py`, `.agents/mcp_config.json`, hook `PreToolUse` (`scripts/margin_guard_hook.py`) y Seguridad en Gemini Enterprise / Google Cloud | [Guía Lab 03 (ES)](labs/lab-03-mcp-and-hooks/README.es.md) \| [EN](labs/lab-03-mcp-and-hooks/README.md)<br>[Prompts (ES)](labs/lab-03-mcp-and-hooks/PROMPTS.es.md) \| [EN](labs/lab-03-mcp-and-hooks/PROMPTS.md) | `labs/lab-03-mcp-and-hooks/{install.sh,verify.sh,apply_solution.sh,deploy_gcp.sh}` |
| **Lab 04** | `02:55 - 03:45` | **Capstone Multi-Agente (Google ADK, A2A, `adk web`, Cloud Run y Gemini Enterprise)**: Enrutamiento Omnicanal (`fulfillment_router.py`), Orquestador ADK + A2A (`adk_a2a_orchestrator.py`), pruebas con `adk web` y despliegue Terraform a Cloud Run y Gemini Enterprise | [Guía Lab 04 (ES)](labs/lab-04-multi-agent-capstone/README.es.md) \| [EN](labs/lab-04-multi-agent-capstone/README.md)<br>[Prompts (ES)](labs/lab-04-multi-agent-capstone/PROMPTS.es.md) \| [EN](labs/lab-04-multi-agent-capstone/PROMPTS.md) | `labs/lab-04-multi-agent-capstone/{install.sh,verify.sh,apply_solution.sh,deploy_gcp.sh}` |
| **Cierre** | `03:45 - 04:00` | Patrones de despliegue en producción y Q&A con arquitectos de Tryolabs | [Guía del Instructor (ES)](INSTRUCTOR_DEMO_GUIDE.es.md) | `./labs/lab-04-multi-agent-capstone/verify.sh` |

---

## 4. Instrucciones de Inicio Rápido

### Prerrequisitos
- **Python 3.10+**
- **Google Antigravity** (IDE de escritorio o CLI `agy`)
- macOS, Linux o Windows (PowerShell)

### 1. Inicializar el Entorno del Taller
Ejecuta el instalador raíz para crear el entorno virtual `.venv`, instalar dependencias (`fastapi`, `uvicorn`, `pydantic`, `pytest`, `httpx`, `mcp`, `google-adk`), poblar la base de datos determinista (`data/retail_pulse.db`), generar exportaciones CSV (`data/exports/`) e inicializar el **Estado Inicial del Lab 01**:

**macOS / Linux:**
```bash
./install.sh
```

**Windows (PowerShell):**
```powershell
.\install.ps1
```

### 2. Iniciar el Retail Pulse Command Center en Vivo
Inicia el servidor FastAPI y abre `http://127.0.0.1:8000` en tu navegador:

```bash
.venv/bin/uvicorn src.main:app --reload --port 8000
```

Verás el **Retail Pulse Command Center** (con la insignia **Delivered by Tryolabs**) mostrando los KPIs iniciales de la crisis:
- **Margin Hold Orders**: `30` órdenes (`-$35,113.25` de fuga de margen)
- **VIP Stockout Risk**: `35` órdenes VIP (`$250,000+` de LTV de clientes expuesto)
- **OTIF Chargeback Recovery**: `6` proveedores en incumplimiento (`$98,250.00` en penalidades recuperables)

### 3. Probar la Orquestación Multi-Agente Localmente con `adk web` (Lab 04)
Inicia la interfaz interactiva **Google ADK Development UI** para inspeccionar `retail_pulse_root_agent` y sus sub-agentes (`wms_inventory_agent`, `merchandising_margin_agent` y `a2a_bridge_agent`):

```bash
# Validación en modo dry-run:
./scripts/run_adk_web.sh --dry-run

# Iniciar la interfaz interactiva ADK Web UI en http://127.0.0.1:8080:
./scripts/run_adk_web.sh --port 8080
```

### 4. Desplegar en Google Cloud Run con Terraform y Registrar en Gemini Enterprise
Valida o ejecuta el pipeline completo de despliegue en Cloud Run + Terraform + registro A2A en Gemini Enterprise:

```bash
# Validación dry-run (no requiere credenciales de GCP):
./deploy/deploy_gcp.sh --dry-run --project-id mi-proyecto-retail-gcp --region us-central1 --gemini-app-id retail-pulse-enterprise-app

# Despliegue en vivo en GCP y registro en Gemini Enterprise:
./deploy/deploy_gcp.sh --project-id TU_GCP_PROJECT_ID --region us-central1 --gemini-app-id TU_GEMINI_ENTERPRISE_APP_ID
```

### 5. Scripts por Laboratorio (`install.sh`, `verify.sh`, `apply_solution.sh`, `deploy_gcp.sh`)
Cada carpeta de laboratorio (`labs/lab-01-*` a `labs/lab-04-*`) es totalmente autónoma e incluye:
- `./labs/<lab-name>/install.sh` — Restaura el workspace al estado inicial exacto de ese laboratorio (aplicando automáticamente los prerrequisitos de laboratorios previos).
- `./labs/<lab-name>/verify.sh` — Ejecuta la suite automatizada de pruebas `pytest` para ese laboratorio.
- `./labs/<lab-name>/apply_solution.sh` — Aplica instantáneamente la solución de referencia de ese laboratorio.
- `./labs/<lab-name>/deploy_gcp.sh` — Despliega el microservicio y agente A2A del laboratorio en Google Cloud Run mediante Terraform.

---

## 5. Seguridad Empresarial, Privacidad y Gobernanza (Google Cloud + Antigravity)

Las empresas retail requieren defensa en profundidad a través de identidad cloud, privacidad de datos, perímetros de red y ejecución local de agentes. Este taller demuestra el **modelo de gobernanza de dos capas** cubierto en detalle en el [Lab 03](labs/lab-03-mcp-and-hooks/README.es.md):

### Capa 1: Gobernanza en Google Cloud y Gemini Enterprise (Plano de Administración Cloud)
- **IAM y Asignación de Licencias**: Aprovisiona acceso mediante el rol IAM `roles/cloudaicompanion.user` federado con grupos SSO en **Cloud Identity, Okta o Microsoft Entra ID (Azure AD)**.
- **Cloud Audit Logs (`cloudaicompanion.googleapis.com`)**: Habilita registros de Actividad de Administración y Acceso a Datos en **Google Cloud Logging** para capturar una traza de auditoría inmutable de cada invocación a la API, identidad de usuario, marca de tiempo y metadatos del proyecto, con enrutamiento opcional vía Log Sinks hacia BigQuery o Chronicle SIEM.
- **Cero Retención de Datos y Sin Entrenamiento de Modelos Base**: Los prompts, esquemas SQL, tablas de costos mayoristas, contratos SLA de proveedores y código fuente **nunca se utilizan para entrenar modelos fundacionales de Google** y permanecen estrictamente aislados dentro del perímetro empresarial.
- **VPC Service Controls (VPC-SC) y Endpoints Regionales**: Protege `cloudaicompanion.googleapis.com` dentro de un perímetro VPC-SC junto con BigQuery y Cloud SQL para prevenir exfiltración de datos, respaldado por la indemnización de propiedad intelectual de Google Cloud.

### Capa 2: Controles de Seguridad del Cliente Antigravity y Workspace (Plano de Ejecución Local)
- **Política de Ejecución de Herramientas**: Configura `strict`, `request-review`, `proceed-in-sandbox` o `always-proceed` para gobernar cuándo los comandos de terminal o escrituras de archivos requieren aprobación humana.
- **Sandbox de Terminal y Aislamiento de Red**: Aplica sandboxing a nivel de sistema operativo (`sandbox-exec` en macOS / namespaces en Linux) y restringe el acceso saliente a internet.
- **Protección contra Acceso Fuera del Workspace**: Impide que los agentes lean o modifiquen archivos fuera del directorio `/antigravity-workshop-retail` (protegiendo `~/.ssh`, `~/.aws` y credenciales locales).
- **Allowlist / Denylist de Comandos y Navegador**: Autoriza ejecutores de pruebas seguros (`.venv/bin/python -m pytest`), bloquea comandos destructivos (`rm -rf`, `curl`) y restringe `/browser` a `http://127.0.0.1:8000`.
- **Hooks Deterministas de Ciclo de Vida (`.agents/hooks.json`)**: Ejecuta validación determinista previa a la herramienta (`scripts/margin_guard_hook.py`) antes de cualquier modificación de archivo, bloqueando intentos de desactivar el piso de margen del 15% con código de salida `2` y registrando cada decisión en `data/logs/hook_compliance_audit.jsonl`.
