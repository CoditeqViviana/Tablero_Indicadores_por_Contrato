#!/usr/bin/env python3
"""Sincroniza datos de Odoo → data/sync.json para el Tablero Truput."""

import json, os, urllib.request
from datetime import datetime, date

# ── Configuración (viene de variables de entorno / GitHub Secrets) ──
ODOO_URL = os.environ.get("ODOO_URL", "https://coditeq.odoo.com/jsonrpc")
ODOO_DB  = os.environ.get("ODOO_DB",  "usrgit-coditeq-coditeq-master-1621259")
ODOO_UID = int(os.environ.get("ODOO_UID", "1259"))
ODOO_KEY = os.environ["ODOO_API_KEY"]
YEAR     = int(os.environ.get("SYNC_YEAR", str(date.today().year)))

# ── JSON-RPC ────────────────────────────────────────────────────────
def rpc(model, method, domain=None, fields=None, limit=50000):
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_UID, ODOO_KEY,
                model, method,
                [domain or []],
                {"fields": fields or [], "limit": limit}
            ]
        }
    }
    req = urllib.request.Request(
        ODOO_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        body = json.loads(resp.read())
    if "error" in body:
        raise Exception(f"Odoo error en {model}.{method}: {body['error']}")
    return body["result"]

def m2o(val):
    """Extrae display_name de un campo many2one [id, 'nombre'] → 'nombre'."""
    if isinstance(val, (list, tuple)) and len(val) == 2:
        return str(val[1])
    return str(val) if val else ""

# ── 1. Reporte Truput  (truput.report) ──────────────────────────────
def fetch_truput():
    domain = [
        ("invoice_date", ">=", f"{YEAR}-01-01"),
        ("invoice_date", "<=", f"{YEAR}-12-31"),
    ]
    fields = [
        "customer_city", "invoice_date", "invoice",
        "customer_nit", "customer_name", "seller_name",
        "product_internal_reference", "product_category",
        "qty_invoiced", "price_no_tax", "unit_cost",
        "price_total", "total_cost", "truput_invoice", "perc_truput",
    ]
    recs = rpc("truput.report", "search_read", domain, fields)
    headers = [
        "Ciudad del cliente", "Fecha factura", "Factura de venta",
        "NIT cliente", "Nombre del cliente", "Nombre del vendedor",
        "Referencia interna del producto", "Categoría del producto",
        "Ctd. Facturada", "Precio de venta unitario sin IVA", "Costo unitario",
        "Venta total", "Costo total", "Truput factura", "% Factura",
    ]
    rows = [headers]
    for r in recs:
        rows.append([
            r.get("customer_city") or "",
            r.get("invoice_date") or "",
            m2o(r.get("invoice")),
            r.get("customer_nit") or "",
            r.get("customer_name") or "",
            r.get("seller_name") or "",
            r.get("product_internal_reference") or "",
            r.get("product_category") or "",
            r.get("qty_invoiced", 0),
            r.get("price_no_tax", 0),
            r.get("unit_cost", 0),
            round(r.get("price_total", 0), 2),
            round(r.get("total_cost", 0), 2),
            round(r.get("truput_invoice", 0), 2),
            round(r.get("perc_truput", 0), 2),
        ])
    return rows

# ── 2. Apunte Contable  (account.move.line) ─────────────────────────
def fetch_apunte():
    domain = [
        ("account_id.code", ">=", "6"),
        ("account_id.code", "<", "7"),
        ("date", ">=", f"{YEAR}-01-01"),
        ("date", "<=", f"{YEAR}-12-31"),
        "|",
        ("ref", "ilike", "autoc"),
        ("name", "ilike", "autoc"),
    ]
    fields = ["date", "move_id", "partner_id", "ref", "name", "debit"]
    recs = rpc("account.move.line", "search_read", domain, fields)
    headers = ["Fecha", "Asiento contable", "Asociado", "Referencia", "Etiqueta", "Debe"]
    rows = [headers]
    for r in recs:
        rows.append([
            r.get("date") or "",
            m2o(r.get("move_id")),
            m2o(r.get("partner_id")),
            r.get("ref") or "",
            r.get("name") or "",
            round(r.get("debit", 0), 2),
        ])
    return rows

# ── 3. Traslado  (stock.picking) ────────────────────────────────────
def fetch_traslado():
    domain = [
        ("name", "ilike", "AUTOC"),
        ("create_date", ">=", f"{YEAR}-01-01 00:00:00"),
    ]
    fields = ["name", "factura", "partner_id"]
    recs = rpc("stock.picking", "search_read", domain, fields)
    headers = ["Referencia", "Factura", "Contacto"]
    rows = [headers]
    for r in recs:
        rows.append([
            r.get("name") or "",
            m2o(r.get("factura")),
            m2o(r.get("partner_id")),
        ])
    return rows

# ── Main ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    print(f"Sincronizando Odoo → Tablero Truput (año {YEAR})...\n")

    print("  1/3  Reporte Truput (truput.report)...")
    truput = fetch_truput()
    print(f"       → {len(truput)-1:,} registros")

    print("  2/3  Apunte Contable (account.move.line)...")
    apunte = fetch_apunte()
    print(f"       → {len(apunte)-1:,} registros")

    print("  3/3  Traslado (stock.picking)...")
    traslado = fetch_traslado()
    print(f"       → {len(traslado)-1:,} registros")

    sync = {
        "updated": datetime.utcnow().isoformat() + "Z",
        "year": YEAR,
        "truput": truput,
        "apunte": apunte,
        "traslado": traslado,
    }
    path = "data/sync.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sync, f, ensure_ascii=False, separators=(",", ":"))

    mb = os.path.getsize(path) / (1024 * 1024)
    print(f"\n  ✓ {path} generado ({mb:.1f} MB)")
    print("  Sincronización completada.")
