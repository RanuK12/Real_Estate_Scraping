"""
Generate a per-zone real-estate market report (PDF) from the scraper's
exported data (CSV/JSON in ``data/``).

For each zone (``location``) reports: stock (listing count), average
price per m², and the % variation vs. the previous scraped snapshot.
"""

import csv
import glob
import json
import os
import statistics
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def load_records(data_dir: str = "data") -> List[Dict[str, Any]]:
    """Load all scraped property records from CSV/JSON files in data_dir."""
    records: List[Dict[str, Any]] = []
    for path in sorted(glob.glob(os.path.join(data_dir, "properties_*.csv"))):
        with open(path, newline="", encoding="utf-8") as f:
            records.extend(csv.DictReader(f))
    for path in sorted(glob.glob(os.path.join(data_dir, "properties_*.json"))):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                records.extend(data)
    return records


def _to_float(value: Any) -> Optional[float]:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _snapshot_date(record: Dict[str, Any]) -> Optional[str]:
    scraped_at = record.get("scraped_at")
    if not scraped_at:
        return None
    return str(scraped_at)[:10]  # YYYY-MM-DD


def build_zone_stats(records: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Group records by zone (``location``) and compute, per zone:
      - stock: number of listings
      - avg_price_per_m2: mean of price_per_m2 across listings that have it
      - variation_pct: % change in avg_price_per_m2 between the two most
        recent snapshot dates for that zone (None if fewer than 2 dates)
    """
    by_zone: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in records:
        zone = r.get("location") or "Sin especificar"
        by_zone[zone].append(r)

    stats: Dict[str, Dict[str, Any]] = {}
    for zone, rows in by_zone.items():
        prices = [p for p in (_to_float(r.get("price_per_m2")) for r in rows) if p is not None]
        avg_price_per_m2 = round(statistics.mean(prices), 2) if prices else None

        by_date: Dict[str, List[float]] = defaultdict(list)
        for r in rows:
            date = _snapshot_date(r)
            price = _to_float(r.get("price_per_m2"))
            if date and price is not None:
                by_date[date].append(price)

        variation_pct = None
        dates = sorted(by_date)
        if len(dates) >= 2:
            prev_avg = statistics.mean(by_date[dates[-2]])
            last_avg = statistics.mean(by_date[dates[-1]])
            if prev_avg:
                variation_pct = round((last_avg - prev_avg) / prev_avg * 100, 2)

        stats[zone] = {
            "stock": len(rows),
            "avg_price_per_m2": avg_price_per_m2,
            "variation_pct": variation_pct,
        }
    return stats


def generate_pdf(
    zone_stats: Dict[str, Dict[str, Any]],
    output_path: str = "Real_Estate_Report.pdf",
) -> str:
    """Render zone_stats into a PDF market report. Returns the output path."""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Informe de Mercado Inmobiliario", styles["Title"]),
        Paragraph(f"Generado el {datetime.now().strftime('%Y-%m-%d')}", styles["Normal"]),
        Spacer(1, 0.3 * inch),
    ]

    header = ["Zona", "Stock", "Precio/m² prom.", "Variación"]
    rows = [header]
    for zone in sorted(zone_stats, key=lambda z: zone_stats[z]["stock"], reverse=True):
        s = zone_stats[zone]
        price = f"${s['avg_price_per_m2']:,.2f}" if s["avg_price_per_m2"] is not None else "N/D"
        variation = f"{s['variation_pct']:+.2f}%" if s["variation_pct"] is not None else "N/D"
        rows.append([zone, str(s["stock"]), price, variation])

    table = Table(rows, colWidths=[2.2 * inch, 0.8 * inch, 1.6 * inch, 1.2 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ]
        )
    )
    story.append(table)
    doc.build(story)
    return output_path


def main() -> None:
    """CLI: build the market report PDF from previously exported scraper data."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Genera un informe de mercado inmobiliario en PDF, por zona."
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Directorio con los CSV/JSON exportados por real-estate-scraper (default: data).",
    )
    parser.add_argument(
        "--output",
        default="Real_Estate_Report.pdf",
        help="Ruta del PDF a generar (default: Real_Estate_Report.pdf).",
    )
    args = parser.parse_args()

    records = load_records(args.data_dir)
    if not records:
        print(f"No hay datos en {args.data_dir}. Corré primero: real-estate-scraper --export csv")
        return

    stats = build_zone_stats(records)
    path = generate_pdf(stats, args.output)
    print(f"Informe generado: {path} ({len(stats)} zonas, {len(records)} propiedades)")


if __name__ == "__main__":
    main()
