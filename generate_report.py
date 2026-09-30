#!/usr/bin/env python3
"""
Genera un informe PDF de mercado inmobiliario a partir de los datos scrapeados.
Busca el CSV más reciente en el directorio data/ o usa scraped_data.csv como fallback.
"""
import pandas as pd
from fpdf import FPDF
import os
import glob
from pathlib import Path


def find_latest_csv(data_dir="data"):
    """Encuentra el CSV más reciente de propiedades en el directorio de datos."""
    # Primero buscar scraped_data.csv en raíz (fallback)
    if os.path.exists("scraped_data.csv"):
        return "scraped_data.csv"
    
    # Buscar en el directorio data/ archivos properties_*.csv
    pattern = os.path.join(data_dir, "properties_*.csv")
    files = glob.glob(pattern)
    if files:
        # El más reciente por timestamp en el nombre
        latest = max(files, key=os.path.getmtime)
        return latest
    
    return None


def generate_report(csv_path, output_pdf="market_report.pdf"):
    """Genera el informe PDF desde el CSV de propiedades."""
    if not csv_path or not os.path.exists(csv_path):
        raise FileNotFoundError(f"No se encontró archivo de datos: {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    if df.empty:
        raise ValueError("No hay datos para generar informe")
    
    # Validar columnas requeridas
    required_cols = ["price", "m2", "location"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Falta columna requerida: {col}")
    
    # Calcular precio por m2 si no existe
    if "price_per_m2" not in df.columns:
        df["price_per_m2"] = df["price"] / df["m2"]
    
    # Extraer zona del location (asumimos formato "Zona, Ciudad" o similar)
    # Si ya existe columna zone, usarla
    if "zone" not in df.columns:
        df["zone"] = df["location"].apply(lambda x: x.split(",")[0].strip() if "," in str(x) else "Desconocida")
    
    # Agrupar por zona y calcular métricas
    report = df.groupby("zone").agg({
        "price_per_m2": ["mean", "count", "std"],
        "price": ["min", "max"],
        "m2": ["mean"]
    }).round(2)
    
    # Aplanar columnas
    report.columns = ['_'.join(col).strip() for col in report.columns.values]
    report = report.rename(columns={
        'price_per_m2_mean': 'avg_price_m2',
        'price_per_m2_count': 'listings',
        'price_per_m2_std': 'std_price_m2',
        'price_min': 'min_price',
        'price_max': 'max_price',
        'm2_mean': 'avg_m2'
    })
    
    # Generar PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Informe de Mercado Inmobiliario", ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Datos fuente: {csv_path}", ln=True)
    pdf.cell(0, 6, f"Total propiedades analizadas: {len(df)}", ln=True)
    pdf.ln(5)
    
    # Tabla comparativa por zona
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Metricas por Zona", ln=True)
    pdf.ln(2)
    
    # Encabezados de tabla
    col_widths = [40, 25, 20, 25, 25, 25, 20]
    headers = ["Zona", "Avg $/m2", "Listados", "Std $/m2", "Min $", "Max $", "Avg m2"]
    
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(70, 130, 180)
    pdf.set_text_color(255, 255, 255)
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 7, header, border=1, fill=True, align="C")
    pdf.ln()
    
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(0, 0, 0)
    fill = False
    for zone, row in report.iterrows():
        if fill:
            pdf.set_fill_color(240, 240, 240)
        else:
            pdf.set_fill_color(255, 255, 255)
        
        pdf.cell(col_widths[0], 6, str(zone)[:25], border=1, fill=fill)
        pdf.cell(col_widths[1], 6, f"${row['avg_price_m2']:,.0f}", border=1, fill=fill, align="R")
        pdf.cell(col_widths[2], 6, str(int(row['listings'])), border=1, fill=fill, align="C")
        pdf.cell(col_widths[3], 6, f"${row['std_price_m2']:,.0f}", border=1, fill=fill, align="R")
        pdf.cell(col_widths[4], 6, f"${row['min_price']:,.0f}", border=1, fill=fill, align="R")
        pdf.cell(col_widths[5], 6, f"${row['max_price']:,.0f}", border=1, fill=fill, align="R")
        pdf.cell(col_widths[6], 6, f"{row['avg_m2']:.0f}", border=1, fill=fill, align="C")
        pdf.ln()
        fill = not fill
    
    pdf.ln(5)
    
    # Resumen general
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Resumen General", ln=True)
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Promedio global $/m2: ${df['price_per_m2'].mean():,.0f}", ln=True)
    pdf.cell(0, 6, f"Precio minimo: ${df['price'].min():,.0f}", ln=True)
    pdf.cell(0, 6, f"Precio maximo: ${df['price'].max():,.0f}", ln=True)
    pdf.cell(0, 6, f"Total zonas analizadas: {len(report)}", ln=True)
    
    pdf.output(output_pdf)
    print(f"📄 Informe generado en {output_pdf}")
    return output_pdf


if __name__ == "__main__":
    csv_file = find_latest_csv()
    if csv_file:
        generate_report(csv_file)
    else:
        print("❌ No se encontraron datos para generar el informe")
        exit(1)