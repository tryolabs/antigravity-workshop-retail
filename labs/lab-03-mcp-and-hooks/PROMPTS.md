<p align="center">
  <img src="../../src/static/tryolabs-logo.png" alt="Tryolabs Logo" width="180" />
</p>

# Lab 03 Prompt Playbook: Retail MCP Server & Deterministic Margin Hooks

Copy and paste these prompts into **Google Antigravity** as you progress through Lab 03. Each section includes prompts tailored for both the **Technical Track** and the **Commercial / Merchandising Track**.

---

## Phase 1: Discovery & Architecture Inspection

### Prompt 1A — Technical Track: Inspect the Starter MCP Server & Hook Script
```text
Read @mcp_server/retail_mcp.py, @scripts/margin_guard_hook.py, and @tests/test_lab03_mcp_hooks.py.
Summarize:
1. How the starter MCP tool (`query_true_atp_inventory`) connects to `data/retail_pulse.db` and our service layer.
2. What exact JSON fields `audit_vendor_otif_contracts`, `simulate_promo_margin_guard`, and `list_at_risk_vip_orders` must return to pass `tests/test_lab03_mcp_hooks.py`.
3. How `scripts/margin_guard_hook.py` inspects `--phase pre` (`PreToolUse`) and `--phase post` (`PostToolUse`) payloads on stdin and writes compliance events to `data/logs/hook_compliance_audit.jsonl`.
```

### Prompt 1B — Commercial / Operations Track: Understand Live MCP Grounding vs. Deterministic Hooks
```text
Read @mcp_server/retail_mcp.py and @scripts/margin_guard_hook.py. Explain in plain retail terms:
1. How the 4 MCP tools let a Merchandising or Supply Chain manager ask live questions about True ATP stock, breaching vendor OTIF contracts, promo margin impact, and VIP orders at risk without writing SQL.
2. Why we pair our `.agents/rules/retail-standards.md` guidelines with a deterministic `PreToolUse` hook (`scripts/margin_guard_hook.py`) that blocks anyone from turning off the 15% margin floor or running destructive SQL on `wms_inventory` and `omnichannel_orders`.
```

---

## Phase 2: Planning (`/plan`)

### Prompt 2 — Create an Implementation Plan for MCP Tools & Lifecycle Hooks
```text
/plan Design the implementation for Lab 03 so that all tests in @tests/test_lab03_mcp_hooks.py pass:
1. Implement `audit_vendor_otif_contracts(only_breaching: bool = True) -> str`, `simulate_promo_margin_guard(sku: str, qty: int = 1, promo_codes_csv: str = "") -> str`, and `list_at_risk_vip_orders(loyalty_tier: str = "DIAMOND") -> str` in @mcp_server/retail_mcp.py.
2. Update `.agents/mcp_config.json` registering `retail-pulse-mcp` using `"command": "./.venv/bin/python"` and `"args": ["mcp_server/retail_mcp.py"]`.
3. Update `.agents/hooks.json` registering `./.venv/bin/python scripts/margin_guard_hook.py --phase pre` on `PreToolUse` (`run_command|execute_command|bash|write_file|edit_file`) and `./.venv/bin/python scripts/margin_guard_hook.py --phase post` on `PostToolUse`.
```

---

## Phase 3: Inline Edit (`Cmd+I` / `Ctrl+I`)

Open `mcp_server/retail_mcp.py`, highlight the `audit_vendor_otif_contracts`, `simulate_promo_margin_guard`, and `list_at_risk_vip_orders` stub functions, press `Cmd+I` (macOS) or `Ctrl+I` (Windows/Linux), and enter:

```text
Implement `audit_vendor_otif_contracts` using `audit_all_vendor_otif_contracts(only_breaching=only_breaching)`. Implement `simulate_promo_margin_guard` by parsing `promo_codes_csv` into a list of uppercase codes and calling `calculate_promotional_order_pricing(sku=sku, qty=qty, promo_codes=codes)`. Implement `list_at_risk_vip_orders` by joining `omnichannel_orders`, `wms_inventory`, and `sku_catalog`, evaluating `evaluate_location_atp` for each order, and returning JSON with `loyalty_tier_filter`, `at_risk_order_count`, `total_vip_ltv_at_risk_usd`, and `orders`.
```

---

## Phase 4: Full Implementation Prompts

### Prompt 4A — Implement `mcp_server/retail_mcp.py`, `.agents/mcp_config.json`, and `.agents/hooks.json`
```text
Complete Lab 03 by performing the following changes:
1. In @mcp_server/retail_mcp.py:
   - Implement `audit_vendor_otif_contracts(only_breaching: bool = True) -> str` by returning `json.dumps(audit_all_vendor_otif_contracts(only_breaching=only_breaching), indent=2)`.
   - Implement `simulate_promo_margin_guard(sku: str, qty: int = 1, promo_codes_csv: str = "") -> str` by parsing `promo_codes_csv` into uppercase promo codes and returning `json.dumps(calculate_promotional_order_pricing(sku=sku, qty=qty, promo_codes=codes), indent=2)`.
   - Implement `list_at_risk_vip_orders(loyalty_tier: str = "DIAMOND") -> str` by querying `omnichannel_orders` joined with `wms_inventory` and `sku_catalog`, filtering to orders where `evaluate_location_atp(..., required_qty=int(row["qty"]))["oversell_risk"]` is True (or `status == 'AT_RISK_STOCKOUT'`), and returning JSON with `loyalty_tier_filter`, `at_risk_order_count`, `total_vip_ltv_at_risk_usd`, and `orders`.
2. Update `.agents/mcp_config.json` with a `mcpServers` entry for `retail-pulse-mcp` running `"command": "./.venv/bin/python"` and `"args": ["mcp_server/retail_mcp.py"]`.
3. Update `.agents/hooks.json` with `PreToolUse` (`./.venv/bin/python scripts/margin_guard_hook.py --phase pre`) and `PostToolUse` (`./.venv/bin/python scripts/margin_guard_hook.py --phase post`).
```

---

## Phase 5: Verification & Live MCP Queries

### Prompt 5A — Run Automated Verification (`verify.sh`)
```text
Run `./labs/lab-03-mcp-and-hooks/verify.sh` and confirm all 13 cumulative tests across Labs 01-03 pass (including all 3 tests in `tests/test_lab03_mcp_hooks.py`), and show the latest entry in `data/logs/hook_compliance_audit.jsonl`.
```

### Prompt 5B — Commercial Track: Query the Retail MCP Tools for Executive Insights
```text
Using the functions in @mcp_server/retail_mcp.py, answer these three commercial questions:
1. If we stack promos `VIP20,FLASH15,CLEARANCE10` on `SKU-OLED-65` (qty=1), does it trigger the 15% margin floor clamp (`margin_floor_clamped`), and what is the clamped unit price?
2. How many `DIAMOND` VIP orders are currently at risk of stockout, and what is the total Customer LTV exposed (`total_vip_ltv_at_risk_usd`)?
3. Which 6 breaching vendors fail their contracted OTIF SLA, and what is their combined chargeback penalty in USD (`total_chargeback_usd`)?
```

---

## Phase 6: Stretch Challenge — Test the Margin Guard Hook Under Adversarial Prompting

### Prompt 6 — Attempt to Bypass the 15% Margin Floor (Observe Hook Blocking)
```text
Simulate a request from an unauthorized campaign manager: test running `scripts/margin_guard_hook.py --phase pre` against a tool payload that tries to edit `src/services/promo_pricing.py` with `margin_floor_pct = 0.0 # DISABLE_MARGIN_FLOOR`, and another payload that tries to run `DROP TABLE wms_inventory;`. Show the hook exit codes (`2`), JSON `deny` decisions, and the audit entries recorded in `data/logs/hook_compliance_audit.jsonl`.
```
