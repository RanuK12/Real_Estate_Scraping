#!/usr/bin/env python3
import argparse
from report_generator import generate_report

def main():
    parser = argparse.ArgumentParser(description="Genera informe PDF de mercado inmobiliario")
    parser.add_argument("--zone", required=True, help="Nombre de la zona (coincide con archivo CSV en data/)")
    args = parser.parse_args()
    pdf_path = generate_report(args.zone)
    print(f"PDF generado: {pdf_path}")

if __name__ == "__main__":
    main()