from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from requests import get

# OAuth2 Parameters
ACCESS_TOKEN_EXPIRE_MINUTES = 60


app = FastAPI()

# Item 02 response -----------------------------------------------
class Item(BaseModel):
    user: str
    order: float
    previousOrder: bool


@app.post("/items")
def create_item(item: Item):
    # falta a response
    return {
        "user": item.user,
        "order": item.order,
        "previous_order": item.previousOrder}
# Item 02 response -----------------------------------------------

# Item 03 response -----------------------------------------------
@app.get("/breweries")
def get_breweries():
    addresses = 'https://api.openbrewerydb.org/breweries/'
    r = get(url= addresses).json()
    response = []
    [response.append(item['name']) for item in r]
    return response
# Item 03 response -----------------------------------------------
