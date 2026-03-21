HOST=0.0.0.0
PORT=9887

SRC=./src

.PHONY: format lint run run-uvicorn run-dev build clean dependencies test
run-uvicorn:
	cd $(SRC) && uvicorn main:app --reload --host $(HOST) --port $(PORT)

dependencies:
	pip3 install -r requirements.txt

run-dev:
	cd $(SRC) && python3 main.py --host $(HOST) --port $(PORT)

run: $(SRC)/dist/finapi_server
	cd $(SRC) && ./dist/finapi_server --host $(HOST) --port $(PORT)

build: $(SRC)/dist/finapi_server

test:
	pytest -v

clean:
	cd $(SRC) && rm -rf dist build __pycache__ *.spec

format:
	ruff format $(SRC)

lint:
	ruff check $(SRC) --fix

$(SRC)/dist/finapi_server: 
	cd $(SRC) && pyinstaller --onefile main.py --name finapi_server