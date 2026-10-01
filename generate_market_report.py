#!/usr/bin/env python3
import json, os, sys
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

data_path = os.path.expanduser("~/.ranukita/projects/real_estate_scraping/data/market_data.json")
out_path = os.path.expanduser("~/.ranukita/projects/real_estate_scraping/reports/market_report.pdf")


def load_data():
    with open(data_path, encoding="utf-8") as f:
        return json.load(f)


def aggregate(records):
    from collections import defaultdict
    zone = defaultdict(lambda: {"price_m2_sum": 0.0, "price_m2_cnt": 0, "stock": 0})
    for r in records:
        z = r.get("zona")
        if not z:
            continue
        precio = r.get("precio")
        superficie = r.get("superficie")
        if precio is not None and superficie and superficie > 0:
            price_m2 = precio / superficie
            zone[z]["price_m2_sum"] += price_m2
            zone[z]["price_m2_cnt"] += 1
        zone[z]["stock"] += 1
    out = []
    for z, v in zone.items():
        avg = v["price_m2_sum"] / v["price_m2_cnt"] if v["price_m2_cnt"] else 0
        out.append([z, f"${avg:.2f}", v["stock"], ""])  # Variación placeholder
    out.sort(key=lambda x: x[0])
    return out


def build_pdf(rows):
    doc = SimpleDocTemplate(out_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elems = [Paragraph("Informe de Mercado por Zona", styles["Title"]), Spacer(1, 12)]
    data = [["Zona", "Precio m² (USD)", "Stock", "Variación %"]] + rows
    t = Table(data, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))
    elems.append(t)
    doc.build(elems)


if __name__ == "__main__":
    try:
        recs = load_data()
        rows = aggregate(recs)
        build_pdf(rows)
        print(f"Reporte generado: {out_path}")
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)