.PHONY: help install run test clean

help:
	@echo "DocuMind - Makefile Commands"
	@echo "==========================="
	@echo "install    Install dependencies"
	@echo "run        Start Streamlit UI"
	@echo "test       Run test suite"
	@echo "clean      Remove generated files and cache"

install:
	pip install -r requirements.txt

run:
	streamlit run app/main.py

test:
	pytest tests/ -v

clean:
	rm -rf data/*
	rm -rf __pycache__
	rm -rf .pytest_cache
	find . -type d -name "__pycache__" -exec rm -r {} +
