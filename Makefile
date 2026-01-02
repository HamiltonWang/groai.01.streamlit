# Makefile for GroAI.01 Streamlit Dashboard

# Load .env file
ifneq (,$(wildcard ./.env.local))
    include .env.local
    export
endif

.PHONY: help dashboard install clean

# Default target
all: help

help:
	@echo "Available targets:"
	@echo "  make dashboard       - Run the Streamlit dashboard"
	@echo "  make install         - Create venv and install dependencies"
	@echo "  make clean           - Remove venv and temporary files"
	@echo "  make help            - Show this help"

# Run the dashboard
dashboard:
	@echo "Running Dashboard..."
	./venv/bin/streamlit run streamlit_app.py --server.port 8501

# Setup environment
install:
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt

# Clean up
clean:
	rm -rf venv
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
