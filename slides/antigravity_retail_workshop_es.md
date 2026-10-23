---
marp: true
theme: default
paginate: true
backgroundColor: #0d1117
color: #f0f6fc
---

![Tryolabs Logo](../assets/tryolabs-logo-dark-bg.png)
##### TALLER EJECUTIVO TRYOLABS • 4 HORAS (10% TEORÍA / 90% LABORATORIOS PRÁCTICOS)
# Ingeniería Agéntica con Google Antigravity — Edición Retail: Construyendo 'Retail Pulse'
**Enrutamiento Omnicanal, Sincronización True ATP e Inteligencia de Márgenes y Contratos OTIF (Impartido por Tryolabs)**

![Architecture Diagram](../assets/retail_domain_es.png)

### Misión del Taller y Arquitectura de Datos
- Datos Técnicos WMS/POS: 150 nodos de inventario (2 DCs + 4 Tiendas), 25 SKUs con GS1 GTIN-14
- Streams de Webhooks y Escaneos: 120 eventos POS/WMS/EDI 856 en JSONL con bloqueos BOPIS y merma
- Datos Comerciales: 200 órdenes omnicanal (LTV Clientes VIP DIAMOND/GOLD, precio vs costo)
- Contratos de Proveedores OTIF: 10 acuerdos comerciales ($500K–$5.5M, metas OTIF y penalizaciones)
- Impacto Medible: Detener $35,113.25 de fuga de margen, rescatar 35 órdenes VIP y cobrar $98,250 OTIF

> **Impartido por Tryolabs • Ejecución 100% Local en Laptop + Despliegue Terraform a Cloud Run y Gemini Enterprise**

<!-- Speaker Notes: Da la bienvenida en nombre de Tryolabs. Destaca el formato 10% teoría / 90% práctica y la combinación de datos técnicos con datos comerciales (contratos, ventas, ingresos/márgenes). -->

---

![Tryolabs Logo](../assets/tryolabs-logo-dark-bg.png)
##### AGENDA Y PROGRESIÓN • 24M TEORÍA / 216M PRÁCTICA
# Ruta Práctica de 4 Horas: Del Triage a Sistemas Multi-Agente ADK y A2A
**Cuatro cápsulas teóricas de 6 minutos seguidas de cuatro laboratorios progresivos de 52–55 minutos**

![Architecture Diagram](../assets/roadmap_es.png)

### Cronograma Minuto a Minuto
- Hora 1 (00:00–00:58): [6m Teoría] Arquitectura Interna y Superficies → [52m Lab 1] Triage y Recuperación Financiera
- Hora 2 (00:58–01:58): [6m Teoría] Rules y Skills Progresivos → [54m Lab 2] Estándares de Dominio y Skill Ejecutivo
- Hora 3 (01:58–02:59): [6m Teoría] MCP, Hooks y Gobernanza Cloud → [55m Lab 3] Servidor FastMCP Local y Hooks
- Hora 4 (02:59–04:00): [6m Teoría] Subagentes, ADK, A2A y Terraform → [55m Lab 4] Capstone Multi-Agente, ADK Dev UI y Cloud
- Checkpoints Auto-Recuperables: ¡Ejecutar ./labs/lab-0X/install.sh aplica las soluciones previas automáticamente!

> **Cada laboratorio incluye README.es.md, PROMPTS.es.md (prompts optimizados), install.sh y verify.sh.**

<!-- Speaker Notes: Explica la agenda de 4 horas y cómo los participantes usarán Antigravity con los prompts optimizados de PROMPTS.es.md. -->

---

![Tryolabs Logo](../assets/tryolabs-logo-dark-bg.png)
##### MÓDULO TEÓRICO 1A (3 MINUTOS) • FUNCIONAMIENTO INTERNO
# Cómo Funciona Google Antigravity Internamente
**Dentro del planificador cognitivo, ensamblador de contexto, compuerta de seguridad y runtime en sandbox**

![Architecture Diagram](../assets/arch_internal_es.png)

### El Ciclo Interno de Ejecución en 5 Etapas
- 1. Cargador Progresivo de Contexto: Recorre el árbol de directorios buscando GEMINI.md y .agents/rules, indexa metadatos YAML de SKILL.md, resuelve menciones @ y gestiona transcript.jsonl
- 2. Planificador Gemini Enterprise: Genera razonamiento intercalado (thinking), sintetiza planes (/plan) y despacha herramientas o subagentes en paralelo
- 3. Compuerta Determinista de Seguridad: Evalúa hooks PreToolUse (código 2 bloquea la acción), políticas de ejecución, ACLs y sandbox de terminal
- 4. Runtime de Herramientas y Puente MCP: Aplica diffs exactos, ejecuta pytest en sandbox e invoca herramientas FastMCP por stdio/SSE
- 5. Verificación en Bucle Cerrado: Ejecuta hooks PostToolUse, analiza resultados de tests y se autocorrige hasta pasar todas las pruebas

> **Concepto Clave: Antigravity no es solo un chat, sino un motor de ingeniería en bucle cerrado verificable.**

<!-- Speaker Notes: Explica en detalle cómo funciona Antigravity por dentro: ensamblaje jerárquico de contexto, razonamiento intercalado, compuerta determinista de hooks/sandbox y bucle de autoverificación. -->

---

![Tryolabs Logo](../assets/tryolabs-logo-dark-bg.png)
##### MÓDULO TEÓRICO 1B (3 MINUTOS) • SUPERFICIES Y MODALIDADES
# Antigravity 2.0, IDE y CLI (`agy`) — Modalidades Clave
**Seleccionando la modalidad y comando slash ideal para cada tarea de ingeniería**

![Architecture Diagram](../assets/surfaces_es.png)

### Funcionalidades que Explorarás Hoy
- Modalidad Pasiva (IDE Tab): Supercomplete sensible al contexto, Tab-to-Jump entre archivos y Tab-to-Auto-Import
- Modalidad Instructiva (Cmd/Ctrl+I y Code Lenses): Selecciona un bloque para refactorización quirúrgica o haz clic en 'Write Tests'
- Modalidad Colaborativa (Chat Canvas y CLI `agy`): Razonamiento multi-archivo con @archivo, @carpeta, @terminal y capturas de pantalla
- Comandos Slash de Alto Impacto: /plan (arquitectura paso a paso), /grill-me (entrevista de diseño), /boost, /teamwork, /learn y /compact
- Panel Auxiliar HTML: Inspección en vivo de Subagentes, Tareas en Segundo Plano, Artefactos y Diffs de Archivos

> **Tip Pro: Inicia tareas complejas con /plan y menciones @archivo; usa Cmd+I para ajustes puntuales de fórmulas.**

<!-- Speaker Notes: Muestra las tres superficies (Antigravity 2.0, IDE y CLI) y cómo combinar @ menciones, /plan y Cmd+I. -->

---

![Tryolabs Logo](../assets/tryolabs-logo-dark-bg.png)
##### LABORATORIO PRÁCTICO 1 (52 MINUTOS) • TRIAGE Y RECUPERACIÓN
# Lab 1: Diagnóstico de Causa Raíz y Recuperación de Ingresos/Márgenes
**Usa Antigravity (/plan, @menciones, Cmd+I, pytest) para corregir dos bugs críticos en producción**

![Architecture Diagram](../assets/retail_domain_es.png)

### Guía del Lab 1 y Prompts Optimizados
- Setup: Ejecuta ./labs/lab-01-margin-inventory-triage/install.sh y abre http://localhost:8002
- Bug #1 (Fuga de Margen Comercial): src/services/promo_pricing.py acumula promos no acumulables e ignora el piso de margen del 15% (-$35,113.25 en pérdidas)
- Bug #2 (Sobreventa Técnica ATP): src/services/inventory_atp.py ignora reserved_bopis_qty, damaged_hold_qty y safety_stock_qty (35 órdenes VIP en riesgo)
- Prompt 1 (/plan): '/plan Inspecciona @src/services/promo_pricing.py, @src/services/inventory_atp.py y @tests/test_lab01_triage.py para diagnosticar los bugs de margen y ATP'
- Prompt 2 (Cmd+I y Fix): Usa Cmd+I en línea para corregir con Decimal y ejecuta ./labs/lab-01-margin-inventory-triage/verify.sh

> **Abre PROMPTS.es.md dentro de labs/lab-01-* para copiar prompts optimizados de Diagnóstico, /plan, Cmd+I y Verificación.**

<!-- Speaker Notes: Inicia el Lab 1. Pide a los asistentes ejecutar install.sh, abrir el dashboard web local y usar los prompts de PROMPTS.es.md. -->

---

![Tryolabs Logo](../assets/tryolabs-logo-dark-bg.png)
##### MÓDULO TEÓRICO 2 (6 MINUTOS) • ARQUITECTURA DE PERSONALIZACIÓN
# Cómo Funcionan Internamente las Rules y Skills Progresivos
**Especializando a Antigravity en tu industria sin saturar la ventana de contexto**

![Architecture Diagram](../assets/customizations_es.png)

### Rules vs. Skills vs. /learn
- Reglas Jerárquicas (GEMINI.md y .agents/rules/*.md): Invariantes de dominio cargados desde la raíz del workspace hasta los subdirectorios (deduplicados automáticamente)
- Skills con Divulgación Progresiva (.agents/skills/<name>/SKILL.md): Solo el frontmatter YAML (name, description) entra al prompt inicial; el cuerpo completo y scripts/ se cargan SOLO al activarse
- Memoria Auto-Mejorable (/learn): Pide a Antigravity codificar un patrón aprendido durante el debugging en una regla o skill permanente
- Jerarquía de Prioridad: Workspace (.agents/) > JSON Declarado (skills.json) > Global (~/.gemini/config/) > Integrado

> **Regla Práctica: Coloca invariantes permanentes en GEMINI.md/rules y flujos multifase con scripts en SKILL.md.**

<!-- Speaker Notes: Explica el mecanismo interno de divulgación progresiva (progressive disclosure) y por qué permite tener decenas de skills sin consumir tokens innecesarios. -->

---

![Tryolabs Logo](../assets/tryolabs-logo-dark-bg.png)
##### LABORATORIO PRÁCTICO 2 (54 MINUTOS) • CEREBRO DE DOMINIO
# Lab 2: Reglas de Industria y Skill de Auditoría Ejecutiva
**Enseña a Antigravity los estándares de tu industria y construye un Auditor Técnico + Comercial**

![Architecture Diagram](../assets/customizations_es.png)

### Guía del Lab 2 y Prompts Optimizados
- Setup: Ejecuta ./labs/lab-02-rules-and-skills/install.sh (aplica la solución del Lab 1 automáticamente)
- Tarea 1 (Reglas de Workspace): Crea GEMINI.md y .agents/rules/retail-standards.md imponiendo Decimal(0.01), validación GS1 Módulo-10 GTIN-14 y piso de margen del 15%
- Tarea 2 (Skill Progresivo): Crea .agents/skills/retail-otif-margin-auditor/SKILL.md correlacionando retrasos EDI 856 con penalizaciones OTIF
- Prompt Optimizado: 'Crea @GEMINI.md, @.agents/rules/retail-standards.md y @.agents/skills/retail-otif-margin-auditor/SKILL.md, y ejecuta @scripts/run_otif_margin_audit.py'
- Verificación: Ejecuta ./labs/lab-02-rules-and-skills/verify.sh y prueba /learn para persistir reglas

> **Abre labs/lab-02-rules-and-skills/PROMPTS.es.md para seguir los prompts paso a paso.**

<!-- Speaker Notes: Guía a los participantes durante el Lab 2 para crear GEMINI.md, reglas de dominio y su primer Skill ejecutable. -->

---

![Tryolabs Logo](../assets/tryolabs-logo-dark-bg.png)
##### MÓDULO TEÓRICO 3 (6 MINUTOS) • MCP, HOOKS Y GOBERNANZA EMPRESARIAL
# Puente MCP en Vivo, Hooks Deterministas y Gobernanza Gemini Enterprise
**Conectando bases de datos en tiempo real con seguridad empresarial demostrable en Google Cloud**

![Architecture Diagram](../assets/governance_es.png)

### Seguridad y Gobernanza en 2 Capas
- Capa 1 — Google Cloud y Gemini Enterprise (Demo en Vivo del Instructor): Cloud IAM (roles/cloudaicompanion.user), Cloud Audit Logs (cloudaicompanion.googleapis.com), perímetros VPC-SC, Cero Retención y Cero Entrenamiento con código del cliente
- Capa 2 — Seguridad Local en Antigravity: Política de Ejecución (strict / request-review / proceed-in-sandbox), Sandbox de Terminal SO, bloqueo de archivos fuera del workspace y listas permitidas/bloqueadas
- Contexto en Vivo vía FastMCP (.agents/mcp_config.json): Expone herramientas Python tipadas sobre SQLite y telemetría vía stdio/SSE
- Hooks Deterministas (.agents/hooks.json): El script PreToolUse inspecciona el JSON en stdin; devolver código 2 bloquea violaciones e imprime un registro de auditoría inmutable

> **Demo del Instructor: Mostrar Cloud Audit Logs en GCP Console + disparar un bloqueo PreToolUse con código 2 localmente.**

<!-- Speaker Notes: Módulo clave de seguridad y gobernanza: muestra en la consola de Google Cloud cómo se auditan las licencias Gemini Enterprise y cómo los Hooks locales bloquean acciones riesgosas. -->

---

![Tryolabs Logo](../assets/tryolabs-logo-dark-bg.png)
##### LABORATORIO PRÁCTICO 3 (55 MINUTOS) • SERVIDOR MCP Y HOOKS
# Lab 3: Servidor FastMCP Local y Guardarraíles de Cumplimiento
**Conecta Antigravity a bases de datos en vivo con protección determinista PreToolUse**

![Architecture Diagram](../assets/governance_es.png)

### Guía del Lab 3 y Prompts Optimizados
- Setup: Ejecuta ./labs/lab-03-mcp-and-hooks/install.sh
- Tarea 1 (Servidor FastMCP): Implementa herramientas en @mcp_server/retail_mcp.py (query_true_atp_inventory, audit_vendor_otif_contracts, simulate_promo_margin_guard, list_at_risk_vip_orders)
- Tarea 2 (MCP y Hook Determinista): Configura .agents/mcp_config.json y .agents/hooks.json (ejecuta @scripts/margin_guard_hook.py bloqueando pisos <15% con código 2)
- Prompt Optimizado: 'Completa @mcp_server/retail_mcp.py, registra @.agents/mcp_config.json y @.agents/hooks.json, y consulta órdenes VIP en riesgo vía MCP'
- Verificación: Ejecuta ./labs/lab-03-mcp-and-hooks/verify.sh y revisa data/logs/hook_compliance_audit.jsonl

> **Abre labs/lab-03-mcp-and-hooks/PROMPTS.es.md para copiar los prompts de construcción y prueba de MCP y Hooks.**

<!-- Speaker Notes: Los asistentes implementan su servidor FastMCP, configuran mcp_config.json y hooks.json, y verifican el bloqueo determinista de violaciones. -->

---

![Tryolabs Logo](../assets/tryolabs-logo-dark-bg.png)
##### MÓDULO TEÓRICO 4 (6 MINUTOS) • SUBAGENTES, GOOGLE ADK, A2A Y TERRAFORM
# Sistemas Multi-Agente con Google ADK, Protocolo A2A y Terraform
**Diseñando arquitecturas multi-agente localmente con `adk web` y desplegando a Cloud Run y Gemini Enterprise**

![Architecture Diagram](../assets/adk_a2a_cloud_es.png)

### Arquitectura Multi-Agente de Punta a Punta
- Subagentes de Antigravity (/teamwork, /boost, /grill-me): Delega tareas paralelas de investigación y programación dentro de Antigravity
- Google ADK (Agent Development Kit): Construye jerarquías multi-agente de dominio (`root_agent` coordinando agentes especialistas Técnico y Comercial con herramientas tipadas)
- Pruebas Locales con ADK Dev UI (`adk web`): Ejecuta `./scripts/run_adk_web.sh` (http://localhost:8080) para inspeccionar trazas de eventos multi-agente, llamadas a herramientas y estado
- Protocolo A2A (Agent2Agent): Publica `GET /.well-known/agent.json` (Agent Card) y `POST /api/v1/a2a` (JSON-RPC 2.0 `tasks/send`) para interoperabilidad entre agentes
- Terraform + Gemini Enterprise: Aprovisiona Cloud Run v2 e IAM vía `infra/terraform/` (`deploy_gcp.sh`) y registra tu agente A2A en Gemini Enterprise (`register_gemini_enterprise_agent.sh`)

> **¡Desarrolla y prueba 100% localmente con `adk web` + `pytest`, y despliega a Google Cloud y Gemini Enterprise con Terraform!**

<!-- Speaker Notes: Explica cómo Antigravity ayuda a diseñar y programar el sistema multi-agente basado en Google ADK + protocolo A2A, cómo probarlo localmente con `adk web` y cómo desplegarlo con Terraform a Google Cloud y Gemini Enterprise. -->

---

![Tryolabs Logo](../assets/tryolabs-logo-dark-bg.png)
##### LABORATORIO PRÁCTICO 4 CAPSTONE (55 MINUTOS) • ADK, A2A Y DESPLIEGUE CLOUD
# Lab 4 Capstone: Construye el Sistema Multi-Agente ADK + A2A
**Usa Antigravity (/grill-me, /boost, Subagentes) para construir, probar en `adk web` y validar Terraform**

![Architecture Diagram](../assets/adk_a2a_cloud_es.png)

### Guía del Lab 4 y Prompts Optimizados
- Setup: Ejecuta ./labs/lab-04-multi-agent-capstone/install.sh
- Tarea 1 (Jerarquía Google ADK): Implementa @src/agents/adk_a2a_orchestrator.py y @adk_agents/retail_pulse/agent.py (WMSInventoryATPAgent + MerchandisingMarginOTIFAgent -> RetailPulseOrchestratorAgent)
- Tarea 2 (Protocolo A2A): Expón GET /.well-known/agent.json y POST /api/v1/a2a (JSON-RPC 2.0 tasks/send) + rutas de enrutamiento omnicanal y reclamos OTIF
- Tarea 3 (ADK Dev UI Local): Ejecuta ./scripts/run_adk_web.sh para probar en `adk web` (http://localhost:8080) y corre ./labs/lab-04-multi-agent-capstone/verify.sh
- Tarea 4 (Terraform y Gemini Enterprise): Valida con ./deploy/deploy_gcp.sh --dry-run, despliega a Cloud Run con Terraform y registra en Gemini Enterprise con ./deploy/register_gemini_enterprise_agent.sh

> **¡Felicidades! Ejecuta ./labs/lab-04-multi-agent-capstone/verify.sh para validar el 100% de la suite de pruebas.**

<!-- Speaker Notes: Guía a los participantes en el Capstone final: pruebas en el dashboard web, en la interfaz interactiva ADK Dev UI (`./scripts/run_adk_web.sh`) y validación de despliegue Terraform (`./deploy/deploy_gcp.sh --dry-run`). -->