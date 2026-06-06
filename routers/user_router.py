from fastapi import APIRouter
from repository.user_repository import UserRepository


user_router = APIRouter()
user_repo = UserRepository()

@user_router.post("/users/")
async def create_user(user: dict):
    user_repo.add_user(user)
    return {"message": "User created successfully"}