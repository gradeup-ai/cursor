from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from models.base import Vacancy, VacancyCreate
from models.auth import TokenData
from services.vacancy_service import VacancyService
from dependencies.auth import get_current_user

router = APIRouter()
vacancy_service = VacancyService()

@router.post("/", response_model=Vacancy)
async def create_vacancy(
    vacancy: VacancyCreate,
    current_user: TokenData = Depends(get_current_user)
):
    return await vacancy_service.create_vacancy(vacancy)

@router.get("/{vacancy_id}", response_model=Vacancy)
async def get_vacancy(
    vacancy_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    vacancy = await vacancy_service.get_vacancy(vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacancy not found"
        )
    return vacancy

@router.get("/", response_model=List[Vacancy])
async def get_vacancies(
    current_user: TokenData = Depends(get_current_user)
):
    return await vacancy_service.get_vacancies()

@router.put("/{vacancy_id}", response_model=Vacancy)
async def update_vacancy(
    vacancy_id: str,
    vacancy: VacancyCreate,
    current_user: TokenData = Depends(get_current_user)
):
    updated_vacancy = await vacancy_service.update_vacancy(vacancy_id, vacancy)
    if not updated_vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacancy not found"
        )
    return updated_vacancy

@router.delete("/{vacancy_id}")
async def delete_vacancy(
    vacancy_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    success = await vacancy_service.delete_vacancy(vacancy_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacancy not found"
        )
    return {"message": "Vacancy deleted successfully"} 