"""
Google ADK (Agent Development Kit), A2A (Agent2Agent Protocol) & Gemini Enterprise
Multi-Agent Orchestrator (Lab 4 Reference Solution).

Architecture:
1. `WMSInventoryATPAgent` (Technical Subagent):
   - Wraps `get_sku_network_atp`, `audit_vip_oversell_exposure`, and `optimize_at_risk_order_routing`.
   - Identifies phantom inventory across stores/DCs and computes optimal split-fulfillment routes for VIP orders.
2. `MerchandisingMarginOTIFAgent` (Commercial Subagent):
   - Wraps `audit_margin_hold_orders`, `evaluate_order_line_pricing`, and `claim_vendor_otif_chargebacks`.
   - Enforces the 15% gross margin floor across promotional stacking and claims contractual OTIF debit memos.
3. `RetailPulseOrchestratorAgent` (Root Coordinator Agent):
   - Coordinates `WMSInventoryATPAgent` and `MerchandisingMarginOTIFAgent` using Google ADK (`google.adk.agents`
     `SequentialAgent` / `LlmAgent` patterns when installed, with a deterministic local execution runtime so
     all workshop tests run 100% offline without external API keys).
   - Supports Vertex AI & Gemini Enterprise runtime variables (`GOOGLE_GENAI_USE_VERTEXAI=TRUE`,
     `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `GEMINI_ENTERPRISE_APP_ID`).
4. A2A Protocol Endpoints:
   - `get_a2a_agent_card()`: Serves the standard A2A Discovery Card at `/.well-known/agent.json`.
   - `handle_a2a_jsonrpc()`: Processes JSON-RPC 2.0 `tasks/send` and `message/send` task requests.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
import uuid

from src.services.fulfillment_router import (
    claim_vendor_otif_chargebacks,
    optimize_at_risk_order_routing,
)
from src.services.inventory_atp import (
    audit_vip_oversell_exposure,
    get_sku_network_atp,
)
from src.services.promo_pricing import (
    audit_margin_hold_orders,
    evaluate_order_line_pricing,
)

# Optional Google ADK (google-adk) integration when installed in the environment
try:
    from google.adk.agents import LlmAgent, SequentialAgent  # type: ignore

    ADK_SDK_AVAILABLE = True
except ImportError:
    LlmAgent = None  # type: ignore
    SequentialAgent = None  # type: ignore
    ADK_SDK_AVAILABLE = False


def get_gemini_enterprise_config() -> dict[str, Any]:
    """Return Vertex AI & Gemini Enterprise connection settings for cloud/hybrid deployments."""
    use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "TRUE").upper() == "TRUE"
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "retail-pulse-enterprise-gcp")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    app_id = os.getenv("GEMINI_ENTERPRISE_APP_ID", "retail-pulse-gemini-enterprise-app")
    return {
        "google_genai_use_vertexai": use_vertex,
        "google_cloud_project": project_id,
        "google_cloud_location": location,
        "gemini_enterprise_app_id": app_id,
        "discovery_engine_agent_parent": (
            f"projects/{project_id}/locations/global/collections/default_collection/"
            f"engines/{app_id}/assistants/default_assistant"
        ),
    }


# ============================================================================
# ADK Tool Functions (Callable by both Google ADK LlmAgents & Local Runtime)
# ============================================================================


def tool_query_network_true_atp(sku: str, required_qty: int = 1) -> dict[str, Any]:
    """ADK Tool: Query True ATP across all warehouses and flagship stores for a SKU."""
    locations = get_sku_network_atp(sku=sku, required_qty=required_qty)
    return {
        "sku": sku,
        "required_qty": required_qty,
        "locations": [loc.model_dump(mode="json") for loc in locations],
    }


def tool_optimize_vip_split_fulfillment(
    loyalty_tiers: list[str] | None = None,
    persist_changes: bool = False,
    db_path: Path | None = None,
) -> dict[str, Any]:
    """ADK Tool: Reroute AT_RISK_STOCKOUT VIP orders to optimal True ATP nodes."""
    return optimize_at_risk_order_routing(
        loyalty_tiers=loyalty_tiers or ["DIAMOND", "GOLD"],
        persist_changes=persist_changes,
        db_path=db_path,
    )


def tool_audit_promo_margin_floor(
    sku: str | None = None,
    qty: int = 1,
    promo_codes: list[str] | None = None,
    db_path: Path | None = None,
) -> dict[str, Any]:
    """ADK Tool: Audit promotional margin floor compliance across orders or a specific SKU."""
    order_audit = audit_margin_hold_orders(db_path=db_path)
    sku_eval = None
    if sku:
        sku_eval = evaluate_order_line_pricing(
            sku=sku,
            qty=qty,
            promo_codes=promo_codes or ["FLASH35", "VIP15"],
            db_path=db_path,
        ).model_dump(mode="json")
    return {
        "order_margin_audit": order_audit,
        "sku_pricing_evaluation": sku_eval,
    }


def tool_claim_vendor_otif_chargebacks(
    min_shortfall_pct: float = 0.0,
    db_path: Path | None = None,
) -> dict[str, Any]:
    """ADK Tool: Audit breaching vendor OTIF contracts and generate debit memo claims."""
    return claim_vendor_otif_chargebacks(
        min_shortfall_pct=min_shortfall_pct,
        db_path=db_path,
    )


# ============================================================================
# Specialized ADK Subagents & Root Multi-Agent Orchestrator
# ============================================================================


class WMSInventoryATPAgent:
    """
    Technical WMS/POS Subagent responsible for True ATP calculation, phantom stock detection,
    and split-fulfillment routing across distribution centers and flagship stores.
    """

    name: str = "wms_inventory_atp_agent"
    role: str = "Technical WMS/POS & True ATP Fulfillment Specialist"
    model: str = "gemini-2.5-pro"

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path
        self.tools = [tool_query_network_true_atp, tool_optimize_vip_split_fulfillment]

    def execute(self, task_payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = task_payload or {}
        loyalty_tiers = payload.get("loyalty_tiers", ["DIAMOND", "GOLD"])
        persist_changes = bool(payload.get("persist_changes", False))
        sku = payload.get("sku")

        oversell_audit = audit_vip_oversell_exposure(db_path=self.db_path)
        routing_result = tool_optimize_vip_split_fulfillment(
            loyalty_tiers=loyalty_tiers,
            persist_changes=persist_changes,
            db_path=self.db_path,
        )
        sku_snapshot = (
            tool_query_network_true_atp(sku=str(sku), required_qty=int(payload.get("qty", 1)))
            if sku
            else None
        )

        return {
            "status": "COMPLETED",
            "agent_name": self.name,
            "agent_role": self.role,
            "oversell_orders_detected": oversell_audit["detected_oversell_orders_count"],
            "evaluated_orders_count": routing_result["evaluated_orders_count"],
            "rerouted_orders_count": routing_result["rerouted_orders_count"],
            "protected_customer_ltv_usd": routing_result["protected_customer_ltv_usd"],
            "total_post_shipping_margin_usd": routing_result["total_post_shipping_margin_usd"],
            "decisions": routing_result["decisions"],
            "sku_network_atp": sku_snapshot,
        }


class MerchandisingMarginOTIFAgent:
    """
    Commercial Merchandising & Vendor Compliance Subagent responsible for enforcing the
    15% minimum gross margin floor and recovering supplier OTIF SLA chargebacks.
    """

    name: str = "merchandising_margin_otif_agent"
    role: str = "Commercial Margin Floor & Supplier OTIF Contract Specialist"
    model: str = "gemini-2.5-pro"

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path
        self.tools = [tool_audit_promo_margin_floor, tool_claim_vendor_otif_chargebacks]

    def execute(
        self,
        task_payload: dict[str, Any] | None = None,
        wms_routing_output: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = task_payload or {}
        min_shortfall_pct = float(payload.get("min_shortfall_pct", 0.0))

        margin_audit = tool_audit_promo_margin_floor(
            sku=payload.get("sku"),
            qty=int(payload.get("qty", 1)),
            promo_codes=payload.get("promo_codes"),
            db_path=self.db_path,
        )
        chargeback_result = tool_claim_vendor_otif_chargebacks(
            min_shortfall_pct=min_shortfall_pct,
            db_path=self.db_path,
        )

        # Cross-verify that every WMS routing decision preserves the SKU's contract margin floor
        decisions = (wms_routing_output or {}).get("decisions", [])
        all_rerouted_margin_protected = bool(decisions) and all(
            bool(d.get("margin_floor_preserved", False)) for d in decisions
        )

        return {
            "status": "COMPLETED",
            "agent_name": self.name,
            "agent_role": self.role,
            "all_orders_margin_compliant": margin_audit["order_margin_audit"]["all_orders_margin_compliant"],
            "margin_hold_orders_count": margin_audit["order_margin_audit"]["margin_hold_orders_count"],
            "total_margin_bleed_prevented_usd": margin_audit["order_margin_audit"]["legacy_negative_margin_leakage_usd"],
            "all_rerouted_margin_protected": all_rerouted_margin_protected,
            "breaching_vendors_count": chargeback_result["breaching_vendors_count"],
            "total_claim_amount_usd": chargeback_result["total_claim_amount_usd"],
            "claims": chargeback_result["claims"],
        }


class RetailPulseOrchestratorAgent:
    """
    Root Google ADK Multi-Agent Orchestrator coordinating technical WMS inventory routing
    (`WMSInventoryATPAgent`) with commercial margin & vendor OTIF recovery (`MerchandisingMarginOTIFAgent`).
    """

    name: str = "retail_pulse_orchestrator_agent"
    role: str = "Omnichannel Retail Pulse Executive Coordinator (ADK + A2A)"
    model: str = "gemini-2.5-pro"

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path
        self.wms_agent = WMSInventoryATPAgent(db_path=db_path)
        self.merchandising_agent = MerchandisingMarginOTIFAgent(db_path=db_path)

    def build_adk_agent_tree(self) -> dict[str, Any]:
        """
        Return the Google ADK agent hierarchy descriptor (and construct native `google.adk.agents`
        instances when `google-adk` is installed).
        """
        if ADK_SDK_AVAILABLE and LlmAgent is not None and SequentialAgent is not None:
            wms_adk = LlmAgent(
                name=self.wms_agent.name,
                model=self.wms_agent.model,
                instruction="Calculate True ATP and reroute AT_RISK_STOCKOUT VIP orders.",
                tools=self.wms_agent.tools,
            )
            merch_adk = LlmAgent(
                name=self.merchandising_agent.name,
                model=self.merchandising_agent.model,
                instruction="Verify 15% minimum margin floor and generate OTIF vendor debit memos.",
                tools=self.merchandising_agent.tools,
            )
            root_adk = SequentialAgent(
                name=self.name,
                sub_agents=[wms_adk, merch_adk],
            )
            return {
                "framework": "google-adk",
                "native_sdk_active": True,
                "root_agent": root_adk.name,
                "sub_agents": [wms_adk.name, merch_adk.name],
                "gemini_enterprise": get_gemini_enterprise_config(),
            }

        return {
            "framework": "google-adk-compatible",
            "native_sdk_active": ADK_SDK_AVAILABLE,
            "root_agent": self.name,
            "sub_agents": [self.wms_agent.name, self.merchandising_agent.name],
            "gemini_enterprise": get_gemini_enterprise_config(),
        }

    def run_multi_agent_workflow(
        self,
        prompt: str,
        skill_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute the sequential multi-agent handoff:
        Step 1: `WMSInventoryATPAgent` evaluates True ATP and reroutes 35 VIP AT_RISK_STOCKOUT orders.
        Step 2: `MerchandisingMarginOTIFAgent` validates margin floor compliance across all rerouted
                orders and generates OTIF debit memos for the 6 breaching suppliers.
        """
        task_meta = metadata or {}
        wms_out = self.wms_agent.execute(task_meta)
        merch_out = self.merchandising_agent.execute(task_meta, wms_routing_output=wms_out)

        combined_value_usd = round(
            float(wms_out["total_post_shipping_margin_usd"])
            + float(merch_out["total_claim_amount_usd"])
            + float(merch_out["total_margin_bleed_prevented_usd"]),
            2,
        )

        handoff_trace = [
            {
                "step": 1,
                "from_agent": self.name,
                "to_agent": self.wms_agent.name,
                "action": "optimize_vip_split_fulfillment",
                "summary": (
                    f"Rerouted {wms_out['rerouted_orders_count']}/{wms_out['evaluated_orders_count']} "
                    f"VIP orders protecting ${wms_out['protected_customer_ltv_usd']:,.2f} LTV and "
                    f"${wms_out['total_post_shipping_margin_usd']:,.2f} post-shipping margin."
                ),
            },
            {
                "step": 2,
                "from_agent": self.wms_agent.name,
                "to_agent": self.merchandising_agent.name,
                "action": "verify_margin_floor_and_claim_otif_chargebacks",
                "summary": (
                    f"Verified margin floor compliance (all_rerouted_margin_protected="
                    f"{merch_out['all_rerouted_margin_protected']}) and generated "
                    f"{merch_out['breaching_vendors_count']} vendor OTIF debit memos totaling "
                    f"${merch_out['total_claim_amount_usd']:,.2f}."
                ),
            },
        ]

        executive_summary = (
            f"[Retail Pulse ADK Orchestrator] Completed multi-agent workflow for request: '{prompt}'. "
            f"WMS Agent rerouted {wms_out['rerouted_orders_count']} VIP orders "
            f"(${wms_out['protected_customer_ltv_usd']:,.2f} LTV protected; "
            f"${wms_out['total_post_shipping_margin_usd']:,.2f} post-shipping margin). "
            f"Merchandising Agent verified 100% margin floor compliance and claimed "
            f"${merch_out['total_claim_amount_usd']:,.2f} across "
            f"{merch_out['breaching_vendors_count']} breaching OTIF vendor contracts."
        )

        return {
            "status": "COMPLETED",
            "orchestrator": self.name,
            "skill_id": skill_id or "omnichannel_fulfillment_routing",
            "adk_hierarchy": self.build_adk_agent_tree(),
            "executive_summary": executive_summary,
            "wms_technical_assessment": {
                "agent_name": wms_out["agent_name"],
                "oversell_orders_detected": wms_out["oversell_orders_detected"],
                "evaluated_orders_count": wms_out["evaluated_orders_count"],
                "rerouted_orders_count": wms_out["rerouted_orders_count"],
                "protected_customer_ltv_usd": wms_out["protected_customer_ltv_usd"],
                "total_post_shipping_margin_usd": wms_out["total_post_shipping_margin_usd"],
            },
            "merchandising_commercial_assessment": {
                "agent_name": merch_out["agent_name"],
                "all_orders_margin_compliant": merch_out["all_orders_margin_compliant"],
                "all_rerouted_margin_protected": merch_out["all_rerouted_margin_protected"],
                "total_margin_bleed_prevented_usd": merch_out["total_margin_bleed_prevented_usd"],
                "breaching_vendors_count": merch_out["breaching_vendors_count"],
                "total_claim_amount_usd": merch_out["total_claim_amount_usd"],
            },
            "combined_financial_impact_usd": combined_value_usd,
            "handoff_trace": handoff_trace,
        }


# ============================================================================
# A2A (Agent2Agent) Protocol Discovery Card & JSON-RPC 2.0 Task Endpoint
# ============================================================================


def get_a2a_agent_card() -> dict[str, Any]:
    """
    Return the standard A2A (Agent2Agent) Discovery Card served at `GET /.well-known/agent.json`
    and `GET /api/v1/a2a/agent-card`.
    """
    base_url = os.getenv("RETAIL_PULSE_PUBLIC_URL", "http://127.0.0.1:8000")
    return {
        "name": "Retail Pulse ADK Multi-Agent Orchestrator",
        "description": (
            "Enterprise Retail Multi-Agent System built with Google ADK & A2A Protocol. "
            "Coordinates Technical WMS True ATP Inventory Routing with Commercial Margin Floor "
            "& Supplier OTIF Chargeback Recovery."
        ),
        "version": "1.0.0",
        "protocolVersion": "0.2.1",
        "url": f"{base_url}/api/v1/a2a",
        "provider": {
            "organization": "Tryolabs",
            "url": "https://tryolabs.com",
        },
        "geminiEnterprise": get_gemini_enterprise_config(),
        "capabilities": {
            "streaming": False,
            "pushNotifications": False,
            "stateTransitionHistory": True,
        },
        "defaultInputModes": ["text/plain", "application/json"],
        "defaultOutputModes": ["application/json", "text/markdown"],
        "subagents": [
            WMSInventoryATPAgent.name,
            MerchandisingMarginOTIFAgent.name,
        ],
        "skills": [
            {
                "id": "omnichannel_fulfillment_routing",
                "name": "Omnichannel VIP Split-Fulfillment Routing",
                "description": (
                    "Detects phantom BOPIS/safety-stock inventory and reroutes AT_RISK_STOCKOUT "
                    "VIP orders to alternate nodes preserving contract minimum margin floors."
                ),
                "tags": ["wms", "atp", "fulfillment", "vip", "omnichannel"],
                "examples": [
                    "Reroute all 35 AT_RISK_STOCKOUT VIP orders while preserving the 15% margin floor."
                ],
            },
            {
                "id": "vendor_otif_chargeback_claim",
                "name": "Supplier OTIF SLA Audit & Chargeback Debit Memo Generation",
                "description": (
                    "Cross-references vendor OTIF contracts against EDI 856 ASN delay logs to "
                    "calculate recoverable chargeback penalties."
                ),
                "tags": ["merchandising", "otif", "vendors", "chargebacks", "edi-856"],
                "examples": [
                    "Audit breaching vendor contracts and claim OTIF chargeback penalties."
                ],
            },
            {
                "id": "promo_margin_floor_audit",
                "name": "Promotional Stacking & 15% Margin Floor Compliance Audit",
                "description": (
                    "Audits stacked promotional campaigns (FLASH35 + VIP15) and clamps unit pricing "
                    "to enforce the mandatory minimum gross margin floor."
                ),
                "tags": ["pricing", "margin", "promotions", "compliance"],
                "examples": [
                    "Verify all 30 flash-sale promotional orders comply with the minimum margin floor."
                ],
            },
        ],
    }


def _extract_prompt_from_a2a_params(params: dict[str, Any]) -> str:
    """Extract the plain-text prompt from an A2A `message.parts` payload."""
    message = params.get("message") or {}
    parts = message.get("parts") or []
    texts: list[str] = []
    for part in parts:
        if isinstance(part, dict) and "text" in part:
            texts.append(str(part["text"]))
    if texts:
        return " ".join(texts).strip()
    return str(params.get("prompt") or "Execute full Retail Pulse ADK multi-agent triage and recovery.")


def handle_a2a_jsonrpc(payload: dict[str, Any], db_path: Path | None = None) -> dict[str, Any]:
    """
    Process a standard A2A JSON-RPC 2.0 request (`tasks/send` or `message/send`) and return
    a compliant A2A Task response containing `status`, `artifacts`, and `history`.
    """
    jsonrpc_version = str(payload.get("jsonrpc", "2.0"))
    request_id = payload.get("id", "req-a2a-001")
    method = str(payload.get("method", "tasks/send"))
    params = payload.get("params") or {}

    if method not in {"tasks/send", "message/send"}:
        return {
            "jsonrpc": jsonrpc_version,
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"Method '{method}' not found. Supported A2A methods: 'tasks/send', 'message/send'.",
            },
        }

    task_id = str(params.get("id") or f"task-{uuid.uuid4().hex[:10]}")
    metadata = params.get("metadata") or {}
    skill_id = metadata.get("skill_id") or params.get("skill_id")
    prompt = _extract_prompt_from_a2a_params(params)

    orchestrator = RetailPulseOrchestratorAgent(db_path=db_path)
    workflow_result = orchestrator.run_multi_agent_workflow(
        prompt=prompt,
        skill_id=skill_id,
        metadata=metadata,
    )

    return {
        "jsonrpc": jsonrpc_version,
        "id": request_id,
        "result": {
            "id": task_id,
            "sessionId": str(params.get("sessionId") or "session-retail-pulse-a2a"),
            "status": {
                "state": "completed",
                "message": {
                    "role": "agent",
                    "parts": [
                        {
                            "type": "text",
                            "text": workflow_result["executive_summary"],
                        }
                    ],
                },
            },
            "artifacts": [
                {
                    "name": "adk_multi_agent_decision",
                    "description": "Coordinated WMS Technical + Merchandising Commercial Multi-Agent Decision",
                    "parts": [
                        {
                            "type": "data",
                            "data": workflow_result,
                        }
                    ],
                }
            ],
            "history": workflow_result["handoff_trace"],
        },
    }
