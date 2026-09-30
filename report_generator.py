import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import os
from datetime import datetime

# Ensure output directory exists
os.makedirs('output', exist_ok=True)

# Load data
csv_path = 'data/sample_properties.csv'
df = pd.read_csv(csv_path)

# Clean price_per_m2: remove $ and commas, convert to float
df['price_per_m2'] = df['price_per_m2'].replace({'\\$': '', ',': ''}, regex=True).astype(float)

# Also clean price and m2 for potential use
df['price'] = df['price'].replace({'\\$': '', ',': ''}, regex=True).astype(float)
df['m2'] = pd.to_numeric(df['m2'], errors='coerce')

# Convert scraped_at to datetime
df['scraped_at'] = pd.to_datetime(df['scraped_at'])
df['year_month'] = df['scraped_at'].dt.to_period('M')

# Group by location (zone) for the latest month
latest_month = df['year_month'].max()
df_latest = df[df['year_month'] == latest_month]

# Group by location
grouped = df_latest.groupby('location').agg(
    avg_price_per_m2=('price_per_m2', 'mean'),
    total_properties=('price_per_m2', 'count'),
    avg_price=('price', 'mean'),
    avg_m2=('m2', 'mean')
).reset_index()

# Calculate monthly variation: compare last two months if available
# Get the last two months of data
months_sorted = sorted(df['year_month'].unique(), reverse=True)
if len(months_sorted) >= 2:
    last_two_months = months_sorted[:2]
    df_recent = df[df['year_month'].isin(last_two_months)]
    # Group by location and month
    monthly_avg = df_recent.groupby(['location', 'year_month'])['price_per_m2'].mean().reset_index()
    # Pivot to have months as columns
    monthly_pivot = monthly_avg.pivot(index='location', columns='year_month', values='price_per_m2')
    # Calculate percentage change: (most recent - previous) / previous * 100
    monthly_pivot.columns = [str(col) for col in monthly_pivot.columns]
    if len(monthly_pivot.columns) >= 2:
        col_recent = monthly_pivot.columns[0]
        col_previous = monthly_pivot.columns[1]
        monthly_pivot['variation_pct'] = (
            (monthly_pivot[col_recent] - monthly_pivot[col_previous]) / monthly_pivot[col_previous] * 100
        )
        # Merge variation into grouped
        grouped = grouped.merge(
            monthly_pivot[['variation_pct']].reset_index(),
            on='location',
            how='left'
        )
    else:
        grouped['variation_pct'] = None
else:
    grouped['variation_pct'] = None

# Create visualizations
sns.set_style("whitegrid")
plt.figure(figsize=(10, 6))
# Bar chart for average price per m2 by location
ax = sns.barplot(data=grouped, x='location', y='avg_price_per_m2', palette='viridis')
plt.title('Average Price per m2 by Location (Latest Month)')
plt.xticks(rotation=45)
plt.tight_layout()
price_chart_path = '/tmp/price_per_m2_by_location.png'
plt.savefig(price_chart_path)
plt.close()

# Pie chart for stock distribution
plt.figure(figsize=(8, 8))
plt.pie(grouped['total_properties'], labels=grouped['location'], autopct='%1.1f%%', startangle=90, colors=sns.color_palette('pastel'))
plt.title('Property Stock Distribution by Location')
plt.tight_layout()
stock_chart_path = '/tmp/stock_distribution.png'
plt.savefig(stock_chart_path)
plt.close()

# Create PDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", 'B', 16)
pdf.cell(0, 10, 'Real Estate Market Report', ln=True, align='C')
pdf.set_font("Arial", '', 12)
pdf.cell(0, 10, f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
pdf.ln(10)

# Add table
pdf.set_font("Arial", 'B', 12)
col_widths = [30, 40, 40, 40, 40, 40]
headers = ['Location', 'Avg Price/m2', 'Total Properties', 'Avg Price', 'Avg m2', 'Monthly Variation (%)']
for i, header in enumerate(headers):
    pdf.cell(col_widths[i], 10, header, border=1, align='C')
pdf.ln()

pdf.set_font("Arial", '', 10)
for _, row in grouped.iterrows():
    pdf.cell(col_widths[0], 10, str(row['location']), border=1)
    pdf.cell(col_widths[1], 10, f"{row['avg_price_per_m2']:.2f}", border=1)
    pdf.cell(col_widths[2], 10, str(int(row['total_properties'])), border=1)
    pdf.cell(col_widths[3], 10, f"{row['avg_price']:.2f}", border=1)
    pdf.cell(col_widths[4], 10, f"{row['avg_m2']:.2f}", border=1)
    variation = row['variation_pct']
    if pd.isna(variation):
        variation_str = "N/A"
    else:
        variation_str = f"{variation:.2f}%"
    pdf.cell(col_widths[5], 10, variation_str, border=1)
    pdf.ln()

pdf.ln(10)

# Add charts
pdf.image(price_chart_path, x=10, w=180)
pdf.add_page()
pdf.image(stock_chart_path, x=10, w=180)

# Output PDF
output_path = f"output/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
pdf.output(output_path)
print(f"Report generated: {output_path}")