"""
Database Schemas for Hulubedeje (ሁሉ በደጄ)

Each Pydantic model below maps to a MongoDB collection with the lowercase
class name as the collection name.

Examples:
- User -> "user"
- Patient -> "patient"
- Appointment -> "appointment"
"""
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, EmailStr
from datetime import date, datetime

# Authentication & Users
class User(BaseModel):
    email: EmailStr
    password_hash: str = Field(..., description="BCrypt hash of password")
    full_name: str
    role: Literal["admin", "doctor", "nurse", "pharmacist", "lab", "patient"]
    phone: Optional[str] = None
    is_active: bool = True
    verified: bool = False

# Patient Management
class Patient(BaseModel):
    user_id: Optional[str] = None
    first_name: str
    last_name: str
    gender: Literal["male", "female", "other"]
    dob: Optional[date] = None
    blood_group: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = "Ethiopia"
    emergency_contact: Optional[str] = None
    medical_history: Optional[List[str]] = []
    allergies: Optional[List[str]] = []

# Doctor Management
class Doctor(BaseModel):
    user_id: Optional[str] = None
    first_name: str
    last_name: str
    specialty: str
    bio: Optional[str] = None
    availability: Optional[List[str]] = []  # e.g., ["Mon 09:00-12:00", ...]

# Appointments
class Appointment(BaseModel):
    patient_id: str
    doctor_id: str
    date: date
    time_slot: str  # e.g., "10:30-11:00"
    status: Literal["scheduled", "completed", "cancelled"] = "scheduled"
    reason: Optional[str] = None

# Pharmacy
class Medicine(BaseModel):
    name: str
    sku: Optional[str] = None
    description: Optional[str] = None
    quantity: int = 0
    price: float = 0.0
    expires_on: Optional[date] = None

class Prescription(BaseModel):
    patient_id: str
    doctor_id: str
    medicines: List[dict] = Field(default_factory=list)  # [{name, dose, frequency, days}]
    notes: Optional[str] = None

# Laboratory
class LabTest(BaseModel):
    patient_id: str
    doctor_id: str
    test_type: str
    status: Literal["requested", "in_progress", "completed"] = "requested"
    result_url: Optional[str] = None  # could be a file link or PDF URL

# Billing & Accounting
class Invoice(BaseModel):
    patient_id: str
    amount: float
    items: List[dict] = Field(default_factory=list)  # [{label, amount}]
    paid: bool = False
    method: Optional[str] = None  # cash/card/insurance

# Nursing
class Vital(BaseModel):
    patient_id: str
    temperature_c: Optional[float] = None
    pulse_bpm: Optional[int] = None
    blood_pressure: Optional[str] = None
    respiration_rate: Optional[int] = None
    notes: Optional[str] = None

class BedAssignment(BaseModel):
    patient_id: str
    ward: str
    bed_number: str
    assigned_on: datetime = Field(default_factory=datetime.utcnow)

# Inventory
class InventoryItem(BaseModel):
    name: str
    category: Optional[str] = None
    quantity: int = 0
    threshold: int = 5
    location: Optional[str] = None

# EHR
class MedicalRecord(BaseModel):
    patient_id: str
    visit_date: datetime = Field(default_factory=datetime.utcnow)
    complaints: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    documents: Optional[List[str]] = []
