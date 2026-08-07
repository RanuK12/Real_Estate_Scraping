#!/usr/bin/env python3
"""
Report Generator for Real Estate Scraping
Generates PDF reports with market data by zone
"""

import pandas as pd
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def load_data(csv_path):
    """Load data from CSV file"""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    df = pd.read_csv(csv_path)
    return df

def process_data(df):
    """Process data to calculate statistics by zone"""
    # Calculate price per m2 if not present
    if 'price_per_m2' not in df.columns:
        df['price_per_m2'] = df['price'] / df['m2']
    
    # Group by location and calculate statistics
    # First, ensure numeric columns are properly typed
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['m2'] = pd.to_numeric(df['m2'], errors='coerce')
    
    # Group by location and calculate statistics
    stats = df.groupby('location').agg({
        'price_per_m2': 'mean',
        'title': 'count',  # Number of properties
        'price': 'mean',   # Average price
        'm2': 'mean'       # Average m2
    }).reset_index()
    
    # Rename columns
    stats.columns = ['Zona', 'Precio Promedio por m²', 'Cantidad de Avisos', 'Precio Promedio', 'Superficie Promedio']
    
    # Calculate percentage variation if historical data is available
    # This is a placeholder - in a real implementation, you'd load previous data
    # For now, we'll just add the column with NaN
    stats['Variación %'] = None
    
    return stats

def generate_pdf_report(data, output_path):
    """Generate PDF report from processed data"""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []
    
    # Title
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.darkblue,
        alignment=1  # Center alignment
    )
    story.append(Paragraph("Informe de Mercado Inmobiliario", title_style))
    story.append(Spacer(1, 12))
    
    # Subtitle with date
    date_str = datetime.now().strftime("%d/%m/%Y")
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.grey,
        alignment=1
    )
    story.append(Paragraph(f"Generado el: {date_str}", subtitle_style))
    story.append(Spacer(1, 20))
    
    # Create table
    table_data = [data.columns.tolist()] + data.values.tolist()
    
    # Style for table
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Footer note
    footer_style = ParagraphStyle(
        'CustomFooter',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        alignment=1
    )
    story.append(Paragraph("Reporte generado automáticamente por Real Estate Scraping", footer_style))
    
    doc.build(story)

def main():
    """Main function to generate report"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate real estate market report')
    parser.add_argument('--output', '-o', default='informe_zona.pdf', 
                       help='Output PDF file path')
    parser.add_argument('--input', '-i', 
                       default='../data/properties_20260803_000000.csv',
                       help='Input CSV file path')
    
    args = parser.parse_args()
    
    # Adjust default path if running from src directory
    if args.input == '../data/properties_20260803_000000.csv':
        # Try to find the CSV file in the data directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(base_dir, 'data', 'properties_20260803_000000.csv')
        if os.path.exists(csv_path):
            args.input = csv_path
    
    # Load and process data
    df = load_data(args.input)
    processed_data = process_data(df)
    
    # Generate PDF
    generate_pdf_report(processed_data, args.output)
    print(f"Report generated successfully: {args.output}")

if __name__ == "__main__":
    main()