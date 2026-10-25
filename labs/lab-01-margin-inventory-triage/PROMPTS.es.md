<p align="center">
  <img src="../../src/static/tryolabs-logo.png" alt="Tryolabs Logo" width="180" />
</p>

# Laboratorio 01 — Guía de Prompts Optimizados de Antigravity (Español)

> **Idioma / Language:** [Español](./PROMPTS.es.md) | [English](./PROMPTS.md) • **Guía del Lab:** [README.es.md](./README.es.md) | [README.md](./README.md) • **PDF:** [ES](./LAB_01_INSTRUCTIONS_ES.pdf) | [EN](./LAB_01_INSTRUCTIONS_EN.pdf)

Utiliza estos prompts listos para copiar y pegar dentro de **Google Antigravity** (Chat Lateral, `/plan`, edición en línea `Cmd+I` o CLI `agy`) para resolver el Laboratorio 01.

---

## 1. Prompt de Descubrimiento (Triaje de Causa Raíz con `@` Mentions)

```text
Inspecciona @src/services/promo_pricing.py, @src/services/inventory_atp.py, @data/logs/pos_wms_webhooks.jsonl y @tests/test_lab01_triage.py.
Ejecuta pytest sobre tests/test_lab01_triage.py y explica:
1. Por qué las 30 órdenes MARGIN_HOLD en omnichannel_orders pierden -$35,113.25 por debajo del costo mayorista cuando se envían códigos como VIP25, FLASH20 y EMP30 juntos.
2. Por qué 35 órdenes VIP DIAMOND y GOLD en STORE-NYC-5TH y WH-EAST-NJ01 sufren sobreventa de stock fantasma debido al retraso de sincronización de webhooks POS.
```

---

## 2. Prompt `/plan` (Plan de Remediación Estructurado)

```text
/plan Crea un plan paso a paso para corregir el Bug #1A en @src/services/promo_pricing.py y el Bug #1B en @src/services/inventory_atp.py para que pasen todas las pruebas en @tests/test_lab01_triage.py:
1. En promo_pricing.py:
   - Usa Decimal cuantizado a Decimal("0.01") con ROUND_HALF_UP y valida el dígito verificador GS1 GTIN-14 mediante validate_gs1_gtin14().
   - Rechaza códigos inactivos (active != 1) o desconocidos en rejected_promo_codes.
   - Aplica reglas de acumulación: promociones no acumulables (is_stackable == 0) no pueden combinarse con ningún otro código; promociones acumulables (is_stackable == 1) se componen multiplicativamente. Elige la opción válida que otorgue el mayor descuento al cliente antes del límite de margen.
   - Limita net_revenue_usd para que gross_margin_pct nunca caiga por debajo de max(contract_min_margin_floor_pct, pisos de promociones aplicadas), marcando margin_floor_clamped = True.
2. En inventory_atp.py:
   - Calcula raw_atp_qty = on_hand_qty - reserved_qty - safety_stock_qty - unprocessed_webhook_delta_qty.
   - Define true_atp_qty = max(0, raw_atp_qty) y oversell_risk = (true_atp_qty < required_qty) o (raw_atp_qty <= 0).
```

---

## 3. Prompt en Línea `Cmd+I` (Edición Rápida en `inventory_atp.py`)

Selecciona la función `calculate_location_atp` en `src/services/inventory_atp.py`, presiona `Cmd+I` (macOS) / `Ctrl+I` (Windows/Linux) y escribe:

```text
Valida gtin_14 usando validate_gs1_gtin14(), calcula raw_atp = on_hand - reserved - safety_stock - webhook_delta, limita true_atp = max(0, raw_atp) y establece oversell_risk = (true_atp < required_qty) o (raw_atp <= 0).
```

---

## 4. Prompt de Implementación y Verificación

```text
Implementa las correcciones completas en @src/services/promo_pricing.py y @src/services/inventory_atp.py siguiendo el plan, y luego ejecuta ./labs/lab-01-margin-inventory-triage/verify.sh para confirmar que las 6 pruebas en test_lab01_triage.py pasen al 100%.
```

---

## 5. Prompts Avanzados (`/grill-me`, `/browser`, `/learn`)

### 5A. Entrevista de Casos Borde (`/grill-me`)
```text
/grill-me Entrevístame sobre casos borde de acumulación promocional en retail omnicanal (por ejemplo, paquetes BOGO, descuentos de empleados combinados con liquidación y redondeo al centavo exacto en órdenes multi-unidad).
```

### 5B. Verificación Visual en el Dashboard (`/browser`)
```text
/browser Abre http://localhost:8002, verifica que las tarjetas KPI "1. Promo Margin Floor Guard" y "2. True ATP & VIP Oversell Radar" muestren PROTECTED y TRUE ATP ACTIVE, y prueba SKU-SONY-OLED65 con los códigos VIP25,FLASH20,EMP30 en el simulador interactivo.
```

### 5C. Persistir Aprendizaje (`/learn`)
```text
/learn Persiste la regla de que todo cálculo de precios en Retail Pulse debe usar Decimal(ROUND_HALF_UP) y respetar contract_min_margin_floor_pct, y que el cálculo de ATP siempre debe restar reserved_qty, safety_stock_qty y unprocessed_webhook_delta_qty.
```
