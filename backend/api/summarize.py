# api/summarize.py
from fastapi import APIRouter, HTTPException
from models.summarize import SummarizeRequest

# Create the router for this group of endpoints
router = APIRouter(tags=["summarize"])

@router.post("/summarize")
def summarize(req: SummarizeRequest):
    try:
        # Stubbed response for now
        return {"summary": req.text + "..."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))