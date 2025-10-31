.PHONY: help install setup run test clean

help:
	@echo "LinkedIn Profile Scraper - Available Commands"
	@echo ""
	@echo "  make install    - Install all dependencies"
	@echo "  make setup      - Initial setup (install + playwright browsers)"
	@echo "  make run        - Run the scraper with example input"
	@echo "  make clean      - Clean output files and cache"
	@echo ""

install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt

setup: install
	@echo "Installing Playwright browsers..."
	playwright install chromium
	@echo ""
	@echo "Setup complete! Next steps:"
	@echo "1. Copy env.example to .env"
	@echo "2. Edit .env with your LinkedIn credentials"
	@echo "3. Run 'make run' to test"

run:
	@echo "Running scraper with example input..."
	python main.py -i example_input.json

test:
	@echo "Testing with a single profile..."
	@python -c "import sys; print('No profile URL provided. Use: make test URL=https://linkedin.com/in/...')"; exit 1

clean:
	@echo "Cleaning output files and cache..."
	rm -rf output/
	rm -rf __pycache__/
	rm -f cookies.json
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "Clean complete!"
