from fastapi import APIRouter, HTTPException
from pathlib import Path
import json, requests

from models.pitch import MultiPitchRequest, MultiPitchResponse
from services.hf_client import generate_pitch

router = APIRouter(tags=["pitch"])

ROOT = Path(__file__).resolve().parents[1]
AUDIENCE_CONFIG_PATH = ROOT / "config" / "audience.json"
AUDIENCES = json.loads(AUDIENCE_CONFIG_PATH.read_text(encoding="utf-8"))

LENGTH_WORDS = {"30s": 65, "60s": 130, "2min": 260}

def _norm(s: str) -> str:
    return " ".join((s or "").split())

def _build_prompt_point(req: MultiPitchRequest, point_idx: int) -> str:
    # Always enforce 2min minimum
    word_target = max(LENGTH_WORDS["2min"], LENGTH_WORDS.get(req.length, 0))
    A = AUDIENCES[req.audience]
    tech_str = ", ".join(req.tech)
    p = req.points[point_idx]

    guidance_lines = []
    if A.get("must_include"):
        guidance_lines.append("Must include:")
        guidance_lines += [f"- {x}" for x in A["must_include"]]
    if A.get("avoid"):
        guidance_lines.append("Avoid:")
        guidance_lines += [f"- {x}" for x in A["avoid"]]
    guidance = "\n".join(guidance_lines)

    nontech_clause = ""
    if req.audience == "Non-Technical":
        nontech_clause = "Avoid technical jargon unless briefly explained in plain language.\n"

    return f"""You are a concise communications coach.

Write a 2-minute project pitch (~{word_target}–{int(word_target*1.2)} words) tailored to: {req.audience}.
Opening guidance: {A.get('opening','')}
Tone: {A.get('tone','')}
{nontech_clause}{guidance}

Project facts (point {point_idx+1} of {len(req.points)}):
- Title: {req.title}
- Problem: {p.problem}
- Solution: {p.solution}
- Impact: {p.impact}
- Tech stack: {tech_str}

Constraints:
- Start with what matters most to a {req.audience}.
- Use 3–5 short paragraphs or bullet sections.
- Be concrete and specific; prefer measurable outcomes.
- End with a single-sentence call-to-action for this audience.
- Hard cap: do not go below ~{word_target} words; do not exceed ~{int(word_target*1.2)} words.

Now produce the pitch."""
    

@router.post("/pitch_multi", response_model=MultiPitchResponse)
def create_multi_pitch(req: MultiPitchRequest):
    if not req.points or len(req.points) < 2:
        raise HTTPException(status_code=400, detail="Provide 2–3 points.")
    if not req.tech:
        raise HTTPException(status_code=400, detail="Include at least one tech stack item.")

    # Basic content guardrail per point
    for i, pt in enumerate(req.points):
        if len(_norm(pt.problem) + _norm(pt.solution) + _norm(pt.impact)) < 80:
            raise HTTPException(status_code=400, detail=f"Point {i+1} needs more detail (~80+ chars combined).")

    pitches = []
    for i in range(len(req.points)):
        prompt = _build_prompt_point(req, i)
        try:
            text = generate_pitch(prompt)
            out = text[len(prompt):].strip() if text.startswith(prompt) else text.strip()
            pitches.append(out)
        except requests.HTTPError as e:
            # Surface the upstream status/body
            resp = e.response
            raise HTTPException(status_code=resp.status_code, detail=(resp.text if resp is not None else str(e)))
        except requests.Timeout:
            raise HTTPException(status_code=503, detail="Model timed out. Try again.")
        except Exception:
            raise HTTPException(status_code=500, detail="Pitch generation failed.")

    return MultiPitchResponse(
        title=req.title,
        audience=req.audience,
        length="2min",
        pitches=pitches
    )