from fastapi import APIRouter, HTTPException
from ..utils.price_generator import generate_crypto_prices

router = APIRouter()

@router.get("/prices")
async def get_prices():
    return generate_crypto_prices()

@router.get("/price/{crypto_name}")
async def get_price(crypto_name: str):
    prices = generate_crypto_prices()
    if crypto_name not in prices:
        raise HTTPException(status_code=404, detail="Криптовалюта не найдена")
    return {"crypto": crypto_name, "price": prices[crypto_name]}