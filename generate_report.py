#!/usr/bin/env python3
import pandas as pd
import glob
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# Find all CSV files in data/
csv_files = sorted(glob.glob("/Users/emilioranucoli/.ranukita/projects/real_estate_scraping/data/*.csv"))
if not csv_files:
    raise FileNotFoundError("No CSV files found in data/")

# Load and concatenate
df_list = []
for f in csv_files:
    df = pd.read_csv(f)
    # Clean price_per_m2: remove $ and commas, convert to float
    df['price_per_m2_clean'] = df['price_per_m2'].replace({'\\$': '', ',': ''}, regex=True).astype(float)
    # Ensure scraped_at is datetime
    df['scraped_at'] = pd.to_datetime(df['scraped_at'])
    df_list.append(df)

df = pd.concat(df_list, ignore_index=True)

# Group by location (zona)
grouped = df.groupby('location').agg(
    precio_m2_prom=('price_per_m2_clean', 'mean'),
    stock_total=('price_per_m2_clean', 'count'),  # number of listings
).reset_index()

# Compute variation per location
def compute_variation(subdf):
    subdf = subdf.sort_values('scraped_at')
    if len(subdf) < 2:
        return 0.0
    first = subdf.iloc[0]['price_per_m2_clean']
    last = subdf.iloc[-1]['price_per_m2_clean']
    if first == 0:
        return 0.0
    return (last - first) / first * 100.0

variation_series = df.groupby('location').apply(compute_variation)
variation_series.name = 'variacion_pct'
grouped = grouped.merge(variation_series, left_on='location', right_index=True)

# Prepare data for PDF
data = [["Zona","Precio m2 promedio","Stock total","Variación %"]]
for _, row in grouped.iterrows():
    data.append([
        row['location'],
        f"${row['precio_m2_prom']:,.2f}",
        int(row['stock_total']),
        f"{row['variacion_pct']:.2f}%"
    ])

# Build PDF
doc = SimpleDocTemplate("informe_mercado.pdf", pagesize=A4)
styles = getSampleStyleSheet()
elements = [Paragraph("Informe de Mercado Inmobiliario", styles['Title']), Spacer(1,12)]

table = Table(data, hAlign='LEFT')
table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.grey),
    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
    ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
]))
elements.append(table)
doc.build(elements)

print("Reporte generado: informe_mercado.pdf")
