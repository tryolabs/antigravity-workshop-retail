<p align="center">
  <img src="../../src/static/tryolabs-logo.png" alt="Tryolabs Logo" width="180" />
</p>

# Laboratorio 01: Triaje de Piso de Margen Promocional e Inventario True ATP

**Impartido por Tryolabs • Potenciado por Google Antigravity y Gemini Enterprise**

> **Idioma / Language:** [Español](./README.es.md) | [English](./README.md) • **Guía de Prompts:** [PROMPTS.es.md](./PROMPTS.es.md) | [PROMPTS.md](./PROMPTS.md) • **PDF:** [ES](./LAB_01_INSTRUCTIONS_ES.pdf) | [EN](./LAB_01_INSTRUCTIONS_EN.pdf)

---

## 1. Escenario e Impacto Comercial

Durante nuestro evento flash omnicanal de fin de semana, **Retail Pulse** sufrió dos incidentes críticos de producción en `WEB_ECOMM`, `MOBILE_APP`, `POS_INSTORE` y `BOPIS`:

1. **Incidente #1A — Fuga de Margen Promocional (`src/services/promo_pricing.py`)**:
   - Los clientes acumularon tres códigos promocionales no acumulables (`VIP25`, `FLASH20`, `EMP30`) simultáneamente.
   - El motor de precios sumó los porcentajes linealmente (`25% + 20% + 30% = 75%` de descuento) usando `float` binario e ignoró por completo el piso contractual `contract_min_margin_floor_pct`.
   - Resultado: **¡30 órdenes en `MARGIN_HOLD` están perdiendo `-$35,113.25` por debajo del costo mayorista!**
2. **Incidente #1B — Sobreventa VIP por Stock Fantasma (`src/services/inventory_atp.py`)**:
   - Las tiendas insignia (`STORE-NYC-5TH`, `STORE-MIA-BRICKELL`) y `WH-EAST-NJ01` sufrieron retrasos de sincronización de webhooks POS (`unprocessed_webhook_delta_qty` registrado en `data/logs/pos_wms_webhooks.jsonl`).
   - El calculador Available-to-Promise (ATP) devolvió directamente `on_hand_qty` sin restar `reserved_qty`, `safety_stock_qty` ni `unprocessed_webhook_delta_qty`.
   - Resultado: **¡35 órdenes VIP `DIAMOND` y `GOLD` (`>$250,000` en Customer LTV) fueron asignadas a ubicaciones donde el True ATP real es `0` (`raw_atp = -1`)!**

---

## 2. Inicialización del Laboratorio

Ejecuta el instalador del Laboratorio 01 desde la raíz del repositorio para inicializar los bugs iniciales y la base de datos SQLite:

```bash
./labs/lab-01-margin-inventory-triage/install.sh
```

Verifica que la suite de pruebas falle inicialmente debido a ambos bugs:

```bash
./.venv/bin/pytest tests/test_lab01_triage.py
```

Opcional — inicia el Dashboard Web Omnicanal en vivo en una segunda terminal:

```bash
./.venv/bin/uvicorn src.main:app --reload --port 8002
```
Abre `http://localhost:8002` para observar las alertas rojas `BUG #1A ACTIVE` y `BUG #1B ACTIVE`.

---

## 3. Resolución Paso a Paso con Google Antigravity

Abre [PROMPTS.es.md](./PROMPTS.es.md) y pega los prompts en **Google Antigravity** (Chat Lateral, `/plan` o Edición en Línea `Cmd+I`):

### Paso 3.1: Descubrimiento de Causa Raíz con Menciones de Contexto `@`
Pega el **Prompt de Descubrimiento** de `PROMPTS.es.md` haciendo referencia a `@src/services/promo_pricing.py`, `@src/services/inventory_atp.py`, `@data/logs/pos_wms_webhooks.jsonl` y `@tests/test_lab01_triage.py`.

### Paso 3.2: Plan de Remediación Estructurado con `/plan`
Ejecuta el **Prompt `/plan`** en Antigravity para verificar los requisitos matemáticos y comerciales exactos antes de editar el código:
- **Corrección #1A (`src/services/promo_pricing.py`)**:
  - Usa `Decimal` con `ROUND_HALF_UP` (`Decimal("0.01")`) y valida el `gtin_14` del SKU mediante `validate_gs1_gtin14`.
  - Rechaza códigos promocionales inactivos (`active == 0`) o desconocidos agregándolos a `rejected_promo_codes`.
  - Nunca combines promociones no acumulables (`is_stackable == 0`). Compara la promoción no acumulable individual más alta contra la composición multiplicativa de promociones acumulables (`is_stackable == 1`), seleccionando la opción que otorgue al cliente el mayor descuento previo al límite de margen.
  - Aplica el piso de margen efectivo (`max(contract_min_margin_floor_pct, pisos de promociones aplicadas)`): limita `net_revenue_usd` para que `gross_margin_pct >= effective_floor_pct` y establece `margin_floor_clamped = True`.
- **Corrección #1B (`src/services/inventory_atp.py`)**:
  - Calcula `raw_atp_qty = on_hand_qty - reserved_qty - safety_stock_qty - unprocessed_webhook_delta_qty`.
  - Calcula `true_atp_qty = max(0, raw_atp_qty)`.
  - Marca `oversell_risk = (true_atp_qty < required_qty) or (raw_atp_qty <= 0)`.

### Paso 3.3: Aplicar Correcciones y Verificar
Permite que Antigravity implemente las correcciones (o usa la edición en línea `Cmd+I` dentro de `src/services/promo_pricing.py` y `src/services/inventory_atp.py`), y luego ejecuta:

```bash
./labs/lab-01-margin-inventory-triage/verify.sh
```

> **¿Necesitas consultar o aplicar la solución de referencia?** Ejecuta `./labs/lab-01-margin-inventory-triage/apply_solution.sh` en cualquier momento.
