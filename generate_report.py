import pandas as pd
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

DATA_PATH = os.path.expanduser("~/.ranukita/projects/real_estate_scraping/data/sample_properties.csv")
OUT_DIR   = os.path.expanduser("~/.ranukita/projects/real_estate_scraping/reports")
os.makedirs(OUT_DIR, exist_ok=True)

# Load data
df = pd.read_csv(DATA_PATH)

# Clean price_per_m2: remove $ and commas, convert to float
df['price_per_m2_clean'] = df['price_per_m2'].replace({r'\$': '', ',': ''}, regex=True).astype(float)

# Ensure date
df['scraped_at'] = pd.to_datetime(df['scraped_at'])
df['mes'] = df['scraped_at'].dt.to_period('M')

# Group by zona (location)
agg = df.groupby('location').agg(
    stock=('price_per_m2_clean', 'count'),
    precio_m2_mean=('price_per_m2_clean', 'mean'),
    precio_m2_std=('price_per_m2_clean', 'std')
).reset_index()

# Monthly variation: compute average price per zona per month, then pct change
variacion = df.groupby(['location', 'mes'])['price_per_m2_clean'].mean().reset_index()
variacion['var_pct'] = variacion.groupby('location')['price_per_m2_clean'].pct_change() * 100
var_last = variacion.groupby('location')['var_pct'].last().reset_index(name='variacion_pct')

# Merge
agg = agg.merge(var_last, on='location', how='left')

# PDF
pdf_path = os.path.join(OUT_DIR, "informe_mercado.pdf")
doc = SimpleDocTemplate(pdf_path, pagesize=A4)
elements = []
styles = getSampleStyleSheet()
elements.append(Paragraph("Informe de Mercado Inmobiliario", styles['Title']))
elements.append(Spacer(1,12))

# Table data
data = [["Zona", "Stock", "Precio medio (€/m²)", "Desviación estándar", "Variación mensual (%)"]]
for _, r in agg.iterrows():
    data.append([
        r['location'],
        int(r['stock']),
        f"{r['precio_m2_mean']:.2f}",
        f"{r['precio_m2_std']:.2f}" if pd.notnull(r['precio_m2_std']) else "0.00",
        f"{r['variacion_pct']:.1f}" if pd.notnull(r['variacion_pct']) else "N/A"
    ])

t = Table(data, hAlign='LEFT')
t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.grey),
    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.beige, colors.white])
]))
elements.append(t)
doc.build(elements)
print(f"Informe generado: {pdf_path}")