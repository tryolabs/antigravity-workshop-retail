<p align="center">
  <img src="../../src/static/tryolabs-logo.png" alt="Tryolabs Logo" width="180" />
</p>

# Laboratorio 02: Reglas del Espacio de Trabajo (`GEMINI.md`) y Habilidades de Divulgación Progresiva (`SKILL.md`)

**Impartido por Tryolabs • Potenciado por Google Antigravity y Gemini Enterprise**

> **Idioma / Language:** [Español](./README.es.md) | [English](./README.md) • **Guía de Prompts:** [PROMPTS.es.md](./PROMPTS.es.md) | [PROMPTS.md](./PROMPTS.md)

---

## 1. Escenario y Objetivo Arquitectónico

En el Laboratorio 01 instruiste manualmente a Antigravity para corregir cálculos con `float`, validación GS1 GTIN-14 y desfase de inventario ATP por webhooks POS.
En un equipo empresarial de ingeniería retail, **nunca deberías repetir los estándares del dominio en cada prompt**.

En el **Laboratorio 02**, transformarás a Antigravity en un **Experto de Dominio Retail y Comercio Omnicanal** mediante dos primitivas clave de personalización:
1. **Reglas Jerárquicas del Proyecto (`GEMINI.md` y `.agents/rules/retail-standards.md`)**:
   - Se cargan automáticamente en el contexto para exigir `Decimal(ROUND_HALF_UP)`, validación GS1 GTIN-14 (`gtin_14`), protección de `contract_min_margin_floor_pct` y la fórmula de True ATP (`on_hand - reserved - safety_stock - unprocessed_webhook_delta_qty`).
2. **Habilidades de Divulgación Progresiva (`.agents/skills/margin-otif-audit/SKILL.md`)**:
   - Antigravity indexa únicamente el bloque YAML (`name`, `description`) sin saturar la ventana de contexto.
   - Cuando el usuario solicita una **Auditoría Ejecutiva de Margen y Contratos OTIF**, Antigravity activa `SKILL.md` bajo demanda, ejecuta `scripts/run_otif_margin_audit.py`, cruza `vendor_contracts` con los eventos `EDI_856_ASN_AUDIT` en `data/logs/pos_wms_webhooks.jsonl`, y genera `data/exports/executive_margin_otif_audit.json` y `.md` (`$98,250.00` en penalidades recuperables sobre 6 proveedores en incumplimiento).

---

## 2. Inicialización del Laboratorio

Ejecuta el instalador del Laboratorio 02 (aplica automáticamente la solución del Laboratorio 01 primero):

```bash
./labs/lab-02-rules-and-skills/install.sh
```

---

## 3. Resolución Paso a Paso con Google Antigravity

Abre [PROMPTS.es.md](./PROMPTS.es.md) y ejecuta los prompts en orden:

1. **Crear `GEMINI.md` y `.agents/rules/retail-standards.md`** con las reglas financieras (`Decimal`, `ROUND_HALF_UP`), validación GS1 (`gtin_14`), pisos de margen (`contract_min_margin_floor_pct`), True ATP (`unprocessed_webhook_delta_qty`) y penalidades OTIF (`otif_target_pct`).
2. **Crear la Habilidad `.agents/skills/margin-otif-audit/SKILL.md`** con frontmatter YAML (`name: margin-otif-audit`, `description: ...`) que invoque `scripts/run_otif_margin_audit.py`.
3. **Invocar la Habilidad y Verificar**:
   ```bash
   ./labs/lab-02-rules-and-skills/verify.sh
   ```

> **Solución de Referencia:** Ejecuta `./labs/lab-02-rules-and-skills/apply_solution.sh`.
