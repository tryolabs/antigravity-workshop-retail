"""
Lab 2 Verification Suite: Antigravity Workspace Rules (`GEMINI.md`, `.agents/rules/`)
and Progressive Disclosure Skills (`.agents/skills/margin-otif-audit/SKILL.md`).
"""

from __future__ import annotations

import json
from pathlib import Path

from scripts.run_otif_margin_audit import generate_executive_audit_report

ROOT_DIR = Path(__file__).resolve().parent.parent


def test_gemini_md_exists_and_enforces_retail_guardrails() -> None:
    gemini_path = ROOT_DIR / "GEMINI.md"
    assert gemini_path.exists(), "GEMINI.md must exist at the workspace root"
    content = gemini_path.read_text(encoding="utf-8")
    assert len(content) >= 300
    assert "Decimal" in content
    assert "gtin_14" in content or "GTIN-14" in content
    assert "contract_min_margin_floor_pct" in content
    assert "unprocessed_webhook_delta_qty" in content


def test_agents_rules_retail_standards_exists() -> None:
    rule_path = ROOT_DIR / ".agents" / "rules" / "retail-standards.md"
    assert rule_path.exists(), ".agents/rules/retail-standards.md must exist"
    content = rule_path.read_text(encoding="utf-8")
    assert "Decimal" in content
    assert "ROUND_HALF_UP" in content
    assert "otif_target_pct" in content or "OTIF" in content


def test_margin_otif_audit_skill_frontmatter_and_structure() -> None:
    skill_path = ROOT_DIR / ".agents" / "skills" / "margin-otif-audit" / "SKILL.md"
    assert skill_path.exists(), ".agents/skills/margin-otif-audit/SKILL.md must exist"
    content = skill_path.read_text(encoding="utf-8")
    assert content.startswith("---\n"), "SKILL.md must start with YAML frontmatter"
    parts = content.split("---", 2)
    assert len(parts) >= 3, "SKILL.md must have opening and closing '---' YAML frontmatter delimiters"
    frontmatter = parts[1]
    assert "name: margin-otif-audit" in frontmatter
    assert "description:" in frontmatter
    assert "scripts/run_otif_margin_audit.py" in content


def test_run_otif_margin_audit_script_generates_executive_reports() -> None:
    skill_path = ROOT_DIR / ".agents" / "skills" / "margin-otif-audit" / "SKILL.md"
    assert skill_path.exists(), "Skill must exist before validating executive audit reports"
    report = generate_executive_audit_report()
    assert report["margin_floor_audit"]["all_orders_margin_compliant"] is True
    assert report["vip_oversell_atp_audit"]["detected_oversell_orders_count"] == 35
    assert report["vendor_otif_breach_audit"]["breaching_contracts_count"] == 6
    assert report["vendor_otif_breach_audit"]["total_recoverable_chargeback_usd"] == 98250.0

    json_file = ROOT_DIR / "data" / "exports" / "executive_margin_otif_audit.json"
    md_file = ROOT_DIR / "data" / "exports" / "executive_margin_otif_audit.md"
    assert json_file.exists()
    assert md_file.exists()
    loaded = json.loads(json_file.read_text(encoding="utf-8"))
    assert loaded["vendor_otif_breach_audit"]["total_recoverable_chargeback_usd"] == 98250.0
