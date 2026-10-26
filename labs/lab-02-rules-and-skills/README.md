<p align="center">
  <img src="../../src/static/tryolabs-logo.png" alt="Tryolabs Logo" width="180" />
</p>

# Lab 02: Workspace Rules (`GEMINI.md`) & Progressive Disclosure Skills (`SKILL.md`)

**Delivered by Tryolabs • Powered by Google Antigravity & Gemini Enterprise**

> **Language / Idioma:** [English](./README.md) | [Español](./README.es.md) • **Prompt Playbook:** [PROMPTS.md](./PROMPTS.md) | [PROMPTS.es.md](./PROMPTS.es.md) • **PDF:** [EN (Dark)](./LAB_02_INSTRUCTIONS_EN.pdf) | [EN (Light)](./LAB_02_INSTRUCTIONS_EN_LIGHT.pdf) | [ES (Dark)](./LAB_02_INSTRUCTIONS_ES.pdf) | [ES (Light)](./LAB_02_INSTRUCTIONS_ES_LIGHT.pdf)

---

## 1. Scenario & Architectural Goal

In Lab 01, you manually instructed Antigravity to fix binary `float` pricing errors, GS1 GTIN-14 validation, and POS webhook lag ATP drift.
In an enterprise retail engineering team, **you should never have to repeat domain standards in every prompt**.

In **Lab 02**, you will transform Antigravity into a permanent **Retail & Omnichannel Commerce Domain Expert** using two core Antigravity Customization primitives:
1. **Hierarchical Workspace Rules (`GEMINI.md` & `.agents/rules/retail-standards.md`)**:
   - Automatically loaded into context to enforce `Decimal(ROUND_HALF_UP)` currency math, GS1 GTIN-14 Modulo-10 check-digit validation (`gtin_14`), `contract_min_margin_floor_pct` protection, and the True ATP formula (`on_hand - reserved - safety_stock - unprocessed_webhook_delta_qty`).
2. **Progressive Disclosure Skills (`.agents/skills/margin-otif-audit/SKILL.md`)**:
   - Lightweight YAML frontmatter (`name`, `description`) is indexed by Antigravity without bloating the token window.
   - When a developer or commercial buyer asks for a **Margin & Supplier OTIF Audit**, Antigravity dynamically loads `SKILL.md`, executes `scripts/run_otif_margin_audit.py`, cross-references SQLite `vendor_contracts` with `EDI_856_ASN_AUDIT` events in `data/logs/pos_wms_webhooks.jsonl`, and produces `data/exports/executive_margin_otif_audit.json` and `.md` (`$98,250.00` in recoverable chargebacks across 6 breaching suppliers!).

---

## 2. Lab Setup

Run the Lab 02 installer (which automatically applies the Lab 01 solution first so latecomers are caught up!):

```bash
./labs/lab-02-rules-and-skills/install.sh
```

---

## 3. Step-by-Step Resolution Using Google Antigravity

Open [PROMPTS.md](./PROMPTS.md) and execute the prompts in order:

### Step 3.1: Generate `GEMINI.md` & `.agents/rules/retail-standards.md`
Use the **Workspace Rules Prompt** in `PROMPTS.md` (or `/plan`) to create:
- `GEMINI.md` at the repository root (`>= 300` characters) documenting the database tables (`sku_catalog`, `wms_inventory`, `vendor_contracts`, `promo_campaigns`, `omnichannel_orders`) and non-negotiable guardrails (`Decimal`, `ROUND_HALF_UP`, `gtin_14`, `contract_min_margin_floor_pct`, `unprocessed_webhook_delta_qty`).
- `.agents/rules/retail-standards.md` documenting financial precision, GS1/RFID standards, True ATP, and Vendor OTIF (`otif_target_pct`) chargeback rules.

### Step 3.2: Create the Progressive Disclosure Skill (`.agents/skills/margin-otif-audit/SKILL.md`)
Create `.agents/skills/margin-otif-audit/SKILL.md` with required YAML frontmatter:
```yaml
---
name: margin-otif-audit
description: >-
  Use this skill when asked to audit commercial gross margin leakage, verify True
  Available-to-Promise (ATP) VIP oversell exposure, or calculate recoverable vendor
  OTIF contract chargeback penalties backed by EDI 856 ASN logs.
---
```
And step-by-step instructions to run `./.venv/bin/python scripts/run_otif_margin_audit.py` and inspect `data/exports/executive_margin_otif_audit.json` and `.md`.

### Step 3.3: Trigger the Skill & Verify
Ask Antigravity in chat:
> *"Run a full executive margin, True ATP, and supplier OTIF chargeback audit using our workspace skill."*

Then run the verification script:
```bash
./labs/lab-02-rules-and-skills/verify.sh
```

> **Reference Solution:** Run `./labs/lab-02-rules-and-skills/apply_solution.sh` at any time.
