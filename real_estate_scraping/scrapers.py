"""
Scrapers para extraer datos de propiedades inmobiliarias.
"""

import json
from typing import Dict, Any, List


def get_real_estate_data(html_content: str) -> Dict[str, Any]:
    """
    Extrae datos de propiedades desde HTML.
    
    Args:
        html_content: HTML de la página.
    
    Returns:
        dict: Datos estructurados de la propiedad.
    """
    # Placeholder: devuelve estructura vacía con key obligatoria
    return {"status": "ok", "data": []}


def get_property_details(html_content: str) -> Dict[str, Any]:
    """
    Extrae detalles específicos de una propiedad.
    
    Args:
        html_content: HTML de la página de detalles.
    
    Returns:
        dict: Detalles de la propiedad.
    """
    return {"status": "ok", "details": {}}
