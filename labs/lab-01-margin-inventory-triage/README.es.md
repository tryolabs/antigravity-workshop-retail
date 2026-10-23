# Laboratorio 01: Triaje de Piso de Margen Promocional e Inventario True ATP

**Impartido por Tryolabs • Potenciado por Google Antigravity y Gemini Enterprise**

> **Idioma / Language:** [Español](./README.es.md) | [English](./README.md) • **Guía de Prompts:** [PROMPTS.es.md](./PROMPTS.es.md) | [PROMPTS.md](./PROMPTS.md)

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

Ejecuta el instalador del Laboratorio 01 desde la raíz del repositorio:

```bash
./labs/lab-01-margin-inventory-triage/install.sh
```

Verifica que la suite de pruebas falle inicialmente debido a ambos bugs:

```bash
./.venv/bin/pytest tests/test_lab01_triage.py
```

Opcional — inicia el Dashboard Web en vivo en otra terminal:

```bash
./.venv/bin/uvicorn src.main:app --reload --port 8002
```
Abre `http://localhost:8002` para observar las alertas rojas `BUG #1A ACTIVE` y `BUG #1B ACTIVE`.

---

## 3. Resolución Paso a Paso con Google Antigravity

Abre [PROMPTS.es.md](./PROMPTS.es.md) y utiliza la secuencia de prompts optimizados en **Google Antigravity**:

1. **Descubrimiento de Causa Raíz (`@` Mentions)**: Analiza `@src/services/promo_pricing.py`, `@src/services/inventory_atp.py`, `@data/logs/pos_wms_webhooks.jsonl` y `@tests/test_lab01_triage.py`.
2. **Planificación Estructurada (`/plan`)**: Genera un plan que reemplace `float` por `Decimal` (`ROUND_HALF_UP`), valide `gtin_14`, impida apilar promociones `is_stackable == 0`, aplique el piso `contract_min_margin_floor_pct`, y calcule `true_atp_qty = max(0, on_hand_qty - reserved_qty - safety_stock_qty - unprocessed_webhook_delta_qty)`.
3. **Implementación y Verificación**:
   ```bash
   ./labs/lab-01-margin-inventory-triage/verify.sh
   ```

> **¿Quieres aplicar la solución de referencia?** Ejecuta `./labs/lab-01-margin-inventory-triage/apply_solution.sh`.
