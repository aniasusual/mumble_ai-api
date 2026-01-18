git clone https://github.com/aniasusual/mumble_ai-api.git
poetry install
poetry run uvicorn src.main:app --reload