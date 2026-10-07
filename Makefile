report:
	python3 generate_report.py
	@echo "PDF generado en: report/informe_mercado.pdf"

clean:
	@rm -rf report