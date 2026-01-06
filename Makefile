.PHONY: help venv install db-up db-down etl seed-db train app report test lint

help:
	@echo "Targets:"
	@echo "  install    - install deps into current environment"
	@echo "  db-up      - start Postgres + app via docker compose"
	@echo "  db-down    - stop docker compose"
	@echo "  etl        - clean CSV -> parquet"
	@echo "  seed-db    - load parquet into Postgres + publish curated tables"
	@echo "  train      - benchmark models + save best artifact"
	@echo "  app        - run Streamlit app locally"
	@echo "  report     - (optional) copy notebook figures into docs"
	@echo "  test       - run pytest"
	@echo "  lint       - run ruff"

install:
	pip install -r requirements.txt
	pip install -e .

db-up:
	docker compose -f docker/docker-compose.yml up --build

db-down:
	docker compose -f docker/docker-compose.yml down

etl:
	python -m hr_analytics.etl --input data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv --out data/processed/hr_clean.parquet

seed-db:
	python -m hr_analytics.db --data data/processed/hr_clean.parquet

train:
	python -m hr_analytics.train --data data/processed/hr_clean.parquet --outdir artifacts/model --metrics reports/metrics.json

app:
	streamlit run app/streamlit_app.py

test:
	pytest -q

lint:
	ruff check .
