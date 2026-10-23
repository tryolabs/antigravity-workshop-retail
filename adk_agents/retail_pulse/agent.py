"""
Google ADK (`adk web`) Multi-Agent System for Retail Pulse (`adk_agents/retail_pulse/agent.py`).

Launch locally in the ADK Development UI:
    ./scripts/run_adk_web.sh
    # Opens http://127.0.0.1:8080 where you can select `retail_pulse`, chat with `root_agent`,
    # inspect the multi-agent trace graph, view tool call events, and test A2A handoffs!

Supports both:
- Local Gemini API key (`GOOGLE_API_KEY`) or Vertex AI (`GOOGLE_GENAI_USE_VERTEXAI=TRUE`,
  `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`)
- Enterprise federation into Gemini Enterprise (`GEMINI_ENTERPRISE_APP_ID`) via A2A protocol.
"""

from __future__ import annotations

import os
from typing import Any

from src.agents.adk_a2a_orchestrator import (
    get_a2a_agent_card,
    get_gemini_enterprise_config,
    handle_a2a_jsonrpc,
    tool_audit_promo_margin_floor,
    tool_claim_vendor_otif_chargebacks,
    tool_optimize_vip_split_fulfillment,
    tool_query_network_true_atp,
)

# Default to Vertex AI when GOOGLE_CLOUD_PROJECT is configured and GOOGLE_API_KEY is not set
if os.getenv("GOOGLE_CLOUD_PROJECT") and not os.getenv("GOOGLE_API_KEY"):
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "TRUE")
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")

DEFAULT_MODEL = os.getenv("ADK_DEFAULT_MODEL", "gemini-2.5-pro")


def query_true_atp_inventory(sku: str, required_qty: int = 1) -> dict[str, Any]:
    """Query True Available-to-Promise (ATP) stock across all warehouses and stores for a SKU.

    Args:
        sku: The product SKU identifier (e.g., 'SKU-OLED-65').
        required_qty: Minimum units required for fulfillment.
    """
    return tool_query_network_true_atp(sku=sku, required_qty=required_qty)


def optimize_vip_split_fulfillment(persist_changes: bool = False) -> dict[str, Any]:
    """Evaluate and reroute all 35 AT_RISK_STOCKOUT VIP (DIAMOND/GOLD) orders to optimal True ATP nodes.

    Args:
        persist_changes: Whether to persist the rerouted fulfillment locations in SQLite.
    """
    return tool_optimize_vip_split_fulfillment(
        loyalty_tiers=["DIAMOND", "GOLD"],
        persist_changes=persist_changes,
    )


def audit_promo_margin_floor(sku: str = "SKU-OLED-65", qty: int = 1) -> dict[str, Any]:
    """Audit promotional discount stacking (FLASH35 + VIP15) and verify 15%+ minimum margin floor compliance.

    Args:
        sku: The SKU to evaluate under stacked promotional codes.
        qty: Order line quantity.
    """
    return tool_audit_promo_margin_floor(sku=sku, qty=qty, promo_codes=["FLASH35", "VIP15"])


def claim_supplier_otif_chargebacks(min_shortfall_pct: float = 0.0) -> dict[str, Any]:
    """Audit supplier On-Time In-Full (OTIF) contracts against EDI 856 ASN logs and generate debit memos.

    Args:
        min_shortfall_pct: Minimum OTIF percentage-point shortfall to include in chargeback claims.
    """
    return tool_claim_vendor_otif_chargebacks(min_shortfall_pct=min_shortfall_pct)


def invoke_a2a_task_handoff(
    prompt: str,
    skill_id: str = "omnichannel_fulfillment_routing",
) -> dict[str, Any]:
    """Invoke the Retail Pulse A2A (Agent2Agent) JSON-RPC 2.0 endpoint and return the A2A Task artifact.

    Args:
        prompt: Natural-language instruction for the remote/local A2A agent.
        skill_id: Target A2A skill identifier ('omnichannel_fulfillment_routing',
                  'vendor_otif_chargeback_claim', or 'promo_margin_floor_audit').
    """
    rpc_payload = {
        "jsonrpc": "2.0",
        "id": "adk-web-a2a-call",
        "method": "tasks/send",
        "params": {
            "id": "task-from-adk-web",
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": prompt}],
            },
            "metadata": {
                "skill_id": skill_id,
                "gemini_enterprise": get_gemini_enterprise_config(),
            },
        },
    }
    return {
        "agent_card": get_a2a_agent_card(),
        "a2a_response": handle_a2a_jsonrpc(rpc_payload),
    }


try:
    from google.adk.agents import Agent  # type: ignore

    wms_inventory_agent = Agent(
        name="wms_inventory_agent",
        model=DEFAULT_MODEL,
        description=(
            "Technical WMS/POS & True ATP Fulfillment Specialist. Calculates True ATP "
            "(deducting BOPIS reservations, safety stock, and POS webhook lag) and reroutes "
            "AT_RISK_STOCKOUT VIP orders."
        ),
        instruction=(
            "You are the Technical WMS & True ATP Specialist for Retail Pulse. "
            "Use `query_true_atp_inventory` and `optimize_vip_split_fulfillment` to detect "
            "phantom stockouts and reroute DIAMOND and GOLD VIP orders to nodes with sufficient True ATP."
        ),
        tools=[query_true_atp_inventory, optimize_vip_split_fulfillment],
    )

    merchandising_margin_agent = Agent(
        name="merchandising_margin_agent",
        model=DEFAULT_MODEL,
        description=(
            "Commercial Merchandising Margin Floor & Supplier OTIF Specialist. Enforces the "
            "mandatory minimum gross margin floor on stacked promotions and claims supplier OTIF chargebacks."
        ),
        instruction=(
            "You are the Commercial Merchandising & Vendor OTIF Specialist for Retail Pulse. "
            "Use `audit_promo_margin_floor` and `claim_supplier_otif_chargebacks` to protect gross margins "
            "and generate debit memos for breaching suppliers."
        ),
        tools=[audit_promo_margin_floor, claim_supplier_otif_chargebacks],
    )

    a2a_bridge_agent = Agent(
        name="a2a_bridge_agent",
        model=DEFAULT_MODEL,
        description=(
            "A2A (Agent2Agent) Protocol & Gemini Enterprise Federation Bridge Agent. "
            "Dispatches JSON-RPC 2.0 `tasks/send` requests and inspects the A2A Agent Card."
        ),
        instruction=(
            "You are the A2A Protocol & Gemini Enterprise Federation Bridge Agent. "
            "Use `invoke_a2a_task_handoff` to execute A2A JSON-RPC 2.0 tasks and inspect "
            "the Agent Discovery Card."
        ),
        tools=[invoke_a2a_task_handoff],
    )

    root_agent = Agent(
        name="retail_pulse_root_agent",
        model=DEFAULT_MODEL,
        description=(
            "Retail Pulse Executive Multi-Agent Orchestrator (Google ADK + A2A + Gemini Enterprise). "
            "Coordinates Technical WMS True ATP routing, Commercial Margin Floor compliance, and "
            "Supplier OTIF Chargeback recovery."
        ),
        instruction=(
            "You are the Retail Pulse Executive Multi-Agent Orchestrator delivered by Tryolabs. "
            "Coordinate `wms_inventory_agent` (for True ATP and VIP order rerouting), "
            "`merchandising_margin_agent` (for promotional margin floor audits and vendor OTIF "
            "chargeback claims), and `a2a_bridge_agent` (for A2A JSON-RPC 2.0 protocol handoffs)."
        ),
        sub_agents=[wms_inventory_agent, merchandising_margin_agent, a2a_bridge_agent],
        tools=[
            query_true_atp_inventory,
            optimize_vip_split_fulfillment,
            audit_promo_margin_floor,
            claim_supplier_otif_chargebacks,
            invoke_a2a_task_handoff,
        ],
    )
except ImportError:
    # Fallback descriptor if google-adk is not installed
    class _FallbackADKAgent:
        def __init__(self, name: str, description: str, tools: list[Any], sub_agents: list[Any] | None = None) -> None:
            self.name = name
            self.description = description
            self.tools = tools
            self.sub_agents = sub_agents or []

    wms_inventory_agent = _FallbackADKAgent(
        name="wms_inventory_agent",
        description="Technical WMS/POS & True ATP Fulfillment Specialist",
        tools=[query_true_atp_inventory, optimize_vip_split_fulfillment],
    )
    merchandising_margin_agent = _FallbackADKAgent(
        name="merchandising_margin_agent",
        description="Commercial Merchandising Margin Floor & Supplier OTIF Specialist",
        tools=[audit_promo_margin_floor, claim_supplier_otif_chargebacks],
    )
    a2a_bridge_agent = _FallbackADKAgent(
        name="a2a_bridge_agent",
        description="A2A Protocol & Gemini Enterprise Federation Bridge Agent",
        tools=[invoke_a2a_task_handoff],
    )
    root_agent = _FallbackADKAgent(
        name="retail_pulse_root_agent",
        description="Retail Pulse Executive Multi-Agent Orchestrator",
        tools=[
            query_true_atp_inventory,
            optimize_vip_split_fulfillment,
            audit_promo_margin_floor,
            claim_supplier_otif_chargebacks,
            invoke_a2a_task_handoff,
        ],
        sub_agents=[wms_inventory_agent, merchandising_margin_agent, a2a_bridge_agent],
    )
