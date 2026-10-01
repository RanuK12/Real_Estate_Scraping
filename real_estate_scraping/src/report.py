#!/usr/bin/env python3
import pandas as pd
import os
from typing import Dict, List, Any
import numpy as np

def build_zone_stats(records: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    if not records:
        return {}
    
    df = pd.DataFrame(records)
    
    # Asegurar que 'location' exista, usando un valor por defecto
    if 'location' not in df.columns:
        df['location'] = 'Sin especificar'
    else:
        df['location'] = df['location'].fillna('Sin especificar')
    
    # Asegurar que 'title' exista para contar el stock
    if 'title' not in df.columns:
        df['title'] = ''
    else:
        df['title'] = df['title'].fillna('')
    
    # Limpiar y convertir precios
    if 'price_per_m2' not in df.columns:
        df['price_per_m2'] = None
    df['price_per_m2'] = pd.to_numeric(df['price_per_m2'].replace(r'[\$,]', '', regex=True), errors='coerce')
    
    # Convertir 'scraped_at' a datetime
    if 'scraped_at' not in df.columns:
        df['scraped_at'] = None
    df['scraped_at'] = pd.to_datetime(df['scraped_at'], errors='coerce')
    
    # Agrupar y calcular estadísticas
    grouped = df.groupby('location').agg({
        'title': 'count',
        'price_per_m2': 'mean'
    }).rename(columns={'title': 'stock', 'price_per_m2': 'avg_price_per_m2'})
    
    # Calcular variación de precios por zona
    variation_results = {}
    
    for location, group in df.groupby('location'):
        if len(group) >= 2:
            # Obtener las dos primeras fechas únicas
            dates = sorted(group['scraped_at'].dt.date.unique())
            if len(dates) >= 2:
                first_date = dates[0]
                second_date = dates[1]
                
                # Obtener precios para las dos fechas
                first_price = group[group['scraped_at'].dt.date == first_date]['price_per_m2'].mean()
                second_price = group[group['scraped_at'].dt.date == second_date]['price_per_m2'].mean()
                
                if pd.notna(first_price) and pd.notna(second_price):
                    variation = ((second_price - first_price) / first_price) * 100
                    variation_results[location] = variation
                else:
                    variation_results[location] = None
            else:
                variation_results[location] = None
        else:
            variation_results[location] = None
    
    # Convertir a diccionario con la estructura esperada
    zone_stats = {}
    for location, stats in grouped.iterrows():
        zone_stats[location] = {
            'stock': int(stats['stock']),
            'avg_price_per_m2': float(stats['avg_price_per_m2']) if pd.notna(stats['avg_price_per_m2']) else None,
            'variation_pct': variation_results.get(location, None)
        }
    return zone_stats

def load_records(data_dir: str) -> List[Dict[str, Any]]:
    records = []
    for file_path in os.listdir(data_dir):
        file = os.path.join(data_dir, file_path)
        if file_path.endswith('.csv'):
            df = pd.read_csv(file)
            for _, row in df.iterrows():
                records.append({
                    'location': row.get('location', 'Sin especificar'),
                    'price_per_m2': row.get('price_per_m2', '0'),
                    'scraped_at': row.get('scraped_at', None),
                    'title': row.get('title', '')
                })
        elif file_path.endswith('.json'):
            with open(file, 'r') as f:
                data = pd.read_json(f)
                for _, row in data.iterrows():
                    records.append({
                        'location': row.get('location', 'Sin especificar'),
                        'price_per_m2': row.get('price_per_m2', '0'),
                        'scraped_at': row.get('scraped_at', None),
                        'title': row.get('title', '')
                    })
    return records

def generate_pdf(zone_stats: Dict[str, Dict[str, Any]], output_path: str) -> str:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Título del informe
    story.append(Paragraph("Informe de Mercado Inmobiliario", styles["Title"]))
    
    # Tabla de datos
    table_data = [
        ['Zona', 'Precio Medio por m²', 'Stock de Propiedades', 'Variación (%)']
    ]
    
    for location, stats in zone_stats.items():
        avg_price = stats['avg_price_per_m2']
        variation = stats['variation_pct']
        table_data.append([
            location,
            f"${avg_price:.2f}" if avg_price is not None else "N/A",
            stats['stock'],
            f"{variation:.1f}%" if variation is not None else "N/A"
        ])
    
    table = Table(table_data)
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
    table.setStyle(table_style)
    story.append(table)
    
    doc.build(story)
    return output_path

if __name__ == "__main__":
    records = load_records("data")
    zone_stats = build_zone_stats(records)
    generate_pdf(zone_stats, "reports/informe_market_20260928.pdf")