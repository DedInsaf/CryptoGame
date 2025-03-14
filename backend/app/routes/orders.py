from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.user import CryptoOrder, User
from ..utils.database import get_db

router = APIRouter()


@router.post("/buy")
async def buy_crypto(
        crypto_name: str,
        amount: float,
        user_id: int,
        db: Session = Depends(get_db)
):
    # Получить текущую цену (заглушка)
    current_price = 30.0  # Здесь можно вызвать generate_crypto_prices()

    # Проверить баланс пользователя
    user = db.query(User).filter(User.id == user_id).first()
    total_cost = amount * current_price

    if user.balance < total_cost:
        raise HTTPException(status_code=400, detail="Недостаточно средств")

    # Создать ордер
    order = CryptoOrder(
        user_id=user_id,
        crypto_name=crypto_name,
        amount=amount,
        price=current_price
    )

    # Обновить баланс
    user.balance -= total_cost
    db.add(order)
    db.commit()

    return {"status": "success", "message": f"Куплено {amount} {crypto_name}"}