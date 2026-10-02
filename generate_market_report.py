#!/usr/bin/env python3
import json, os, sys
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from collections import defaultdict
from datetime import datetime

data_path = os.path.expanduser("~/.ranukita/projects/real_estate_scraping/data/market_data.json")
out_path = os.path.expanduser("~/.ranukita/projects/real_estate_scraping/reports/market_report.pdf")


def load_data():
    with open(data_path, encoding="utf-8") as f:
        return json.load(f)


def aggregate(records):
    # Agrupar por zona y luego por mes
    zone_data = defaultdict(lambda: defaultdict(list))  # zona -> mes -> lista de price_m2
    
    for r in records:
        z = r.get("zona")
        if not z:
            continue
        precio = r.get("precio")
        superficie = r.get("superficie")
        fecha_str = r.get("fecha")
        if precio is not None and superficie and superficie > 0 and fecha_str:
            price_m2 = precio / superficie
            # Extraer año-mes de la fecha (YYYY-MM-DD -> YYYY-MM)
            try:
                mes = fecha_str[:7]  # YYYY-MM
                zone_data[z][mes].append(price_m2)
            except:
                continue
    
    out = []
    for zona, meses in zone_data.items():
        # Ordenar meses cronológicamente
        sorted_meses = sorted(meses.keys())
        if not sorted_meses:
            continue
            
        # Calcular promedio del mes más reciente
        latest_mes = sorted_meses[-1]
        latest_prices = meses[latest_mes]
        avg_latest = sum(latest_prices) / len(latest_prices) if latest_prices else 0
        
        # Calcular variación respecto al mes anterior si existe
        variacion = 0.0
        if len(sorted_meses) >= 2:
            prev_mes = sorted_meses[-2]
            prev_prices = meses[prev_mes]
            avg_prev = sum(prev_prices) / len(prev_prices) if prev_prices else 0
            if avg_prev > 0:
                variacion = ((avg_latest - avg_prev) / avg_prev) * 100
        
        # Calcular stock total (propiedades en todos los meses)
        total_stock = sum(len(prices) for prices in meses.values())
        
        out.append([
            zona,
            f"${avg_latest:.2f}",
            total_stock,
            f"{variacion:+.1f}%"
        ])
    
    out.sort(key=lambda x: x[0])  # Ordenar alfabéticamente por zona
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