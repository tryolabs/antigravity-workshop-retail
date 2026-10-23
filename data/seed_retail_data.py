#!/usr/bin/env python3
"""
Deterministic Retail Data Generator for the Google Antigravity Retail Workshop.
Seeds SQLite database (data/retail_pulse.db), CSV snapshots (data/exports/),
and POS/WMS/EDI JSONL telemetry logs (data/logs/pos_wms_webhooks.jsonl).
"""

from __future__ import annotations

import csv
import json
import random
import sqlite3
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "retail_pulse.db"
EXPORTS_DIR = DATA_DIR / "exports"
LOGS_DIR = DATA_DIR / "logs"
JSONL_PATH = LOGS_DIR / "pos_wms_webhooks.jsonl"


def compute_gs1_gtin14_check_digit(prefix_13: str) -> str:
    """Compute standard GS1 Modulo-10 check digit for a 13-digit GTIN prefix."""
    if len(prefix_13) != 13 or not prefix_13.isdigit():
        raise ValueError(f"Expected 13 numeric digits, got: {prefix_13!r}")
    total = 0
    for idx, ch in enumerate(prefix_13):
        digit = int(ch)
        multiplier = 3 if idx % 2 == 0 else 1
        total += digit * multiplier
    check_digit = (10 - (total % 10)) % 10
    return f"{prefix_13}{check_digit}"


def validate_gs1_gtin14(gtin_14: str) -> bool:
    """Verify whether a 14-digit string is a valid GS1 GTIN-14 identifier."""
    if len(gtin_14) != 14 or not gtin_14.isdigit():
        return False
    return compute_gs1_gtin14_check_digit(gtin_14[:13]) == gtin_14


VENDOR_CONTRACTS: list[dict[str, Any]] = [
    {
        "contract_id": "VND-SONY-001",
        "vendor_name": "Sony Consumer Electronics NA",
        "category": "Electronics",
        "buyer_id": "BUY-ELEC-101",
        "annual_spend_commitment_usd": 5400000.00,
        "wholesale_unit_cost_usd": 620.00,
        "contract_min_margin_floor_pct": 22.0,
        "otif_target_pct": 97.0,
        "actual_otif_pct": 84.5,
        "late_shipments_count": 14,
        "short_shipments_count": 9,
        "delayed_po_value_usd": 420000.00,
        "chargeback_penalty_pct": 4.5,
        "status": "BREACH_HOLD",
    },
    {
        "contract_id": "VND-NIKE-002",
        "vendor_name": "Nike Global Footwear Supply",
        "category": "Footwear",
        "buyer_id": "BUY-FTWR-104",
        "annual_spend_commitment_usd": 4200000.00,
        "wholesale_unit_cost_usd": 88.00,
        "contract_min_margin_floor_pct": 28.0,
        "otif_target_pct": 96.0,
        "actual_otif_pct": 97.2,
        "late_shipments_count": 2,
        "short_shipments_count": 1,
        "delayed_po_value_usd": 0.00,
        "chargeback_penalty_pct": 3.5,
        "status": "COMPLIANT",
    },
    {
        "contract_id": "VND-DYSON-003",
        "vendor_name": "Dyson Home Appliances Ltd",
        "category": "Home Appliances",
        "buyer_id": "BUY-HOME-108",
        "annual_spend_commitment_usd": 3800000.00,
        "wholesale_unit_cost_usd": 410.00,
        "contract_min_margin_floor_pct": 24.0,
        "otif_target_pct": 98.0,
        "actual_otif_pct": 82.0,
        "late_shipments_count": 18,
        "short_shipments_count": 11,
        "delayed_po_value_usd": 510000.00,
        "chargeback_penalty_pct": 5.0,
        "status": "BREACH_HOLD",
    },
    {
        "contract_id": "VND-LEVI-004",
        "vendor_name": "Levi Strauss Apparel Wholesale",
        "category": "Apparel",
        "buyer_id": "BUY-APPR-112",
        "annual_spend_commitment_usd": 2600000.00,
        "wholesale_unit_cost_usd": 44.00,
        "contract_min_margin_floor_pct": 32.0,
        "otif_target_pct": 95.0,
        "actual_otif_pct": 96.4,
        "late_shipments_count": 3,
        "short_shipments_count": 1,
        "delayed_po_value_usd": 0.00,
        "chargeback_penalty_pct": 3.0,
        "status": "COMPLIANT",
    },
    {
        "contract_id": "VND-SAMS-005",
        "vendor_name": "Samsung Display & TV Distribution",
        "category": "Electronics",
        "buyer_id": "BUY-ELEC-101",
        "annual_spend_commitment_usd": 5500000.00,
        "wholesale_unit_cost_usd": 980.00,
        "contract_min_margin_floor_pct": 20.0,
        "otif_target_pct": 97.5,
        "actual_otif_pct": 86.2,
        "late_shipments_count": 15,
        "short_shipments_count": 8,
        "delayed_po_value_usd": 680000.00,
        "chargeback_penalty_pct": 4.0,
        "status": "BREACH_HOLD",
    },
    {
        "contract_id": "VND-NESP-006",
        "vendor_name": "Nespresso Gourmet Coffee Systems",
        "category": "Kitchen & Beverage",
        "buyer_id": "BUY-KTCH-119",
        "annual_spend_commitment_usd": 1450000.00,
        "wholesale_unit_cost_usd": 165.00,
        "contract_min_margin_floor_pct": 26.0,
        "otif_target_pct": 96.0,
        "actual_otif_pct": 88.5,
        "late_shipments_count": 9,
        "short_shipments_count": 6,
        "delayed_po_value_usd": 195000.00,
        "chargeback_penalty_pct": 4.0,
        "status": "BREACH_HOLD",
    },
    {
        "contract_id": "VND-PATA-007",
        "vendor_name": "Patagonia Outdoor Gear",
        "category": "Outdoor & Active",
        "buyer_id": "BUY-OUTD-122",
        "annual_spend_commitment_usd": 2100000.00,
        "wholesale_unit_cost_usd": 115.00,
        "contract_min_margin_floor_pct": 30.0,
        "otif_target_pct": 95.0,
        "actual_otif_pct": 95.8,
        "late_shipments_count": 2,
        "short_shipments_count": 2,
        "delayed_po_value_usd": 0.00,
        "chargeback_penalty_pct": 3.0,
        "status": "COMPLIANT",
    },
    {
        "contract_id": "VND-BOSE-008",
        "vendor_name": "Bose Premium Audio Corp",
        "category": "Electronics",
        "buyer_id": "BUY-ELEC-101",
        "annual_spend_commitment_usd": 1950000.00,
        "wholesale_unit_cost_usd": 225.00,
        "contract_min_margin_floor_pct": 25.0,
        "otif_target_pct": 96.5,
        "actual_otif_pct": 81.4,
        "late_shipments_count": 16,
        "short_shipments_count": 12,
        "delayed_po_value_usd": 310000.00,
        "chargeback_penalty_pct": 4.5,
        "status": "BREACH_HOLD",
    },
    {
        "contract_id": "VND-LULU-009",
        "vendor_name": "Technical Athleisure Collective",
        "category": "Apparel",
        "buyer_id": "BUY-APPR-112",
        "annual_spend_commitment_usd": 1750000.00,
        "wholesale_unit_cost_usd": 58.00,
        "contract_min_margin_floor_pct": 31.0,
        "otif_target_pct": 95.5,
        "actual_otif_pct": 97.0,
        "late_shipments_count": 1,
        "short_shipments_count": 1,
        "delayed_po_value_usd": 0.00,
        "chargeback_penalty_pct": 3.5,
        "status": "COMPLIANT",
    },
    {
        "contract_id": "VND-BREV-010",
        "vendor_name": "Breville Smart Kitchen Group",
        "category": "Kitchen & Beverage",
        "buyer_id": "BUY-KTCH-119",
        "annual_spend_commitment_usd": 980000.00,
        "wholesale_unit_cost_usd": 390.00,
        "contract_min_margin_floor_pct": 23.0,
        "otif_target_pct": 96.0,
        "actual_otif_pct": 87.9,
        "late_shipments_count": 8,
        "short_shipments_count": 5,
        "delayed_po_value_usd": 140000.00,
        "chargeback_penalty_pct": 3.5,
        "status": "BREACH_HOLD",
    },
]

FULFILLMENT_LOCATIONS: list[dict[str, Any]] = [
    {"location_id": "WH-EAST-NJ01", "location_type": "WAREHOUSE", "region": "EAST", "shipping_cost_usd": 8.50},
    {"location_id": "WH-WEST-CA02", "location_type": "WAREHOUSE", "region": "WEST", "shipping_cost_usd": 9.50},
    {"location_id": "WH-CENTRAL-TX03", "location_type": "WAREHOUSE", "region": "CENTRAL", "shipping_cost_usd": 7.50},
    {"location_id": "STORE-NYC-5TH", "location_type": "FLAGSHIP_STORE", "region": "EAST", "shipping_cost_usd": 14.00},
    {"location_id": "STORE-CHI-MAG", "location_type": "FLAGSHIP_STORE", "region": "CENTRAL", "shipping_cost_usd": 12.50},
    {"location_id": "STORE-MIA-BRICKELL", "location_type": "FLAGSHIP_STORE", "region": "SOUTH", "shipping_cost_usd": 13.00},
]

RAW_SKUS: list[tuple[str, str, str, str, str, float, float, float]] = [
    # (sku, gtin_prefix_13, product_name, category, contract_id, wholesale_cost, unit_price, min_margin_pct)
    ("SKU-SONY-OLED65", "0001234567890", "Sony Bravia XR 65-inch 4K OLED TV", "Electronics", "VND-SONY-001", 1120.00, 1799.00, 22.0),
    ("SKU-SONY-XM5ANC", "0001234567891", "Sony WH-1000XM5 Wireless ANC Headphones", "Electronics", "VND-SONY-001", 215.00, 399.00, 22.0),
    ("SKU-SONY-PS5PRO", "0001234567892", "Sony PlayStation 5 Pro 2TB Console Bundle", "Electronics", "VND-SONY-001", 495.00, 699.00, 22.0),
    ("SKU-NIKE-AF1LOW", "0002345678901", "Nike Air Force 1 '07 Craft Leather", "Footwear", "VND-NIKE-002", 68.00, 130.00, 28.0),
    ("SKU-NIKE-PEG41", "0002345678902", "Nike Air Zoom Pegasus 41 Road Running", "Footwear", "VND-NIKE-002", 74.00, 145.00, 28.0),
    ("SKU-NIKE-VAPOR3", "0002345678903", "Nike Vaporfly 3 Carbon Marathon Elite", "Footwear", "VND-NIKE-002", 142.00, 260.00, 28.0),
    ("SKU-DYSON-V15DT", "0003456789012", "Dyson V15 Detect Cordless Laser Vacuum", "Home Appliances", "VND-DYSON-003", 445.00, 749.00, 24.0),
    ("SKU-DYSON-AIRWRP", "0003456789013", "Dyson Airwrap Multi-Styler Complete Long", "Home Appliances", "VND-DYSON-003", 360.00, 599.00, 24.0),
    ("SKU-DYSON-PURIFY", "0003456789014", "Dyson Purifier Hot+Cool Formaldehyde HP09", "Home Appliances", "VND-DYSON-003", 480.00, 799.00, 24.0),
    ("SKU-LEVI-501SEL", "0004567890123", "Levi's 501 Original Selvedge Denim Jeans", "Apparel", "VND-LEVI-004", 54.00, 128.00, 32.0),
    ("SKU-LEVI-TRKRJK", "0004567890124", "Levi's Vintage Sherpa Trucker Jacket", "Apparel", "VND-LEVI-004", 62.00, 148.00, 32.0),
    ("SKU-SAMS-QN90D75", "0005678901234", "Samsung 75-inch Neo QLED 4K QN90D Smart TV", "Electronics", "VND-SAMS-005", 1390.00, 2199.00, 20.0),
    ("SKU-SAMS-S95D55", "0005678901235", "Samsung 55-inch OLED Glare-Free S95D TV", "Electronics", "VND-SAMS-005", 1050.00, 1699.00, 20.0),
    ("SKU-SAMS-Q990DSB", "0005678901236", "Samsung HW-Q990D 11.1.4ch Dolby Atmos Soundbar", "Electronics", "VND-SAMS-005", 790.00, 1299.00, 20.0),
    ("SKU-NESP-VERTCR", "0006789012345", "Nespresso Vertuo Creatista Brushed Steel", "Kitchen & Beverage", "VND-NESP-006", 385.00, 649.00, 26.0),
    ("SKU-NESP-LATTPR", "0006789012346", "Nespresso Gran Lattissima Espresso System", "Kitchen & Beverage", "VND-NESP-006", 340.00, 599.00, 26.0),
    ("SKU-PATA-TORR3L", "0007890123456", "Patagonia Torrentshell 3L Alpine Shell", "Outdoor & Active", "VND-PATA-007", 92.00, 179.00, 30.0),
    ("SKU-PATA-NANOPF", "0007890123457", "Patagonia Nano Puff Insulated Hoodie", "Outdoor & Active", "VND-PATA-007", 135.00, 289.00, 30.0),
    ("SKU-PATA-BLKHL55", "0007890123458", "Patagonia Black Hole Wheeled Duffel 55L", "Outdoor & Active", "VND-PATA-007", 178.00, 359.00, 30.0),
    ("SKU-BOSE-QCULTR", "0008901234567", "Bose QuietComfort Ultra Spatial Headphones", "Electronics", "VND-BOSE-008", 245.00, 429.00, 25.0),
    ("SKU-BOSE-SNDMX", "0008901234568", "Bose SoundLink Max Portable Speaker", "Electronics", "VND-BOSE-008", 220.00, 399.00, 25.0),
    ("SKU-LULU-ABCJOG", "0009012345678", "Technical ABC Warpstreme Tapered Jogger", "Apparel", "VND-LULU-009", 56.00, 138.00, 31.0),
    ("SKU-LULU-DFNJKT", "0009012345679", "Technical Define Luon Performance Jacket", "Apparel", "VND-LULU-009", 52.00, 128.00, 31.0),
    ("SKU-BREV-BRSTPR", "0009123456789", "Breville Barista Touch Impress Espresso", "Kitchen & Beverage", "VND-BREV-010", 860.00, 1499.00, 23.0),
    ("SKU-BREV-JouleOV", "0009123456780", "Breville Smart Oven Air Fryer Pro Joule", "Kitchen & Beverage", "VND-BREV-010", 285.00, 499.00, 23.0),
]

PROMO_CAMPAIGNS: list[dict[str, Any]] = [
    {
        "promo_code": "VIP25",
        "campaign_name": "VIP Diamond Tier 25% Exclusive",
        "discount_pct": 25.0,
        "is_stackable": 0,
        "min_margin_floor_pct": 20.0,
        "active": 1,
    },
    {
        "promo_code": "FLASH20",
        "campaign_name": "Omnichannel Weekend Flash 20%",
        "discount_pct": 20.0,
        "is_stackable": 0,
        "min_margin_floor_pct": 22.0,
        "active": 1,
    },
    {
        "promo_code": "HOLIDAY15",
        "campaign_name": "Seasonal Holiday Preview 15%",
        "discount_pct": 15.0,
        "is_stackable": 1,
        "min_margin_floor_pct": 18.0,
        "active": 1,
    },
    {
        "promo_code": "EMP30",
        "campaign_name": "Corporate Partner & Associate 30%",
        "discount_pct": 30.0,
        "is_stackable": 0,
        "min_margin_floor_pct": 24.0,
        "active": 1,
    },
    {
        "promo_code": "BUNDLE10",
        "campaign_name": "Multi-Item Bundle 10% Stackable",
        "discount_pct": 10.0,
        "is_stackable": 1,
        "min_margin_floor_pct": 18.0,
        "active": 1,
    },
    {
        "promo_code": "CLEARANCE40",
        "campaign_name": "End-of-Season Vault Clearance 40%",
        "discount_pct": 40.0,
        "is_stackable": 0,
        "min_margin_floor_pct": 18.0,
        "active": 1,
    },
    {
        "promo_code": "LOYALTY5",
        "campaign_name": "Loyalty Rewards 5% Stackable Booster",
        "discount_pct": 5.0,
        "is_stackable": 1,
        "min_margin_floor_pct": 18.0,
        "active": 1,
    },
    {
        "promo_code": "EXPIRED50",
        "campaign_name": "Expired Cyber Monday Doorbuster 50%",
        "discount_pct": 50.0,
        "is_stackable": 0,
        "min_margin_floor_pct": 25.0,
        "active": 0,
    },
]


def seed_all() -> dict[str, Any]:
    """Generate SQLite DB, CSV exports, and JSONL logs deterministically."""
    rng = random.Random(20260415)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE vendor_contracts (
            contract_id TEXT PRIMARY KEY,
            vendor_name TEXT NOT NULL,
            category TEXT NOT NULL,
            buyer_id TEXT NOT NULL,
            annual_spend_commitment_usd REAL NOT NULL,
            wholesale_unit_cost_usd REAL NOT NULL,
            contract_min_margin_floor_pct REAL NOT NULL,
            otif_target_pct REAL NOT NULL,
            actual_otif_pct REAL NOT NULL,
            late_shipments_count INTEGER NOT NULL,
            short_shipments_count INTEGER NOT NULL,
            delayed_po_value_usd REAL NOT NULL,
            chargeback_penalty_pct REAL NOT NULL,
            status TEXT NOT NULL
        );

        CREATE TABLE sku_catalog (
            sku TEXT PRIMARY KEY,
            gtin_14 TEXT NOT NULL UNIQUE,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            contract_id TEXT NOT NULL,
            rfid_epc_prefix TEXT NOT NULL,
            unit_wholesale_cost_usd REAL NOT NULL,
            unit_price_usd REAL NOT NULL,
            contract_min_margin_floor_pct REAL NOT NULL,
            FOREIGN KEY (contract_id) REFERENCES vendor_contracts(contract_id)
        );

        CREATE TABLE wms_inventory (
            inventory_id TEXT PRIMARY KEY,
            location_id TEXT NOT NULL,
            location_type TEXT NOT NULL,
            shipping_cost_usd REAL NOT NULL,
            gtin_14 TEXT NOT NULL,
            sku TEXT NOT NULL,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            rfid_epc_prefix TEXT NOT NULL,
            on_hand_qty INTEGER NOT NULL,
            reserved_qty INTEGER NOT NULL,
            safety_stock_qty INTEGER NOT NULL,
            unprocessed_webhook_delta_qty INTEGER NOT NULL,
            last_scan_ts TEXT NOT NULL
        );

        CREATE TABLE promo_campaigns (
            promo_code TEXT PRIMARY KEY,
            campaign_name TEXT NOT NULL,
            discount_pct REAL NOT NULL,
            is_stackable INTEGER NOT NULL,
            min_margin_floor_pct REAL NOT NULL,
            active INTEGER NOT NULL
        );

        CREATE TABLE pos_telemetry (
            event_id TEXT PRIMARY KEY,
            store_id TEXT NOT NULL,
            pos_terminal_id TEXT NOT NULL,
            channel TEXT NOT NULL,
            sku TEXT NOT NULL,
            qty_delta INTEGER NOT NULL,
            payment_gateway_latency_ms INTEGER NOT NULL,
            webhook_sync_lag_sec INTEGER NOT NULL,
            http_status INTEGER NOT NULL,
            error_code TEXT,
            event_ts TEXT NOT NULL
        );

        CREATE TABLE omnichannel_orders (
            order_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            customer_segment TEXT NOT NULL,
            loyalty_tier TEXT NOT NULL,
            customer_ltv_usd REAL NOT NULL,
            channel TEXT NOT NULL,
            sku TEXT NOT NULL,
            qty INTEGER NOT NULL,
            unit_price_usd REAL NOT NULL,
            unit_wholesale_cost_usd REAL NOT NULL,
            applied_promo_codes TEXT NOT NULL,
            discount_amount_usd REAL NOT NULL,
            net_revenue_usd REAL NOT NULL,
            gross_margin_usd REAL NOT NULL,
            gross_margin_pct REAL NOT NULL,
            fulfillment_location_id TEXT NOT NULL,
            order_status TEXT NOT NULL
        );
        """
    )

    # 1. Insert Vendor Contracts
    for vc in VENDOR_CONTRACTS:
        cur.execute(
            """
            INSERT INTO vendor_contracts (
                contract_id, vendor_name, category, buyer_id,
                annual_spend_commitment_usd, wholesale_unit_cost_usd,
                contract_min_margin_floor_pct, otif_target_pct, actual_otif_pct,
                late_shipments_count, short_shipments_count, delayed_po_value_usd,
                chargeback_penalty_pct, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                vc["contract_id"],
                vc["vendor_name"],
                vc["category"],
                vc["buyer_id"],
                vc["annual_spend_commitment_usd"],
                vc["wholesale_unit_cost_usd"],
                vc["contract_min_margin_floor_pct"],
                vc["otif_target_pct"],
                vc["actual_otif_pct"],
                vc["late_shipments_count"],
                vc["short_shipments_count"],
                vc["delayed_po_value_usd"],
                vc["chargeback_penalty_pct"],
                vc["status"],
            ),
        )

    # 2. Insert SKUs & WMS Inventory across 6 Locations
    sku_records: list[dict[str, Any]] = []
    wms_records: list[dict[str, Any]] = []
    jsonl_events: list[dict[str, Any]] = []
    pos_telemetry_rows: list[tuple[Any, ...]] = []

    inv_seq = 1
    pos_seq = 1
    for idx, (sku, prefix_13, prod_name, cat, contract_id, cost, price, margin_floor) in enumerate(RAW_SKUS, start=1):
        gtin_14 = compute_gs1_gtin14_check_digit(prefix_13)
        rfid_prefix = f"urn:epc:id:sgtin:{prefix_13[:7]}.{prefix_13[7:]}"
        sku_info = {
            "sku": sku,
            "gtin_14": gtin_14,
            "product_name": prod_name,
            "category": cat,
            "contract_id": contract_id,
            "rfid_epc_prefix": rfid_prefix,
            "unit_wholesale_cost_usd": cost,
            "unit_price_usd": price,
            "contract_min_margin_floor_pct": margin_floor,
        }
        sku_records.append(sku_info)
        cur.execute(
            """
            INSERT INTO sku_catalog (
                sku, gtin_14, product_name, category, contract_id,
                rfid_epc_prefix, unit_wholesale_cost_usd, unit_price_usd,
                contract_min_margin_floor_pct
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sku,
                gtin_14,
                prod_name,
                cat,
                contract_id,
                rfid_prefix,
                cost,
                price,
                margin_floor,
            ),
        )

        for loc_idx, loc in enumerate(FULFILLMENT_LOCATIONS):
            loc_id = loc["location_id"]
            loc_type = loc["location_type"]
            ship_cost = loc["shipping_cost_usd"]
            inv_id = f"INV-{inv_seq:04d}"
            inv_seq += 1

            # Create intentional phantom-stock / webhook-drift hotspots at STORE-NYC-5TH and WH-EAST-NJ01
            # while guaranteeing healthy True ATP at WH-CENTRAL-TX03 and WH-WEST-CA02 for rerouting!
            if loc_id in ("STORE-NYC-5TH", "STORE-MIA-BRICKELL") and idx <= 12:
                on_hand = 14
                reserved = 6
                safety_stock = 4
                webhook_delta = 5  # True ATP = 14 - 6 - 4 - 5 = -1 (0 available!)
            elif loc_id == "WH-EAST-NJ01" and idx <= 8:
                on_hand = 22
                reserved = 10
                safety_stock = 6
                webhook_delta = 7  # True ATP = 22 - 10 - 6 - 7 = -1 (0 available!)
            elif loc_id == "WH-CENTRAL-TX03":
                on_hand = 85 + (idx % 20)
                reserved = 10
                safety_stock = 8
                webhook_delta = 2  # True ATP >= 65
            elif loc_id == "WH-WEST-CA02":
                on_hand = 70 + (idx % 15)
                reserved = 8
                safety_stock = 8
                webhook_delta = 1  # True ATP >= 53
            else:
                on_hand = rng.randint(28, 64)
                reserved = rng.randint(3, 8)
                safety_stock = rng.randint(4, 6)
                webhook_delta = rng.randint(0, 3)

            scan_ts = f"2026-10-22T{14 + (loc_idx % 6):02d}:{10 + (idx % 45):02d}:00Z"
            wms_row = {
                "inventory_id": inv_id,
                "location_id": loc_id,
                "location_type": loc_type,
                "shipping_cost_usd": ship_cost,
                "gtin_14": gtin_14,
                "sku": sku,
                "product_name": prod_name,
                "category": cat,
                "rfid_epc_prefix": rfid_prefix,
                "on_hand_qty": on_hand,
                "reserved_qty": reserved,
                "safety_stock_qty": safety_stock,
                "unprocessed_webhook_delta_qty": webhook_delta,
                "last_scan_ts": scan_ts,
            }
            wms_records.append(wms_row)
            cur.execute(
                """
                INSERT INTO wms_inventory (
                    inventory_id, location_id, location_type, shipping_cost_usd,
                    gtin_14, sku, product_name, category, rfid_epc_prefix,
                    on_hand_qty, reserved_qty, safety_stock_qty,
                    unprocessed_webhook_delta_qty, last_scan_ts
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    inv_id,
                    loc_id,
                    loc_type,
                    ship_cost,
                    gtin_14,
                    sku,
                    prod_name,
                    cat,
                    rfid_prefix,
                    on_hand,
                    reserved,
                    safety_stock,
                    webhook_delta,
                    scan_ts,
                ),
            )

            # Log POS webhook lag events when webhook_delta > 0
            if webhook_delta > 0 and loc_id in ("STORE-NYC-5TH", "STORE-MIA-BRICKELL", "WH-EAST-NJ01"):
                ev_id = f"POS-EVT-{pos_seq:04d}"
                pos_seq += 1
                term_id = f"TERM-{loc_id.split('-')[1]}-{(pos_seq % 8) + 1:02d}"
                latency_ms = rng.randint(1450, 4800)
                lag_sec = rng.randint(180, 940)
                http_status = 504 if lag_sec > 500 else 429
                err_code = "POS_WEBHOOK_GATEWAY_TIMEOUT" if http_status == 504 else "WMS_QUEUE_RATE_LIMITED"
                pos_telemetry_rows.append(
                    (
                        ev_id,
                        loc_id,
                        term_id,
                        "POS_INSTORE" if loc_type == "FLAGSHIP_STORE" else "BOPIS",
                        sku,
                        webhook_delta,
                        latency_ms,
                        lag_sec,
                        http_status,
                        err_code,
                        scan_ts,
                    )
                )
                jsonl_events.append(
                    {
                        "event_type": "POS_CHECKOUT_WEBHOOK_LAG",
                        "event_id": ev_id,
                        "timestamp": scan_ts,
                        "store_id": loc_id,
                        "pos_terminal_id": term_id,
                        "channel": "POS_INSTORE" if loc_type == "FLAGSHIP_STORE" else "BOPIS",
                        "sku": sku,
                        "gtin_14": gtin_14,
                        "rfid_epc_prefix": rfid_prefix,
                        "unprocessed_webhook_delta_qty": webhook_delta,
                        "payment_gateway_latency_ms": latency_ms,
                        "webhook_sync_lag_sec": lag_sec,
                        "http_status": http_status,
                        "error_code": err_code,
                    }
                )

    for pt in pos_telemetry_rows:
        cur.execute(
            """
            INSERT INTO pos_telemetry (
                event_id, store_id, pos_terminal_id, channel, sku, qty_delta,
                payment_gateway_latency_ms, webhook_sync_lag_sec, http_status,
                error_code, event_ts
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            pt,
        )

    # Also log EDI 856 ASN events for vendor contracts in JSONL
    asn_seq = 1
    for vc in VENDOR_CONTRACTS:
        is_breach = vc["status"] == "BREACH_HOLD"
        num_asn_logs = 3 if is_breach else 1
        for k in range(num_asn_logs):
            asn_id = f"ASN-856-{asn_seq:04d}"
            po_num = f"PO-2026-{asn_seq + 5000}"
            asn_seq += 1
            delay_hrs = rng.randint(36, 128) if is_breach else 0
            ordered_q = rng.randint(250, 900)
            short_q = rng.randint(25, 110) if is_breach else 0
            jsonl_events.append(
                {
                    "event_type": "EDI_856_ASN_AUDIT",
                    "event_id": f"EDI-EVT-{asn_seq:04d}",
                    "timestamp": f"2026-10-21T{10 + (k * 3):02d}:15:00Z",
                    "asn_id": asn_id,
                    "po_number": po_num,
                    "contract_id": vc["contract_id"],
                    "vendor_name": vc["vendor_name"],
                    "category": vc["category"],
                    "otif_target_pct": vc["otif_target_pct"],
                    "actual_otif_pct": vc["actual_otif_pct"],
                    "delay_hours": delay_hrs,
                    "ordered_qty": ordered_q,
                    "received_qty": ordered_q - short_q,
                    "short_qty": short_q,
                    "delayed_po_value_usd": round(vc["delayed_po_value_usd"] / num_asn_logs, 2) if is_breach else 0.0,
                    "chargeback_penalty_pct": vc["chargeback_penalty_pct"],
                    "otif_compliant": not is_breach,
                    "edi_error_code": "ASN_856_LATE_OR_SHORT_SHIPMENT" if is_breach else "OK",
                }
            )

    # 3. Insert Promotional Campaigns
    for promo in PROMO_CAMPAIGNS:
        cur.execute(
            """
            INSERT INTO promo_campaigns (
                promo_code, campaign_name, discount_pct,
                is_stackable, min_margin_floor_pct, active
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                promo["promo_code"],
                promo["campaign_name"],
                promo["discount_pct"],
                promo["is_stackable"],
                promo["min_margin_floor_pct"],
                promo["active"],
            ),
        )

    # 4. Generate 200 Omnichannel Sales Orders
    # Includes:
    # - 30 orders with abusive promo stacking ("VIP25,FLASH20,EMP30") causing negative margin leakage under Bug 1A
    # - 35 high-LTV DIAMOND/GOLD orders placed against phantom-stock locations (STORE-NYC-5TH, WH-EAST-NJ01, STORE-MIA-BRICKELL) in AT_RISK_STOCKOUT
    # - 135 diverse omnichannel orders across WEB_ECOMM, MOBILE_APP, POS_INSTORE, BOPIS
    orders_list: list[dict[str, Any]] = []
    channels = ["WEB_ECOMM", "MOBILE_APP", "POS_INSTORE", "BOPIS"]
    segments = ["VIP_CONCIERGE", "ENTERPRISE_B2B", "LOYAL_REPEAT", "NEW_ACQUISITION"]

    for ord_idx in range(1, 201):
        order_id = f"ORD-2026-{ord_idx:04d}"
        customer_id = f"CUST-{(ord_idx * 17) % 140 + 1000}"

        if ord_idx <= 30:
            # Intentional Margin-Bleed / Promo-Stacking orders (MARGIN_HOLD)
            sku_obj = sku_records[(ord_idx - 1) % 14]  # High ticket electronics & appliances
            loyalty_tier = "DIAMOND" if ord_idx % 2 == 0 else "GOLD"
            customer_segment = "VIP_CONCIERGE"
            ltv = round(rng.uniform(6500.0, 18500.0), 2)
            channel = channels[ord_idx % 4]
            qty = 4 if ord_idx <= 29 else 5
            applied_promos = "VIP25,FLASH20,EMP30"  # 75% additive discount under Bug 1A!
            unit_price = sku_obj["unit_price_usd"]
            unit_cost = sku_obj["unit_wholesale_cost_usd"]
            gross_rev = round(unit_price * qty, 2)
            # Buggy discount recorded when order was ingested prior to Margin Guard:
            discount_amt = round(gross_rev * 0.75, 2)
            net_rev = round(gross_rev - discount_amt, 2)
            gross_margin_usd = round(net_rev - (unit_cost * qty), 2)
            gross_margin_pct = round((gross_margin_usd / net_rev) * 100.0, 2) if net_rev > 0 else -100.0
            fulfillment_loc = "WH-CENTRAL-TX03" if ord_idx % 2 == 0 else "WH-WEST-CA02"
            order_status = "MARGIN_HOLD"
        elif ord_idx <= 65:
            # Intentional High-LTV VIP orders assigned to locations with phantom stock (AT_RISK_STOCKOUT)
            sku_obj = sku_records[(ord_idx - 31) % 8]  # SKUs 1..8 have 0 True ATP at STORE-NYC-5TH and WH-EAST-NJ01
            loyalty_tier = "DIAMOND" if ord_idx <= 50 else "GOLD"
            customer_segment = "VIP_CONCIERGE" if loyalty_tier == "DIAMOND" else "LOYAL_REPEAT"
            ltv = round(rng.uniform(8200.0, 18500.0), 2) if loyalty_tier == "DIAMOND" else round(rng.uniform(3500.0, 8000.0), 2)
            channel = "BOPIS" if ord_idx % 2 == 0 else "WEB_ECOMM"
            qty = rng.randint(1, 3)
            applied_promos = "LOYALTY5"
            unit_price = sku_obj["unit_price_usd"]
            unit_cost = sku_obj["unit_wholesale_cost_usd"]
            gross_rev = round(unit_price * qty, 2)
            discount_amt = round(gross_rev * 0.05, 2)
            net_rev = round(gross_rev - discount_amt, 2)
            gross_margin_usd = round(net_rev - (unit_cost * qty), 2)
            gross_margin_pct = round((gross_margin_usd / net_rev) * 100.0, 2)
            fulfillment_loc = "STORE-NYC-5TH" if ord_idx % 2 == 0 else "WH-EAST-NJ01"
            order_status = "AT_RISK_STOCKOUT"
        else:
            sku_obj = sku_records[ord_idx % len(sku_records)]
            tier_choice = ["GOLD", "SILVER", "STANDARD", "DIAMOND"][ord_idx % 4]
            loyalty_tier = tier_choice
            customer_segment = segments[ord_idx % len(segments)]
            ltv_ranges = {
                "DIAMOND": (9000.0, 18500.0),
                "GOLD": (3500.0, 8900.0),
                "SILVER": (1200.0, 3400.0),
                "STANDARD": (450.0, 1150.0),
            }
            low_ltv, high_ltv = ltv_ranges[loyalty_tier]
            ltv = round(rng.uniform(low_ltv, high_ltv), 2)
            channel = channels[ord_idx % 4]
            qty = rng.randint(1, 4)
            applied_promos = "HOLIDAY15" if ord_idx % 3 == 0 else ("BUNDLE10,LOYALTY5" if ord_idx % 5 == 0 else "")
            disc_rate = 0.15 if applied_promos == "HOLIDAY15" else (0.1425 if applied_promos == "BUNDLE10,LOYALTY5" else 0.0)
            unit_price = sku_obj["unit_price_usd"]
            unit_cost = sku_obj["unit_wholesale_cost_usd"]
            gross_rev = round(unit_price * qty, 2)
            discount_amt = round(gross_rev * disc_rate, 2)
            net_rev = round(gross_rev - discount_amt, 2)
            gross_margin_usd = round(net_rev - (unit_cost * qty), 2)
            gross_margin_pct = round((gross_margin_usd / net_rev) * 100.0, 2)
            fulfillment_loc = "WH-CENTRAL-TX03" if ord_idx % 2 == 0 else "WH-WEST-CA02"
            order_status = "PENDING_ROUTING" if ord_idx <= 90 else "FULFILLED"

        ord_record = {
            "order_id": order_id,
            "customer_id": customer_id,
            "customer_segment": customer_segment,
            "loyalty_tier": loyalty_tier,
            "customer_ltv_usd": ltv,
            "channel": channel,
            "sku": sku_obj["sku"],
            "qty": qty,
            "unit_price_usd": unit_price,
            "unit_wholesale_cost_usd": unit_cost,
            "applied_promo_codes": applied_promos,
            "discount_amount_usd": discount_amt,
            "net_revenue_usd": net_rev,
            "gross_margin_usd": gross_margin_usd,
            "gross_margin_pct": gross_margin_pct,
            "fulfillment_location_id": fulfillment_loc,
            "order_status": order_status,
        }
        orders_list.append(ord_record)
        cur.execute(
            """
            INSERT INTO omnichannel_orders (
                order_id, customer_id, customer_segment, loyalty_tier,
                customer_ltv_usd, channel, sku, qty, unit_price_usd,
                unit_wholesale_cost_usd, applied_promo_codes, discount_amount_usd,
                net_revenue_usd, gross_margin_usd, gross_margin_pct,
                fulfillment_location_id, order_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                order_id,
                customer_id,
                customer_segment,
                loyalty_tier,
                ltv,
                channel,
                sku_obj["sku"],
                qty,
                unit_price,
                unit_cost,
                applied_promos,
                discount_amt,
                net_rev,
                gross_margin_usd,
                gross_margin_pct,
                fulfillment_loc,
                order_status,
            ),
        )

    conn.commit()
    conn.close()

    # Write CSV exports
    with open(EXPORTS_DIR / "vendor_contracts.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(VENDOR_CONTRACTS[0].keys()))
        writer.writeheader()
        writer.writerows(VENDOR_CONTRACTS)

    with open(EXPORTS_DIR / "wms_inventory.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(wms_records[0].keys()))
        writer.writeheader()
        writer.writerows(wms_records)

    with open(EXPORTS_DIR / "omnichannel_orders.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(orders_list[0].keys()))
        writer.writeheader()
        writer.writerows(orders_list)

    # Write JSONL telemetry logs
    with open(JSONL_PATH, "w", encoding="utf-8") as f:
        for ev in jsonl_events:
            f.write(json.dumps(ev) + "\n")

    margin_leakage_total = sum(abs(o["gross_margin_usd"]) for o in orders_list if o["gross_margin_usd"] < 0)
    return {
        "db_path": str(DB_PATH),
        "vendor_contracts_count": len(VENDOR_CONTRACTS),
        "sku_count": len(sku_records),
        "wms_inventory_rows": len(wms_records),
        "promo_campaigns_count": len(PROMO_CAMPAIGNS),
        "orders_count": len(orders_list),
        "jsonl_events_count": len(jsonl_events),
        "negative_margin_leakage_usd": round(margin_leakage_total, 2),
    }


if __name__ == "__main__":
    summary = seed_all()
    print(json.dumps(summary, indent=2))
