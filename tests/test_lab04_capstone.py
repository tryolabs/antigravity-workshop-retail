"""
Lab 4 Verification Suite: Multi-Agent Capstone — Intelligent Omnichannel Split-Fulfillment
Routing, Supplier OTIF Chargeback Recovery, Google ADK Multi-Agent Orchestration,
A2A (Agent2Agent) Protocol Discovery & JSON-RPC 2.0, and Cloud Run / Terraform / Gemini Enterprise Readiness.
"""

from __future__ import annotations

from pathlib import Path
import subprocess

from fastapi.testclient import TestClient

from adk_agents.retail_pulse.agent import root_agent
from src.agents.adk_a2a_orchestrator import RetailPulseOrchestratorAgent
from src.main import app

client = TestClient(app)
ROOT_DIR = Path(__file__).resolve().parent.parent


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


def test_adk_multi_agent_orchestration_wms_and_merchandising_handoff() -> None:
    orchestrator = RetailPulseOrchestratorAgent()
    result = orchestrator.run_multi_agent_workflow(
        prompt="Reroute 35 VIP stockout orders and claim breaching vendor OTIF chargebacks.",
        skill_id="omnichannel_fulfillment_routing",
    )
    assert result["status"] == "COMPLETED"
    assert result["orchestrator"] == "retail_pulse_orchestrator_agent"

    wms = result["wms_technical_assessment"]
    assert wms["agent_name"] == "wms_inventory_atp_agent"
    assert wms["rerouted_orders_count"] == 35
    assert wms["protected_customer_ltv_usd"] >= 250000.0
    assert wms["total_post_shipping_margin_usd"] >= 14500.0

    merch = result["merchandising_commercial_assessment"]
    assert merch["agent_name"] == "merchandising_margin_otif_agent"
    assert merch["all_orders_margin_compliant"] is True
    assert merch["all_rerouted_margin_protected"] is True
    assert merch["breaching_vendors_count"] == 6
    assert merch["total_claim_amount_usd"] == 98250.0

    assert len(result["handoff_trace"]) == 2
    assert result["handoff_trace"][0]["to_agent"] == "wms_inventory_atp_agent"
    assert result["handoff_trace"][1]["to_agent"] == "merchandising_margin_otif_agent"

    # Also verify the ADK Development UI (`adk web`) root_agent package structure
    assert root_agent.name == "retail_pulse_root_agent"
    sub_names = [a.name for a in root_agent.sub_agents]
    assert "wms_inventory_agent" in sub_names
    assert "merchandising_margin_agent" in sub_names
    assert "a2a_bridge_agent" in sub_names


def test_a2a_agent_card_discovery_endpoint() -> None:
    for path in ("/.well-known/agent.json", "/api/v1/a2a/agent-card"):
        resp = client.get(path)
        assert resp.status_code == 200, f"Expected 200 OK on {path}, got {resp.status_code}: {resp.text}"
        card = resp.json()
        assert card["name"] == "Retail Pulse ADK Multi-Agent Orchestrator"
        assert card["provider"]["organization"] == "Tryolabs"
        assert "wms_inventory_atp_agent" in card["subagents"]
        assert "merchandising_margin_otif_agent" in card["subagents"]
        skill_ids = {s["id"] for s in card["skills"]}
        assert {
            "omnichannel_fulfillment_routing",
            "vendor_otif_chargeback_claim",
            "promo_margin_floor_audit",
        }.issubset(skill_ids)


def test_a2a_jsonrpc_tasks_send_and_message_send() -> None:
    rpc_payload = {
        "jsonrpc": "2.0",
        "id": "req-capstone-001",
        "method": "tasks/send",
        "params": {
            "id": "task-vip-otif-001",
            "message": {
                "role": "user",
                "parts": [
                    {
                        "type": "text",
                        "text": "Coordinate WMS True ATP rerouting for VIP orders and claim OTIF debit memos.",
                    }
                ],
            },
            "metadata": {
                "skill_id": "omnichannel_fulfillment_routing",
            },
        },
    }
    resp = client.post("/api/v1/a2a", json=rpc_payload)
    assert resp.status_code == 200, f"Expected 200 OK, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert body["jsonrpc"] == "2.0"
    assert body["id"] == "req-capstone-001"
    task = body["result"]
    assert task["id"] == "task-vip-otif-001"
    assert task["status"]["state"] == "completed"
    assert len(task["artifacts"]) == 1

    artifact_data = task["artifacts"][0]["parts"][0]["data"]
    assert artifact_data["wms_technical_assessment"]["rerouted_orders_count"] == 35
    assert artifact_data["merchandising_commercial_assessment"]["total_claim_amount_usd"] == 98250.0
    assert len(task["history"]) == 2

    # Also test `message/send` on `/api/v1/a2a/tasks/send`
    rpc_payload_msg = {
        **rpc_payload,
        "id": "req-capstone-002",
        "method": "message/send",
    }
    resp2 = client.post("/api/v1/a2a/tasks/send", json=rpc_payload_msg)
    assert resp2.status_code == 200
    assert resp2.json()["result"]["status"]["state"] == "completed"


def test_terraform_cloud_run_and_adk_web_deployment_readiness() -> None:
    assert (ROOT_DIR / "Dockerfile").exists()
    assert (ROOT_DIR / ".dockerignore").exists()
    for tf_file in ("versions.tf", "variables.tf", "main.tf", "outputs.tf", "terraform.tfvars.example"):
        assert (ROOT_DIR / "infra" / "terraform" / tf_file).exists(), f"Missing {tf_file}"

    adk_check = subprocess.run(
        [str(ROOT_DIR / "scripts" / "run_adk_web.sh"), "--dry-run"],
        cwd=str(ROOT_DIR),
        capture_output=True,
        text=True,
        check=False,
    )
    assert adk_check.returncode == 0, f"run_adk_web.sh --dry-run failed: {adk_check.stderr}"

    gcp_check = subprocess.run(
        [str(ROOT_DIR / "labs" / "lab-04-multi-agent-capstone" / "deploy_gcp.sh"), "--dry-run"],
        cwd=str(ROOT_DIR),
        capture_output=True,
        text=True,
        check=False,
    )
    assert gcp_check.returncode == 0, f"deploy_gcp.sh --dry-run failed: {gcp_check.stderr}"
    assert "Google Cloud + Terraform + Gemini Enterprise dry-run validation succeeded!" in gcp_check.stdout
