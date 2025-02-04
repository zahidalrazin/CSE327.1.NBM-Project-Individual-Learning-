from typing import Union, Optional
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI example!"}

@app.get("/items/{item_id}")
def read_item(
    item_id: int,
    q: Optional[str] = Query(None, min_length=3, max_length=50, description="Query string"),
    price: Optional[float] = Query(None, gt=0, description="Price of the item")
):
    return {
        "item_id": item_id,
        "query": q,
        "price": price
    }