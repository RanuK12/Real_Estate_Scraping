import pandas as pd
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

def generate_report():
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    if not csv_files:
        print("No CSV files found in data directory")
        return
    
    # Load the most recent CSV
    latest_csv = max(csv_files, key=lambda f: os.path.getmtime(os.path.join(data_dir, f)))
    df = pd.read_csv(os.path.join(data_dir, latest_csv))
    
    print(f"Loaded {len(df)} properties from {latest_csv}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Clean price column (remove $ and commas)
    df['price_clean'] = df['price'].str.replace('$', '').str.replace(',', '').astype(float)
    df['price_per_m2_clean'] = df['price_per_m2'].astype(float)
    df['m2_clean'] = df['m2'].astype(float)
    
    # Group by location
    grouped = df.groupby('location').agg(
        count=('title', 'count'),
        avg_price=('price_clean', 'mean'),
        avg_price_per_m2=('price_per_m2_clean', 'mean'),
        avg_m2=('m2_clean', 'mean'),
        min_price=('price_clean', 'min'),
        max_price=('price_clean', 'max')
    ).reset_index()
    
    # Round for readability
    grouped['avg_price'] = grouped['avg_price'].round(0)
    grouped['avg_price_per_m2'] = grouped['avg_price_per_m2'].round(0)
    grouped['avg_m2'] = grouped['avg_m2'].round(1)
    grouped['min_price'] = grouped['min_price'].round(0)
    grouped['max_price'] = grouped['max_price'].round(0)
    
    # Create PDF
    output_path = os.path.join(data_dir, 'market_report.pdf')
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title = Paragraph("Informe de Mercado Inmobiliario", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Subtitle
    subtitle = Paragraph(f"Generado el {pd.Timestamp.now().strftime('%d/%m/%Y')} | Datos de {latest_csv}", styles['Normal'])
    story.append(subtitle)
    story.append(Spacer(1, 24))
    
    # Summary
    total_props = len(df)
    avg_price_m2 = df['price_per_m2_clean'].mean()
    summary_text = f"Total de propiedades analizadas: {total_props}<br/>Precio promedio por m²: ${avg_price_m2:,.0f}"
    summary = Paragraph(summary_text, styles['Normal'])
    story.append(summary)
    story.append(Spacer(1, 24))
    
    # Table data
    table_data = [['Zona', 'Avisos', 'Precio Prom.', 'Precio/m² Prom.', 'm² Prom.', 'Precio Mín.', 'Precio Máx.']]
    for _, row in grouped.iterrows():
        table_data.append([
            row['location'],
            str(int(row['count'])),
            f"${row['avg_price']:,.0f}",
            f"${row['avg_price_per_m2']:,.0f}",
            f"{row['avg_m2']}",
            f"${row['min_price']:,.0f}",
            f"${row['max_price']:,.0f}"
        ])
    
    table = Table(table_data, colWidths=[2.5*cm, 1.2*cm, 2.2*cm, 2.2*cm, 1.8*cm, 2.2*cm, 2.2*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4DA6FF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
    ]))
    story.append(table)
    story.append(Spacer(1, 24))
    
    # Note about variation
    note = Paragraph("<b>Nota sobre variación:</b> No hay datos históricos disponibles para calcular variación temporal. Se recomienda ejecutar el scraper periódicamente para generar series temporales.", styles['Normal'])
    story.append(note)
    
    doc.build(story)
    print(f"PDF generado: {output_path}")

if __name__ == '__main__':
    generate_report()
