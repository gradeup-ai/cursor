from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from models.base import Interview, InterviewCreate
from models.auth import TokenData
from services.interview_service import InterviewService
from dependencies.auth import get_current_user

router = APIRouter()
interview_service = InterviewService()

@router.post("/", response_model=Interview)
async def create_interview(
    interview: InterviewCreate,
    current_user: TokenData = Depends(get_current_user)
):
    return await interview_service.create_interview(interview)

@router.get("/{interview_id}", response_model=Interview)
async def get_interview(
    interview_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    interview = await interview_service.get_interview(interview_id)
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    return interview

@router.get("/", response_model=List[Interview])
async def get_interviews(
    current_user: TokenData = Depends(get_current_user)
):
    return await interview_service.get_interviews()

@router.put("/{interview_id}", response_model=Interview)
async def update_interview(
    interview_id: str,
    interview: InterviewCreate,
    current_user: TokenData = Depends(get_current_user)
):
    updated_interview = await interview_service.update_interview(interview_id, interview)
    if not updated_interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    return updated_interview

@router.delete("/{interview_id}")
async def delete_interview(
    interview_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    success = await interview_service.delete_interview(interview_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    return {"message": "Interview deleted successfully"}

@router.post("/start")
async def start_interview(
    candidate_name: str,
    candidate_email: str,
    job_title: str,
    job_level: str,
    current_user: TokenData = Depends(get_current_user)
):
    session_id = await interview_service.create_session(
        candidate_name,
        candidate_email,
        job_title,
        job_level
    )
    return {"session_id": session_id}

@router.post("/{interview_id}/process")
async def process_interview_response(
    interview_id: str,
    response: str,
    current_user: TokenData = Depends(get_current_user)
):
    next_question = await interview_service.process_response(interview_id, response)
    return {"next_question": next_question} 