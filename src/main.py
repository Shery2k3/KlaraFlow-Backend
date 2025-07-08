from fastapi import FastAPI

app = FastAPI(title="KlaraFlow", version="0.0.1b")

@app.get("/")
def read_root():
  return {"message": "Welcome to the KlaraFlow server!"}

# poetry run uvicorn src.main:app --reload