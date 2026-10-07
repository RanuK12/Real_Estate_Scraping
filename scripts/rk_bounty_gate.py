#!/usr/bin/env python3
import json
import subprocess
import sys
import os

def revisar(ctx):
    # Verificar que el script existe y es ejecutable
    if not os.path.exists('generate_report.py'):
        print("ERROR: El script generate_report.py no existe.")
        sys.exit(1)
    
    # Verificar que el archivo PDF generado existe
    if not os.path.exists('report/informe_mercado.pdf'):
        print("ERROR: El archivo PDF de informe no existe.")
        sys.exit(1)
    
    # Verificar que el Makefile está presente
    if not os.path.exists('Makefile'):
        print("ERROR: El archivo Makefile no existe.")
        sys.exit(1)
    
    # Verificar que el repositorio está actualizado
    try:
        subprocess.run(['git', 'fetch', 'origin'], check=True, capture_output=True)
        subprocess.run(['git', 'merge', '--ff-only', 'origin/main'], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: El repositorio no está actualizado: {e}")
        sys.exit(1)
    
    print("Portón revisado con éxito.")
    sys.exit(0)

if __name__ == "__main__":
    ctx = {
        'changes': {
            'added_files': ['generate_report.py', 'report/informe_mercado.pdf'],
            'modified_files': ['Makefile']
        }
    }
    revisar(ctx)