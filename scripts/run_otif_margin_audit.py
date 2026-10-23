#!/usr/bin/env python3
"""
Executive Commercial Margin & Vendor OTIF Audit Helper Script (Used by Lab 2 Skill).

Generates both a JSON report (`data/exports/executive_margin_otif_audit.json`)
and a Markdown Executive Brief (`data/exports/executive_margin_otif_audit.md`),
and prints the structured JSON report to stdout.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.services.inventory_atp import audit_vip_oversell_exposure
from src.services.promo_pricing import audit_margin_hold_orders
from src.services.vendor_otif_auditor import audit_vendor_contracts


def generate_executive_audit_report() -> dict[str, Any]:
    margin_summary = audit_margin_hold_orders()
    vip_atp_summary = audit_vip_oversell_exposure()
    vendor_otif_summary = audit_vendor_contracts(only_breaching=True)

    report = {
        "report_title": "Retail Pulse Executive Margin, True ATP & Vendor OTIF Audit",
        "margin_floor_audit": margin_summary,
        "vip_oversell_atp_audit": {
            "at_risk_orders_total": vip_atp_summary["at_risk_orders_total"],
            "detected_oversell_orders_count": vip_atp_summary["detected_oversell_orders_count"],
            "exposed_customer_ltv_usd": vip_atp_summary["exposed_customer_ltv_usd"],
        },
        "vendor_otif_breach_audit": {
            "breaching_contracts_count": vendor_otif_summary["breaching_contracts_count"],
            "total_delayed_po_value_usd": vendor_otif_summary["total_delayed_po_value_usd"],
            "total_recoverable_chargeback_usd": vendor_otif_summary["total_recoverable_chargeback_usd"],
            "breaching_contracts": vendor_otif_summary["contracts"],
        },
    }

    exports_dir = ROOT_DIR / "data" / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)

    json_out = exports_dir / "executive_margin_otif_audit.json"
    md_out = exports_dir / "executive_margin_otif_audit.md"

    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    md_lines = [
        "# Retail Pulse Executive Margin, True ATP & Supplier OTIF Audit Report",
        "",
        "## 1. Promotional Margin Floor Protection (`MARGIN_HOLD` Audit)",
        f"- **Evaluated Margin-Hold Orders**: {margin_summary['margin_hold_orders_count']}",
        f"- **Legacy Negative Margin Leakage Eliminated**: ${margin_summary['legacy_negative_margin_leakage_usd']:,.2f}",
        f"- **Recalculated Guarded Gross Margin**: ${margin_summary['recalculated_total_margin_usd']:,.2f}",
        f"- **All Orders Margin Compliant**: `{margin_summary['all_orders_margin_compliant']}`",
        "",
        "## 2. True Available-to-Promise (ATP) & VIP Oversell Exposure",
        f"- **At-Risk VIP Orders Audited**: {vip_atp_summary['at_risk_orders_total']}",
        f"- **Detected Phantom-Stock Oversell Orders**: {vip_atp_summary['detected_oversell_orders_count']}",
        f"- **Protected VIP Customer LTV Exposure**: ${vip_atp_summary['exposed_customer_ltv_usd']:,.2f}",
        "",
        "## 3. Supplier Commercial OTIF Breaches & Recoverable Chargebacks",
        f"- **Breaching Suppliers Count**: {vendor_otif_summary['breaching_contracts_count']}",
        f"- **Total Delayed PO Exposure**: ${vendor_otif_summary['total_delayed_po_value_usd']:,.2f}",
        f"- **Total Recoverable Chargeback Penalties**: ${vendor_otif_summary['total_recoverable_chargeback_usd']:,.2f}",
        "",
        "| Contract ID | Vendor Name | Target OTIF % | Actual OTIF % | Delayed PO $ | Chargeback % | Recoverable Penalty $ |",
        "| :--- | :--- | :---: | :---: | :---: | :---: | :---: |",
    ]
    for c in vendor_otif_summary["contracts"]:
        md_lines.append(
            f"| `{c['contract_id']}` | {c['vendor_name']} | {c['otif_target_pct']}% | "
            f"{c['actual_otif_pct']}% | ${float(c['delayed_po_value_usd']):,.2f} | "
            f"{c['chargeback_penalty_pct']}% | **${float(c['recoverable_chargeback_usd']):,.2f}** |"
        )

    with open(md_out, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    return report


if __name__ == "__main__":
    result = generate_executive_audit_report()
    print(json.dumps(result, indent=2))
