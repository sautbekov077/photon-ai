import os
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Image Selection Microservice")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

FALLBACK_IMAGE_URL = (
    "https://images.unsplash.com/photo-1557426272-fc759fdf7a8d"
    "?w=800&auto=format&fit=crop"
)


class ImageRequest(BaseModel):
    query: str
    language: str = "ru"


class ImageResponse(BaseModel):
    url: str
    source: str


async def search_unsplash(query: str) -> str | None:
    if not UNSPLASH_ACCESS_KEY:
        return None
    url = "https://api.unsplash.com/search/photos"
    params = {"query": query, "per_page": 1, "orientation": "landscape"}
    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            if results:
                return results[0]["urls"]["regular"]
    return None


async def search_pexels(query: str) -> str | None:
    if not PEXELS_API_KEY:
        return None
    url = "https://api.pexels.com/v1/search"
    params = {"query": query, "per_page": 1, "orientation": "landscape"}
    headers = {"Authorization": PEXELS_API_KEY}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            photos = data.get("photos", [])
            if photos:
                return photos[0]["src"]["large"]
    return None


@app.get("/health")
async def health():
    return {"status": "ok", "service": "image-service"}


@app.post("/get-image", response_model=ImageResponse)
async def get_image(req: ImageRequest):
    # Translate query to English if needed for better search results
    search_query = req.query

    image_url = await search_unsplash(search_query)
    if image_url:
        return ImageResponse(url=image_url, source="unsplash")

    image_url = await search_pexels(search_query)
    if image_url:
        return ImageResponse(url=image_url, source="pexels")

    return ImageResponse(url=FALLBACK_IMAGE_URL, source="fallback")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
