import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

async def generate_presentation_data(topic, slides_count, style, language, content_size, include_images):
    if not client:
        return {"title": "Ошибка", "slides": [{"title": "API Ключ не найден", "subtitle": "Добавьте GROQ_API_KEY в .env", "items": [{"heading": "Ошибка", "text": "Ключ отсутствует"}]}]}

    items_count = "4-6" if content_size.lower() == "detailed" else "3-4"
    
    system_prompt = f"""
    Ты - креативный директор и копирайтер SaaS-платформы. 
    Тема: "{topic}". Язык: {language}. Стиль: {style}. Слайдов: {slides_count}.
    
    ПРАВИЛО ДИЗАЙНА: Мы используем строгую блочную верстку (без картинок).
    Каждый слайд должен иметь ПОДЗАГОЛОВОК и набор ЭЛЕМЕНТОВ (items). 
    В каждом элементе должен быть короткий ЗАГОЛОВОК (2-3 слова) и ТЕКСТ (10-15 слов).
    Генерируй от {items_count} элементов на слайд.
    
    Верни строго валидный JSON:
    {{
      "title": "Главное название презентации",
      "slides": [
        {{
          "title": "Заголовок слайда",
          "subtitle": "Короткое вводное предложение, раскрывающее суть слайда",
          "items": [
            {{"heading": "Блок 1", "text": "Емкое описание для этого блока."}},
            {{"heading": "Блок 2", "text": "Емкое описание для этого блока."}}
          ]
        }}
      ]
    }}
    """
    
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Сделай структуру презентации: {topic}"}
            ],
            model="groq/compound",
            temperature=0.6,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match: 
            content = match.group(0)
        data = json.loads(content)
    except Exception as e:
        data = {
            "title": "Сбой генерации", 
            "slides": [{
                "title": "Сбой", 
                "subtitle": "Повторите запрос позже", 
                "items": [{"heading": "Ошибка", "text": str(e)}]
            }]
        }

    return data