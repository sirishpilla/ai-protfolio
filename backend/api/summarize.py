# api/summarize.py
from fastapi import APIRouter, HTTPException
from models.summarize import SummarizeRequest
from services.hf_client import summarize_text

# Create the router for this group of endpoints
router = APIRouter(tags=["summarize"])

@router.post("/summarize")
def summarize(req: SummarizeRequest):
    text = req.text.strip()
    if len(text) < 40:
        raise HTTPException(
            status_code=400,
            detail="Please provide at least 40 characters so I have enough context to summarize."
        )
    try:
        result = summarize_text(req.text)
        return {"summary": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))