HOST=0.0.0.0
PORT=9887

.PHONY: format lint run
dependencies:
	pip3 install -r requirements.txt

run:
	uvicorn main:app --reload --host $(HOST) --port $(PORT)

format:
	ruff format .

lint:
	ruff check . --fix