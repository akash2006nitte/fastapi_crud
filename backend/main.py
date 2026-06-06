from fastapi import FastAPI
from routers.instagram_router import instagram_router
app = FastAPI()


app.include_router(instagram_router)

@app.get("/")
async def root():
    return {"message": "Instagram-like backend is running"}
