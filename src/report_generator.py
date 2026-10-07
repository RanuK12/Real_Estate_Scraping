#!/usr/bin/env python3
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import argparse
import os

def generate_report(data_path, output_path):
    # Cargar datos
    with open(data_path, 'r') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    
    # Calcular precio por m2
    df['precio_m2'] = df['precio'] / df['superficie']
    
    # Agrupar por zona para tabla
    grouped = df.groupby('zona').agg({
        'precio_m2': ['mean', 'min', 'max', 'count'],
        'fecha': 'max'
    }).reset_index()
    
    # Renombrar columnas
    grouped.columns = ['zona', 'precio_m2_promedio', 'precio_m2_minimo', 'precio_m2_maximo', 'cantidad_propiedades', 'fecha_ultima_actualizacion']
    
    # Crear tabla para el PDF
    table_data = [
        ['Zona', 'Precio m2 Promedio', 'Precio m2 Mínimo', 'Precio m2 Máximo', 'Cantidad de Propiedades', 'Fecha Última Actualización']
    ]
    
    for _, row in grouped.iterrows():
        table_data.append([
            row['zona'],
            f"${row['precio_m2_promedio']:.2f}",
            f"${row['precio_m2_minimo']:.2f}",
            f"${row['precio_m2_maximo']:.2f}",
            row['cantidad_propiedades'],
            row['fecha_ultima_actualizacion']
        ])
    
    # Crear gráficos
    plt.figure(figsize=(10, 6))
    # Agrupar por zona para obtener promedio de precio_m2 para el gráfico
    df_plot = df.groupby('zona')['precio_m2'].mean().reset_index()
    sns.barplot(x='zona', y='precio_m2', data=df_plot, errorbar=None, palette='viridis')
    plt.title('Precio Promedio por m2 por Zona')
    plt.xticks(rotation=45)
    plt.ylabel('Precio por m2 ($)')
    plt.xlabel('Zona')
    plt.tight_layout()
    
    # Guardar gráficos
    chart_path = 'chart.png'
    plt.savefig(chart_path)
    plt.close()
    
    # Crear PDF
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Añadir título
    title = Paragraph("Informe de Mercado Inmobiliario", styles['Title'])
    
    # Añadir tabla
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    # Añadir gráficos
    img = Paragraph('<img src="%s" width="600" height="400" />' % chart_path, styles['Normal'])
    
    # Construir el documento
    elements = [title, Spacer(1, 12), table, Spacer(1, 24), img]
    
    doc.build(elements)
    
    # Eliminar el archivo temporal del gráfico
    os.remove(chart_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a market report from scraped data.')
    parser.add_argument('--data', required=True, help='Path to scraped data JSON file')
    parser.add_argument('--out', default='market_report.pdf', help='Output PDF file path')
    
    args = parser.parse_args()
    generate_report(args.data, args.out)
    print(f"Informe generado en {args.out}")