<div align="center">
  <img src="https://raw.githubusercontent.com/tryolabs/brand-assets/main/tryolabs-logo.png" alt="Tryolabs" height="44" />
</div>

# Guía de Requisitos y Pre-Aprovisionamiento para Administradores de TI
**Taller**: Ingeniería Agéntica con Google Antigravity — Taller Práctico de 4 Horas (Ediciones Telecom y Retail)
**Impartido por**: Tryolabs
**Audiencia Objetivo**: Administradores de TI Corporativos, Equipos de Seguridad Endpoint y Soporte de Estaciones de Trabajo

---

## 1. Resumen Ejecutivo para Administradores de TI (Modo Asistente Sin Privilegios)

Los asistentes al taller **no cuentan con permisos de administrador local (`sudo` / Administrador)** en sus computadoras corporativas y no podrán instalar software, binarios del sistema ni paquetes de Python durante la sesión en vivo.

Para garantizar una experiencia fluida en los 4 laboratorios prácticos, **el equipo de TI debe pre-instalar todos los requisitos descritos en este documento antes del taller** y pre-construir el entorno virtual `.venv` dentro del repositorio. Una vez aprovisionado el equipo mediante el script incluido `admin_provision_workstation.sh` (macOS/Linux) o `admin_provision_workstation.ps1` (Windows):
- **El 100% de los Laboratorios 1, 2, 3 y 4 se ejecuta en espacio de usuario estándar** sin requerir privilegios administrativos.
- **Cero descargas o instalaciones en tiempo de ejecución (`pip install` / `brew` / `apt` / `winget`)**: todos los scripts del taller (`./install.sh` y `./labs/lab-0X-.../install.sh`) detectan automáticamente el entorno `.venv` pre-instalado y operan en **Modo Cero-Instalación (Zero-Install Mode)**.
- **Base de Datos y Servicios 100% Locales**: Todos los datos residen en un archivo SQLite embebido (`data/telecom_nexus.db` o `data/retail_pulse.db`) dentro de la carpeta del repositorio; no se requieren motores de bases de datos externos ni demonios Docker.

---

## 2. Requisitos de Hardware, Sistema Operativo, Puertos Locales y Reglas EDR/Firewall

### 2.1 Línea Base de Hardware y Sistema Operativo
| Componente | Requisito Mínimo | Especificación Recomendada |
| :--- | :--- | :--- |
| **Sistema Operativo** | **macOS 13+** (Ventura/Sonoma/Sequoia), **Windows 10/11 (64-bit)** con Git Bash o WSL2, o **Linux** (Ubuntu 22.04+, Debian 12+, RHEL 9+) | macOS 14+ (Apple Silicon M1–M4) o Ubuntu 22.04+ / Windows 11 con WSL2 |
| **CPU y Memoria (RAM)** | 4 núcleos vCPU / **8 GB RAM** | 8+ núcleos vCPU / **16 GB RAM** |
| **Espacio Libre en Disco** | **5 GB** disponibles en el directorio del usuario | **10 GB** disponibles |

### 2.2 Puertos TCP Locales (Loopback `127.0.0.1` Sin Privilegios)
Durante los laboratorios, los asistentes inician servidores locales FastAPI y la interfaz de desarrollo de Google ADK vinculados exclusivamente a `127.0.0.1` (localhost). No se exponen puertos hacia la red externa:
- **Puerto TCP `8001` (`127.0.0.1:8001`)**: Dashboard Web NOC en vivo de Telecom Nexus (`uvicorn src.main:app --port 8001`).
- **Puerto TCP `8002` (`127.0.0.1:8002`)**: Command Center Web en vivo de Retail Pulse (`uvicorn src.main:app --port 8002`).
- **Puerto TCP `8080` (`127.0.0.1:8080`)**: Interfaz Web de Desarrollo de Google ADK (`adk web --port 8080` vía `./scripts/run_adk_web.sh`).

### 2.3 Reglas de Antivirus / EDR y Firewall de Salida
1. **Ejecución de Subprocesos Locales (`stdio`)**: En el Laboratorio 3, Google Antigravity invoca el intérprete local de Python (`./.venv/bin/python`) como subproceso vía entrada/salida estándar (`stdio`) para ejecutar el servidor FastMCP (`mcp_server/telecom_mcp.py` o `mcp_server/retail_mcp.py`) y los hooks deterministas de seguridad (`scripts/audit_hook.py`). Verifique que CrowdStrike Falcon, Microsoft Defender o SentinelOne **no bloqueen la ejecución de subprocesos Python sin privilegios** dentro de la carpeta del taller.
2. **Dominios HTTPS de Salida Permitidos (Puerto `443`)**:
   - `*.googleapis.com` (`cloudaicompanion.googleapis.com`, `aiplatform.googleapis.com`, `discoveryengine.googleapis.com`, `run.googleapis.com`)
   - `accounts.google.com` y `oauth2.googleapis.com` (Autenticación SSO con Google Cloud / Gemini Enterprise)

---

## 3. Matriz Completa de Software del Sistema y Binarios CLI

Los Administradores de TI deben instalar las siguientes aplicaciones y herramientas CLI a nivel de sistema y asegurarse de que estén incluidas en la variable `PATH` del usuario estándar:

| # | Software / Binario | Versión Requerida | Comando de Verificación | Uso en el Taller | ¿Obligatorio? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Google Antigravity** (App de Escritorio Antigravity 2.0, Antigravity IDE y CLI `agy`) | Última versión Enterprise | `agy --version` (o abrir Antigravity 2.0 / IDE) | Todos los Labs (Labs 1–4) | **OBLIGATORIO** |
| **2** | **Python 3 Runtime** (incluyendo módulos estándar `venv`, `pip`, `sqlite3`, `decimal`) | **>= 3.11** (`>= 3.10` compatible; **3.11 o 3.12 recomendado**) | `python3 --version` | Todos los Labs (Labs 1–4) | **OBLIGATORIO** |
| **3** | **Astral `uv`** (Gestor rápido de entornos y paquetes Python) | **>= 0.5.0** | `uv --version` | Gestión de `.venv` y ejecución MCP | **OBLIGATORIO** |
| **4** | **Git CLI** | **>= 2.39** | `git --version` | Clonación y control de diffs | **OBLIGATORIO** |
| **5** | **SQLite 3 CLI** | **>= 3.37** | `sqlite3 --version` | Inspección SQLite y pruebas de Hooks (Labs 1 y 3) | **OBLIGATORIO** |
| **6** | **Shell POSIX (`bash`) y `curl`** | `bash >= 3.2` (macOS) / `>= 4.0` (Linux / Git Bash en Windows) | `bash --version` y `curl --version` | Ejecución de `./install.sh`, `./verify.sh` y pruebas A2A | **OBLIGATORIO** |
| **7** | **HashiCorp Terraform CLI** | **>= 1.5.0** | `terraform -version` | Lab 4 (Validación IaC en `infra/terraform/` y Cloud Run) | **OBLIGATORIO (Lab 4)** |
| **8** | **Google Cloud SDK (`gcloud`)** | **>= 460.0.0** | `gcloud --version` | Autenticación Gemini Enterprise y despliegue Lab 4 | **OBLIGATORIO (Lab 4)** |
| **9** | **Navegador Web Chromium** | Google Chrome o Microsoft Edge (Última versión) | Abrir navegador | Visualización de UI (`:8001`/`:8002`), `adk web` (`:8080`) y slides | **OBLIGATORIO** |

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

Todas las librerías de Python deben pre-instalarse dentro del entorno virtual `.venv` del repositorio (`antigravity-workshop-telecom/.venv` y/o `antigravity-workshop-retail/.venv`) para que los asistentes no necesiten ejecutar `pip install`.

### 4.1 Librerías Principales de Python y Mapeo por Laboratorio
| Paquete Python | Versión Mínima | Versión Exacta Verificada | Propósito en los Laboratorios |
| :--- | :--- | :--- | :--- |
| `fastapi` | `>=0.110.0` | `0.141.1` | API REST principal y endpoint A2A JSON-RPC 2.0 (`/api/v1/a2a`) en Labs 1–4 |
| `uvicorn` | `>=0.27.0` | `0.54.0` | Servidor ASGI local para los dashboards web (`:8001` Telecom / `:8002` Retail) |
| `pydantic` | `>=2.6.0` | `2.14.1` | Validación estricta de esquemas para CDRs, slices 5G, inventario WMS y payloads A2A |
| `pytest` | `>=8.0.0` | `9.1.1` | Suite de pruebas automatizadas ejecutada por `verify.sh` en los Labs 1, 2, 3 y 4 |
| `httpx` | `>=0.27.0` | `0.28.1` | Cliente HTTP asíncrono y transporte para `TestClient` de FastAPI |
| `mcp` | `>=1.2.0` | `2.3.0` | SDK oficial de Model Context Protocol (`FastMCP`) para el servidor MCP local (Lab 3) |
| `google-adk` | `>=1.0.0` | `2.12.0` | Google Agent Development Kit (`LlmAgent`, `Runner` y Dev UI `adk web` en Lab 4) |
| `google-genai` | `>=1.0.0` | `2.33.0` | SDK de Google GenAI / Vertex AI utilizado por agentes ADK y Gemini Enterprise |
| `google-auth` | `>=2.28.0` | `2.62.0` | Autenticación con Google Cloud IAM y Application Default Credentials |
| `aiosqlite` | `>=0.20.0` | `0.22.1` | Almacenamiento asíncrono de sesiones SQLite utilizado por `adk web` |
| `sse-starlette` | `>=2.0.0` | `3.5.0` | Transporte Server-Sent Events para FastMCP y streaming de eventos ADK |
| `starlette` | `>=0.36.0` | `1.9.0` | Enrutamiento y middleware ASGI |
| `websockets` | `>=12.0` | `15.0.1` | Comunicación bidireccional en tiempo real para `adk web` |
| `python-dotenv` | `>=1.0.0` | `1.2.4` | Carga de variables de entorno para configuración local vs. Vertex AI / Gemini Enterprise |
| `python-multipart` | `>=0.0.9` | `0.0.32` | Procesamiento de formularios requerido por FastAPI y ADK Web UI |
| `PyYAML` | `>=6.0.1` | `6.0.3` | Lectura de frontmatter YAML en los archivos `SKILL.md` (Lab 2) |
| `tenacity` | `>=8.2.0` | `9.1.4` | Reintentos resilientes en invocación de herramientas de agentes |
| `requests` | `>=2.31.0` | `2.34.2` | Utilidades de cliente HTTP |
| `opentelemetry-api` / `sdk` | `>=1.24.0` | `1.42.1` | Trazabilidad de eventos multi-agente visualizada en `adk web` |

### 4.2 Instalación Offline mediante Wheelhouse Local (Opcional para Redes Restringidas)
Si las estaciones de trabajo no tienen acceso directo a `pypi.org`, el Administrador de TI puede descargar los 59 paquetes fijados en `requirements-lock.txt` una sola vez hacia una carpeta `./wheelhouse` dentro del repositorio:
```bash
pip download -r requirements-lock.txt -d ./wheelhouse
```
Cuando la carpeta `./wheelhouse` está presente, tanto `./admin_provision_workstation.sh` como `./install.sh` instalan todas las dependencias de manera 100% offline usando `--no-index --find-links ./wheelhouse`.

---

## 5. Permisos de Sistema de Archivos Críticos para Asistentes Sin Privilegios

> **IMPORTANTE PARA ADMINISTRADORES DE TI**:
> Si clona el repositorio y construye el entorno `.venv` utilizando una cuenta elevada (`root` o `Administrator`), **DEBE transferir la propiedad recursiva de toda la carpeta del repositorio al usuario estándar del asistente** antes de entregar el equipo.

¿Por qué es indispensable? Durante los laboratorios prácticos, el asistente (sin permisos de administrador) ejecuta scripts que crean y modifican archivos locales dentro del repositorio:
- `data/telecom_nexus.db` o `data/retail_pulse.db` (La base de datos SQLite y sus archivos temporales WAL requieren permisos de escritura en `data/`)
- `data/exports/` y `data/logs/hook_audit.log` (Reportes generados en el Lab 2 y bitácora de auditoría en el Lab 3)
- `GEMINI.md` y `.agents/` (`rules/`, `skills/`, `mcp_config.json`, `hooks.json` creados en los Labs 2 y 3)
- `src/services/`, `src/agents/` y `mcp_server/` (Archivos editados en los Labs 1, 3 y 4, y restaurados por `./labs/lab-0X-.../install.sh`)

**Solución Automatizada (macOS / Linux)**:
```bash
sudo ./admin_requirements/admin_provision_workstation.sh --user <usuario_asistente>
```
**Solución Manual (macOS / Linux)**:
```bash
sudo chown -R <usuario_asistente>:<grupo_asistente> /ruta/a/antigravity-workshop-telecom
sudo chmod -R u+rwX /ruta/a/antigravity-workshop-telecom
```
**Solución Manual (Windows PowerShell como Administrador)**:
```powershell
icacls "C:\Workshopsntigravity-workshop-telecom" /grant "<UsuarioAsistente>:(OI)(CI)M" /T
```

---

## 6. Lista de Verificación de 10 Puntos antes del Taller (Checklist para TI)

Ejecute `./admin_requirements/admin_provision_workstation.sh --verify-only` iniciando sesión como el **usuario estándar del asistente (sin sudo)** y confirme que los 10 puntos pasen exitosamente:

1. `python3 --version` reporta `Python 3.10+` (`3.11` o `3.12` recomendado).
2. `uv --version` reporta `uv 0.5+`.
3. `git --version` y `sqlite3 --version` responden correctamente desde el `PATH`.
4. `terraform -version` y `gcloud --version` están disponibles en el `PATH` (para el Lab 4).
5. Google Antigravity (`Antigravity 2.0`, `Antigravity IDE` y/o CLI `agy`) abre e inicia sesión correctamente.
6. `./.venv/bin/python -c "import fastapi, uvicorn, pydantic, pytest, httpx, mcp, google.adk, google.genai"` finaliza con código `0`.
7. `./.venv/bin/adk --version` (o `./scripts/run_adk_web.sh --check`) finaliza con código `0`.
8. Ejecutar `./install.sh` muestra `[OK] Pre-provisioned .venv detected with all required packages (zero-install mode)` e inicializa `data/*.db` sin errores de permisos.
9. Ejecutar `./verify.sh` pasa el 100% de las pruebas automatizadas (`21 passed` en Telecom / `20 passed` en Retail).
10. Los puertos locales `127.0.0.1:8001`, `127.0.0.1:8002` y `127.0.0.1:8080` pueden abrirse sin bloqueos del firewall local.
