from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from auth import create_access_token, get_password_hash, verify_password, repo

auth_router = APIRouter(prefix="/auth")


@auth_router.post("/register")
def register(username: str, email: str, password: str):
    hashed = get_password_hash(password)
    try:
        user = repo.create_user(username, email, password_hash=hashed)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"id": user.id, "username": user.username}


@auth_router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # form_data.username contains username
    # allow login by username or email
    users = repo.list_users()
    user = next((u for u in users if u.username == form_data.username or u.email == form_data.username), None)
    if not user or not user.hashed_password or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
