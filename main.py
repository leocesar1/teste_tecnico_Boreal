from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from passlib.context import CryptContext
from jose import JWTError, jwt

from requests import get


SECRET_KEY = 'ec4390a67a86e203bf75fd4682e7fcb91d1c98f29a1f1cbae0cfa3dd22c44fa8'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_users_db = {
    "geanderson": {
        "username": "geanderson",
        "full_name": "Geanderson Lenz",
        "email": "faraday_lenz@gmail.com",
        "hashed_password":   "$2b$12$yAHkQz9Bx0C43Hp4FksR4.K65yoqDpmZ57fPkckYZ5XIe4u4JMRi.", # senha: senhasecreta
        "disabled": False,
    },
    "leonardo": {
        "username": "leonardo",
        "full_name": "Leonardo Marques",
        "email": "leocesar.rj@gmail.com",
        "hashed_password":   "$2b$12$yAHkQz9Bx0C43Hp4FksR4.K65yoqDpmZ57fPkckYZ5XIe4u4JMRi.", # senha: senhasecreta
        "disabled": False,
    }
}

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def fake_decode_token(token):
    user = get_user(fake_users_db, token)
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="O usuário está inativo")
    return current_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorreta",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Item 02 response -----------------------------------------------
class Item(BaseModel):
    user: str
    order: float
    previousOrder: bool


@app.post("/items")
def create_item(item: Item, current_user: User = Depends(get_current_active_user)):
    return {
        "user": item.user,
        "order": item.order,
        "previous_order": item.previousOrder}
# Item 02 response -----------------------------------------------

# Item 03 response -----------------------------------------------
@app.get("/breweries")
def get_breweries(current_user: User = Depends(get_current_active_user)):
    addresses = 'https://api.openbrewerydb.org/breweries/'
    r = get(url= addresses).json()
    response = []
    [response.append(item['name']) for item in r]
    return response
# Item 03 response -----------------------------------------------