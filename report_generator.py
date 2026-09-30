#!/usr/bin/env python3
"""
Generador de informe de mercado inmobiliario por zona.
Lee datos de market_data.json y genera un PDF con estadísticas por zona.
"""
import json
import os
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "market_data.json")
OUT_DIR = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(OUT_DIR, exist_ok=True)

with open(DATA_PATH, encoding="utf-8") as f:
    listings = json.load(f)

# Calcular precio por m2 y agrupar por zona
stats = {}
for l in listings:
    zona = l["zona"]
    precio_m2 = l["precio"] / l["superficie"]
    stats.setdefault(zona, {"precios": [], "count": 0})
    stats[zona]["precios"].append(precio_m2)
    stats[zona]["count"] += 1

today = datetime.date.today().isoformat()
pdf_path = os.path.join(OUT_DIR, f"market_report_{today}.pdf")
c = canvas.Canvas(pdf_path, pagesize=A4)
width, height = A4
y = height - 50
c.setFont("Helvetica-Bold", 14)
c.drawString(50, y, f"Informe de mercado – {today}")
y -= 30
c.setFont("Helvetica", 11)
for zona, d in stats.items():
    avg = sum(d["precios"]) / len(d["precios"])
    line = f"{zona}: {d['count']} activos, precio medio m2 = {avg:.0f} USD"
    c.drawString(60, y, line)
    y -= 18
    if y < 50:
        c.showPage()
        y = height - 50
c.save()
print(f"PDF generado: {pdf_path}")
