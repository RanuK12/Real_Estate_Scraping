#!/usr/bin/env python3
import json, os, sys
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict
from datetime import datetime
import pandas as pd

data_path = os.path.expanduser("~/.ranukita/projects/real_estate_scraping/data/market_data.json")
out_path = os.path.expanduser("~/.ranukita/projects/real_estate_scraping/reports/market_report.pdf")
chart_path = os.path.expanduser("~/.ranukita/projects/real_estate_scraping/reports/chart.png")
reports_dir = os.path.dirname(out_path)
os.makedirs(reports_dir, exist_ok=True)


def load_data():
    try:
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"El archivo de datos no existe: {data_path}")
        with open(data_path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("Los datos deben ser una lista de registros")
        return data
    except Exception as e:
        print(f"Error al cargar datos: {e}")
        return []


def aggregate(records):
    # Group by zone and then by month (we have dates like 2026-01-15)
    zone_data = defaultdict(list)  # zone -> list of (date, price_m2)
    property_types = defaultdict(int)
    rooms_data = defaultdict(list)
    
    for r in records:
        z = r.get("zona")
        if not z:
            continue
        precio = r.get("precio")
        superficie = r.get("superficie")
        habitaciones = r.get("habitaciones")
        tipo = r.get("tipo", "Desconocido")
        
        property_types[tipo] += 1
        
        if precio is not None and superficie and superficie > 0:
            price_m2 = precio / superficie
            fecha_str = r.get("fecha")
            try:
                date = datetime.strptime(fecha_str, "%Y-%m-%d")
            except:
                continue
            zone_data[z].append((date, price_m2))
            
            if habitaciones and habitaciones > 0:
                rooms_data[z].append(habitaciones)
    
    # Calculate additional metrics
    total_properties = len(records)
    total_zones = len(zone_data)
    avg_price_total = sum(sum([price_m2 for _, price_m2 in entries]) / len(entries) for entries in zone_data.values()) / len(zone_data) if zone_data else 0
    
    # Generate executive summary
    summary = {
        "total_properties": total_properties,
        "total_zones": total_zones,
        "avg_price_m2": avg_price_total,
        "property_types": dict(property_types),
        "most_expensive_zone": None,
        "most_affordable_zone": None
    }
    
    # Find most expensive and affordable zones
    zone_avg_prices = {}
    for zone, entries in zone_data.items():
        avg_price = sum([price_m2 for _, price_m2 in entries]) / len(entries)
        zone_avg_prices[zone] = avg_price
    
    if zone_avg_prices:
        summary["most_expensive_zone"] = max(zone_avg_prices.items(), key=lambda x: x[1])
        summary["most_affordable_zone"] = min(zone_avg_prices.items(), key=lambda x: x[1])
    
    # For each zone, sort by date, compute average price per m2 per month? 
    # We'll compute the average price per m2 for the first and last month to get variation.
    rows = []
    zone_rooms_avg = {}
    
    for zone, entries in zone_data.items():
        if not entries:
            continue
        entries.sort(key=lambda x: x[0])
        # Group by month (year-month) to get monthly average
        monthly = defaultdict(list)
        for date, price_m2 in entries:
            key = date.strftime("%Y-%m")
            monthly[key].append(price_m2)
        # Compute average per month
        months_sorted = sorted(monthly.keys())
        avg_per_month = [sum(monthly[m])/len(monthly[m]) for m in months_sorted]
        # Overall average price m2 (for the period)
        avg_price_m2 = sum(avg_per_month)/len(avg_per_month) if avg_per_month else 0
        # Stock: total number of properties in the zone
        stock = len(entries)
        # Variation % from first to last month
        if len(avg_per_month) >= 2:
            first = avg_per_month[0]
            last = avg_per_month[-1]
            variation = ((last - first) / first) * 100 if first != 0 else 0
        else:
            variation = 0
        # Average rooms per property in this zone
        avg_rooms = sum(rooms_data[zone])/len(rooms_data[zone]) if rooms_data[zone] else 0
        zone_rooms_avg[zone] = avg_rooms
        
        rows.append([zone, f"${avg_price_m2:.2f}", stock, f"{variation:.1f}%", f"{avg_rooms:.1f}"])
        # Store for chart: we need to return also the monthly data for plotting
        # We'll return a dict with zone -> (months_sorted, avg_per_month)
    # We'll return rows and also the chart data
    chart_data = {}
    for zone, entries in zone_data.items():
        entries.sort(key=lambda x: x[0])
        monthly = defaultdict(list)
        for date, price_m2 in entries:
            key = date.strftime("%Y-%m")
            monthly[key].append(price_m2)
        months_sorted = sorted(monthly.keys())
        avg_per_month = [sum(monthly[m])/len(monthly[m]) for m in months_sorted]
        chart_data[zone] = (months_sorted, avg_per_month)
    
    return rows, chart_data, summary, zone_rooms_avg


def build_pdf(rows, chart_data, summary, zone_rooms_avg):
    doc = SimpleDocTemplate(out_path, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.darkblue,
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    
    # Executive Summary Section
    elems = [Paragraph("Informe de Mercado Inmobiliario", title_style), Spacer(1, 20)]
    elems.append(Paragraph("Resumen Ejecutivo", heading_style))
    
    summary_text = f"""
    <b>Total de Propiedades Analizadas:</b> {summary['total_properties']}<br/>
    <b>Zonas Monitoreadas:</b> {summary['total_zones']}<br/>
    <b>Precio Promedio m²:</b> ${summary['avg_price_m2']:.2f}<br/>
    <b>Zona Más Cara:</b> {summary['most_expensive_zone'][0]} (${summary['most_expensive_zone'][1]:.2f}/m²)<br/>
    <b>Zona Más Accesible:</b> {summary['most_affordable_zone'][0]} (${summary['most_affordable_zone'][1]:.2f}/m²)
    """
    elems.append(Paragraph(summary_text, styles['Normal']))
    elems.append(Spacer(1, 20))
    
    # Property Types Distribution
    elems.append(Paragraph("Distribución por Tipo de Propiedad", heading_style))
    property_types_text = "<b>Propiedades por tipo:</b><br/>"
    for prop_type, count in summary['property_types'].items():
        percentage = (count / summary['total_properties']) * 100
        property_types_text += f"• {prop_type}: {count} ({percentage:.1f}%)<br/>"
    elems.append(Paragraph(property_types_text, styles['Normal']))
    elems.append(Spacer(1, 20))
    
    # Detailed Table
    elems.append(Paragraph("Análisis Detallado por Zona", heading_style))
    data = [["Zona", "Precio m² (USD)", "Stock", "Variación %", "Habitaciones Promedio"]] + rows
    t = Table(data, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), 'CENTER'),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elems.append(t)
    elems.append(Spacer(1, 20))
    
    # Chart
    if chart_data:
        plt.figure(figsize=(10, 6), dpi=100)
        for zone, (months, avgs) in chart_data.items():
            plt.plot(months, avgs, marker='o', linewidth=2, markersize=6, label=zone)
        plt.title("Evolución del Precio m² Promedio por Zona", fontsize=14, fontweight='bold')
        plt.xlabel("Mes", fontsize=12)
        plt.ylabel("Precio m² (USD)", fontsize=12)
        plt.xticks(rotation=45, fontsize=10)
        plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(chart_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        if os.path.exists(chart_path):
            elems.append(Paragraph("Gráfico de Evolución de Precios", heading_style))
            elems.append(Spacer(1, 6))
            # Limit image width to page width
            img = Image(chart_path, width=6*inch, height=3.6*inch)
            elems.append(img)
    
    # Footer
    elems.append(Spacer(1, 20))
    footer_text = f"Generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Ranuk IT Solutions"
    elems.append(Paragraph(footer_text, styles['Normal']))
    
    doc.build(elems)


if __name__ == "__main__":
    try:
        recs = load_data()
        if not recs:
            print("No se encontraron datos para generar el reporte")
            sys.exit(1)
            
        rows, chart_data, summary, zone_rooms_avg = aggregate(recs)
        build_pdf(rows, chart_data, summary, zone_rooms_avg)
        print(f"Reporte generado: {out_path}")
        print(f"Total propiedades: {summary['total_properties']}")
        print(f"Zonas analizadas: {summary['total_zones']}")
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)