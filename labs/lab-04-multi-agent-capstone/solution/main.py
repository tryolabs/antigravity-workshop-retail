"""
FastAPI REST API, A2A Protocol Server & Live Omnichannel Command Center Dashboard
for Retail Pulse (Lab 4 Solution).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import Body, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.agents.adk_a2a_orchestrator import (
    get_a2a_agent_card,
    handle_a2a_jsonrpc,
)
from src.database import fetch_all
from src.models import PromoEvaluationRequest
from src.services.fulfillment_router import (
    claim_vendor_otif_chargebacks,
    optimize_at_risk_order_routing,
)
from src.services.inventory_atp import (
    audit_vip_oversell_exposure,
    calculate_location_atp,
    get_sku_network_atp,
)
from src.services.promo_pricing import (
    audit_margin_hold_orders,
    evaluate_order_line_pricing,
)
from src.services.vendor_otif_auditor import audit_vendor_contracts

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title="Retail Pulse: Omnichannel Order, Inventory Sync & Commercial Margin Intelligence",
    version="1.0.0",
    description=(
        "Google Antigravity Retail Industry Workshop API combining POS/WMS/RFID/EDI "
        "technical telemetry with Commercial Margin Floors, VIP LTV, Vendor OTIF Contracts, "
        "Google ADK Multi-Agent Orchestration, and the A2A (Agent2Agent) Protocol."
    ),
)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class OptimizeRoutingRequest(BaseModel):
    loyalty_tiers: list[str] | None = Field(
        default=None,
        description="Optional filter for loyalty tiers (e.g., ['DIAMOND', 'GOLD'])",
    )
    persist_changes: bool = Field(
        default=False,
        description="Whether to persist rerouted fulfillment locations in SQLite",
    )


class ClaimChargebacksRequest(BaseModel):
    min_shortfall_pct: float = Field(
        default=0.0,
        ge=0.0,
        description="Minimum OTIF percentage point shortfall to include in claims",
    )


@app.get("/", response_class=HTMLResponse)
def serve_dashboard(
    lang: str | None = Query(default=None, description="UI language: en or es"),
    theme: str | None = Query(default=None, description="UI theme: dark or light"),
) -> Any:
    """Serve the Live Omnichannel Command Center & Commercial Margin Web Dashboard."""
    is_es = bool(lang and lang.lower() == "es")
    is_light = bool(theme and theme.lower() == "light")
    if is_es and is_light:
        f = STATIC_DIR / "index.es.light.html"
        if f.exists():
            return FileResponse(str(f))
    if is_es:
        es_file = STATIC_DIR / "index.es.html"
        if es_file.exists():
            return FileResponse(str(es_file))
    if is_light:
        light_file = STATIC_DIR / "index.light.html"
        if light_file.exists():
            return FileResponse(str(light_file))
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return HTMLResponse("<h1>Retail Pulse Dashboard not found</h1>", status_code=404)
    return FileResponse(str(index_file))


@app.get("/es", response_class=HTMLResponse)
def serve_dashboard_es(theme: str | None = Query(default=None, description="UI theme: dark or light")) -> Any:
    """Serve the Spanish Live Omnichannel Command Center & Commercial Margin Web Dashboard."""
    if theme and theme.lower() == "light":
        f = STATIC_DIR / "index.es.light.html"
        if f.exists():
            return FileResponse(str(f))
    es_file = STATIC_DIR / "index.es.html"
    if es_file.exists():
        return FileResponse(str(es_file))
    return serve_dashboard(lang="es", theme=theme)


@app.get("/light", response_class=HTMLResponse)
def serve_dashboard_light(lang: str | None = Query(default=None, description="UI language: en or es")) -> Any:
    """Serve the Light-Mode Live Omnichannel Command Center Web Dashboard."""
    return serve_dashboard(lang=lang, theme="light")


@app.get("/es/light", response_class=HTMLResponse)
def serve_dashboard_es_light() -> Any:
    """Serve the Spanish Light-Mode Live Omnichannel Command Center Web Dashboard."""
    return serve_dashboard(lang="es", theme="light")


@app.get("/api/v1/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "retail-pulse-omnichannel-api"}


# ============================================================================
# A2A (Agent2Agent) Protocol Discovery & JSON-RPC 2.0 Endpoints (Lab 4)
# ============================================================================


@app.get("/.well-known/agent.json")
@app.get("/api/v1/a2a/agent-card")
def api_a2a_agent_card() -> dict[str, Any]:
    """Serve the A2A Protocol Agent Discovery Card."""
    card = get_a2a_agent_card()
    if card.get("status") == "NOT_IMPLEMENTED_STUB":
        raise HTTPException(
            status_code=501,
            detail="A2A Agent Discovery Card is not implemented yet (Complete Lab 4 ADK & A2A Capstone).",
        )
    return card


@app.post("/api/v1/a2a")
@app.post("/api/v1/a2a/tasks/send")
def api_a2a_jsonrpc(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Handle A2A JSON-RPC 2.0 `tasks/send` and `message/send` multi-agent tasks."""
    response = handle_a2a_jsonrpc(payload)
    if response.get("status") == "NOT_IMPLEMENTED_STUB":
        raise HTTPException(
            status_code=501,
            detail="A2A JSON-RPC 2.0 task handler is not implemented yet (Complete Lab 4 ADK & A2A Capstone).",
        )
    return response


# ============================================================================
# Retail Pulse Domain REST API Endpoints
# ============================================================================


@app.post("/api/v1/pricing/evaluate")
def api_evaluate_pricing(req: PromoEvaluationRequest) -> dict[str, Any]:
    try:
        res = evaluate_order_line_pricing(
            sku=req.sku,
            qty=req.qty,
            promo_codes=req.promo_codes,
        )
        return res.model_dump(mode="json")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/v1/inventory/atp/{sku}")
def api_get_sku_atp(
    sku: str,
    location_id: str | None = Query(default=None),
    required_qty: int = Query(default=1, ge=1),
) -> dict[str, Any]:
    try:
        if location_id:
            loc_res = calculate_location_atp(sku=sku, location_id=location_id, required_qty=required_qty)
            return {"sku": sku, "locations": [loc_res.model_dump(mode="json")]}
        net_res = get_sku_network_atp(sku=sku, required_qty=required_qty)
        if not net_res:
            raise ValueError(f"Unknown SKU: {sku}")
        return {"sku": sku, "locations": [r.model_dump(mode="json") for r in net_res]}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/v1/vendors/otif-audit")
def api_vendor_otif_audit(only_breaching: bool = Query(default=False)) -> dict[str, Any]:
    return audit_vendor_contracts(only_breaching=only_breaching)


@app.post("/api/v1/fulfillment/optimize-routing")
def api_optimize_routing(req: OptimizeRoutingRequest | None = None) -> dict[str, Any]:
    payload = req or OptimizeRoutingRequest()
    result = optimize_at_risk_order_routing(
        loyalty_tiers=payload.loyalty_tiers,
        persist_changes=payload.persist_changes,
    )
    if result.get("status") == "NOT_IMPLEMENTED_STUB":
        raise HTTPException(
            status_code=501,
            detail="Fulfillment routing engine is not implemented yet (Complete Lab 4 Capstone).",
        )
    return result


@app.post("/api/v1/vendors/claim-chargebacks")
def api_claim_chargebacks(req: ClaimChargebacksRequest | None = None) -> dict[str, Any]:
    payload = req or ClaimChargebacksRequest()
    result = claim_vendor_otif_chargebacks(min_shortfall_pct=payload.min_shortfall_pct)
    if result.get("status") == "NOT_IMPLEMENTED_STUB":
        raise HTTPException(
            status_code=501,
            detail="Vendor chargeback engine is not implemented yet (Complete Lab 4 Capstone).",
        )
    return result


@app.get("/api/v1/dashboard/summary")
def api_dashboard_summary() -> dict[str, Any]:
    """Return full live KPIs and tables for the Retail Pulse Web Dashboard."""
    margin_audit = audit_margin_hold_orders()
    vip_atp_audit = audit_vip_oversell_exposure()
    vendor_audit = audit_vendor_contracts(only_breaching=False)
    routing_sim = optimize_at_risk_order_routing(persist_changes=False)
    chargeback_sim = claim_vendor_otif_chargebacks(min_shortfall_pct=0.0)
    pos_events = fetch_all("SELECT * FROM pos_telemetry ORDER BY webhook_sync_lag_sec DESC LIMIT 12")
    sample_inventory = fetch_all(
        """
        SELECT * FROM wms_inventory
        WHERE location_id IN ('STORE-NYC-5TH', 'WH-EAST-NJ01', 'WH-CENTRAL-TX03')
        ORDER BY sku, location_id
        LIMIT 18
        """
    )
    enriched_inventory = []
    for row in sample_inventory:
        atp = calculate_location_atp(sku=row["sku"], location_id=row["location_id"], required_qty=1)
        enriched_inventory.append(atp.model_dump(mode="json"))

    return {
        "margin_audit": margin_audit,
        "vip_atp_audit": vip_atp_audit,
        "vendor_audit": vendor_audit,
        "routing_simulation": routing_sim,
        "chargeback_simulation": chargeback_sim,
        "pos_telemetry": pos_events,
        "inventory_snapshot": enriched_inventory,
    }
