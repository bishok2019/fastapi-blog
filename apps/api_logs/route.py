from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from apps.database import get_db
from base.pagination import paginate
from base.route import StandardResponse

from .models import APILog, ErrorLog
from .schemas import APILogList, ErrorLogList

router = APIRouter()


@router.get("/api-logs", response_model=StandardResponse)
def list_api_logs(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
):
    """List all API logs"""
    result = paginate(
        query=db.query(APILog).order_by(APILog.created_at.desc()),
        page=page,
        page_size=page_size,
        schema=APILogList,
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=StandardResponse.success_response(
            data=result.data,
            message="API logs fetched successfully.",
            meta=result.meta,
        ).model_dump(),
    )


@router.get("/error-logs", response_model=StandardResponse)
def list_error_logs(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
):
    """List all error logs"""
    result = paginate(
        query=db.query(ErrorLog).order_by(ErrorLog.created_at.desc()),
        page=page,
        page_size=page_size,
        schema=ErrorLogList,
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=StandardResponse.success_response(
            data=result.data,
            message="Error logs fetched successfully.",
            meta=result.meta,
        ).model_dump(),
    )
