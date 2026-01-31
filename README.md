git clone https://github.com/aniasusual/mumble_ai-api.git
poetry install
poetry add emergentintegrations --source emergent
poetry run uvicorn src.main:app --reload