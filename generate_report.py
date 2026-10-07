#!/usr/bin/env python3
import pandas as pd
from fpdf import FPDF
from pathlib import Path

def load_data():
    try:
        df = pd.read_json('output/leads.json', orient='records')
        return df
    except FileNotFoundError:
        raise FileNotFoundError("El archivo output/leads.json no existe. Ejecutá el scraper primero.")

def enrich_dataframe(df):
    """Prepara el DataFrame con las columnas necesarias y calcula precio_m2."""
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df['precio_m2'] = df['precio'] / df['superficie']
    return df

def calculate_metrics(df):
    """Calcula métricas clave por zona."""
    df['mes'] = df['fecha'].dt.to_period('M')
    
    # Agrupar por zona y mes para calcular variación mensual
    df['variacion'] = df.groupby(['zona', 'mes'])['precio_m2'].pct_change().fillna(0) * 100
    
    # Obtener la última variación mensual por zona
    df_mensual = df.groupby(['zona', 'mes'])['precio_m2'].last().unstack(fill_value=0)
    
    # Calcular métricas por zona
    report = df.groupby('zona').agg(
        precio_promedio_m2=('precio_m2', 'mean'),
        stock=('id', 'count')
    ).reset_index()
    
    # Asignar la última variación mensual a cada zona
    for zona in report['zona']:
        report.loc[report['zona'] == zona, 'variacion'] = df_mensual.loc[zona, df_mensual.columns[-1]]
    
    return report

def generate_pdf(report):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(200, 10, txt="INFORME DE MERCADO INMOBILIARIO", ln=1, align="C")

    for _, row in report.iterrows():
        pdf.cell(200, 10, txt=f"\nZona: {row['zona']}", ln=1)
        pdf.cell(200, 10, txt=f"Precio promedio m²: ${row['precio_promedio_m2']:.2f}", ln=1)
        pdf.cell(200, 10, txt=f"Stock disponible: {row['stock']} unidades", ln=1)
        pdf.cell(200, 10, txt=f"Variación mensual: {row['variacion']:.1f}%", ln=1)

    pdf.output("report/informe_mercado.pdf")

def main():
    try:
        df = load_data()
        df = enrich_dataframe(df)
        report = calculate_metrics(df)
        generate_pdf(report)
        print("PDF generado en: report/informe_mercado.pdf")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()