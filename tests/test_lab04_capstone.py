"""
Lab 4 Verification Suite: Multi-Agent Capstone — Intelligent Omnichannel Split-Fulfillment
Routing & Supplier OTIF Chargeback Recovery API Endpoints.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_optimize_routing_prioritizes_vip_and_preserves_margin_floors() -> None:
    resp = client.post(
        "/api/v1/fulfillment/optimize-routing",
        json={"loyalty_tiers": ["DIAMOND", "GOLD"], "persist_changes": False},
    )
    assert resp.status_code == 200, f"Expected 200 OK, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == "OPTIMIZED"
    assert data["evaluated_orders_count"] == 35
    assert data["rerouted_orders_count"] == 35
    assert data["protected_customer_ltv_usd"] >= 250000.0
    assert data["total_post_shipping_margin_usd"] >= 14500.0

    decisions = data["decisions"]
    assert len(decisions) == 35

    # Verify DIAMOND orders are prioritized ahead of GOLD orders
    tiers = [d["loyalty_tier"] for d in decisions]
    first_gold_idx = tiers.index("GOLD")
    assert all(t == "DIAMOND" for t in tiers[:first_gold_idx])
    assert all(t == "GOLD" for t in tiers[first_gold_idx:])

    # Verify DIAMOND orders are sorted by descending customer_ltv_usd
    diamond_ltvs = [float(d["customer_ltv_usd"]) for d in decisions[:first_gold_idx]]
    assert diamond_ltvs == sorted(diamond_ltvs, reverse=True)

    # Verify every rerouted order moved from phantom-stock node to a healthy node with margin floor preserved
    for dec in decisions:
        assert dec["assigned_location_id"] != dec["original_location_id"]
        assert dec["assigned_location_true_atp"] >= dec["qty"]
        assert dec["margin_floor_preserved"] is True
        assert float(dec["post_shipping_margin_pct"]) >= float(dec["contract_min_margin_floor_pct"])
        assert dec["routing_status"] == "REROUTED_MARGIN_PROTECTED"


def test_claim_vendor_chargebacks_computes_exact_debit_memos() -> None:
    resp = client.post(
        "/api/v1/vendors/claim-chargebacks",
        json={"min_shortfall_pct": 5.0},
    )
    assert resp.status_code == 200, f"Expected 200 OK, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == "CLAIMS_GENERATED"
    assert data["breaching_vendors_count"] == 6
    assert data["total_claim_amount_usd"] == 98250.0

    for claim in data["claims"]:
        assert float(claim["actual_otif_pct"]) < float(claim["otif_target_pct"])
        assert float(claim["claim_amount_usd"]) > 0.0
        assert int(claim["edi_asn_evidence_count"]) >= 1
        assert claim["claim_status"] == "DEBIT_MEMO_READY"


def test_dashboard_summary_endpoint_aggregates_all_kpis() -> None:
    resp = client.get("/api/v1/dashboard/summary")
    assert resp.status_code == 200
    body = resp.json()
    assert body["margin_audit"]["all_orders_margin_compliant"] is True
    assert body["vip_atp_audit"]["detected_oversell_orders_count"] == 35
    assert body["vendor_audit"]["breaching_contracts_count"] == 6
    assert body["routing_simulation"]["rerouted_orders_count"] == 35
    assert body["chargeback_simulation"]["total_claim_amount_usd"] == 98250.0
