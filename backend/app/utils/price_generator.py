import random
from typing import Dict

CRYPTOS = {
    "KidCoin": {"min_price": 1, "max_price": 50, "emoji": "👦"},
    "EduToken": {"min_price": 10, "max_price": 100, "emoji": "🎓"},
    "CryptoStar": {"min_price": 5, "max_price": 75, "emoji": "⭐"},
}

def generate_crypto_prices() -> Dict[str, dict]:
    return {
        name: {
            "price": round(random.uniform(data["min_price"], data["max_price"]), 2),
            "emoji": data["emoji"]
        }
        for name, data in CRYPTOS.items()
    }