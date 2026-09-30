#!/usr/bin/env python3
import json, os, datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "market_data.json")
OUT_DIR   = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(OUT_DIR, exist_ok=True)

with open(DATA_PATH, encoding="utf-8") as f:
    listings = json.load(f)

# agregación por zona
stats = {}
for l in listings:
    z = l["zona"]
    precio_m2 = l["precio"] / l["superficie"]
    stats.setdefault(z, {"precios_m2":[], "count":0})
    stats[z]["precios_m2"].append(precio_m2)
    stats[z]["count"] += 1

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
    avg = sum(d["precios_m2"])/len(d["precios_m2"])
    line = f"{zona}: {d['count']} activos, precio medio m2 = {avg:.0f} USD"
    c.drawString(60, y, line)
    y -= 18
    if y < 50:
        c.showPage()
        y = height - 50
c.save()
print(f"PDF generado: {pdf_path}")