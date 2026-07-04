# 🏡 Real Estate Scraper — Servicio en Upwork

> **Scraper profesional de propiedades** para Zonaprop (CABA) y MercadoLibre (Uruguay). Extrae datos normalizados en CSV/JSON, con proxy rotation, fallback stealth y CLI. **Hecho por Ranuk IT Solutions**.

---

## 🎯 ¿Qué incluye?

✅ **Scraper listo para usar** (Python 3.10+):
- Extrae propiedades de Zonaprop (Argentina) y MercadoLibre (Uruguay).
- Exporta a CSV y JSON con campos normalizados (precio, m², ubicación, dormitorios, baños, URL, fuente, timestamp).
- CLI profesional: `real-estate-scraper --source zonaprop --zone CABA`.

✅ **Features avanzadas**:
- **Proxy rotation**: evita bloqueos rotando proxies automáticamente.
- **Fallback stealth**: usa Camofox si los requests HTTP fallan.
- **Personalizable**: heredá de `BaseScraper` para agregar otros sitios.
- **Documentación clara**: README con instalación y ejemplos.

✅ **Tests unitarios**: 51 tests que cubren parsing, manejo de errores y exportación.

---

## 📦 ¿Qué entregás?

- **Código fuente completo** del scraper (Python).
- **Archivos de configuración**: `pyproject.toml`, `requirements.txt`.
- **Documentación detallada**: `README.md` con ejemplos de uso.
- **Tests**: suite completa para validar el código.
- **Soporte básico**: 1 semana de ajustes menores por email.

---

## ⚙️ Requisitos técnicos

- **Python 3.10+** (recomendado 3.11).
- **pip 23+** (o Poetry).
- **Camofox** (solo para modo stealth): `pip install ".[stealth]"` (opcional).

---

## 🚀 ¿Cómo empezar?

1. **Instalá las dependencias**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```
2. **Ejecutá el CLI**:
   ```bash
   real-estate-scraper --source zonaprop --zone CABA --format json --output data/
   ```
3. **¡Listo!** Los datos se guardan en `data/zonaprop_CABA.json`.

---

## 📊 Ejemplo de salida (JSON)

```json
[
  {
    "title": "PH en Palermo Hollywood",
    "price": "$50.000 USD",
    "price_per_m2": "$3.500 USD/m²",
    "m2": 142,
    "location": "Palermo, CABA, Argentina",
    "bedrooms": 3,
    "bathrooms": 2,
    "source": "zonaprop",
    "url": "https://www.zonaprop.com.ar/...",
    "scraped_at": "2026-07-04T12:14:00Z"
  }
]
```

---

## 💰 Precios

| Paquete | Precio | Incluye |
|---------|--------|---------|
| **Básico** | **$100 USD** | Código + README + 51 tests pasados |
| **Premium** | **$200 USD** | Todo lo del Básico + 1 semana de soporte para customizar el scraper (ej: agregar otro sitio) |

---

## 🛠️ ¿Necesitás algo más?

- **¿Querés que agregue otro sitio?** (ej: Properati, Argenprop) → Comprá el plan **Premium**.
- **¿Necesitás un scraper desde cero para otro país?** → Hacemos un presupuesto a medida.
- **¿Querés que lo deploye en tu servidor?** → Consultame por un fee extra.

---

## 🔒 Garantía

- **Código probado**: 51 tests unitarios que pasan.
- **Documentación clara**: README con ejemplos reales.
- **Soporte incluido**: 1 semana de ajustes por email (plan Premium).

---

## 📧 Contacto

- **Email**: ranucoliemilio@gmail.com
- **GitHub**: [RanuK12/real_estate_scraping](https://github.com/RanuK12/real_estate_scraping)
- **Web**: [ranuk.dev](https://ranuk.dev)

---

**✅ Hecho por Ranuk IT Solutions | Propiedad de Emilio Ranucoli**
> "Automatizamos lo que otros no quieren hacer"
