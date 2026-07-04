# 🏡 Real Estate Scraper — Producto Digital

> **Scraper profesional de propiedades** listo para usar y personalizar. Extrae datos de Zonaprop (CABA) y MercadoLibre (Uruguay) en CSV/JSON. Incluye proxy rotation, fallback stealth (Camofox) y CLI. **Hecho por Ranuk IT Solutions**.

---

## 🎯 ¿Qué incluye?

✅ **Código completo** (Python 3.10+): Scraper robusto con rotación de proxies y fallback stealth.
✅ **Multi-fuente**: Zonaprop (Argentina) y MercadoLibre (Uruguay) ya configurados.
✅ **Exportación flexible**: CSV y JSON con campos normalizados (precio, m², ubicación, dormitorios, baños, URL, fuente, timestamp).
✅ **CLI profesional**: `real-estate-scraper --source zonaprop --zone CABA --format json --output data/`
✅ **Documentación clara**: README con instalación, ejemplos y API.
✅ **Tests unitarios**: 51 tests que cubren parsing, manejo de errores y exportación.
✅ **Personalizable**: heredá de `BaseScraper` para agregar tu propia fuente.
✅ **Stealth mode**: fallback automático a Camofox si los requests fallan.

---

## 📦 ¿Qué recibís?

- **Código fuente completo** del scraper (Python).
- **Archivos de configuración**: `pyproject.toml`, `requirements.txt`.
- **Documentación detallada**: `README.md` con ejemplos de uso.
- **Tests**: suite completa para validar el código.
- **Soporte básico**: 1 semana de ajustes menores por email (si comprás el plan Premium).

---

## 💰 Planes y precios

| Plan | Precio | Incluye |
|------|--------|---------|
| **Básico** | **$20 USD** | Código + README + 51 tests pasados |
| **Premium** | **$50 USD** | Todo lo del Básico + 1 semana de soporte para customizar el scraper (ej: agregar otro sitio) |

---

## 🚀 ¿Cómo empezar?

1. **Descargá el ZIP** después de comprar.
2. **Instalá las dependencias**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```
3. **Ejecutá el CLI**:
   ```bash
   real-estate-scraper --source zonaprop --zone CABA --format json --output data/
   ```
4. **¡Listo!** Abrí el archivo `data/zonaprop_CABA.json` para ver los resultados.

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

## 🛠️ ¿Necesitás algo más?

- **¿Querés que agregue otro sitio?** (ej: Properati, Argenprop) → Comprá el plan **Premium** y escribime por email.
- **¿Necesitás un scraper desde cero para otro país?** → Hacemos un presupuesto a medida.
- **¿Querés que lo deploye en tu servidor?** → Consultame por un fee extra.

---

## ⚙️ Requisitos técnicos

- **Python 3.10+** (recomendado 3.11).
- **pip 23+** (o Poetry).
- **Camofox** (solo para modo stealth): `pip install ".[stealth]"`.

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
