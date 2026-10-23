# Lab 02 — Optimized Antigravity Prompts Playbook (English)

Use these copy-pasteable prompts inside **Google Antigravity** to complete Lab 02.

---

## 1. Discovery Prompt (Explore Domain & Audit Script)

```text
Inspect @src/models.py, @src/services/vendor_otif_auditor.py, @scripts/run_otif_margin_audit.py, and @tests/test_lab02_rules_skills.py.
Summarize the exact requirements that GEMINI.md, .agents/rules/retail-standards.md, and .agents/skills/margin-otif-audit/SKILL.md must satisfy.
```

---

## 2. `/plan` Prompt (Design Workspace Rules & Progressive Disclosure Skill)

```text
/plan Plan the creation of our Antigravity workspace customizations for Retail Pulse:
1. Root GEMINI.md (>= 300 chars) documenting our SQLite schema and non-negotiable engineering/commercial rules: Decimal with ROUND_HALF_UP, GS1 gtin_14 Modulo-10 validation, contract_min_margin_floor_pct clamping, True ATP formula deducting unprocessed_webhook_delta_qty, and VIP DIAMOND/GOLD prioritization.
2. .agents/rules/retail-standards.md reinforcing Decimal(ROUND_HALF_UP), gtin_14/RFID rules, True ATP, and Vendor OTIF (otif_target_pct) chargeback formulas.
3. .agents/skills/margin-otif-audit/SKILL.md with valid YAML frontmatter (name: margin-otif-audit and third-person description) and step-by-step instructions to execute scripts/run_otif_margin_audit.py and inspect data/exports/executive_margin_otif_audit.json and .md.
```

---

## 3. Implementation Prompt (Create Rules & Skill Files)

```text
Create GEMINI.md, .agents/rules/retail-standards.md, and .agents/skills/margin-otif-audit/SKILL.md according to the plan so they satisfy all assertions in @tests/test_lab02_rules_skills.py.
```

---

## 4. Skill Activation & Verification Prompt

```text
Activate our margin-otif-audit skill to generate the executive margin, True ATP, and vendor OTIF audit report. Summarize the 6 breaching vendors and total recoverable chargeback USD, then run ./labs/lab-02-rules-and-skills/verify.sh.
```

---

## 5. Power-User & Stretch Prompts (`/learn`, `/schedule`, `/compact`)

### 5A. Auto-Generate Rules with `/learn`
```text
/learn Whenever writing a new endpoint or service in Retail Pulse, always return monetary fields quantized via Decimal("0.01") and cross-check any vendor contract status against EDI_856_ASN_AUDIT records in data/logs/pos_wms_webhooks.jsonl.
```

### 5B. Recurring Executive OTIF Audit (`/schedule`)
```text
/schedule Run scripts/run_otif_margin_audit.py every 30 minutes and alert me if total_recoverable_chargeback_usd exceeds $90,000 or if any DIAMOND order falls into AT_RISK_STOCKOUT.
```
