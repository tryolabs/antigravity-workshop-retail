---
name: margin-otif-audit
description: >-
  Use this skill when asked to audit commercial gross margin leakage, verify True
  Available-to-Promise (ATP) VIP oversell exposure, or calculate recoverable vendor
  OTIF contract chargeback penalties backed by EDI 856 ASN logs.
---

# Retail Pulse Margin, True ATP & Vendor OTIF Audit Skill

Follow this runbook whenever the user asks for an executive commercial margin audit, VIP stockout risk assessment, or supplier OTIF chargeback calculation.

## Step-by-Step Procedure

1. **Run the Executive Margin & OTIF Audit Script**:
   Execute the helper script using the workspace virtual environment:
   ```bash
   ./.venv/bin/python scripts/run_otif_margin_audit.py
   ```
2. **Inspect Generated Audit Artifacts**:
   - Read `data/exports/executive_margin_otif_audit.json` for structured metrics.
   - Read `data/exports/executive_margin_otif_audit.md` for the formatted Markdown table.
3. **Verify the Three Core Pillars**:
   - **Pillar 1 — Promo Margin Floor Protection (`MARGIN_HOLD`)**:
     Confirm `all_orders_margin_compliant` is `true` and report how much legacy negative margin leakage (`legacy_negative_margin_leakage_usd`) was eliminated.
   - **Pillar 2 — True ATP & VIP Oversell Exposure (`AT_RISK_STOCKOUT`)**:
     Report `detected_oversell_orders_count` and total `exposed_customer_ltv_usd` across `DIAMOND` and `GOLD` loyalty tiers caused by POS webhook sync lag (`unprocessed_webhook_delta_qty`).
   - **Pillar 3 — Supplier OTIF Breaches & Chargebacks (`BREACH_HOLD`)**:
     List all breaching vendor contracts (`actual_otif_pct < otif_target_pct`), their `delayed_po_value_usd`, `chargeback_penalty_pct`, and total `total_recoverable_chargeback_usd`.
4. **Run Automated Verification**:
   ```bash
   ./.venv/bin/pytest tests/test_lab02_rules_skills.py -v
   ```
