# Real Estate Scraping

Proyecto de scraping inmobiliario para generación de leads y análisis de mercado.

## Características

- Scraper automatizado de propiedades inmobiliarias
- Generación de leads con verificación de dominio y correo
- Análisis de mercado por zona con informe PDF

## Entregables

### 1. Informe de Mercado (PDF)

Genera un informe mensual con datos reales del scraper:
- Precio promedio m² por zona
- Stock total de propiedades
- Variación porcentual respecto al período anterior
- Gráfico de evolución de precios

**Metodología:**
- Datos obtenidos del scraper en `data/sample_properties.csv`
- Cálculo de precios promedio por zona agrupando propiedades similares
- Variación calculada comparando con datos históricos de `data/market_data.json`
- Gráfico generado con matplotlib mostrando evolución mensual

**Ejecutar:**
```bash
python generate_market_report.py
```

**Salida:** `reports/market_report.pdf`

### 2. Datos del Scraper

- Datos de propiedades: `data/sample_properties.csv`
- Datos históricos de mercado: `data/market_data.json`

## Requisitos

- Python 3.8+
- Dependencias: `pip install -r requirements.txt`

## Estructura del Proyecto

```
real_estate_scraping/
├── data/                 # Datos del scraper
├── reports/              # Informes generados
├── generate_market_report.py  # Script de generación de informe
├── report.py            # Script principal del scraper
└── README.md            # Este archivo
```