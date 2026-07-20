# Real‑Estate Scraping

> Scraper robusto de propiedades con rotación de proxies, fallback stealth, y soporte multi‑fuente.  
> Hecho por [Ranuk IT Solutions](https://ranuk.dev).

---

## Características

- **Multi‑fuente**: Zonaprop (CABA) y MercadoLibre (Uruguay) listos para usar.
- **Proxy rotation**: evita bloqueos rotando proxies automáticamente.
- **Stealth fallback**: cuando el request HTTP falla, usa `rk-stealth-browse` (Camofox) como plan B.
- **Exportación**: CSV y JSON con campos normalizados (title, price, price_per_m2, m2, location, bedrooms, bathrooms, source, url, scraped_at).
- **CLI**: interfaz de línea de comandos para scrapear sin escribir código.
- **Extensible**: heredá de `BaseScraper` para agregar tu propia fuente.

---

## Requisitos

- Python 3.10+
- pip 23+ (o Poetry)
- Camofox (solo para modo stealth — integración en `~/Apps/ranukita-bridge/integrations/`)

## Instalación

### macOS

```bash
brew install python@3.11
```

### Linux (Ubuntu/Debian)

```bash
sudo apt install python3.11 python3.11-venv
```

### El proyecto

```bash
# Clonar
git clone https://github.com/RanuK12/real_estate_scraping.git
cd real_estate_scraping

# Crear virtualenv y activar
python3 -m venv .venv
source .venv/bin/activate

# Instalar en modo editable (recomendado)
pip install -e .

# Con soporte stealth (Camofox)
pip install -e ".[stealth]"

# Para desarrollo (tests + reportes)
pip install -e ".[dev]"
```

## Uso CLI

```bash
# Scrapear Zonaprop CABA
real-estate-scraper --source zonaprop --zone CABA

# Scrapear MercadoLibre Uruguay
real-estate-scraper --source mercadolibre --zone Uruguay

# Exportar a JSON
real-estate-scraper --source zonaprop --export json --output-dir data/

# Con proxy propio
real-estate-scraper --source zonaprop --proxies http://user:pass@host:port

# Con timeout y retries personalizados
real-estate-scraper --source zonaprop --timeout 60 --max-retries 5 --request-delay 1.0

# Con stealth fallback
real-estate-scraper --source mercadolibre --use-stealth
```

## Uso como librería

```python
from src.scraper import RealEstateScraper

scraper = RealEstateScraper(
    use_stealth=True,          # fallback a Camofox si falla HTTP
    proxy_list=["http://..."], # proxies opcionales
)

# Scrapear propiedades
listings = scraper.scrape_real("zonaprop", zone="CABA")

# Exportar resultados
scraper.export_data(listings, "csv", "data/")
scraper.export_data(listings, "json", "data/")

# También podés scrapear una propiedad individual
prop = scraper.scrape_property("prop-123")
print(prop["title"], prop["price"], prop["location"])
```

## API

### `RealEstateScraper(base_url, timeout, max_retries, backoff_factor, use_stealth, proxy_list)`

| Parámetro     | Tipo  | Default | Descripción |
|---------------|-------|---------|-------------|
| `base_url`    | str   | `""`    | URL base del sitio a scrapear. |
| `timeout`     | int   | `30`    | Timeout por request (segundos). |
| `max_retries` | int   | `3`     | Intentos antes de fallar o caer a stealth. |
| `backoff_factor` | float | `1.0` | Factor de backoff exponencial. |
| `use_stealth` | bool  | `False` | Usar Camofox como fallback. |
| `proxy_list`  | list  | `[]`    | Lista de proxies `http://user:pass@host:port`. |
| `request_delay` | float | `0.0` | Delay entre requests en segundos (rate‑limiting). |

### Métodos principales

- **`fetch(endpoint)`** — GET con retry + proxy rotation + stealth fallback.
- **`scrape_property(property_id)`** — Scrapea una propiedad individual.
- **`scrape_real(source, zone)`** — Scrapea listados de una fuente real.
- **`export_data(data, fmt, output_dir)`** — Exporta a CSV o JSON.

---

## Tests

```bash
pip install -e ".[dev]"
pytest -v
```

Los tests usan `unittest.mock` para simular respuestas HTTP sin depender de sitios reales.

## Logging estructurado (loguru)

El scraper ahora usa `loguru` para logging estructurado con JSON. Los logs se pueden redirigir a un archivo o stdout para facilitar la depuración y el monitoreo.

Ejemplo de log en JSON:
```json
{
  "time": "2025-07-05T12:00:00.000000Z",
  "level": "ERROR",
  "message": "Timeout",
  "error": "ReadTimeout(10.0s)"
}
```

Para redirigir logs a un archivo:
```python
from loguru import logger
logger.add("scraper.log", level="INFO", format="{time} | {level} | {message}")
```

---

## Estructura del proyecto

```
real_estate_scraping/
├── src/
│   ├── __init__.py       # metadatos del paquete
│   ├── cli.py            # interfaz CLI
│   └── scraper.py        # scraper principal
├── tests/
│   └── test_scraper.py   # tests unitarios
├── data/                 # exports (gitignored)
├── logs/                 # logs (gitignored)
├── pyproject.toml        # build config
└── README.md
```

---

## Licencia

MIT — [Ranuk IT Solutions](https://ranuk.dev)
