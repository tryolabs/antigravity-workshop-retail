"""
Lab 3 Verification Suite: FastMCP Server Tools (`mcp_server/retail_mcp.py`),
`.agents/mcp_config.json`, and Lifecycle Guard Hooks (`.agents/hooks.json` & `scripts/margin_guard_hook.py`).
"""

from __future__ import annotations

import json
from pathlib import Path

import mcp_server.retail_mcp as retail_mcp
from scripts.margin_guard_hook import evaluate_hook_payload

ROOT_DIR = Path(__file__).resolve().parent.parent


def test_mcp_server_exposes_all_four_retail_tools() -> None:
    for fn_name in (
        "query_true_atp_inventory",
        "audit_vendor_otif_contracts",
        "simulate_promo_margin_guard",
        "list_at_risk_vip_orders",
    ):
        assert hasattr(retail_mcp, fn_name), f"mcp_server/retail_mcp.py is missing tool '{fn_name}'"

    # 1. Test query_true_atp_inventory
    atp_res = retail_mcp.query_true_atp_inventory("SKU-SONY-OLED65", location_id="STORE-NYC-5TH", required_qty=1)
    assert atp_res["locations"][0]["true_atp_qty"] == 0
    assert atp_res["locations"][0]["oversell_risk"] is True

    # 2. Test audit_vendor_otif_contracts
    otif_res = retail_mcp.audit_vendor_otif_contracts(only_breaching=True)
    assert otif_res["breaching_contracts_count"] == 6
    assert otif_res["total_recoverable_chargeback_usd"] == 98250.0

    # 3. Test simulate_promo_margin_guard
    sim_res = retail_mcp.simulate_promo_margin_guard(
        sku="SKU-DYSON-V15DT",
        qty=2,
        promo_codes_csv="VIP25,FLASH20,EMP30",
    )
    assert sim_res["margin_floor_clamped"] is True
    assert sim_res["margin_compliant"] is True

    # 4. Test list_at_risk_vip_orders
    vip_res = retail_mcp.list_at_risk_vip_orders(loyalty_tier="DIAMOND")
    assert vip_res["matching_at_risk_orders_count"] == 20
    assert vip_res["exposed_customer_ltv_usd"] > 150000.0


def test_mcp_config_json_is_valid_and_registers_retail_server() -> None:
    mcp_cfg_path = ROOT_DIR / ".agents" / "mcp_config.json"
    assert mcp_cfg_path.exists(), ".agents/mcp_config.json must exist"
    cfg = json.loads(mcp_cfg_path.read_text(encoding="utf-8"))
    assert "mcpServers" in cfg
    assert "retail-pulse-mcp" in cfg["mcpServers"]
    srv = cfg["mcpServers"]["retail-pulse-mcp"]
    assert "command" in srv
    assert any("retail_mcp.py" in arg for arg in srv.get("args", []))


def test_hooks_json_and_margin_guard_hook_script() -> None:
    hooks_path = ROOT_DIR / ".agents" / "hooks.json"
    assert hooks_path.exists(), ".agents/hooks.json must exist"
    hooks_cfg = json.loads(hooks_path.read_text(encoding="utf-8"))
    assert len(hooks_cfg) >= 1
    first_hook = next(iter(hooks_cfg.values()))
    assert "PreToolUse" in first_hook
    pre_list = first_hook["PreToolUse"]
    assert len(pre_list) >= 1
    assert "margin_guard_hook.py" in pre_list[0]["hooks"][0]["command"]

    # Safe payload -> allow
    safe_decision = evaluate_hook_payload(
        {
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "pytest tests/test_lab03_mcp_hooks.py"},
            }
        }
    )
    assert safe_decision["decision"] == "allow"

    # Destructive SQL payload -> deny
    drop_decision = evaluate_hook_payload(
        {
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "sqlite3 data/retail_pulse.db 'DROP TABLE vendor_contracts;'"},
            }
        }
    )
    assert drop_decision["decision"] == "deny"

    # Margin floor bypass payload -> deny
    bypass_decision = evaluate_hook_payload(
        {
            "toolCall": {
                "name": "edit_file",
                "args": {"Replacement": "contract_min_margin_floor_pct = 0.0"},
            }
        }
    )
    assert bypass_decision["decision"] == "deny"
