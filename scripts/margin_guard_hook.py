#!/usr/bin/env python3
"""
Antigravity Lifecycle PreToolUse Guard Hook (`scripts/margin_guard_hook.py`).

Enforces Commercial Margin Floors, Database Integrity, and Local Compliance Audit Logging
before tool execution:
1. Reads the Antigravity `PreToolUse` JSON payload from `stdin` (camelCase keys: `toolCall`, `stepIdx`, `conversationId`).
2. Inspects `toolCall.name` and `toolCall.args` for destructive SQL operations (`DROP TABLE`,
   `DELETE FROM vendor_contracts`, `DELETE FROM omnichannel_orders`) or unsafe promotional
   overrides (`DISABLE_MARGIN_FLOOR`, `BYPASS_CONTRACT_MARGIN_FLOOR`, `contract_min_margin_floor_pct = 0`).
3. Appends an immutable compliance audit entry to `data/logs/hook_compliance_audit.jsonl`
   (complementing Google Cloud `cloudaicompanion.googleapis.com` Audit Logs).
4. Emits a valid JSON decision on `stdout`:
   `{"decision": "allow" | "deny", "reason": "..."}`
"""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent
AUDIT_LOG_PATH = ROOT_DIR / "data" / "logs" / "hook_compliance_audit.jsonl"

FORBIDDEN_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"DROP\s+TABLE\s+(vendor_contracts|omnichannel_orders|wms_inventory|sku_catalog)", re.IGNORECASE),
        "Destructive SQL DROP TABLE on core Retail Pulse tables is prohibited.",
    ),
    (
        re.compile(r"DELETE\s+FROM\s+(vendor_contracts|omnichannel_orders)", re.IGNORECASE),
        "Deleting commercial vendor contracts or omnichannel orders violates audit retention rules.",
    ),
    (
        re.compile(r"DISABLE_MARGIN_FLOOR|BYPASS_CONTRACT_MARGIN_FLOOR|enforce_floor\s*=\s*False", re.IGNORECASE),
        "Bypassing commercial contract margin floors is strictly prohibited by Retail Pulse governance.",
    ),
    (
        re.compile(r"contract_min_margin_floor_pct\s*=\s*0(\.0+)?", re.IGNORECASE),
        "Setting contract_min_margin_floor_pct to 0% violates supplier commercial terms.",
    ),
]


def _append_compliance_audit_log(payload: dict[str, Any], decision_obj: dict[str, Any]) -> None:
    try:
        AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        tool_call = payload.get("toolCall") or {}
        tool_name = tool_call.get("name") or payload.get("tool_name") or "unknown"
        entry = {
            "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
            "conversationId": payload.get("conversationId", "local-test"),
            "stepIdx": payload.get("stepIdx", 0),
            "toolName": tool_name,
            "decision": decision_obj.get("decision"),
            "reason": decision_obj.get("reason"),
        }
        with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass


def evaluate_hook_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Inspect a PreToolUse hook payload, log the audit decision, and return {'decision': 'allow'|'deny', 'reason': ...}."""
    tool_call = payload.get("toolCall") or {}
    tool_name = str(tool_call.get("name") or payload.get("tool_name") or "")
    args = tool_call.get("args") or payload.get("tool_input") or payload

    serialized_args = json.dumps(args)
    for pattern, reason in FORBIDDEN_PATTERNS:
        if pattern.search(serialized_args):
            result = {
                "decision": "deny",
                "reason": f"[Retail Pulse Margin & Contract Guard] Blocked {tool_name}: {reason}",
            }
            _append_compliance_audit_log(payload, result)
            return result

    result = {
        "decision": "allow",
        "reason": "Passed Retail Pulse Margin & Commercial Contract Guard.",
    }
    _append_compliance_audit_log(payload, result)
    return result


def main() -> None:
    raw = sys.stdin.read().strip()
    if not raw:
        print(json.dumps({"decision": "allow", "reason": "Empty hook stdin payload."}))
        return
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        print(json.dumps({"decision": "allow", "reason": "Non-JSON stdin payload."}))
        return

    result = evaluate_hook_payload(payload)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
