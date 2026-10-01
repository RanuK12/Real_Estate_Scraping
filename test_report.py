import pandas as pd
import sys
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import matplotlib.pyplot as plt

# Cargar datos
path = '/Users/emilioranucoli/.ranukita/projects/real_estate_scraping/data/market_data.json'
df = pd.read_json(path)

# Calcular métricas
if not df.empty:
    df['price_per_m2'] = df['precio'] / df['superficie']
    df['price_per_m2'] = pd.to_numeric(df['price_per_m2'], errors='coerce')
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    
    # Agrupar por zona y calcular métricas
    zone_stats = {}
    for zona, group in df.groupby('zona'):
        stock = len(group)
        avg_price = group['price_per_m2'].mean()
        std_price = group['price_per_m2'].std()
        
        # Calcular variación de precios si hay al menos 2 fechas distintas
        variation = None
        if len(group) >= 2:
            dates = sorted(group['fecha'].dt.date.unique())
            if len(dates) >= 2:
                first_date = dates[0]
                second_date = dates[1]
                
                first_price = group[group['fecha'].dt.date == first_date]['price_per_m2'].mean()
                second_price = group[group['fecha'].dt.date == second_date]['price_per_m2'].mean()
                
                if pd.notna(first_price) and pd.notna(second_price):
                    variation = ((second_price - first_price) / first_price) * 100
        
        zone_stats[zona] = {
            'stock': int(stock),
            'avg_price_per_m2': float(avg_price) if pd.notna(avg_price) else None,
            'std_price_per_m2': float(std_price) if pd.notna(std_price) else None,
            'variation_pct': float(variation) if variation is not None else None
        }
    
    # Generar PDF
    doc = SimpleDocTemplate('/Users/emilioranucoli/.ranukita/projects/real_estate_scraping/report_test.pdf', pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Estilo para títulos
    title_style = ParagraphStyle(name='Title', fontSize=18, leading=22, spaceAfter=12, alignment=TA_CENTER, textColor=colors.Color(0.26, 0.69, 1.0))
    subtitle_style = ParagraphStyle(name='Subtitle', fontSize=14, leading=18, textColor=colors.Color(0.26, 0.69, 1.0))
    
    story = []
    story.append(Paragraph("Informe de Mercado Inmobiliario", title_style))
    story.append(Paragraph("Resumen Ejecutivo", subtitle_style))
    story.append(Paragraph("Este informe presenta un análisis detallado del mercado inmobiliario en las zonas seleccionadas.", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Tabla de datos
    table_data = [
        ['Zona', 'Precio Medio por m²', 'Stock de Propiedades', 'Variación (%)', 'Desviación Estándar']
    ]
    
    for zona, stats in zone_stats.items():
        avg_price = stats['avg_price_per_m2']
        variation = stats['variation_pct']
        std_price = stats['std_price_per_m2']
        
        table_data.append([
            zona,
            f"${avg_price:.2f}" if avg_price is not None else "N/A",
            stats['stock'],
            f"{variation:.1f}%" if variation is not None else "N/A",
            f"${std_price:.2f}" if std_price is not None else "N/A"
        ])
    
    table = Table(table_data)
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.8, 0.8, 0.8)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    table.setStyle(table_style)
    story.append(table)
    
    doc.build(story)
    print("PDF generado con éxito en /Users/emilioranucoli/.ranukita/projects/real_estate_scraping/report_test.pdf")
else:
    print("No hay datos disponibles para generar el informe.")