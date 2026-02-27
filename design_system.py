import random

THEMES = {
    "modern-blue": {
        "id": "modern-blue", "name": "Corporate Blue",
        "bg": "#f8fafc", "primary": "#2563eb", "accent": "#dbeafe", 
        "text_dark": "#0f172a", "text_gray": "#475569"
    },
    "warm-sunset": {
        "id": "warm-sunset", "name": "Creative Orange",
        "bg": "#fffbeb", "primary": "#ea580c", "accent": "#ffedd5", 
        "text_dark": "#431407", "text_gray": "#9a3412"
    },
    "dark-elegant": {
        "id": "dark-elegant", "name": "Dark Mode",
        "bg": "#111827", "primary": "#10b981", "accent": "#374151", 
        "text_dark": "#f9fafb", "text_gray": "#9ca3af"
    },
    "green-nature": {
        "id": "green-nature", "name": "Green Eco",
        "bg": "#ffffff", "primary": "#16a34a", "accent": "#dcfce7", 
        "text_dark": "#14532d", "text_gray": "#166534"
    }
}

def get_all_themes(): 
    return list(THEMES.values())

def pick_theme(selected_theme=None):
    if selected_theme and selected_theme in THEMES: 
        return THEMES[selected_theme]
    return THEMES["modern-blue"]

def apply_design(presentation_data, design_theme, design_mode, design_randomness):
    presentation_data["theme"] = pick_theme(design_theme)
    
    slides = presentation_data.get("slides") or []
    for i, slide in enumerate(slides):
        items = slide.get("items") or [] # Если items = null, будет []
        items_count = len(items)
        
        if i == 0:
            slide["layout"] = "hero_center" 
        elif items_count <= 2:
            slide["layout"] = "large_cards" 
        elif items_count == 3:
            slide["layout"] = "grid_3_cols" 
        else:
            slide["layout"] = "grid_2x2" 
            
    return presentation_data