from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from models.base import Candidate, CandidateCreate
from models.auth import TokenData
from services.candidate_service import CandidateService
from dependencies.auth import get_current_user

router = APIRouter()
candidate_service = CandidateService()

@router.post("/", response_model=Candidate)
async def create_candidate(
    candidate: CandidateCreate,
    current_user: TokenData = Depends(get_current_user)
):
    return await candidate_service.create_candidate(candidate)

@router.get("/{candidate_id}", response_model=Candidate)
async def get_candidate(
    candidate_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    candidate = await candidate_service.get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    return candidate

@router.get("/", response_model=List[Candidate])
async def get_candidates(
    current_user: TokenData = Depends(get_current_user)
):
    return await candidate_service.get_candidates()

@router.put("/{candidate_id}", response_model=Candidate)
async def update_candidate(
    candidate_id: str,
    candidate: CandidateCreate,
    current_user: TokenData = Depends(get_current_user)
):
    updated_candidate = await candidate_service.update_candidate(candidate_id, candidate)
    if not updated_candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    return updated_candidate

@router.delete("/{candidate_id}")
async def delete_candidate(
    candidate_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    success = await candidate_service.delete_candidate(candidate_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    return {"message": "Candidate deleted successfully"} 