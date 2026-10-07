#!/usr/bin/env python3
import json, os, sys
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict
from datetime import datetime

data_path = os.path.expanduser("~/.ranukita/projects/real_estate_scraping/data/market_data.json")
out_path = os.path.expanduser("~/.ranukita/projects/real_estate_scraping/reports/market_report.pdf")
chart_path = os.path.expanduser("~/.ranukita/projects/real_estate_scraping/reports/chart.png")


def load_data():
    with open(data_path, encoding="utf-8") as f:
        return json.load(f)


def aggregate(records):
    # Group by zone and then by month (we have dates like 2026-01-15)
    zone_data = defaultdict(list)  # zone -> list of (date, price_m2)
    for r in records:
        z = r.get("zona")
        if not z:
            continue
        precio = r.get("precio")
        superficie = r.get("superficie")
        if precio is not None and superficie and superficie > 0:
            price_m2 = precio / superficie
            fecha_str = r.get("fecha")
            try:
                date = datetime.strptime(fecha_str, "%Y-%m-%d")
            except:
                continue
            zone_data[z].append((date, price_m2))
    
    # For each zone, sort by date, compute average price per m2 per month? 
    # We'll compute the average price per m2 for the first and last month to get variation.
    rows = []
    for zone, entries in zone_data.items():
        if not entries:
            continue
        entries.sort(key=lambda x: x[0])
        # Group by month (year-month) to get monthly average
        monthly = defaultdict(list)
        for date, price_m2 in entries:
            key = date.strftime("%Y-%m")
            monthly[key].append(price_m2)
        # Compute average per month
        months_sorted = sorted(monthly.keys())
        avg_per_month = [sum(monthly[m])/len(monthly[m]) for m in months_sorted]
        # Overall average price m2 (for the period)
        avg_price_m2 = sum(avg_per_month)/len(avg_per_month) if avg_per_month else 0
        # Stock: total number of properties in the zone
        stock = len(entries)
        # Variation % from first to last month
        if len(avg_per_month) >= 2:
            first = avg_per_month[0]
            last = avg_per_month[-1]
            variation = ((last - first) / first) * 100 if first != 0 else 0
        else:
            variation = 0
        rows.append([zone, f"${avg_price_m2:.2f}", stock, f"{variation:.1f}%"])
        # Store for chart: we need to return also the monthly data for plotting
        # We'll return a dict with zone -> (months_sorted, avg_per_month)
    # We'll return rows and also the chart data
    chart_data = {}
    for zone, entries in zone_data.items():
        entries.sort(key=lambda x: x[0])
        monthly = defaultdict(list)
        for date, price_m2 in entries:
            key = date.strftime("%Y-%m")
            monthly[key].append(price_m2)
        months_sorted = sorted(monthly.keys())
        avg_per_month = [sum(monthly[m])/len(monthly[m]) for m in months_sorted]
        chart_data[zone] = (months_sorted, avg_per_month)
    return rows, chart_data


def build_pdf(rows, chart_data):
    doc = SimpleDocTemplate(out_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elems = [Paragraph("Informe de Mercado por Zona", styles["Title"]), Spacer(1, 12)]
    
    # Table
    data = [["Zona", "Precio m² (USD)", "Stock", "Variación %"]] + rows
    t = Table(data, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))
    elems.append(t)
    elems.append(Spacer(1, 12))
    
    # Chart
    if chart_data:
        plt.figure(figsize=(8, 4))
        for zone, (months, avgs) in chart_data.items():
            plt.plot(months, avgs, marker='o', label=zone)
        plt.title("Evolución del Precio m² Promedio por Zona")
        plt.xlabel("Mes")
        plt.ylabel("Precio m² (USD)")
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()
        
        if os.path.exists(chart_path):
            elems.append(Paragraph("Gráfico de Evolución de Precios", styles["Heading2"]))
            elems.append(Spacer(1, 6))
            # Limit image width to page width
            img = Image(chart_path, width=480, height=288)  # adjust as needed
            elems.append(img)
    
    doc.build(elems)


if __name__ == "__main__":
    try:
        recs = load_data()
        rows, chart_data = aggregate(recs)
        build_pdf(rows, chart_data)
        print(f"Reporte generado: {out_path}")
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)