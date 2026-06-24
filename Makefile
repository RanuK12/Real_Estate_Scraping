.PHONY: install install-dev test lint clean run run-json

# Install production dependencies
install:
	pip install -e .

# Install with dev dependencies
install-dev:
	pip install -e ".[dev]"

# Run all tests
test:
	python -m pytest tests/ -v

# Lint with ruff
lint:
	ruff check src/ tests/

# Clean cache and build artifacts
clean:
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Scrape Zonaprop CABA (default)
run:
	real-estate-scraper --source zonaprop --zone CABA

# Scrape MercadoLibre Uruguay, export JSON
run-json:
	real-estate-scraper --source mercadolibre --zone Uruguay --export json

# Run all checks before pushing
ci: lint test
