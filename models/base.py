from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID, uuid4

class VacancyBase(BaseModel):
    title: str
    level: str = Field(..., description="junior/middle/senior")
    hard_skills: List[str]
    soft_skills: List[str]
    tasks: List[str]
    tools: List[str]

class VacancyCreate(VacancyBase):
    pass

class Vacancy(VacancyBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True

class CandidateBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    gender: str

class CandidateCreate(CandidateBase):
    pass

class Candidate(CandidateBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True

class InterviewBase(BaseModel):
    candidate_id: str
    vacancy_id: str
    status: str = Field(..., description="in_progress/completed")
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    recording_url: Optional[str] = None
    transcript: Optional[str] = None
    questions: List[str] = Field(default_factory=list)
    answers: List[str] = Field(default_factory=list)
    emotions_analysis: List[dict] = Field(default_factory=list)

class InterviewCreate(InterviewBase):
    pass

class Interview(InterviewBase):
    id: str = Field(default_factory=lambda: str(uuid4()))

    class Config:
        from_attributes = True

class ReportBase(BaseModel):
    interview_id: str
    hard_skills_assessment: dict
    soft_skills_assessment: dict
    emotions_analysis: dict
    verdict: dict
    feedback: Optional[str] = None

class ReportCreate(ReportBase):
    pass

class Report(ReportBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True

class HRManagerBase(BaseModel):
    name: str
    email: EmailStr
    password: str

class HRManagerCreate(HRManagerBase):
    pass

class HRManager(HRManagerBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.now)
    hashed_password: str

    class Config:
        from_attributes = True 