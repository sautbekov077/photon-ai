from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional
from ai_engine import generate_presentation_data
from design_system import apply_design, get_all_themes
from exporter import export_to_pdf, export_to_pptx

app = FastAPI(title="Photon AI")

class GenerateRequest(BaseModel):
    topic: str
    slides_count: int
    style: str
    language: str
    content_size: str
    include_images: bool
    format: str
    # Новые параметры дизайна:
    design_theme: Optional[str] = None
    design_mode: str = "creative"
    design_randomness: int = 50

@app.get("/")
async def serve_frontend():
    return FileResponse("index.html")

# Новый эндпоинт для селектора тем
@app.get("/themes")
async def get_themes():
    return {"themes": get_all_themes()}

@app.post("/generate")
async def generate_presentation(req: GenerateRequest):
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Тема не может быть пустой")
    if not (1 <= req.slides_count <= 15):
        raise HTTPException(status_code=400, detail="Разрешено от 1 до 15 слайдов")

    # 1. Генерируем "голый" контент
    raw_data = await generate_presentation_data(
        topic=req.topic,
        slides_count=req.slides_count,
        style=req.style,
        language=req.language,
        content_size=req.content_size,
        include_images=req.include_images
    )

    # 2. Оборачиваем в дизайн-систему (Тема, Layouts, Декорации)
    presentation_data = apply_design(
        raw_data, 
        design_theme=req.design_theme,
        design_mode=req.design_mode,
        design_randomness=req.design_randomness
    )

    # 3. Экспорт с учетом дизайна
    if req.format.upper() == "PDF":
        file_stream = export_to_pdf(presentation_data)
        media_type = "application/pdf"
        filename = "presentation.pdf"
    else:
        file_stream = export_to_pptx(presentation_data)
        media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        filename = "presentation.pptx"

    return StreamingResponse(
        file_stream, 
        media_type=media_type, 
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )