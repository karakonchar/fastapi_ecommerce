from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime

class CategoryCreate(BaseModel):
    """
    Модель для создания и обновления категории.
    Используется в POST и PUT запросах.
    """
    name: str = Field(min_length=3, max_length=50,
                      description="Название категории (3-50 символов)")
    parent_id: Optional[int] = Field(None, description="ID родительской категории, если есть")


class Category(BaseModel):
    """
    Модель для ответа с данными категории.
    Используется в GET-запросах.
    """
    id: int = Field(description="Уникальный идентификатор категории")
    name: str = Field(description="Название категории")
    parent_id: Optional[int] = Field(None, description="ID родительской категории, если есть")
    is_active: bool = Field(description="Активность категории")

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    """
    Модель для создания и обновления товара.
    Используется в POST и PUT запросах.
    """
    name: str = Field(min_length=3, max_length=100,
                      description="Название товара (3-100 символов)")
    description: Optional[str] = Field(None, max_length=500,
                                       description="Описание товара (до 500 символов)")
    price: float = Field(gt=0, description="Цена товара (больше 0)")
    image_url: Optional[str] = Field(None, max_length=200, description="URL изображения товара")
    stock: int = Field(ge=0, description="Количество товара на складе (0 или больше)")
    category_id: int = Field(description="ID категории, к которой относится товар")


class Product(BaseModel):
    """
    Модель для ответа с данными товара.
    Используется в GET-запросах.
    """
    id: int = Field(description="Уникальный идентификатор товара")
    name: str = Field(description="Название товара")
    description: Optional[str] = Field(None, description="Описание товара")
    price: float = Field(description="Цена товара")
    image_url: Optional[str] = Field(None, description="URL изображения товара")
    stock: int = Field(description="Количество товара на складе")
    category_id: int = Field(description="ID категории")
    is_active: bool = Field(description="Активность товара")
    rating: float = Field(description="Рейтинг товара")

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    """
    Модель для создания пользователя.
    Используется в POST запросах.
    """
    email: EmailStr = Field(description="Email пользователя")
    password: str = Field(min_length=8, description="Пароль (минимум 8 символов)")
    role: str = Field(default="buyer", pattern="^(buyer|seller|admin)$", description="Роль: 'buyer' или 'seller'")

class User(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    role: str
    model_config = ConfigDict(from_attributes=True)

class ReviewCreate(BaseModel):
    """
    Модель для создания отзыва.
    Используется в POST запросах.
    """
    product_id: int = Field(description="ID товара, к которому относится отзыв")
    comment: Optional[str] = Field(None, description="Текстовое поле для отзыва")
    grade: int = Field(description="Оценка товара от 1 до 5")

class Review(BaseModel):
    """
    Модель для ответа с отзывом о товаре.
    Используется в GET-запросах.
    """
    id: int = Field(description="Уникальный идентификатор отзыва")
    user_id: int = Field(description="ID пользователя, котороый написал отзыв")
    product_id: int = Field(description="ID товара, к которому относится отзыв")
    comment: Optional[str] = Field(None, description="Текстовое поле для отзыва")
    comment_date: datetime = Field(description="Поле даты и времени")
    grade: int = Field(ge=1, le=5, description="Оценка товара от 1 до 5")
    is_active: bool = Field(description="Активность отзыва")

    model_config = ConfigDict(from_attributes=True)


