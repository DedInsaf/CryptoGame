from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.models.user import User, CryptoOrder
from backend.app.utils.database import get_db
from backend.app.utils.price_generator import generate_crypto_prices

router = APIRouter()


@router.get("/prices")
def get_prices():
    return generate_crypto_prices()


@router.post("/buy")
def buy_crypto(
        user_id: int,
        crypto_name: str,
        amount: float,
        db: Session = Depends(get_db)
):
    # Получаем текущие цены
    prices = generate_crypto_prices()

    # Проверяем существование криптовалюты
    if crypto_name not in prices:
        raise HTTPException(status_code=404, detail="Crypto not found")

    # Получаем пользователя
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Рассчитываем стоимость
    price = prices[crypto_name]["price"]
    total_cost = round(amount * price, 2)

    # Проверяем баланс
    if user.balance < total_cost:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # Создаем ордер
    new_order = CryptoOrder(
        user_id=user_id,
        crypto_name=crypto_name,
        amount=amount,
        price=price
    )

    # Обновляем баланс
    user.balance -= total_cost

    # Сохраняем изменения
    db.add(new_order)
    db.commit()

    return {
        "status": "success",
        "message": f"Purchased {amount} {crypto_name} for {total_cost}",
        "new_balance": user.balance
    }