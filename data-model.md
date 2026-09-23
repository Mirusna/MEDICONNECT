# Data Model (Phase 1 sketch)

## Entities

**User**
- id (PK)
- name
- email (unique)
- password_hash
- role (enum: `patient` | `doctor`)
- created_at

**Doctor** (1:1 with User where role = doctor)
- id (PK)
- user_id (FK → User)
- specialty
- bio
- years_experience

**Appointment**
- id (PK)
- patient_id (FK → User)
- doctor_id (FK → Doctor)
- start_time
- end_time
- status (enum: `booked` | `cancelled` | `completed`)
- created_at

## Phase 2 additions (not built yet)

**Symptom**
- id (PK)
- name
- specialty (FK-ish lookup → maps to a Doctor specialty)

**Disease**
- id (PK)
- name
- diet_dos (text)
- diet_donts (text)
- general_tips (text)

## Relationships

- User (1) —— (0 or 1) Doctor
- User/patient (1) —— (many) Appointment
- Doctor (1) —— (many) Appointment
- Symptom (many) —— (1) Specialty [string match for now, no separate Specialty table yet]

## Notes / open questions for Step 4

- Should `Doctor.specialty` be a free-text string or its own `Specialty` table?
  Free text is faster to ship for Phase 1; normalize later if the symptom
  lookup (Phase 2, Step 8) needs strict matching.
- Appointment conflict checking (Step 6) needs an index on
  `(doctor_id, start_time, end_time)` to make overlap queries fast.
