from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.instagram_router import instagram_router

app = FastAPI()

# Allow local frontend during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(instagram_router)

@app.get("/")
async def root():
    return {"message": "Instagram-like backend is running"}
