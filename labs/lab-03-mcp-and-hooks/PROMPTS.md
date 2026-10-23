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
1. How the two existing MCP tools (`query_true_atp_inventory` and `audit_vendor_otif_contracts`) connect to `data/retail_pulse.db` and our service layer.
2. What exact JSON fields `simulate_promo_margin_guard` and `list_at_risk_vip_orders` must return to pass `tests/test_lab03_mcp_hooks.py`.
3. How `scripts/margin_guard_hook.py` inspects `PreToolUse` payloads on stdin and writes compliance events to `data/logs/hook_compliance_audit.jsonl`.
```

### Prompt 1B — Commercial / Operations Track: Understand Live MCP Grounding vs. Deterministic Hooks
```text
Read @mcp_server/retail_mcp.py and @scripts/margin_guard_hook.py. Explain in plain retail terms:
1. How the 4 MCP tools let a Merchandising or Supply Chain manager ask live questions about True ATP stock, breaching vendor OTIF contracts, promo margin impact, and VIP orders at risk without writing SQL.
2. Why we pair our `.agents/rules/retail-standards.md` guidelines with a deterministic `PreToolUse` hook (`scripts/margin_guard_hook.py`) that blocks anyone from turning off the 15% margin floor.
```

---

## Phase 2: Planning (`/plan`)

### Prompt 2 — Create an Implementation Plan for MCP Tools & Lifecycle Hooks
```text
/plan Design the implementation for Lab 03 so that all 5 tests in @tests/test_lab03_mcp_hooks.py pass:
1. Implement `simulate_promo_margin_guard(promo_code: str, category: str = "", loyalty_tier: str = "SILVER") -> str` and `list_at_risk_vip_orders(loyalty_tier: str = "DIAMOND", limit: int = 20) -> str` in @mcp_server/retail_mcp.py.
2. Create `.agents/mcp_config.json` registering `retail-pulse-mcp` using `.venv/bin/python -m mcp_server.retail_mcp`.
3. Create `.agents/hooks.json` registering `.venv/bin/python scripts/margin_guard_hook.py` as a `PreToolUse` hook matching `write_file|edit_file|replace_file_content`.
```

---

## Phase 3: Inline Edit (`Cmd+I` / `Ctrl+I`)

Open `mcp_server/retail_mcp.py`, highlight the `simulate_promo_margin_guard` and `list_at_risk_vip_orders` stub functions, press `Cmd+I` (macOS) or `Ctrl+I` (Windows/Linux), and enter:

```text
Implement `simulate_promo_margin_guard` using `evaluate_sku_promo` from `src.services.promo_pricing` (with `enforce_floor=True`) so it returns JSON with `promo_code`, `loyalty_tier`, `category_filter`, `total_skus_evaluated`, `floor_violations_count`, `requires_vp_merchandising_override`, and `skus`. Then implement `list_at_risk_vip_orders` querying `omnichannel_orders` where `status = 'AT_RISK_STOCKOUT'` ordered by `customer_ltv_usd DESC`, returning JSON with `loyalty_tier_filter`, `count`, `total_ltv_exposed_usd`, and `orders`.
```

---

## Phase 4: Full Implementation Prompts

### Prompt 4A — Implement `mcp_server/retail_mcp.py`, `.agents/mcp_config.json`, and `.agents/hooks.json`
```text
Complete Lab 03 by performing the following changes:
1. In @mcp_server/retail_mcp.py:
   - Implement `simulate_promo_margin_guard(promo_code: str, category: str = "", loyalty_tier: str = "SILVER") -> str` by querying `wms_inventory` for distinct SKUs (filtered by `category` if provided), calling `evaluate_sku_promo(conn, sku, promo_code=promo_code, loyalty_tier=loyalty_tier, enforce_floor=True)`, and returning JSON with `promo_code`, `loyalty_tier`, `category_filter`, `total_skus_evaluated`, `floor_violations_count`, `requires_vp_merchandising_override`, and `skus`.
   - Implement `list_at_risk_vip_orders(loyalty_tier: str = "DIAMOND", limit: int = 20) -> str` by querying `omnichannel_orders` where `status = 'AT_RISK_STOCKOUT'` (and `customer_loyalty_tier = ?` unless `loyalty_tier.upper() == "ALL"`), ordered by `customer_ltv_usd DESC LIMIT ?`, and returning JSON with `loyalty_tier_filter`, `count`, `total_ltv_exposed_usd`, and `orders`.
2. Create `.agents/mcp_config.json` with a `mcpServers` entry for `retail-pulse-mcp` running `.venv/bin/python -m mcp_server.retail_mcp`.
3. Create `.agents/hooks.json` with a `PreToolUse` hook matching `write_file|edit_file|replace_file_content` that runs `.venv/bin/python scripts/margin_guard_hook.py`.
```

---

## Phase 5: Verification & Live MCP Queries

### Prompt 5A — Run Automated Verification (`verify.sh`)
```text
Run `./labs/lab-03-mcp-and-hooks/verify.sh` and confirm all 5 tests in `tests/test_lab03_mcp_hooks.py` pass, and show the latest entry in `data/logs/hook_compliance_audit.jsonl`.
```

### Prompt 5B — Commercial Track: Query the Retail MCP Tools for Executive Insights
```text
Using the functions in @mcp_server/retail_mcp.py, answer these three commercial questions:
1. If we stack promo `VIP-EXTRA-15` for `DIAMOND` loyalty members across the `Electronics` category, how many SKUs hit the 15% margin floor clamp?
2. How many `DIAMOND` VIP orders are currently in `AT_RISK_STOCKOUT` status, and what is the total Customer LTV exposed?
3. Which breaching vendors have an OTIF score below 85%, and what is their combined chargeback penalty in USD?
```

---

## Phase 6: Stretch Challenge — Test the Margin Guard Hook Under Adversarial Prompting

### Prompt 6 — Attempt to Bypass the 15% Margin Floor (Observe Hook Blocking)
```text
Simulate a request from an unauthorized campaign manager: test running `scripts/margin_guard_hook.py` against a tool payload that tries to edit `src/services/promo_pricing.py` with `enforce_floor=False`, and another payload that tries to set `"minimum_margin_pct": 0.05`. Show the hook exit codes, stderr messages, and the audit entries recorded in `data/logs/hook_compliance_audit.jsonl`.
```
