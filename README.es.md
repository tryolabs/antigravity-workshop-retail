<div align="center">
  <img src="src/static/tryolabs-logo.png" alt="Tryolabs Logo" height="48" />
  <h1>Retail Pulse — Workshop Práctico de Google Antigravity</h1>
  <p><strong>Plataforma de Inteligencia de Pedidos Omnicanal, Sincronización de Inventario y Márgenes / Contratos de Proveedores</strong></p>
  <p><em>Impartido por <strong>Tryolabs</strong> | Workshop Empresarial de 4 Horas para Retail y Comercio Omnicanal</em></p>
  <p><a href="README.md"><strong>English</strong></a> | <a href="README.es.md"><strong>Español</strong></a> | <a href="INSTRUCTOR_DEMO_GUIDE.md"><strong>Instructor Demo Guide (EN)</strong></a> | <a href="INSTRUCTOR_DEMO_GUIDE.es.md"><strong>Guía del Instructor (ES)</strong></a></p>
</div>

---

## 1. Resumen Ejecutivo y Diseño de Doble Track

Bienvenido al **Workshop de la Industria Retail de Google Antigravity**, diseñado e impartido por **Tryolabs**.

Durante eventos estacionales pico (Flash Sales / Black Friday), las empresas de retail enfrentan una crisis simultánea entre **Ingeniería de Plataforma** y **Operaciones Comerciales / Merchandising**:
1. **Acumulación de Descuentos Promocionales sin Límite (`-$35,113.25` de Fuga de Margen)**: Los códigos promocionales de campaña se acumulan multiplicativamente con los descuentos por nivel de lealtad sin aplicar el piso mínimo de margen bruto del 15% (`minimum_margin_pct`), vendiendo productos insignia por debajo de su costo mayorista unitario.
2. **Inventario Fantasma y Riesgo de Quiebre de Stock (`+$250,000` de LTV VIP Expuesto)**: El motor Available-to-Promise (`ATP`) consulta `on_hand_qty` bruto ignorando `reserved_bopis_qty`, `damaged_hold_qty` y `safety_stock_qty`, dejando **35 pedidos VIP (`DIAMOND`/`GOLD`)** bloqueados en estado `AT_RISK_STOCKOUT`.
3. **Penalizaciones OTIF de Proveedores sin Reclamar (`$98,250.00` en Chargebacks Recuperables)**: 6 de los 10 proveedores estratégicos incumplen sus SLAs contractuales On-Time In-Full (`OTIF`) (`actual_otif_pct < otif_target_pct`), dejando casi `$100K` en penalizaciones contractuales sin reclamar.

Este repositorio soporta **tanto a Ingenieros Técnicos como a Gerentes Comerciales/Operativos** trabajando en equipo:
- **Track Técnico (Ingenieros de Software, Datos y Plataforma)**: Depuran microservicios Python/FastAPI, escriben suites de `pytest`, construyen herramientas FastMCP (`mcp_server/retail_mcp.py`), aplican hooks deterministas `PreToolUse` (`scripts/margin_guard_hook.py`) y orquestan el enrutamiento omnicanal multi-agente (`src/services/fulfillment_router.py`).
- **Track Comercial (Merchandising, Gestión de Categorías y Supply Chain)**: Auditan exportaciones CSV (`data/exports/`), codifican reglas corporativas de margen y OTIF (`GEMINI.md`, `.agents/rules/retail-standards.md`), crean skills reutilizables de auditoría ejecutiva (`.agents/skills/`), consultan bases de datos en vivo mediante herramientas MCP en lenguaje natural y validan KPIs en el **Centro de Comando de Retail Pulse** (`http://127.0.0.1:8000`).

---

## 2. Arquitectura del Sistema

```
+---------------------------------------------------------------------------------------------------+
|                           GOOGLE ANTIGRAVITY IDE & AGENT RUNTIME                                  |
|  - Comandos Slash: /plan, /boost, /teamwork, /browser, /learn, /compact, /goal                    |
|  - Personalizaciones: GEMINI.md | .agents/rules/ | .agents/skills/ | .agents/hooks.json           |
+------------------------------------+-----------------------------------+--------------------------+
                                     |                                   |
                   Stdio FastMCP     |                                   | HTTP / REST & /browser
                                     v                                   v
+------------------------------------+-----------------------------------+--------------------------+
|  SERVIDOR MCP (mcp_server/retail_mcp.py)     |  APP FASTAPI & CENTRO DE COMANDO (src/main.py)     |
|  - query_true_atp_inventory                  |  - UI Web: src/static/index.html (Marca Tryolabs)  |
|  - audit_vendor_otif_contracts               |  - Precios Promo: src/services/promo_pricing.py    |
|  - simulate_promo_margin_guard               |  - True ATP Sync: src/services/inventory_atp.py    |
|  - list_at_risk_vip_orders                   |  - Auditor OTIF:  src/services/vendor_otif_auditor |
|                                              |  - Router Óptimo: src/services/fulfillment_router  |
+------------------------------------+---------+-------------------------+--------------------------+
                                     |                                   |
                                     +-----------------+-----------------+
                                                       |
                                                       v
+---------------------------------------------------------------------------------------------------+
|                           CAPA DE DATOS DETERMINISTA DE RETAIL (data/)                            |
|  - Base SQLite: data/retail_pulse.db (vendor_contracts, wms_inventory, promo_campaigns, orders)   |
|  - Exportaciones CSV Comerciales: data/exports/{vendor_contracts,wms_inventory,orders}.csv        |
|  - Logs de Webhooks y Cumplimiento: data/logs/{pos_wms_webhooks.jsonl, hook_compliance_audit.jsonl}|
+---------------------------------------------------------------------------------------------------+
```

---

## 3. Agenda del Workshop de 4 Horas y Matriz de Laboratorios

| Módulo | Duración | Área de Enfoque y Capacidades de Antigravity | Guía de Laboratorio y Playbook de Prompts | Scripts de Automatización |
| :--- | :--- | :--- | :--- | :--- |
| **Setup e Introducción** | `00:00 - 00:30` | Configuración de entorno, recorrido por el Centro de Comando Retail Pulse, vista general de Antigravity IDE + Agent Manager | [Guía del Instructor (ES)](INSTRUCTOR_DEMO_GUIDE.es.md) / [EN](INSTRUCTOR_DEMO_GUIDE.md) | `./install.sh` (o `./install.ps1`) |
| **Lab 01** | `00:30 - 01:15` | **Triaje Omnicanal de Flash-Sale**: Menciones `@`, `/plan`, Edición en Línea (`Cmd+I`), corrección de Acumulación de Márgenes Promo (Bug #1A) e Inventario Fantasma ATP (Bug #1B) | [Guía Lab 01 (ES)](labs/lab-01-margin-inventory-triage/README.es.md) \| [EN](labs/lab-01-margin-inventory-triage/README.md)<br>[Prompts (ES)](labs/lab-01-margin-inventory-triage/PROMPTS.es.md) \| [EN](labs/lab-01-margin-inventory-triage/PROMPTS.md) | `labs/lab-01-margin-inventory-triage/{install.sh,verify.sh,apply_solution.sh}` |
| **Lab 02** | `01:15 - 02:00` | **Personalizaciones (`GEMINI.md`, Reglas y Skills)**: Codificación de estándares GS1 GTIN-14, piso de margen del 15% y OTIF en `.agents/rules/retail-standards.md` y creación de `.agents/skills/retail-otif-margin-auditor/SKILL.md` | [Guía Lab 02 (ES)](labs/lab-02-rules-and-skills/README.es.md) \| [EN](labs/lab-02-rules-and-skills/README.md)<br>[Prompts (ES)](labs/lab-02-rules-and-skills/PROMPTS.es.md) \| [EN](labs/lab-02-rules-and-skills/PROMPTS.md) | `labs/lab-02-rules-and-skills/{install.sh,verify.sh,apply_solution.sh}` |
| **Lab 03** | `02:00 - 02:55` | **Servidor FastMCP, Hooks Deterministas y Gobernanza Empresarial**: Construcción de `mcp_server/retail_mcp.py`, `.agents/mcp_config.json`, hook `PreToolUse` (`scripts/margin_guard_hook.py`) y Seguridad en Gemini Enterprise / Cloud | [Guía Lab 03 (ES)](labs/lab-03-mcp-and-hooks/README.es.md) \| [EN](labs/lab-03-mcp-and-hooks/README.md)<br>[Prompts (ES)](labs/lab-03-mcp-and-hooks/PROMPTS.es.md) \| [EN](labs/lab-03-mcp-and-hooks/PROMPTS.md) | `labs/lab-03-mcp-and-hooks/{install.sh,verify.sh,apply_solution.sh}` |
| **Lab 04** | `02:55 - 03:45` | **Capstone Multi-Agente**: Orquestación de `/plan`, `/boost`, `/teamwork` y `/browser` para construir el Enrutamiento Inteligente (`src/services/fulfillment_router.py`) y salvar 35 pedidos VIP (`$14,774` margen neto) | [Guía Lab 04 (ES)](labs/lab-04-multi-agent-capstone/README.es.md) \| [EN](labs/lab-04-multi-agent-capstone/README.md)<br>[Prompts (ES)](labs/lab-04-multi-agent-capstone/PROMPTS.es.md) \| [EN](labs/lab-04-multi-agent-capstone/PROMPTS.md) | `labs/lab-04-multi-agent-capstone/{install.sh,verify.sh,apply_solution.sh}` |
| **Cierre** | `03:45 - 04:00` | Patrones de despliegue en producción, preguntas y respuestas con arquitectos de soluciones de Tryolabs | [Guía del Instructor (ES)](INSTRUCTOR_DEMO_GUIDE.es.md) | `./labs/lab-04-multi-agent-capstone/verify.sh` |

---

## 4. Instrucciones de Inicio Rápido

### Prerrequisitos
- **Python 3.10+**
- **Google Antigravity** (IDE de escritorio o CLI `agy`)
- macOS, Linux o Windows (PowerShell)

### 1. Inicializar el Entorno del Workshop
Ejecuta el instalador raíz para crear el entorno virtual `.venv`, instalar dependencias (`fastapi`, `uvicorn`, `pydantic`, `pytest`, `httpx`, `mcp`), poblar la base de datos determinista de retail (`data/retail_pulse.db`), generar exportaciones CSV (`data/exports/`) e inicializar el **Estado Inicial del Laboratorio 01**:

**macOS / Linux:**
```bash
./install.sh
```

**Windows (PowerShell):**
```powershell
.\install.ps1
```

### 2. Iniciar el Centro de Comando en Vivo de Retail Pulse
Inicia el servidor FastAPI y abre `http://127.0.0.1:8000` en tu navegador:

```bash
.venv/bin/uvicorn src.main:app --reload --port 8000
```

Verás el **Centro de Comando de Retail Pulse** (con la insignia **Delivered by Tryolabs**) mostrando las métricas iniciales de la crisis:
- **Margin Hold Orders**: `30` pedidos (`-$35,113.25` de fuga de margen)
- **VIP Stockout Risk**: `35` pedidos VIP (`+$250,000` de LTV de clientes expuesto)
- **OTIF Chargeback Recovery**: `6` proveedores en incumplimiento (`$98,250.00` en penalizaciones recuperables)

### 3. Ejecutar Instaladores, Verificadores y Soluciones por Laboratorio
Cada carpeta de laboratorio (`labs/lab-01-*` a `labs/lab-04-*`) es completamente autónoma e incluye:
- `./labs/<lab-name>/install.sh` — Restablece el workspace al estado inicial exacto de ese laboratorio (aplicando automáticamente los prerrequisitos de laboratorios anteriores).
- `./labs/<lab-name>/verify.sh` — Ejecuta la suite automatizada de pruebas `pytest` para ese laboratorio.
- `./labs/<lab-name>/apply_solution.sh` — Aplica instantáneamente la solución de referencia para ese laboratorio.

---

## 5. Seguridad Empresarial, Privacidad y Gobernanza (Google Cloud + Antigravity)

Las empresas de retail requieren defensa en profundidad a través de identidad en la nube, privacidad de datos, perímetros de red y ejecución local de agentes. Este workshop demuestra el **modelo de gobernanza de dos capas** cubierto en detalle en el [Laboratorio 03](labs/lab-03-mcp-and-hooks/README.es.md):

### Capa 1: Gobernanza en Google Cloud & Gemini Enterprise (Plano de Administración Cloud)
- **IAM y Asignación de Licencias**: Aprovisionamiento mediante el rol de Google Cloud IAM `roles/cloudaicompanion.user` federado con grupos SSO de **Cloud Identity, Okta o Microsoft Entra ID (Azure AD)**.
- **Cloud Audit Logs (`cloudaicompanion.googleapis.com`)**: Habilitación de logs Admin Activity y Data Access en **Google Cloud Logging** para capturar una pista de auditoría inmutable de cada invocación a la API, identidad de usuario, marca de tiempo y metadatos del proyecto, con enrutamiento opcional mediante Log Sinks a BigQuery o Chronicle SIEM.
- **Cero Retención de Datos y Sin Entrenamiento de Modelos**: Los prompts de clientes, esquemas SQL, tablas de costos mayoristas, contratos SLA de proveedores y código fuente **nunca se utilizan para entrenar modelos fundacionales de Google** y permanecen estrictamente aislados dentro de tu perímetro empresarial.
- **VPC Service Controls (VPC-SC) y Endpoints Regionales**: Protección de `cloudaicompanion.googleapis.com` dentro de un perímetro VPC-SC junto con BigQuery y Cloud SQL para prevenir la exfiltración de datos, respaldado por la indemnización de derechos de autor de Google Cloud.

### Capa 2: Controles de Seguridad del Cliente y Workspace de Antigravity (Plano de Ejecución Local)
- **Política de Ejecución de Herramientas**: Configuración de `strict`, `request-review`, `proceed-in-sandbox` o `always-proceed` para gobernar cuándo los comandos de terminal o escrituras de archivos requieren aprobación humana.
- **Sandbox de Terminal y Aislamiento de Red**: Aplicación de sandboxing a nivel de sistema operativo (`sandbox-exec` en macOS / namespaces en Linux) y restricción de acceso saliente a internet.
- **Protección de Acceso a Archivos Fuera del Workspace**: Impedir que los agentes lean o modifiquen archivos fuera del límite del workspace `/antigravity-workshop-retail` (protegiendo `~/.ssh`, `~/.aws` y credenciales del host).
- **Lista Blanca / Negra de Comandos y Lista Blanca del Navegador**: Permitir ejecutores de pruebas seguros (`.venv/bin/python -m pytest`) bloqueando comandos destructivos (`rm -rf`, `curl`) y restringiendo `/browser` a `http://127.0.0.1:8000`.
- **Hooks Deterministas de Ciclo de Vida (`.agents/hooks.json`)**: Ejecución de validación determinista previa a herramientas (`scripts/margin_guard_hook.py`) antes de cualquier modificación de archivos, bloqueando intentos de evadir el piso de margen del 15% con código de salida `2` y registrando cada decisión en `data/logs/hook_compliance_audit.jsonl`.

---

## 6. Estructura del Repositorio

```text
antigravity-workshop-retail/
├── README.md                                 # Guía del Workshop en Inglés
├── README.es.md                              # Guía del Workshop en Español
├── INSTRUCTOR_DEMO_GUIDE.md                  # Guía Paso a Paso del Instructor en Inglés
├── INSTRUCTOR_DEMO_GUIDE.es.md               # Guía Paso a Paso del Instructor en Español
├── install.sh / install.ps1                  # Inicializador multiplataforma de entorno y BD
├── requirements.txt / pyproject.toml         # Dependencias Python y configuración pytest
├── data/
│   ├── seed_retail_data.py                   # Generador determinista de datos (SQLite + CSV + JSONL)
│   ├── retail_pulse.db                       # Base de datos SQLite poblada
│   ├── exports/                              # Exportaciones CSV comerciales (contratos, stock, pedidos)
│   └── logs/                                 # Webhooks POS/WMS y hook_compliance_audit.jsonl
├── src/
│   ├── main.py                               # Aplicación FastAPI y endpoints REST
│   ├── database.py / models.py               # Conexión SQLite y esquemas Pydantic
│   ├── services/                             # promo_pricing, inventory_atp, vendor_otif, fulfillment_router
│   └── static/                               # Centro de Comando index.html y tryolabs-logo.png
├── mcp_server/
│   └── retail_mcp.py                         # Servidor FastMCP exponiendo 4 herramientas en vivo
├── scripts/
│   ├── run_otif_margin_audit.py              # Script CLI de auditoría para la Skill del Lab 02
│   └── margin_guard_hook.py                  # Hook determinista PreToolUse de cumplimiento (Lab 03)
├── labs/
│   ├── lab-01-margin-inventory-triage/       # Starter, Solution, README (EN/ES), PROMPTS (EN/ES), scripts
│   ├── lab-02-rules-and-skills/              # Starter, Solution, README (EN/ES), PROMPTS (EN/ES), scripts
│   ├── lab-03-mcp-and-hooks/                 # Starter, Solution, README (EN/ES), PROMPTS (EN/ES), scripts
│   └── lab-04-multi-agent-capstone/          # Starter, Solution, README (EN/ES), PROMPTS (EN/ES), scripts
└── tests/
    ├── test_lab01_triage.py                  # 4 pruebas para el Lab 01
    ├── test_lab02_rules_skills.py            # 3 pruebas para el Lab 02
    ├── test_lab03_mcp_hooks.py               # 5 pruebas para el Lab 03
    └── test_lab04_capstone.py                # 4 pruebas para el Lab 04 (16 pruebas en total)
```
