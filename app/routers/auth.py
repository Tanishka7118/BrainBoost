from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.database import get_db
from app.models.models import Student
from app.schemas.schemas import StudentCreate, StudentOut, Token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
def register(student: StudentCreate, db: Session = Depends(get_db)):
    existing = db.query(Student).filter(Student.email == student.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_student = Student(
        name=student.name.strip(),
        email=student.email.lower(),
        hashed_password=get_password_hash(student.password),
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.email == form_data.username.lower()).first()
    if not student or not verify_password(form_data.password, student.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(data={"sub": str(student.id)})
    return Token(access_token=token)
