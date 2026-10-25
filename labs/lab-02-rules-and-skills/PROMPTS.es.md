<p align="center">
  <img src="../../src/static/tryolabs-logo.png" alt="Tryolabs Logo" width="180" />
</p>

# Laboratorio 02 — Guía de Prompts Optimizados de Antigravity (Español)

> **Idioma / Language:** [Español](./PROMPTS.es.md) | [English](./PROMPTS.md) • **Guía del Lab:** [README.es.md](./README.es.md) | [README.md](./README.md) • **PDF:** [ES](./LAB_02_INSTRUCTIONS_ES.pdf) | [EN](./LAB_02_INSTRUCTIONS_EN.pdf)

Utiliza estos prompts listos para copiar y pegar dentro de **Google Antigravity** para completar el Laboratorio 02.

---

## 1. Prompt de Descubrimiento (Explorar Estándares y Script de Auditoría)

```text
Inspecciona @src/models.py, @src/services/vendor_otif_auditor.py, @scripts/run_otif_margin_audit.py y @tests/test_lab02_rules_skills.py.
Resume los requisitos exactos que deben cumplir GEMINI.md, .agents/rules/retail-standards.md y .agents/skills/margin-otif-audit/SKILL.md.
```

---

## 2. Prompt `/plan` (Diseñar Reglas y Habilidad de Divulgación Progresiva)

```text
/plan Planifica la creación de nuestras personalizaciones de Antigravity para Retail Pulse:
1. GEMINI.md en la raíz (>= 300 caracteres) documentando el esquema SQLite y las reglas innegociables: Decimal con ROUND_HALF_UP, validación GS1 gtin_14 Módulo-10, límite contract_min_margin_floor_pct, fórmula True ATP restando unprocessed_webhook_delta_qty y priorización VIP DIAMOND/GOLD.
2. .agents/rules/retail-standards.md reforzando Decimal(ROUND_HALF_UP), estándares gtin_14/RFID, True ATP y fórmulas de penalidades OTIF (otif_target_pct).
3. .agents/skills/margin-otif-audit/SKILL.md con frontmatter YAML válido (name: margin-otif-audit y description en tercera persona) e instrucciones paso a paso para ejecutar scripts/run_otif_margin_audit.py e inspeccionar data/exports/executive_margin_otif_audit.json y .md.
```

---

## 3. Prompt de Implementación (Crear Archivos de Reglas y Habilidad)

```text
Crea GEMINI.md, .agents/rules/retail-standards.md y .agents/skills/margin-otif-audit/SKILL.md siguiendo el plan para cumplir todas las validaciones en @tests/test_lab02_rules_skills.py.
```

---

## 4. Prompt de Activación de Habilidad y Verificación

```text
Activa nuestra habilidad margin-otif-audit para generar el reporte ejecutivo de margen, True ATP y contratos OTIF. Resume los 6 proveedores en incumplimiento y el monto total recuperable en USD, y luego ejecuta ./labs/lab-02-rules-and-skills/verify.sh.
```

---

## 5. Prompts Avanzados (`/learn`, `/schedule`, `/compact`)

### 5A. Autogenerar Reglas con `/learn`
```text
/learn Siempre que escribas un nuevo endpoint o servicio en Retail Pulse, devuelve los campos monetarios cuantizados mediante Decimal("0.01") y cruza cualquier estado de contrato de proveedor contra los registros EDI_856_ASN_AUDIT en data/logs/pos_wms_webhooks.jsonl.
```

### 5B. Auditoría Ejecutiva Programada (`/schedule`)
```text
/schedule Ejecuta scripts/run_otif_margin_audit.py cada 30 minutos y avísame si total_recoverable_chargeback_usd supera los $90,000 o si alguna orden DIAMOND entra en estado AT_RISK_STOCKOUT.
```
