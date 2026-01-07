from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from apps.database import get_db
from base.pagination import paginate
from base.route import StandardResponse

from .models import Stock, StockHistory
from .schema import (
    StockCreateSchema,
    StockHistoryRetrieveSchema,
    StockListSchema,
    StockRetrieveSchema,
    StockUpdateSchema,
)

router = APIRouter()


@router.get("/list", response_model=StandardResponse)
def list_stocks(
    page: int = 1,  # we are passing page and page_size in paginate() directly
    page_size: int = 1,
    db: Session = Depends(get_db),
):
    """List all stocks"""
    result = paginate(
        query=db.query(Stock),
        page=page,  # we are passing page and page_size in paginate() directly
        page_size=page_size,
        schema=StockListSchema,
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=StandardResponse.success_response(
            data=result.data,
            message="Stock fetched successfully.",
            meta=result.meta,
        ).model_dump(),
    )


@router.post("/create", response_model=StandardResponse)
def create_stock(
    stock: StockCreateSchema,
    db: Session = Depends(get_db),
):
    try:
        db_stock = Stock(**stock.model_dump())
        db.add(db_stock)
        db.flush()  # get ID, no commit yet

        # create price history
        historical_price = StockHistory(
            stock_id=db_stock.id,
            price=db_stock.price,
        )
        db.add(historical_price)

        db.commit()
        db.refresh(db_stock)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=StandardResponse.success_response(
                data=StockRetrieveSchema.model_validate(db_stock),
                message="Stock created successfully.",
            ).model_dump(),
        )

    except IntegrityError:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=StandardResponse.error_response(
                message="Stock with this symbol already exists."
            ).model_dump(),
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create stock: {str(e)}",
        )


# @router.get("/retrieve/{stock_id}", response_model=StandardResponse)
# def retrieve_stock(
#     stock_id: int,
#     db: Session = Depends(get_db),
# ):
#     """Retrieve a stock by ID"""
#     db_stock = db.query(Stock).filter(Stock.id == stock_id).first()
#     if not db_stock:
#         return JSONResponse(
#             status_code=status.HTTP_404_NOT_FOUND,
#             content=StandardResponse.error_response(
#                 message="Stock not found."
#             ).model_dump(),
#         )
#     return JSONResponse(
#         status_code=status.HTTP_200_OK,
#         content=StandardResponse.success_response(
#             data=StockRetrieveSchema.model_validate(db_stock),
#             message="Stock retrieved successfully.",
#         ).model_dump(),
#     )


@router.get("/retrieve/{stock_id}", response_model=StandardResponse)
def retrieve_stock(
    stock_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve a stock by ID"""
    db_stock = (
        db.query(Stock)
        .options(joinedload(Stock.history))
        .filter(Stock.id == stock_id)
        .first()
    )

    if not db_stock:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=StandardResponse.error_response(
                message="Stock not found."
            ).model_dump(),
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=StandardResponse.success_response(
            data=StockHistoryRetrieveSchema.model_validate(db_stock).model_dump(
                mode="json"
            ),
            message="Stock retrieved successfully.",
        ).model_dump(),
    )


@router.patch("/update/{stock_id}", response_model=StandardResponse)
def update_stock(
    stock_id: int,
    stock: StockUpdateSchema,
    db: Session = Depends(get_db),
):
    try:
        db_stock = db.query(Stock).filter(Stock.id == stock_id).first()
        if not db_stock:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=StandardResponse.error_response(
                    message="Stock not found."
                ).model_dump(),
            )
        # Track price change
        if stock.price is not None and db_stock.price != stock.price:
            historical_price = StockHistory(
                stock_id=stock_id,
                price=stock.price,
            )
            db.add(historical_price)
            db_stock.price = stock.price

        if stock.symbol is not None:
            db_stock.symbol = stock.symbol
        if stock.company_name is not None:
            db_stock.company_name = stock.company_name
        if stock.last_updated is not None:
            db_stock.last_updated = stock.last_updated

        db.commit()
        db.refresh(db_stock)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=StandardResponse.success_response(
                data=StockRetrieveSchema.model_validate(db_stock),
                message="Stock updated successfully.",
            ).model_dump(),
        )
    except IntegrityError:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=StandardResponse.error_response(
                message="Stock with this symbol already exists."
            ).model_dump(),
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update stock: {str(e)}",
        )
