from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.sql import func

from app.models.reviews import Review as ReviewModel
from app.models.products import Product as ProductModel
from app.schemas import ReviewCreate, Review as ReviewSchema
from app.db_depends import get_async_db
from app.models.users import User as UserModel
from app.auth import get_buyer, get_admin

# Маршрутизатор для отзывов
router = APIRouter(prefix="/reviews", tags=["reviews"])


async def update_product_rating(db: AsyncSession, product_id: int) -> None:
    """
    Пересчёт рейтинга товара после добавления или удаления отзыва
    """

    result = await db.execute(
        select(func.avg(ReviewModel.grade)).where(
            ReviewModel.product_id == product_id,
            ReviewModel.is_active == True
        )
    )
    avg_rating = result.scalar() or 0.0
    product = await db.get(ProductModel, product_id)
    product.rating = avg_rating
    await db.commit()

@router.get("/", response_model=list[ReviewSchema])
async def get_all_reviews(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех отзывов.
    """

    result = await db.scalars(select(ReviewModel).where(ReviewModel.is_active == True))
    reviews = result.all()
    return reviews

@router.get("/products/{product_id}/reviews/", response_model=list[ReviewSchema], status_code=status.HTTP_200_OK)
async def get_review_by_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает отзывы о товаре по его ID.
    """

    # Проверка существования product_id
    result = await db.scalars(
        select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True)
    )
    product = result.first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")

    result = await db.scalars(select(ReviewModel).where(ReviewModel.is_active == True).where(ReviewModel.product_id == product_id))
    reviews = result.all()
    return reviews

@router.post("/", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(
    review: ReviewCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_buyer)
):
    """
    Создаёт новый отзыв для указанного товара (только для 'buyer').
    """

    # Проверка существования product_id
    result = await db.scalars(
        select(ProductModel).where(ProductModel.id == review.product_id, ProductModel.is_active == True)
    )
    if not result.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")

    # Проверка корректности оценки
    if not 1 <= review.grade <= 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Grade should be from 1 to 5")

    db_review = ReviewModel(**review.model_dump(), user_id=current_user.id)
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)  # Для получения id и is_active из базы
    await update_product_rating(db, review.product_id) # Пересчёт рейтинга
    await db.commit()
    return db_review

@router.delete("/{review_id}")
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_admin)
):
    """
    Выполняет мягкое удаление отзыва (только для 'admin').
    """

    # Проверка существования отзыва и его активности
    result = await db.scalars(
        select(ReviewModel).where(ReviewModel.id == review_id, ReviewModel.is_active == True)
    )
    review = result.first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found or inactive")

    await db.execute(
        update(ReviewModel).where(ReviewModel.id == review_id).values(is_active=False)
    )
    await db.commit()
    await db.refresh(review)  # Для возврата is_active = False
    await update_product_rating(db, review.product_id) # Пересчёт рейтинга
    return {"message": "Review deleted"}
