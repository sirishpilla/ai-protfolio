# main.py
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from api.summarize import router as summarize_router
from api.pitch import router as pitch_router

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(pitch_router)

app.include_router(summarize_router)

for r in app.routes:
    if getattr(r, "methods", None):
        print("ROUTE:", r.path, r.methods)