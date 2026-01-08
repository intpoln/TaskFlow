from pydantic import BaseModel


class CategoryAdd(BaseModel):
    title: str


class Category(CategoryAdd):
    id: int


class CategoryUpdate(BaseModel):
    title: str
