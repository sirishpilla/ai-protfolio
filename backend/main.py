# main.py
from fastapi import FastAPI
from api.summarize import router as summarize_router

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

# Register the summarize routes
app.include_router(summarize_router)