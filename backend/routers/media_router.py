from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path

router = APIRouter(prefix="/media")

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    if file.content_type.split("/")[0] != "image":
        raise HTTPException(status_code=400, detail="Invalid image type")
    dest = UPLOAD_DIR / file.filename
    # prevent overwriting by appending timestamp if exists
    if dest.exists():
        import time
        dest = UPLOAD_DIR / f"{int(time.time())}_{file.filename}"
    with open(dest, "wb") as f:
        content = await file.read()
        f.write(content)
    url = f"/static/uploads/{dest.name}"
    return JSONResponse({"url": url})
