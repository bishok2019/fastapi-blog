# apps/common/pagination.py

from math import ceil
from typing import Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")
SchemaType = TypeVar("SchemaType")


class PaginationMeta(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    previous_page: Optional[int]
    next_page: Optional[int]


class CustomPagination(BaseModel, Generic[SchemaType]):
    data: List[SchemaType]
    meta: PaginationMeta


def paginate(
    *,
    query,
    page: int,
    page_size: int,
    schema: Type[SchemaType],
) -> CustomPagination[SchemaType]:
    if page < 1:
        raise ValueError("page must be >= 1")
    if page_size < 1 or page_size > 100:
        raise ValueError("page_size must be between 1 and 100")

    total = query.count()
    total_pages = ceil(total / page_size) if total else 1

    if page > total_pages:
        raise ValueError("Page not found")

    items = query.offset((page - 1) * page_size).limit(page_size).all()

    data = [schema.model_validate(item) for item in items]

    return CustomPagination(
        data=data,
        meta=PaginationMeta(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            previous_page=page - 1 if page > 1 else None,
            next_page=page + 1 if page < total_pages else None,
        ),
    )
