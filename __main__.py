#!/usr/bin/env python3
import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from report import load_data, generate_market_report

def main():
    parser = argparse.ArgumentParser(description='Genera informe de mercado inmobiliario por zona en PDF')
    parser.add_argument('--zona', required=True, help='Zona a analizar (ej: Centro, Norte, Sur, Este)')
    parser.add_argument('--output', required=True, help='Ruta del archivo PDF de salida')
    args = parser.parse_args()

    json_path = os.path.join(os.path.dirname(__file__), 'data', 'market_data.json')
    if not os.path.exists(json_path):
        print(f"Error: No se encontró el archivo de datos en {json_path}", file=sys.stderr)
        sys.exit(1)

    try:
        df = load_data(json_path)
        generate_market_report(df, args.zona, args.output)
        print(f"Informe generado exitosamente: {args.output}")
    except Exception as e:
        print(f"Error al generar el informe: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()