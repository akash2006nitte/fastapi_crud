from fastapi import APIRouter
from repository.user_repository import UserRepository
from schemas.user_schemas import UserCreate, UserUpdate

user_router = APIRouter()
user_repo = UserRepository()

@user_router.post("/users/")
async def create_user(user: UserCreate):
    newuser=user_repo.add_user(user)
    return {"message": "User created successfully", "user": newuser}

@user_router.get("/users/{user_id}")
async def read_user(user_id: int):
    user = user_repo.get_user(user_id)
    if user:
        return {"user": user}
    return {"message": "User not found"}

@user_router.put("/users/{user_id}")
async def update_user(user_id: int, user: UserUpdate):
    success = user_repo.update_user(user_id, user.name, user.email)
    if success:
        return {"message": "User updated successfully"}
    return {"message": "User not found"}

@user_router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    success = user_repo.delete_user(user_id)
    if success:
        return {"message": "User deleted successfully"}
    return {"message": "User not found"}

@user_router.get("/users/")
async def read_users():
    users = user_repo.get_all_users()
    return {"users": users}