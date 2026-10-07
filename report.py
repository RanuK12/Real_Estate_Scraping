import json
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import os
from datetime import datetime

def load_data(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    # calcular precio por m2
    df['precio_m2'] = df['precio'] / df['superficie']
    # convertir fecha a datetime
    df['fecha'] = pd.to_datetime(df['fecha'])
    return df

def generate_market_report(df, zona, out_path):
    # filtrar por zona
    df_zona = df[df['zona'] == zona].copy()
    if df_zona.empty:
        raise ValueError(f"No data for zona: {zona}")
    
    # asegurar orden cronologico
    df_zona = df_zona.sort_values('fecha')
    
    # obtener ultimo mes y penultimo mes
    df_zona['year_month'] = df_zona['fecha'].dt.to_period('M')
    monthly = df_zona.groupby('year_month').agg(
        avg_price_m2=('precio_m2', 'mean'),
        count=('precio_m2', 'size')
    ).reset_index()
    monthly['year_month_str'] = monthly['year_month'].astype(str)
    
    if len(monthly) < 2:
        # si solo hay un mes, variacion = 0
        variacion = 0.0
        latest = monthly.iloc[-1]
        prev_avg = latest['avg_price_m2']
    else:
        latest = monthly.iloc[-1]
        prev = monthly.iloc[-2]
        variacion = ((latest['avg_price_m2'] - prev['avg_price_m2']) / prev['avg_price_m2']) * 100
    
    precio_m2_medio = latest['avg_price_m2']
    stock = int(latest['count'])
    
    # crear PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(0, 10, txt=f"Informe de Mercado - Zona: {zona}", ln=1, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=f"Fecha del reporte: {datetime.now().strftime('%Y-%m-%d')}", ln=1)
    pdf.ln(5)
    
    # tabla de resultados
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(60, 10, txt="Metrico", border=1)
    pdf.cell(60, 10, txt="Valor", border=1)
    pdf.ln()
    
    pdf.set_font("Arial", size=12)
    pdf.cell(60, 10, txt="Precio medio por m2", border=1)
    pdf.cell(60, 10, txt=f"${precio_m2_medio:,.2f}", border=1)
    pdf.ln()
    pdf.cell(60, 10, txt="Stock (propiedades ultimo mes)", border=1)
    pdf.cell(60, 10, txt=f"{stock}", border=1)
    pdf.ln()
    pdf.cell(60, 10, txt="Variacion % vs mes anterior", border=1)
    pdf.cell(60, 10, txt=f"{variacion:+.2f}%", border=1)
    pdf.ln(10)
    
    # grafico de barras: precio medio por m2 por mes (ultimos 6 meses)
    plt.figure(figsize=(6,4))
    # usar últimos 6 meses si existen
    plot_monthly = monthly.tail(6).copy()
    plot_monthly['mes_str'] = plot_monthly['year_month_str']
    plt.bar(plot_monthly['mes_str'], plot_monthly['avg_price_m2'], color='skyblue')
    plt.title(f'Precio medio por m2 por mes - {zona}')
    plt.ylabel('Precio medio ($/m2)')
    plt.xlabel('Mes')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # guardar grafico temporalmente
    img_path = '/tmp/price_trend.png'
    plt.savefig(img_path)
    plt.close()
    
    # insertar imagen en PDF
    pdf.image(img_path, x=10, w=190)
    pdf.ln(5)
    
    # guardar PDF
    pdf.output(out_path)
    
    # limpiar imagen temporal
    try:
        os.remove(img_path)
    except:
        pass
    
    return out_path

if __name__ == "__main__":
    # para permitir ejecucion directa (aunque se usa __main__.py)
    pass