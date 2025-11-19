import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from database import db, create_document, get_documents
from schemas import User, Patient, Doctor, Appointment, Medicine, Prescription, LabTest, Invoice, Vital, BedAssignment, InventoryItem, MedicalRecord

app = FastAPI(title="Hulubedeje API", description="Hospital Management System API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"name": "Hulubedeje", "status": "ok"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or "❌ Not Set"
            try:
                response["collections"] = db.list_collection_names()[:20]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:100]}"
        else:
            response["database"] = "❌ Not Initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:100]}"
    return response

# ------------- Auth (simplified placeholder, not production auth) -------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@app.post("/auth/login")
def login(payload: LoginRequest):
    # For demo only: find user by email; password check omitted
    users = get_documents("user", {"email": payload.email}, limit=1) if db else []
    if not users:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user = users[0]
    return {"message": "Logged in", "role": user.get("role"), "user": {"email": user.get("email"), "full_name": user.get("full_name")}}

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str

@app.post("/auth/signup")
def signup(payload: SignupRequest):
    if not db:
        raise HTTPException(status_code=500, detail="Database not available")
    exists = get_documents("user", {"email": payload.email}, limit=1)
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    doc = {
        "email": payload.email,
        "password_hash": payload.password,  # NOTE: hash in real apps
        "full_name": payload.full_name,
        "role": payload.role,
        "is_active": True,
        "verified": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    user_id = create_document("user", doc)
    return {"message": "Signup successful", "user_id": user_id}

# ------------- Minimal CRUD endpoints for core modules -------------

@app.post("/patients")
def create_patient(payload: Patient):
    patient_id = create_document("patient", payload)
    return {"id": patient_id}

@app.get("/patients")
def list_patients():
    return get_documents("patient", limit=100)

@app.post("/doctors")
def create_doctor(payload: Doctor):
    doctor_id = create_document("doctor", payload)
    return {"id": doctor_id}

@app.get("/doctors")
def list_doctors():
    return get_documents("doctor", limit=100)

@app.post("/appointments")
def create_appointment(payload: Appointment):
    appt_id = create_document("appointment", payload)
    return {"id": appt_id}

@app.get("/appointments")
def list_appointments():
    return get_documents("appointment", limit=100)

@app.post("/pharmacy/medicines")
def add_medicine(payload: Medicine):
    med_id = create_document("medicine", payload)
    return {"id": med_id}

@app.get("/pharmacy/medicines")
def list_medicines():
    return get_documents("medicine", limit=200)

@app.post("/pharmacy/prescriptions")
def add_prescription(payload: Prescription):
    pid = create_document("prescription", payload)
    return {"id": pid}

@app.get("/pharmacy/prescriptions")
def list_prescriptions():
    return get_documents("prescription", limit=100)

@app.post("/lab/tests")
def add_lab_test(payload: LabTest):
    tid = create_document("labtest", payload)
    return {"id": tid}

@app.get("/lab/tests")
def list_lab_tests():
    return get_documents("labtest", limit=100)

@app.post("/billing/invoices")
def add_invoice(payload: Invoice):
    iid = create_document("invoice", payload)
    return {"id": iid}

@app.get("/billing/invoices")
def list_invoices():
    return get_documents("invoice", limit=100)

@app.post("/nursing/vitals")
def add_vital(payload: Vital):
    vid = create_document("vital", payload)
    return {"id": vid}

@app.get("/nursing/vitals")
def list_vitals():
    return get_documents("vital", limit=200)

@app.post("/nursing/bed-assignments")
def add_bed_assignment(payload: BedAssignment):
    bid = create_document("bedassignment", payload)
    return {"id": bid}

@app.get("/nursing/bed-assignments")
def list_bed_assignments():
    return get_documents("bedassignment", limit=200)

@app.post("/inventory/items")
def add_inventory_item(payload: InventoryItem):
    iid = create_document("inventoryitem", payload)
    return {"id": iid}

@app.get("/inventory/items")
def list_inventory_items():
    return get_documents("inventoryitem", limit=200)

@app.post("/ehr/records")
def add_medical_record(payload: MedicalRecord):
    rid = create_document("medicalrecord", payload)
    return {"id": rid}

@app.get("/ehr/records")
def list_medical_records(patient_id: Optional[str] = None):
    filt = {"patient_id": patient_id} if patient_id else {}
    return get_documents("medicalrecord", filter_dict=filt, limit=200)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
