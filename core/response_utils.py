# db포맷 맞추기 존나 헷갈려서 만듦
def format_clothes_response(cloth) -> dict:
    return {
        "id": cloth.id,
        "imageUri": cloth.image_url,
        "mainCategory": cloth.category,
        "category": cloth.subcategory,
        "color": cloth.color,
        "fit": cloth.fit,
        "material": cloth.material,
        "length": cloth.length,
        "sleeveLength": cloth.sleeve_length,
        "collar": cloth.collar
    }

def format_recommendation_response(selected_item_id: str, tpo: str, result_dict: dict) -> dict:
    from .closet_utils import get_clothing_by_id

    formatted = []
    for category, items in result_dict.items():
        formatted_items = [format_clothes_response(item) for item in items]
        formatted.append({
            "mainCategory": category,
            "items": formatted_items
        })

    return {
        "selected_item_id": selected_item_id,
        "tpo": tpo,
        "recommendations": formatted
    }