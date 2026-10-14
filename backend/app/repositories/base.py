from typing import Any, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session

T = TypeVar("T")


class Repository[T]:
    def __init__(self, db: Session, model: type[T]):
        self.db, self.model = db, model

    def get(self, item_id: Any) -> T | None:
        return self.db.get(self.model, item_id)

    def list(self, page: int = 1, page_size: int = 20, order_by: Any = None) -> tuple[list[T], int]:
        query = select(self.model)
        query = query.order_by(order_by) if order_by is not None else query
        items = list(self.db.scalars(query.offset((page - 1) * page_size).limit(page_size)))
        total = self.db.scalar(select(func.count()).select_from(self.model)) or 0
        return items, total
