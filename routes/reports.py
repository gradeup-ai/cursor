from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from models.base import Report, ReportCreate
from models.auth import TokenData
from services.report_service import ReportService
from dependencies.auth import get_current_user

router = APIRouter()
report_service = ReportService()

@router.post("/", response_model=Report)
async def create_report(
    report: ReportCreate,
    current_user: TokenData = Depends(get_current_user)
):
    return await report_service.create_report(report)

@router.get("/{report_id}", response_model=Report)
async def get_report(
    report_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    report = await report_service.get_report(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    return report

@router.get("/", response_model=List[Report])
async def get_reports(
    current_user: TokenData = Depends(get_current_user)
):
    return await report_service.get_reports()

@router.put("/{report_id}/status")
async def update_report_status(
    report_id: str,
    status: str,
    current_user: TokenData = Depends(get_current_user)
):
    report = await report_service.update_report_status(report_id, status)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    return report

@router.post("/{report_id}/send")
async def send_report(
    report_id: str,
    hr_email: str,
    current_user: TokenData = Depends(get_current_user)
):
    success = await report_service.send_report(report_id, hr_email)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    return {"message": "Report sent successfully"} 