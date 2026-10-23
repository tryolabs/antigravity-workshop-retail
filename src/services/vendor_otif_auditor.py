"""
Combined Technical EDI 856 ASN + Commercial Vendor OTIF Contract Auditor.
"""

from __future__ import annotations

import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

from src.database import ROOT_DIR, fetch_all
from src.models import VendorOTIFAuditRecord

TWO_PLACES = Decimal("0.01")
HUNDRED = Decimal("100.00")


def _q2(val: Decimal | float | int | str) -> Decimal:
    return Decimal(str(val)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def load_edi_856_alerts_by_contract(jsonl_path: Path | None = None) -> dict[str, list[dict[str, Any]]]:
    """Read EDI_856_ASN_AUDIT records from data/logs/pos_wms_webhooks.jsonl grouped by contract_id."""
    target = jsonl_path or (ROOT_DIR / "data" / "logs" / "pos_wms_webhooks.jsonl")
    grouped: dict[str, list[dict[str, Any]]] = {}
    if not target.exists():
        return grouped
    with open(target, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            ev = json.loads(line)
            if ev.get("event_type") == "EDI_856_ASN_AUDIT":
                cid = str(ev.get("contract_id", ""))
                grouped.setdefault(cid, []).append(ev)
    return grouped


def audit_vendor_contracts(
    only_breaching: bool = False,
    db_path: Path | None = None,
    jsonl_path: Path | None = None,
) -> dict[str, Any]:
    """
    Cross-reference commercial vendor_contracts in SQLite with technical EDI 856 ASN
    delay/short-shipment logs to calculate OTIF compliance gaps and recoverable chargebacks.
    """
    rows = fetch_all("SELECT * FROM vendor_contracts ORDER BY contract_id", db_path=db_path)
    edi_by_contract = load_edi_856_alerts_by_contract(jsonl_path=jsonl_path)

    records: list[VendorOTIFAuditRecord] = []
    total_recoverable_usd = Decimal("0.00")
    total_delayed_po_usd = Decimal("0.00")
    breaching_count = 0

    for r in rows:
        cid = str(r["contract_id"])
        target_pct = _q2(r["otif_target_pct"])
        actual_pct = _q2(r["actual_otif_pct"])
        otif_gap = _q2(max(Decimal("0.00"), target_pct - actual_pct))
        delayed_po = _q2(r["delayed_po_value_usd"])
        penalty_pct = _q2(r["chargeback_penalty_pct"])

        is_breaching = actual_pct < target_pct or str(r["status"]) == "BREACH_HOLD"
        if only_breaching and not is_breaching:
            continue

        if is_breaching:
            breaching_count += 1
            recoverable = _q2(delayed_po * (penalty_pct / HUNDRED))
            action = "ISSUE_DEBIT_MEMO_AND_REROUTE_SAFETY_STOCK"
        else:
            recoverable = Decimal("0.00")
            action = "MAINTAIN_PREFERRED_VENDOR_ALLOCATION"

        total_recoverable_usd = _q2(total_recoverable_usd + recoverable)
        total_delayed_po_usd = _q2(total_delayed_po_usd + delayed_po)

        edi_events = edi_by_contract.get(cid, [])
        non_compliant_asns = [e for e in edi_events if not e.get("otif_compliant", True)]

        records.append(
            VendorOTIFAuditRecord(
                contract_id=cid,
                vendor_name=str(r["vendor_name"]),
                category=str(r["category"]),
                buyer_id=str(r["buyer_id"]),
                annual_spend_commitment_usd=_q2(r["annual_spend_commitment_usd"]),
                contract_min_margin_floor_pct=_q2(r["contract_min_margin_floor_pct"]),
                otif_target_pct=target_pct,
                actual_otif_pct=actual_pct,
                otif_gap_pct=otif_gap,
                late_shipments_count=int(r["late_shipments_count"]),
                short_shipments_count=int(r["short_shipments_count"]),
                delayed_po_value_usd=delayed_po,
                chargeback_penalty_pct=penalty_pct,
                recoverable_chargeback_usd=recoverable,
                edi_856_asn_alerts_count=len(non_compliant_asns),
                status="BREACH_HOLD" if is_breaching else "COMPLIANT",
                recommended_action=action,
            )
        )

    return {
        "evaluated_contracts_count": len(records),
        "breaching_contracts_count": breaching_count,
        "total_delayed_po_value_usd": float(total_delayed_po_usd),
        "total_recoverable_chargeback_usd": float(total_recoverable_usd),
        "contracts": [rec.model_dump(mode="json") for rec in records],
    }
