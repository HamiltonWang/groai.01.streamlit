# Makefile for managing MLflow server

# Default target (run with just `make`)
all: restart-mlflow

# Load .env file
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

# Help target to show usage
help:
	@echo "Available targets:"
	@echo "  make start-mlflow      - Start MLflow server in foreground"
	@echo "  make stop-mlflow       - Stop any running MLflow servers"
	@echo "  make restart-mlflow    - Stop and restart MLflow server in foreground"
	@echo "  make start-background  - Start MLflow server in background (detached)"
	@echo "  make train             - Run the training script"
	@echo "  make predict_model     - Run the prediction script"
	@echo "  make predict_history   - Run the history prediction script"
	@echo "  make start-api         - Start the prediction API server"
	@echo "                           Usage: make start-api logged_model='...' HORIZON=6"
	@echo "  make test-api          - Run integration tests against running API"
	@echo "  make help              - Show this help"


# Variables
PROJECT = GroAI.01
SERVICE = mlflow-tracking

# Dashboard
.PHONY: dashboard
dashboard:
	@echo "Running Dashboard..."
	streamlit run streamlit_app.py --server.port 8501
