from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi import Request, Form


app = FastAPI()


@app.post("/signup")
def signup(username: str, password: str, db: Session = Depends(get_db)):
    user = User(username=username, password=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created successfully", "user_id": user.id}


Login (POST /login)

@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or user.password != password:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    # Here you would generate a JWT token for the user
    return {"access_token": "jwt_token", "token_type": "bearer"}

from typing import List

@app.get("/flowers", response_model=List[Flower])
def get_flowers(db: Session = Depends(get_db)):
    return db.query(Flower).all()

@app.post("/flowers")
def add_flower(name: str, price: float, db: Session = Depends(get_db)):
    flower = Flower(name=name, price=price)
    db.add(flower)
    db.commit()
    db.refresh(flower)
    return {"flower_id": flower.id}

@app.patch("/flowers/{flower_id}")
def update_flower(flower_id: int, name: str = None, price: float = None, db: Session = Depends(get_db)):
    flower = db.query(Flower).filter(Flower.id == flower_id).first()
    if not flower:
        raise HTTPException(status_code=404, detail="Flower not found")
    if name:
        flower.name = name
    if price:
        flower.price = price
    db.commit()
    return {"message": "Flower updated"}

@app.delete("/flowers/{flower_id}")
def delete_flower(flower_id: int, db: Session = Depends(get_db)):
    flower = db.query(Flower).filter(Flower.id == flower_id).first()
    if not flower:
        raise HTTPException(status_code=404, detail="Flower not found")
    db.delete(flower)
    db.commit()
    return {"message": "Flower deleted"}



Cart (POST /cart/items, GET /cart/items)

@app.post("/cart/items")
def add_to_cart(flower_id: int = Form(), request: Request):
    cart = request.session.get("cart", [])
    cart.append(flower_id)
    request.session["cart"] = cart
    return {"message": "Flower added to cart"}

@app.get("/cart/items")
def get_cart_items(request: Request, db: Session = Depends(get_db)):
    cart = request.session.get("cart", [])
    flowers = db.query(Flower).filter(Flower.id.in_(cart)).all()
    total_price = sum([flower.price for flower in flowers])
    return {"flowers": flowers, "total_price": total_price}


@app.post("/purchased")
def purchase_items(request: Request, db: Session = Depends(get_db)):
    user_id = 1  # Example user ID
    cart = request.session.get("cart", [])
    for flower_id in cart:
        purchase = Purchase(user_id=user_id, flower_id=flower_id)
        db.add(purchase)
    db.commit()
    request.session["cart"] = []  # Clear the cart after purchase
    return {"message": "Purchase successful"}

@app.get("/purchased")
def get_purchased_items(user_id: int = 1, db: Session = Depends(get_db)):
    purchases = db.query(Purchase).filter(Purchase.user_id == user_id).all()
    flower_ids = [purchase.flower_id for purchase in purchases]
    flowers = db.query(Flower).filter(Flower.id.in_(flower_ids)).all()
    return {"purchased_flowers": flowers}
