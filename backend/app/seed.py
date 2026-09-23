"""
Seed script for Phase 2 lookup data + sample doctors so the frontend has
something to show immediately. Idempotent-ish: skips rows that already
exist by unique name/email.

Run with: python -m app.seed
"""
from app.database import SessionLocal, engine, Base
from app import models, auth

SYMPTOM_SPECIALTY_MAP = [
    # ENT
    ("ear pain", "ENT"),
    ("sore throat", "ENT"),
    ("hearing loss", "ENT"),
    ("runny nose", "ENT"),
    ("sinus congestion", "ENT"),
    # Cardiology
    ("chest pain", "Cardiology"),
    ("palpitations", "Cardiology"),
    ("high blood pressure", "Cardiology"),
    ("shortness of breath", "Cardiology"),
    # Dermatology
    ("skin rash", "Dermatology"),
    ("acne", "Dermatology"),
    ("itching", "Dermatology"),
    ("hair loss", "Dermatology"),
    ("skin allergy", "Dermatology"),
    # Orthopedics
    ("joint pain", "Orthopedics"),
    ("back pain", "Orthopedics"),
    ("fracture", "Orthopedics"),
    ("leg pain", "Orthopedics"),
    ("knee pain", "Orthopedics"),
    ("shoulder pain", "Orthopedics"),
    ("ankle pain", "Orthopedics"),
    ("neck pain", "Orthopedics"),
    ("muscle pain", "Orthopedics"),
    ("sprain", "Orthopedics"),
    # Neurology
    ("headache", "Neurology"),
    ("dizziness", "Neurology"),
    ("numbness", "Neurology"),
    ("migraine", "Neurology"),
    ("insomnia", "Neurology"),
    # Ophthalmology
    ("blurred vision", "Ophthalmology"),
    ("eye pain", "Ophthalmology"),
    ("red eyes", "Ophthalmology"),
    # Gastroenterology
    ("stomach pain", "Gastroenterology"),
    ("abdominal pain", "Gastroenterology"),
    ("nausea", "Gastroenterology"),
    ("vomiting", "Gastroenterology"),
    ("diarrhea", "Gastroenterology"),
    ("constipation", "Gastroenterology"),
    ("acid reflux", "Gastroenterology"),
    # Endocrinology
    ("frequent urination", "Endocrinology"),
    ("excessive thirst", "Endocrinology"),
    ("weight gain", "Endocrinology"),
    ("weight loss", "Endocrinology"),
    ("thyroid problem", "Endocrinology"),
    # Pediatrics
    ("child fever", "Pediatrics"),
    ("child not eating", "Pediatrics"),
    ("growth concerns", "Pediatrics"),
    # Psychiatry
    ("anxiety", "Psychiatry"),
    ("depression", "Psychiatry"),
    ("stress", "Psychiatry"),
    # Urology
    ("urinary tract infection", "Urology"),
    ("burning urination", "Urology"),
    ("kidney stone", "Urology"),
    # General Physician
    ("fatigue", "General Physician"),
    ("fever", "General Physician"),
    ("cough", "General Physician"),
    ("common cold", "General Physician"),
    ("body ache", "General Physician"),
]

DISEASE_TIPS = [
    (
        "diabetes",
        "Whole grains, leafy greens, beans, nuts, fish, and high-fiber fruits like berries and apples.",
        "Sugary drinks, white bread/rice, fried foods, and processed snacks with added sugar.",
        "Monitor blood sugar regularly, stay active most days, keep meals consistent in timing and size, "
        "and follow up with an Endocrinologist for medication adjustments.",
    ),
    (
        "hypertension",
        "Fruits, vegetables, low-fat dairy, whole grains, and foods low in sodium.",
        "Salty/processed foods, canned soups, fatty red meat, and excess alcohol.",
        "Track blood pressure at home, reduce sodium intake, manage stress, and take medications "
        "consistently even when you feel fine.",
    ),
    (
        "asthma",
        "Anti-inflammatory foods like fruits, vegetables, and omega-3 rich fish.",
        "Foods you know trigger reactions (varies by person), and excess sulfite-containing foods "
        "(dried fruit, wine) for sensitive patients.",
        "Keep a rescue inhaler accessible, identify and avoid personal triggers (dust, smoke, pollen), "
        "and follow your prescribed controller medication schedule.",
    ),
]

# Age-specific overlays. Each tuple: (disease_name, age_group, dos, donts, tips)
DISEASE_AGE_TIPS = [
    # ---- Diabetes ----
    ("diabetes", "children", "Balanced meals with fruit, whole grains, and dairy at consistent times; keep juice/snacks on hand for lows.",
     "Sugary sodas, candy, and skipping meals, which can cause dangerous blood sugar swings.",
     "Involve school staff in the care plan, teach the child to recognize low blood sugar symptoms, and check levels before sports."),
    ("diabetes", "teen", "Protein-rich breakfasts, high-fiber snacks, and staying hydrated with water instead of sugary drinks.",
     "Skipping insulin/medication doses due to social pressure, and binge eating at parties.",
     "Encourage the teen to carry fast-acting glucose, involve them in their own meal planning, and monitor for signs of disordered eating."),
    ("diabetes", "adult", "Whole grains, leafy greens, beans, nuts, fish, and high-fiber fruits like berries and apples.",
     "Sugary drinks, white bread/rice, fried foods, and processed snacks with added sugar.",
     "Monitor blood sugar regularly, stay active most days, and keep meal timing consistent."),
    ("diabetes", "senior", "Soft, fiber-rich foods (cooked vegetables, oats), smaller frequent meals, and adequate protein to preserve muscle.",
     "Very low-calorie crash diets, excess salt if also managing blood pressure, and skipping meals before medication.",
     "Watch for low blood sugar which can look like confusion or dizziness, coordinate with all prescribing doctors, and get regular foot and eye checks."),

    # ---- Hypertension ----
    ("hypertension", "children", "Fresh fruit, vegetables, and limiting processed snacks; encourage regular active play.",
     "Excess salty packaged snacks and sugary drinks, which contribute to early weight gain.",
     "Pediatric hypertension is often linked to weight or kidney issues — a full workup with a Pediatrician is important."),
    ("hypertension", "teen", "Home-cooked meals with vegetables, low-fat dairy, and whole grains; regular physical activity.",
     "Energy drinks, excess fast food, and added salt at the table.",
     "Limit screen time in favor of activity, and check blood pressure if there's a family history."),
    ("hypertension", "adult", "Fruits, vegetables, low-fat dairy, whole grains, and foods low in sodium.",
     "Salty/processed foods, canned soups, fatty red meat, and excess alcohol.",
     "Track blood pressure at home, reduce sodium intake, and manage stress."),
    ("hypertension", "senior", "Potassium-rich foods (bananas, potatoes) if kidney function allows, and modest portions of lean protein.",
     "High-sodium canned/processed foods, and NSAIDs without checking with a doctor first, as they can raise blood pressure.",
     "Rise slowly from sitting/lying to avoid dizziness from blood pressure medication, and get levels checked regularly."),

    # ---- Asthma ----
    ("asthma", "children", "Warm fluids, fruits rich in vitamin C, and foods with omega-3s like fish (if not allergic).",
     "Cold drinks right after activity, and known personal food triggers.",
     "Make sure the school has a copy of the action plan and keep the inhaler technique checked regularly by a doctor."),
    ("asthma", "teen", "Anti-inflammatory foods — fruits, vegetables, and fish; staying well hydrated during sports.",
     "Smoking or vaping, which significantly worsens asthma control.",
     "Warm up properly before exercise and always carry a rescue inhaler to school or sports practice."),
    ("asthma", "adult", "Anti-inflammatory foods like fruits, vegetables, and omega-3 rich fish.",
     "Known personal triggers, and excess sulfite-containing foods (dried fruit, wine) for sensitive patients.",
     "Keep a rescue inhaler accessible and follow your prescribed controller medication schedule."),
    ("asthma", "senior", "Light, warm meals and adequate hydration; foods rich in antioxidants (berries, leafy greens).",
     "Overexertion in cold/dry air, and any new medication without checking for interactions with asthma drugs.",
     "Get an annual flu shot, as respiratory infections hit asthmatic seniors harder, and review inhaler technique at each visit."),
]

SAMPLE_DOCTORS = [
    ("Dr. Asha Rao", "asha.rao@mediconnect.dev", "ENT", "ENT specialist, 10 years in ear/nose/throat care.", 10),
    ("Dr. Vikram Sinha", "vikram.sinha@mediconnect.dev", "Cardiology", "Cardiologist focused on preventive heart health.", 14),
    ("Dr. Priya Menon", "priya.menon@mediconnect.dev", "Dermatology", "Dermatologist treating skin, hair, and nail conditions.", 8),
    ("Dr. Karthik Iyer", "karthik.iyer@mediconnect.dev", "Orthopedics", "Orthopedic surgeon specializing in joints and sports injuries.", 12),
    ("Dr. Meera Nair", "meera.nair@mediconnect.dev", "Neurology", "Neurologist treating headaches, seizures, and nerve disorders.", 9),
    ("Dr. Sanjay Gupta", "sanjay.gupta@mediconnect.dev", "General Physician", "General physician for everyday illness and checkups.", 15),
    ("Dr. Ritu Verma", "ritu.verma@mediconnect.dev", "Endocrinology", "Endocrinologist specializing in diabetes and thyroid care.", 11),
    ("Dr. Ananya Das", "ananya.das@mediconnect.dev", "Ophthalmology", "Eye specialist treating vision and eye-health concerns.", 7),
    ("Dr. Rohan Kulkarni", "rohan.kulkarni@mediconnect.dev", "Gastroenterology", "Gastroenterologist for digestive and stomach conditions.", 13),
    ("Dr. Neha Kapoor", "neha.kapoor@mediconnect.dev", "Pediatrics", "Pediatrician caring for infants, children, and teens.", 10),
    ("Dr. Arjun Malhotra", "arjun.malhotra@mediconnect.dev", "Psychiatry", "Psychiatrist supporting mental health across all ages.", 9),
    ("Dr. Divya Pillai", "divya.pillai@mediconnect.dev", "Urology", "Urologist treating urinary tract and kidney conditions.", 11),
]

DEFAULT_DOCTOR_PASSWORD = "doctor123"  # dev-only seed password; change before real use


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Symptoms — upsert specialty in case a mapping changed
        existing_symptoms = {s.name: s for s in db.query(models.Symptom).all()}
        for name, specialty in SYMPTOM_SPECIALTY_MAP:
            if name in existing_symptoms:
                existing_symptoms[name].specialty = specialty
            else:
                db.add(models.Symptom(name=name, specialty=specialty))
        db.commit()

        # Diseases (base/default tips)
        diseases_by_name = {d.name: d for d in db.query(models.Disease).all()}
        for name, dos, donts, tips in DISEASE_TIPS:
            if name not in diseases_by_name:
                d = models.Disease(name=name, diet_dos=dos, diet_donts=donts, general_tips=tips)
                db.add(d)
                db.flush()
                diseases_by_name[name] = d
        db.commit()

        # Age-specific tips
        existing_age_tips = {
            (t.disease_id, t.age_group.value)
            for t in db.query(models.DiseaseAgeTip).all()
        }
        for disease_name, age_group, dos, donts, tips in DISEASE_AGE_TIPS:
            disease = diseases_by_name.get(disease_name)
            if not disease:
                continue
            key = (disease.id, age_group)
            if key not in existing_age_tips:
                db.add(
                    models.DiseaseAgeTip(
                        disease_id=disease.id,
                        age_group=models.AgeGroup(age_group),
                        diet_dos=dos,
                        diet_donts=donts,
                        general_tips=tips,
                    )
                )
        db.commit()

        # Sample doctors (each is a User + Doctor row)
        for name, email, specialty, bio, years in SAMPLE_DOCTORS:
            if db.query(models.User).filter(models.User.email == email).first():
                continue
            user = models.User(
                name=name,
                email=email,
                password_hash=auth.hash_password(DEFAULT_DOCTOR_PASSWORD),
                role=models.UserRole.doctor,
            )
            db.add(user)
            db.flush()
            db.add(models.Doctor(user_id=user.id, specialty=specialty, bio=bio, years_experience=years))
        db.commit()

        print("Seed complete.")
        print(f"Sample doctor login password: '{DEFAULT_DOCTOR_PASSWORD}' (dev only)")
    finally:
        db.close()


if __name__ == "__main__":
    run()
