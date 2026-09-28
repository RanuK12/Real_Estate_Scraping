#!/usr/bin/env python3
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd

def generate_report(data_path, output_pdf):
    # Leer datos
    df = pd.read_csv(data_path)
    
    # Limpiar la columna price_per_m2: eliminar '$' y ',' y convertir a float
    df['price_per_m2_clean'] = df['price_per_m2'].replace('[\$,]', '', regex=True).astype(float)
    
    # Agrupar por zona y calcular métricas
    grouped = df.groupby('location').agg({
        'price_per_m2_clean': 'mean',
        'title': 'count'  # Contar propiedades como stock
    }).rename(columns={'title': 'stock', 'price_per_m2_clean': 'avg_price_per_m2'})
    
    # Preparar datos para el informe
    data = []
    for location, row in grouped.iterrows():
        data.append([
            location,
            f"${row['avg_price_per_m2']:.2f}",
            row['stock']
        ])
    
    # Estilos para el PDF
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    
    # Crear el PDF
    doc = SimpleDocTemplate(output_pdf, pagesize=letter)
    elements = []
    
    # Título
    title = Paragraph("Informe de Mercado Inmobiliario", title_style)
    elements.append(title)
    
    # Tabla de datos
    table_data = [
        ['Zona', 'Precio Medio por m²', 'Stock de Propiedades']
    ]
    
    for row in data:
        table_data.append(row)
    
    table = Table(table_data)
    table.setStyle(table_style)
    elements.append(table)
    
    # Guardar el PDF
    doc.build(elements)

if __name__ == "__main__":
    generate_report(
        data_path="data/sample_properties.csv",
        output_pdf="reports/informe_market_20260928.pdf"
    )
    print("Informe generado: reports/informe_market_20260928.pdf")