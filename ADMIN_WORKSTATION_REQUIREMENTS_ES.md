<div align="center">
  <img src="https://raw.githubusercontent.com/tryolabs/brand-assets/main/tryolabs-logo.png" alt="Tryolabs" height="44" />
</div>

# Guía de Requisitos y Pre-Aprovisionamiento para Administradores de TI — Edición Retail (Retail Pulse)
**Taller**: Ingeniería Agéntica con Google Antigravity — Taller Práctico de 4 Horas
**Edición**: Edición Retail (Retail Pulse) — Enrutamiento Omnicanal, Sincronización de Inventario True ATP, Piso de Margen y Contratos OTIF
**Repositorio**: `antigravity-workshop-retail`
**Impartido por**: Tryolabs

---

## 1. Resumen Ejecutivo para Administradores de TI (Modo Asistente Sin Privilegios)

Los asistentes al taller **no cuentan con permisos de administrador local (`sudo` / Administrador)** en sus computadoras corporativas y no podrán instalar software, binarios del sistema ni paquetes de Python durante la sesión en vivo.

Para garantizar una experiencia fluida en los 4 laboratorios prácticos de `antigravity-workshop-retail`, **el equipo de TI debe pre-instalar todos los requisitos descritos en este documento antes del taller** y pre-construir el entorno virtual `.venv` dentro del repositorio. Una vez aprovisionado el equipo mediante el script incluido `admin_provision_workstation.sh` (macOS/Linux) o `admin_provision_workstation.ps1` (Windows):
- **El 100% de los Laboratorios 1, 2, 3 y 4 se ejecuta en espacio de usuario estándar** sin requerir privilegios administrativos.
- **Cero descargas o instalaciones en tiempo de ejecución (`pip install` / `brew` / `apt` / `winget`)**: todos los scripts del taller (`./install.sh` y `./labs/lab-01-margin-inventory-triage/install.sh`) detectan automáticamente el entorno `.venv` pre-instalado y operan en **Modo Cero-Instalación (Zero-Install Mode)**.
- **Base de Datos y Servicios 100% Locales**: Todos los datos residen en un archivo SQLite embebido (`data/retail_pulse.db`) dentro de `antigravity-workshop-retail/`; no se requieren motores de bases de datos externos ni demonios Docker.

---

## 2. Requisitos de Hardware, Sistema Operativo, Puertos Locales y Reglas EDR/Firewall

### 2.1 Línea Base de Hardware y Sistema Operativo
| Componente | Requisito Mínimo | Especificación Recomendada |
| :--- | :--- | :--- |
| **Sistema Operativo** | **macOS 13+** (Ventura/Sonoma/Sequoia), **Windows 10/11 (64-bit)** con Git Bash o WSL2, o **Linux** (Ubuntu 22.04+, Debian 12+, RHEL 9+) | macOS 14+ (Apple Silicon M1–M4) o Ubuntu 22.04+ / Windows 11 con WSL2 |
| **CPU y Memoria (RAM)** | 4 núcleos vCPU / **8 GB RAM** | 8+ núcleos vCPU / **16 GB RAM** |
| **Espacio Libre en Disco** | **5 GB** disponibles en el directorio del usuario | **10 GB** disponibles |

### 2.2 Puertos TCP Locales (Loopback `127.0.0.1` Sin Privilegios)
Durante los laboratorios, los asistentes inician el servidor local FastAPI y la interfaz de desarrollo de Google ADK vinculados exclusivamente a `127.0.0.1` (localhost). No se exponen puertos hacia la red externa:
- **Puerto TCP `8002` (`127.0.0.1:8002`)**: Command Center Web en vivo de Retail Pulse (`uvicorn src.main:app --port 8002`).
- **Puerto TCP `8080` (`127.0.0.1:8080`)**: Interfaz Web de Desarrollo de Google ADK (`adk web adk_agents/retail_pulse --port 8080` vía `./scripts/run_adk_web.sh`).

### 2.3 Reglas de Antivirus / EDR y Firewall de Salida
1. **Ejecución de Subprocesos Locales (`stdio`)**: En el Laboratorio 3, Google Antigravity invoca el intérprete local de Python (`./.venv/bin/python`) como subproceso vía entrada/salida estándar (`stdio`) para ejecutar el servidor FastMCP (`mcp_server/retail_mcp.py`) y los hooks deterministas de seguridad (`scripts/audit_hook.py`). Verifique que CrowdStrike Falcon, Microsoft Defender o SentinelOne **no bloqueen la ejecución de subprocesos Python sin privilegios** dentro de `antigravity-workshop-retail/`.
2. **Dominios HTTPS de Salida Permitidos (Puerto `443`)**:
   - `*.googleapis.com` (`cloudaicompanion.googleapis.com`, `aiplatform.googleapis.com`, `discoveryengine.googleapis.com`, `run.googleapis.com`)
   - `accounts.google.com` y `oauth2.googleapis.com` (Autenticación SSO con Google Cloud / Gemini Enterprise)

---

## 3. Matriz Completa de Software del Sistema y Binarios CLI

Los Administradores de TI deben instalar las siguientes aplicaciones y herramientas CLI a nivel de sistema y asegurarse de que estén incluidas en la variable `PATH` del usuario estándar:

| # | Software / Binario | Versión Requerida | Comando de Verificación | Uso en `antigravity-workshop-retail` | ¿Obligatorio? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Google Antigravity** (App de Escritorio Antigravity 2.0, Antigravity IDE y CLI `agy`) | Última versión Enterprise | `agy --version` (o abrir Antigravity 2.0 / IDE) | Todos los Labs (Labs 1–4) | **OBLIGATORIO** |
| **2** | **Python 3 Runtime** (incluyendo módulos estándar `venv`, `pip`, `sqlite3`, `decimal`) | **>= 3.11** (`>= 3.10` compatible; **3.11 o 3.12 recomendado**) | `python3 --version` | Todos los Labs (Labs 1–4) | **OBLIGATORIO** |
| **3** | **Astral `uv`** (Gestor rápido de entornos y paquetes Python) | **>= 0.5.0** | `uv --version` | Gestión de `.venv` y ejecución FastMCP | **OBLIGATORIO** |
| **4** | **Git CLI** | **>= 2.39** | `git --version` | Clonación de `antigravity-workshop-retail` y control de diffs | **OBLIGATORIO** |
| **5** | **SQLite 3 CLI** | **>= 3.37** | `sqlite3 --version` | Inspección de `data/retail_pulse.db` y pruebas de Hooks (Labs 1 y 3) | **OBLIGATORIO** |
| **6** | **Shell POSIX (`bash`) y `curl`** | `bash >= 3.2` (macOS) / `>= 4.0` (Linux / Git Bash en Windows) | `bash --version` y `curl --version` | Ejecución de `./install.sh`, `./verify.sh` y pruebas A2A | **OBLIGATORIO** |
| **7** | **HashiCorp Terraform CLI** | **>= 1.5.0** | `terraform -version` | Lab 4 (Validación IaC en `infra/terraform/` y Cloud Run) | **OBLIGATORIO (Lab 4)** |
| **8** | **Google Cloud SDK (`gcloud`)** | **>= 460.0.0** | `gcloud --version` | Autenticación Gemini Enterprise y despliegue Lab 4 | **OBLIGATORIO (Lab 4)** |
| **9** | **Navegador Web Chromium** | Google Chrome o Microsoft Edge (Última versión) | Abrir navegador | Visualización de UI (`:8002`), `adk web` (`:8080`) y slides | **OBLIGATORIO** |

### Comandos Rápidos de Instalación por Sistema Operativo (Para Administradores de TI)
- **macOS (Homebrew)**:
  ```bash
  brew install python@3.12 uv git sqlite terraform
  brew install --cask google-cloud-sdk
  ```
- **Ubuntu / Debian Linux (`apt`)**:
  ```bash
  sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-pip git sqlite3 curl bash unzip
  curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="/usr/local/bin" sh
  ```
- **Windows 10/11 (PowerShell como Administrador vía `winget`)**:
  ```powershell
  winget install -e --id Python.Python.3.12 --scope machine
  winget install -e --id Astral-sh.uv --scope machine
  winget install -e --id Git.Git --scope machine
  winget install -e --id SQLite.SQLite --scope machine
  winget install -e --id Hashicorp.Terraform --scope machine
  winget install -e --id Google.CloudSDK --scope machine
  ```

---

## 4. Especificación Completa de Librerías Python (`requirements.txt` y `requirements-lock.txt`)

Todas las librerías de Python deben pre-instalarse dentro de `antigravity-workshop-retail/.venv` para que los asistentes no necesiten ejecutar `pip install`.

### 4.1 Librerías Principales de Python y Mapeo por Laboratorio
| Paquete Python | Versión Mínima | Versión Exacta Verificada | Propósito en los Laboratorios de `antigravity-workshop-retail` |
| :--- | :--- | :--- | :--- |
| `fastapi` | `>=0.110.0` | `0.141.1` | API REST principal y endpoint A2A JSON-RPC 2.0 (`/api/v1/a2a`) en Labs 1–4 |
| `uvicorn` | `>=0.27.0` | `0.54.0` | Servidor ASGI local para el dashboard web en vivo (`127.0.0.1:8002`) |
| `pydantic` | `>=2.6.0` | `2.14.1` | Validación estricta de esquemas para SKUs GS1 GTIN-14, nodos de inventario WMS, promociones, contratos OTIF y payloads A2A |
| `pytest` | `>=8.0.0` | `9.1.1` | Suite de pruebas automatizadas ejecutada por `verify.sh` en los Labs 1, 2, 3 y 4 (20 passed) |
| `httpx` | `>=0.27.0` | `0.28.1` | Cliente HTTP asíncrono y transporte para `TestClient` de FastAPI |
| `mcp` | `>=1.2.0` | `2.3.0` | SDK oficial de Model Context Protocol (`FastMCP`) para el Lab 3 (`mcp_server/retail_mcp.py`) |
| `google-adk` | `>=1.0.0` | `2.12.0` | Google Agent Development Kit (`LlmAgent`, `Runner` y Dev UI `adk web` para `adk_agents/retail_pulse`) |
| `google-genai` | `>=1.0.0` | `2.33.0` | SDK de Google GenAI / Vertex AI utilizado por agentes ADK y Gemini Enterprise |
| `google-auth` | `>=2.28.0` | `2.62.0` | Autenticación con Google Cloud IAM y Application Default Credentials |
| `aiosqlite` | `>=0.20.0` | `0.22.1` | Almacenamiento asíncrono de sesiones SQLite utilizado por `adk web` |
| `sse-starlette` | `>=2.0.0` | `3.5.0` | Transporte Server-Sent Events para FastMCP y streaming de eventos ADK |
| `starlette` | `>=0.36.0` | `1.9.0` | Enrutamiento y middleware ASGI |
| `websockets` | `>=12.0` | `15.0.1` | Comunicación bidireccional en tiempo real para `adk web` (`:8080`) |
| `python-dotenv` | `>=1.0.0` | `1.2.4` | Carga de variables de entorno para configuración local vs. Vertex AI / Gemini Enterprise |
| `python-multipart` | `>=0.0.9` | `0.0.32` | Procesamiento de formularios requerido por FastAPI y ADK Web UI |
| `PyYAML` | `>=6.0.1` | `6.0.3` | Lectura de frontmatter YAML en los archivos `SKILL.md` (Lab 2) |
| `tenacity` | `>=8.2.0` | `9.1.4` | Reintentos resilientes en invocación de herramientas de agentes |
| `requests` | `>=2.31.0` | `2.34.2` | Utilidades de cliente HTTP |
| `opentelemetry-api` / `sdk` | `>=1.24.0` | `1.42.1` | Trazabilidad de eventos multi-agente visualizada en `adk web` |

### 4.2 Instalación Offline mediante Wheelhouse Local (Opcional para Redes Restringidas)
Si las estaciones de trabajo no tienen acceso directo a `pypi.org`, el Administrador de TI puede descargar los 59 paquetes fijados en `requirements-lock.txt` una sola vez hacia `antigravity-workshop-retail/wheelhouse/`:
```bash
pip download -r requirements-lock.txt -d ./wheelhouse
```
Cuando la carpeta `./wheelhouse` está presente, tanto `./admin_provision_workstation.sh` como `./install.sh` instalan todas las dependencias de manera 100% offline usando `--no-index --find-links ./wheelhouse`.

---

## 5. Permisos de Sistema de Archivos Críticos para Asistentes Sin Privilegios

> **IMPORTANTE PARA ADMINISTRADORES DE TI**:
> Si clona `antigravity-workshop-retail` y construye el entorno `.venv` utilizando una cuenta elevada (`root` o `Administrator`), **DEBE transferir la propiedad recursiva de toda la carpeta `antigravity-workshop-retail` al usuario estándar del asistente** antes de entregar el equipo.

¿Por qué es indispensable? Durante los laboratorios prácticos, el asistente (sin permisos de administrador) ejecuta scripts que crean y modifican archivos locales dentro de `antigravity-workshop-retail/`:
- `data/retail_pulse.db` (La base de datos SQLite y sus archivos temporales WAL requieren permisos de escritura en `data/`)
- `data/exports/` y `data/logs/hook_audit.log` (Reportes generados en el Lab 2 y bitácora de auditoría en el Lab 3)
- `GEMINI.md` y `.agents/` (`rules/`, `skills/`, `mcp_config.json`, `hooks.json` creados en los Labs 2 y 3)
- `src/services/`, `src/agents/` y `mcp_server/retail_mcp.py` (Archivos editados en los Labs 1, 3 y 4, y restaurados por `./labs/lab-01-margin-inventory-triage/install.sh`)

**Solución Automatizada (macOS / Linux)**:
```bash
sudo ./admin_requirements/admin_provision_workstation.sh --user <usuario_asistente>
```
**Solución Manual (macOS / Linux)**:
```bash
sudo chown -R <usuario_asistente>:<grupo_asistente> /ruta/a/antigravity-workshop-retail
sudo chmod -R u+rwX /ruta/a/antigravity-workshop-retail
```
**Solución Manual (Windows PowerShell como Administrador)**:
```powershell
icacls "C:\Workshops\antigravity-workshop-retail" /grant "<UsuarioAsistente>:(OI)(CI)M" /T
```

---

## 6. APIs, Roles IAM y Permisos de Google Cloud para Antigravity + Gemini Enterprise

Para permitir que los asistentes autentiquen **Google Antigravity** (`agy`, Antigravity IDE y Antigravity 2.0) con **Gemini Enterprise**, ejecuten **Google ADK (`adk web`)** contra **Vertex AI** y desplieguen/registren el agente A2A **`retail-pulse`** en el Laboratorio 4, el Administrador de Google Cloud debe habilitar las siguientes APIs y otorgar los siguientes roles IAM en el proyecto de Google Cloud del taller (`<WORKSHOP_GCP_PROJECT_ID>`).

### 6.1 APIs de Google Cloud que Deben Habilitarse (`gcloud services enable`)
| Nombre del Servicio API en GCP | Título del Servicio | Propósito en `antigravity-workshop-retail` | Estado |
| :--- | :--- | :--- | :--- |
| `cloudaicompanion.googleapis.com` | **Gemini for Google Cloud API** (Cloud AI Companion API) | API principal de backend para **Google Antigravity** (`agy`, IDE y 2.0) bajo suscripciones Gemini Enterprise, generación de código, uso de herramientas agénticas y validación de licencia | **OBLIGATORIA (Labs 1–4)** |
| `aiplatform.googleapis.com` | **Vertex AI API** | Impulsa **Google Agent Development Kit (`google-adk`)** y el SDK `google-genai` (`GOOGLE_GENAI_USE_VERTEXAI=TRUE`) para la jerarquía multi-agente y `adk web` del Lab 4 | **OBLIGATORIA (Lab 4)** |
| `discoveryengine.googleapis.com` | **Gemini Enterprise / Discovery Engine API** | Permite registrar e invocar el endpoint A2A (`AgentCard`) de `retail-pulse` dentro de Gemini Enterprise (`./deploy/register_gemini_enterprise_agent.sh`) | **OBLIGATORIA (Lab 4)** |
| `serviceusage.googleapis.com` | **Service Usage API** | Permite a los asistentes verificar APIs activas y asociar el consumo de cuota al proyecto del taller (`x-goog-user-project`) | **OBLIGATORIA (Labs 1–4)** |
| `cloudresourcemanager.googleapis.com` | **Cloud Resource Manager API** | Inspección de metadatos del proyecto e inicialización del proveedor Terraform | **OBLIGATORIA (Lab 4)** |
| `run.googleapis.com` | **Cloud Run Admin API** | Despliega el servicio contenedorizado FastAPI + ADK + A2A (`retail-pulse`) en Cloud Run v2 (`infra/terraform/`) | **OBLIGATORIA (Lab 4 Deploy)** |
| `artifactregistry.googleapis.com` | **Artifact Registry API** | Almacena la imagen Docker del servicio `retail-pulse` (`retail-pulse-repo`) | **OBLIGATORIA (Lab 4 Deploy)** |
| `cloudbuild.googleapis.com` | **Cloud Build API** | Construye la imagen de contenedor de `retail-pulse` mediante `gcloud builds submit` | **OBLIGATORIA (Lab 4 Deploy)** |
| `iam.googleapis.com` | **Identity and Access Management (IAM) API** | Crea la cuenta de servicio de mínimo privilegio para Cloud Run (`retail-pulse-sa`) | **OBLIGATORIA (Lab 4 Deploy)** |
| `logging.googleapis.com` | **Cloud Logging API** | Registra los Cloud Audit Logs de `cloudaicompanion.googleapis.com` y la telemetría de Cloud Run | **OBLIGATORIA (Labs 1–4)** |

### 6.2 Roles IAM y Permisos Específicos para Cada Asistente (`user:<asistente>@empresa.com`)
Además de asignar una **licencia activa de Gemini Enterprise / Gemini Code Assist Enterprise** a cada asistente en la consola de Google Cloud (**Admin for Gemini -> License Management**), otorgue a cada asistente los siguientes roles IAM en el proyecto de GCP del taller:

| Rol IAM en Google Cloud | Nombre del Rol | Permisos IAM Clave Incluidos | Por Qué Es Necesario |
| :--- | :--- | :--- | :--- |
| `roles/cloudaicompanion.user` | **Gemini for Google Cloud User** | `cloudaicompanion.companions.generateChat`, `cloudaicompanion.companions.generateCode`, `cloudaicompanion.instances.completeCode`, `cloudaicompanion.instances.generateChat`, `cloudaicompanion.instances.generateCode`, `cloudaicompanion.instances.queryEffectiveSetting`, `cloudaicompanion.entitlements.get` | **Obligatorio para Google Antigravity**: Autoriza al desarrollador a iniciar sesión en `agy`, Antigravity IDE y Antigravity 2.0 con Gemini Enterprise y ejecutar inferencia agéntica |
| `roles/serviceusage.serviceUsageConsumer` | **Service Usage Consumer** | `serviceusage.services.use`, `serviceusage.services.get`, `serviceusage.services.list` | **Obligatorio para Cuota de API**: Permite que la sesión del asistente (`gcloud auth application-default set-quota-project`) utilice la cuota del proyecto de GCP del taller |
| `roles/aiplatform.user` | **Vertex AI User** | `aiplatform.endpoints.predict`, `aiplatform.endpoints.generateContent`, `aiplatform.endpoints.streamGenerateContent`, `aiplatform.models.get` | **Obligatorio para ADK en el Lab 4**: Permite a `adk web adk_agents/retail_pulse` y al `Runner` de ADK invocar modelos Gemini en Vertex AI (`GOOGLE_GENAI_USE_VERTEXAI=TRUE`) |
| `roles/discoveryengine.editor` *(o `roles/discoveryengine.viewer`)* | **Discovery Engine Editor / Viewer** | `discoveryengine.engines.get`, `discoveryengine.engines.list`, `discoveryengine.assistants.get`, `discoveryengine.agents.create`, `discoveryengine.agents.update` | **Requerido en el Lab 4 (Gemini Enterprise)**: Permite inspeccionar motores de Gemini Enterprise y registrar el `AgentCard` A2A de `retail-pulse` (`/.well-known/agent.json`) |
| `roles/viewer` | **Project Viewer** | `resourcemanager.projects.get`, `run.services.get`, `run.services.list` | **Recomendado**: Permite consultar la URL del servicio Cloud Run `retail-pulse` y la configuración del proyecto |

### 6.3 Roles IAM para el Administrador Cloud / Instructor y Cuenta de Servicio de Cloud Run
| Identidad / Rol Operativo | Roles IAM Requeridos | Propósito |
| :--- | :--- | :--- |
| **Administrador Cloud / Instructor** (`user:<instructor>@empresa.com`) | `roles/cloudaicompanion.admin`, `roles/logging.privateLogViewer`, `roles/run.admin`, `roles/artifactregistry.admin`, `roles/cloudbuild.builds.editor`, `roles/iam.serviceAccountAdmin`, `roles/iam.serviceAccountUser`, `roles/serviceusage.serviceUsageAdmin` | Asigna licencias de Gemini Enterprise, demuestra los Cloud Audit Logs de `cloudaicompanion.googleapis.com` en el Bloque 1 y ejecuta `terraform apply` (`infra/terraform/`) para desplegar `retail-pulse` en Cloud Run v2 |
| **Cuenta de Servicio de Cloud Run** (`retail-pulse-sa@<project>.iam.gserviceaccount.com`) | `roles/aiplatform.user`, `roles/discoveryengine.viewer`, `roles/logging.logWriter` | Creada automáticamente por `infra/terraform/main.tf` como identidad de mínimo privilegio asociada al servicio Cloud Run `retail-pulse` |

### 6.4 Comandos `gcloud` de Aprovisionamiento en Un Solo Paso para el Administrador Cloud
```bash
export PROJECT_ID="<WORKSHOP_GCP_PROJECT_ID>"

# 1. Habilitar todas las APIs requeridas para Antigravity, Gemini Enterprise, Vertex AI, ADK y Cloud Run
gcloud services enable \
  cloudaicompanion.googleapis.com \
  aiplatform.googleapis.com \
  discoveryengine.googleapis.com \
  serviceusage.googleapis.com \
  cloudresourcemanager.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  iam.googleapis.com \
  logging.googleapis.com \
  --project="${PROJECT_ID}"

# 2. Otorgar los roles IAM requeridos a cada asistente del taller
export ATTENDEE_EMAIL="<asistente>@empresa.com"
for ROLE in \
  roles/cloudaicompanion.user \
  roles/serviceusage.serviceUsageConsumer \
  roles/aiplatform.user \
  roles/discoveryengine.editor \
  roles/viewer; do
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="user:${ATTENDEE_EMAIL}" \
    --role="${ROLE}"
done
```

---

## 7. Lista de Verificación antes del Taller (Checklist para TI)

Ejecute `./admin_requirements/admin_provision_workstation.sh --verify-only` iniciando sesión como el **usuario estándar del asistente (sin sudo)** y confirme que todos los puntos pasen exitosamente:

1. `python3 --version` reporta `Python 3.10+` (`3.11` o `3.12` recomendado).
2. `uv --version` reporta `uv 0.5+`.
3. `git --version` y `sqlite3 --version` responden correctamente desde el `PATH`.
4. `terraform -version` y `gcloud --version` están disponibles en el `PATH` (para el Lab 4).
5. Google Antigravity (`Antigravity 2.0`, `Antigravity IDE` y/o CLI `agy`) abre e inicia sesión correctamente con `roles/cloudaicompanion.user` y `roles/serviceusage.serviceUsageConsumer`.
6. `./.venv/bin/python -c "import fastapi, uvicorn, pydantic, pytest, httpx, mcp, google.adk, google.genai"` finaliza con código `0`.
7. `./.venv/bin/adk --version` y `./scripts/run_adk_web.sh --check` finalizan con código `0`.
8. Ejecutar `./install.sh` muestra `[OK] Pre-provisioned .venv detected with all required packages (zero-install mode)` e inicializa `data/retail_pulse.db` sin errores de permisos.
9. Ejecutar `./verify.sh` (con las soluciones aplicadas) pasa el 100% de las pruebas automatizadas (`20 passed`).
10. Los puertos locales `127.0.0.1:8002` y `127.0.0.1:8080` pueden abrirse sin bloqueos del firewall local.
