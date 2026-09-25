import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"   # carpeta donde el scraper guarda CSV/JSON
OUT_DIR  = Path(__file__).parent / "output"
OUT_DIR.mkdir(exist_ok=True)

def load_data(zone: str) -> pd.DataFrame:
    # Asume archivos <zone>.csv con columnas del scraper real
    file = DATA_DIR / f"{zone}.csv"
    if not file.exists():
        # Si no existe archivo por zona, usar sample_properties.csv
        file = DATA_DIR / "sample_properties.csv"
        if not file.exists():
            raise FileNotFoundError(f"Datos no encontrados para zona {zone}")
    df = pd.read_csv(file, parse_dates=["scraped_at"])
    # Normalizar columnas
    df = df.rename(columns={
        "price_per_m2": "price_m2",
        "scraped_at": "date",
        "url": "listing_id"
    })
    # Limpiar price_m2 (quitar $ y comas)
    df["price_m2"] = df["price_m2"].astype(str).str.replace(r"[$,]", "", regex=True).astype(float)
    return df

def summary_stats(df: pd.DataFrame) -> dict:
    latest = df.groupby('date').price_m2.mean().sort_index()
    price_now = latest.iloc[-1]
    price_prev = latest.iloc[-2] if len(latest) > 1 else price_now
    variation = (price_now - price_prev) / price_prev * 100 if price_prev else 0
    stock = df.listing_id.nunique()
    return {"price_now": price_now, "variation": variation, "stock": stock, "trend": latest}

def plot_trend(trend: pd.Series, zone: str) -> Path:
    plt.figure(figsize=(6,3))
    sns.lineplot(x=trend.index, y=trend.values)
    plt.title(f"Evolucion precio m2 - {zone}")
    plt.ylabel("Precio EUR/m2")
    plt.xlabel("Fecha")
    img_path = OUT_DIR / f"trend_{zone}.png"
    plt.tight_layout()
    plt.savefig(img_path, dpi=150)
    plt.close()
    return img_path

class PDFReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, self.title, ln=1, align="C")
        self.ln(5)

def build_pdf(zone: str, stats: dict, img_path: Path) -> Path:
    pdf = PDFReport()
    pdf.title = f"Informe de mercado - {zone}"
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, f"Precio medio m2: EUR{stats['price_now']:.2f}", ln=1)
    pdf.cell(0, 10, f"Variacion mensual: {stats['variation']:.2f} %", ln=1)
    pdf.cell(0, 10, f"Stock de inmuebles: {stats['stock']}", ln=1)
    pdf.ln(5)
    pdf.image(str(img_path), w=180)
    out_file = OUT_DIR / f"Informe_{zone}.pdf"
    pdf.output(str(out_file))
    return out_file

def generate_report(zone: str) -> Path:
    df = load_data(zone)
    stats = summary_stats(df)
    img = plot_trend(stats["trend"], zone)
    return build_pdf(zone, stats, img)

if __name__ == "__main__":
    import argparse, sys
    parser = argparse.ArgumentParser(description="Genera PDF de mercado por zona")
    parser.add_argument("--zone", required=True, help="Nombre de la zona (coincide con archivo CSV)")
    args = parser.parse_args()
    try:
        pdf_path = generate_report(args.zone)
        print(f"PDF generado: {pdf_path}")
    except Exception as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)