from sqlite3 import IntegrityError

from fastapi import APIRouter, HTTPException, status
from repository.user_repository import UserRepository
from schemas.user_schemas import UserCreate, UserUpdate

user_router = APIRouter()
user_repo = UserRepository()

@user_router.post("/users/")
async def create_user(user: UserCreate):
    try:
        new_user = user_repo.add_user(user.name, user.email)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )
    return {"message": "User created successfully", "user": new_user.__dict__}

@user_router.get("/users/{user_id}")
async def read_user(user_id: int):
    user = user_repo.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return {"user": user.__dict__}

@user_router.put("/users/{user_id}")
async def update_user(user_id: int, user: UserUpdate):
    success = user_repo.update_user(user_id, user.name, user.email)
    if success:
        return {"message": "User updated successfully"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found",
    )

@user_router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    success = user_repo.delete_user(user_id)
    if success:
        return {"message": "User deleted successfully"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found",
    )

@user_router.get("/users/")
async def read_users():
    users = user_repo.get_all_users()
    return {"users": [user.__dict__ for user in users]}