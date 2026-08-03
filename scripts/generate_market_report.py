#!/usr/bin/env python3
"""
Generador de informes de mercado inmobiliario.

Lee datos del scraper y genera un PDF con análisis por zona:
- Precio promedio por m2
- Cantidad de propiedades (stock)
- Variación porcentual (si hay histórico)
"""

import pandas as pd
import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.colors import black, blue, gray
from reportlab.lib import colors
import glob


def find_latest_data_file(data_dir="data"):
    """Encuentra el archivo CSV o JSON más reciente en el directorio."""
    csv_files = glob.glob(os.path.join(data_dir, "properties_*.csv"))
    json_files = glob.glob(os.path.join(data_dir, "properties_*.json"))
    
    all_files = csv_files + json_files
    if not all_files:
        raise FileNotFoundError(f"No se encontraron archivos de datos en {data_dir}")
    
    # Ordenar por fecha de modificación y tomar el más reciente
    latest_file = max(all_files, key=os.path.getmtime)
    return latest_file


def load_data(filepath):
    """Carga datos desde CSV o JSON."""
    if filepath.endswith('.csv'):
        return pd.read_csv(filepath)
    elif filepath.endswith('.json'):
        with open(filepath, 'r', encoding='utf-8') as f:
            return pd.DataFrame(json.load(f))
    else:
        raise ValueError("Formato de archivo no soportado. Use CSV o JSON.")


def analyze_market_data(df):
    """Analiza los datos y devuelve métricas por zona."""
    # Asegurarse de que las columnas necesarias existen
    required_columns = ['price', 'price_per_m2', 'm2', 'location']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Columna requerida '{col}' no encontrada en los datos")
    
    # Limpiar datos - convertir precios a numéricos
    df['price'] = pd.to_numeric(df['price'].replace('[\$,]', '', regex=True), errors='coerce')
    df['price_per_m2'] = pd.to_numeric(df['price_per_m2'].replace('[\$,]', '', regex=True), errors='coerce')
    
    # Agrupar por zona
    zone_stats = df.groupby('location').agg({
        'price': 'mean',
        'price_per_m2': 'mean',
        'm2': 'mean',
        'title': 'count'  # Cuenta de propiedades
    }).rename(columns={
        'price': 'avg_price',
        'price_per_m2': 'avg_price_per_m2',
        'm2': 'avg_size',
        'title': 'property_count'
    }).reset_index()
    
    # Ordenar por cantidad de propiedades
    zone_stats = zone_stats.sort_values('property_count', ascending=False)
    
    return zone_stats


def generate_pdf_report(data, output_path="market_report.pdf"):
    """Genera un PDF con el análisis de mercado."""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Título personalizado
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=blue,
        alignment=1  # Centrado
    )
    
    # Estilo para subtítulos
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=gray
    )
    
    # Título del reporte
    title = Paragraph("Informe de Mercado Inmobiliario", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Fecha actual
    date_str = datetime.now().strftime("%d/%m/%Y")
    date_para = Paragraph(f"Fecha: {date_str}", styles['Normal'])
    story.append(date_para)
    story.append(Spacer(1, 30))
    
    # Resumen ejecutivo
    story.append(Paragraph("Resumen Ejecutivo", subtitle_style))
    story.append(Spacer(1, 10))
    
    total_properties = data['property_count'].sum()
    avg_price_all = data['avg_price'].mean()
    
    summary_text = f"""
    Se analizaron {total_properties} propiedades en total, distribuidas en {len(data)} zonas.
    El precio promedio general es de ${avg_price_all:,.0f}.
    """
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Análisis por zona
    story.append(Paragraph("Análisis por Zona", subtitle_style))
    story.append(Spacer(1, 10))
    
    # Preparar datos para la tabla
    table_data = [['Zona', 'Propiedades', 'Precio Promedio', 'Precio/m² Promedio', 'Tamaño Promedio (m²)']]
    
    for _, row in data.iterrows():
        table_data.append([
            row['location'],
            str(row['property_count']),
            f"${row['avg_price']:,.0f}",
            f"${row['avg_price_per_m2']:,.0f}",
            f"{row['avg_size']:.1f}"
        ])
    
    # Crear tabla
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    story.append(Spacer(1, 30))
    
    # Notas
    story.append(Paragraph("Notas", subtitle_style))
    story.append(Spacer(1, 10))
    
    notes_text = """
    - Los precios están expresados en USD.
    - El análisis se basa en datos recopilados por el scraper.
    - No se incluyen variaciones porcentuales debido a la falta de histórico de datos.
    """
    story.append(Paragraph(notes_text, styles['Normal']))
    
    # Construir PDF
    doc.build(story)
    return output_path


def main():
    """Función principal."""
    try:
        # Encontrar el archivo de datos más reciente
        data_file = find_latest_data_file()
        print(f"Usando archivo de datos: {data_file}")
        
        # Cargar datos
        df = load_data(data_file)
        print(f"Cargados {len(df)} registros de datos")
        
        # Analizar datos
        market_data = analyze_market_data(df)
        print("Análisis completado")
        
        # Generar reporte
        output_file = "market_report.pdf"
        generate_pdf_report(market_data, output_file)
        print(f"Reporte generado: {output_file}")
        
        return output_file
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


if __name__ == "__main__":
    main()