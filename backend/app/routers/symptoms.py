import difflib
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app import models, schemas
from app.routers.doctors import _doctor_out

router = APIRouter(tags=["symptom-advisor"])

AGE_GROUP_LABELS = {
    "children": "Children (2-12)",
    "teen": "Teens (13-19)",
    "adult": "Adults (20-59)",
    "senior": "Senior Citizens (60+)",
}

STOPWORDS = {"pain", "ache", "aches", "problem", "problems", "issue", "issues", "feeling", "having", "in", "my", "a", "the"}


def _find_best_symptom(db: Session, q_norm: str) -> models.Symptom | None:
    """
    Three-pass matching so real-world phrasing ("leg pain", "my knee hurts a
    lot") still resolves instead of returning nothing:
      1. Exact substring match either direction.
      2. Fuzzy string match (typos, near-misses) via difflib.
      3. Keyword overlap: any meaningful shared word wins.
    """
    all_symptoms = db.query(models.Symptom).all()
    if not all_symptoms:
        return None

    # Pass 1: substring match either direction
    for s in all_symptoms:
        if q_norm in s.name or s.name in q_norm:
            return s

    # Pass 2: fuzzy match on the whole phrase
    names = [s.name for s in all_symptoms]
    close = difflib.get_close_matches(q_norm, names, n=1, cutoff=0.6)
    if close:
        return next(s for s in all_symptoms if s.name == close[0])

    # Pass 3: shared keyword overlap (ignoring generic words like "pain")
    q_words = {w for w in q_norm.split() if w not in STOPWORDS and len(w) > 2}
    best, best_score = None, 0
    for s in all_symptoms:
        s_words = {w for w in s.name.split() if w not in STOPWORDS}
        score = len(q_words & s_words)
        if score > best_score:
            best, best_score = s, score
    return best


@router.get("/symptoms/lookup", response_model=schemas.SymptomLookupResponse)
def lookup_symptom(q: str = Query(..., description="Symptom text, e.g. 'leg pain'"), db: Session = Depends(get_db)):
    """Rule-based symptom -> specialty lookup (Phase 2, Step 8)."""
    q_norm = q.strip().lower()
    if not q_norm:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    symptom = _find_best_symptom(db, q_norm)

    if not symptom:
        return schemas.SymptomLookupResponse(
            matched_symptom=None,
            specialty=None,
            doctors=[],
            message=(
                f"No specific match for '{q}'. Try describing it differently, "
                "or book with a General Physician who can refer you onward."
            ),
        )

    doctors = (
        db.query(models.Doctor)
        .options(joinedload(models.Doctor.user))
        .filter(models.Doctor.specialty.ilike(symptom.specialty))
        .all()
    )

    return schemas.SymptomLookupResponse(
        matched_symptom=symptom.name,
        specialty=symptom.specialty,
        doctors=[_doctor_out(d) for d in doctors],
        message=f"'{symptom.name.title()}' is usually handled by {symptom.specialty}. Pick a doctor below to see their open slots.",
    )


@router.get("/diseases/{name}/tips", response_model=schemas.DiseaseTipsOut)
def disease_tips(name: str, db: Session = Depends(get_db)):
    """Phase 2, Step 9: Disease -> diet/care recommendations, broken out by age group."""
    disease = (
        db.query(models.Disease)
        .options(joinedload(models.Disease.age_tips))
        .filter(models.Disease.name.ilike(name))
        .first()
    )
    if not disease:
        raise HTTPException(status_code=404, detail=f"No tips found for '{name}'")

    age_specific = [
        schemas.AgeGroupTipsOut(
            age_group=t.age_group.value,
            label=AGE_GROUP_LABELS.get(t.age_group.value, t.age_group.value.title()),
            diet_dos=t.diet_dos,
            diet_donts=t.diet_donts,
            general_tips=t.general_tips,
        )
        for t in disease.age_tips
    ]
    # Keep a stable, predictable order regardless of insertion order.
    order = ["children", "teen", "adult", "senior"]
    age_specific.sort(key=lambda t: order.index(t.age_group) if t.age_group in order else 99)

    return schemas.DiseaseTipsOut(
        name=disease.name,
        diet_dos=disease.diet_dos,
        diet_donts=disease.diet_donts,
        general_tips=disease.general_tips,
        age_specific=age_specific,
    )


@router.get("/diseases", response_model=List[str])
def list_diseases(db: Session = Depends(get_db)):
    """So the frontend can populate a dropdown without guessing valid names."""
    return [d.name for d in db.query(models.Disease).all()]
