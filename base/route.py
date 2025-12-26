from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from apps.database import get_db

from .pagination import paginate

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")
ReadSchemaType = TypeVar("ReadSchemaType")


class StandardResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[str] = None
    errors: Optional[List[Dict[str, str]]] = None
    meta: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    )

    @classmethod
    def success_response(
        cls,
        data: Any = None,
        message: str = "Operation successful",
        meta: Optional[Dict[str, Any]] = None,
    ) -> "StandardResponse":
        return cls(
            success=True,
            data=data,
            message=message,
            # meta=meta,
            **({} if meta is None else {"meta": meta}),
        )

    @classmethod
    def error_response(
        cls,
        message: str = "Error occurred",
        error: Optional[str] = None,
        errors: Optional[List[Dict[str, str]]] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> "StandardResponse":
        return cls(
            success=False,
            message=message,
            error=error,
            errors=errors,
            # meta=meta,
            **({} if meta is None else {"meta": meta}),
        )


class CreateRouter(Generic[ModelType, CreateSchemaType]):
    def __init__(
        self,
        model: Type[ModelType],
        schema: Type[CreateSchemaType],
        prefix: str = "",
        tags: list[str] | None = None,
    ):
        if prefix and not prefix.startswith("/"):
            prefix = "/" + prefix
        self.model = model
        self.schema = schema
        self.router = APIRouter(prefix=prefix, tags=tags)
        self.router.post("", response_model=StandardResponse)(self.create)

    def create(self, item: CreateSchemaType, db: Session = Depends(get_db)):
        db_item = self.model(**item.model_dump())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return StandardResponse(
            success=True,
            data=self.schema.model_validate(db_item),
            message="Created successfully",
        )


class ReadRouter(Generic[ModelType, ReadSchemaType]):
    def __init__(
        self,
        model: Type[ModelType],
        schema: Type[ReadSchemaType],
        prefix: str = "",
        tags: list[str] | None = None,
    ):
        if prefix and not prefix.startswith("/"):
            prefix = "/" + prefix
        self.model = model
        self.schema = schema
        self.router = APIRouter(prefix=prefix, tags=tags)
        self.router.get("", response_model=StandardResponse)(self.read_all)

    def read_all(
        self, page: int = 1, page_size: int = 10, db: Session = Depends(get_db)
    ):
        try:
            result = paginate(
                query=db.query(self.model),
                page=page,
                page_size=page_size,
                schema=self.schema,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

        # Convert meta to dict if needed
        meta_dict = (
            result.meta.model_dump()
            if hasattr(result.meta, "model_dump")
            else dict(result.meta)
        )
        meta_dict["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return StandardResponse(
            success=True,
            data=result.data,
            message="Retrieved successfully",
            meta=meta_dict,
        )


class RetrieveRouter(Generic[ModelType, ReadSchemaType]):
    def __init__(
        self,
        model: Type[ModelType],
        schema: Type[ReadSchemaType],
        prefix: str = "",
        tags: list[str] | None = None,
    ):
        if prefix and not prefix.startswith("/"):
            prefix = "" + prefix
        self.model = model
        self.schema = schema
        self.router = APIRouter(prefix=prefix, tags=tags)
        self.router.get("", response_model=StandardResponse)(self.retrieve)

    def retrieve(self, id: int, db: Session = Depends(get_db)):
        db_item = db.query(self.model).filter(self.model.id == id).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="Not found")
        return StandardResponse(
            success=True,
            data=self.schema.model_validate(db_item),
            message="Retrieved successfully",
        )


class UpdateRouter(Generic[ModelType, UpdateSchemaType, ReadSchemaType]):
    def __init__(
        self,
        model: Type[ModelType],
        update_schema: Type[UpdateSchemaType],
        read_schema: Type[ReadSchemaType],
        prefix: str = "",
        tags: list[str] | None = None,
    ):
        if prefix and not prefix.startswith("/"):
            prefix = "/" + prefix
        self.model = model
        self.update_schema = update_schema
        self.read_schema = read_schema
        self.router = APIRouter(prefix=prefix, tags=tags)
        self.router.patch("", response_model=StandardResponse)(self.update)

    def update(self, id: int, item: UpdateSchemaType, db: Session = Depends(get_db)):
        db_item = db.query(self.model).filter(self.model.id == id).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="Not found")
        for field, value in item.model_dump(exclude_unset=True).items():
            setattr(db_item, field, value)
        db.commit()
        db.refresh(db_item)
        return StandardResponse(
            success=True,
            data=self.read_schema.model_validate(db_item),
            message="Updated successfully",
        )
