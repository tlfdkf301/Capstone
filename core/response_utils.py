# db포맷 맞추기 존나 헷갈려서 만듦
# db포맷 맞추기 dict 기반으로 수정
def format_clothes_response(cloth) -> dict:
    if isinstance(cloth, dict):
        return {
            "id": cloth.get("id"),
            "imageUri": cloth.get("image_url"),
            "mainCategory": cloth.get("maincategory"),
            "category": cloth.get("category"),
            "color": cloth.get("color"),
            "fit": cloth.get("fit"),
            "material": cloth.get("material"),
            "length": cloth.get("length"),
            "sleeveLength": cloth.get("sleeve_length"),
            "collar": cloth.get("collar")
        }
    else:  # SQLAlchemy ORM 객체
        return {
            "id": cloth.id,
            "imageUri": cloth.image_url,
            "mainCategory": cloth.maincategory,
            "category": cloth.category,
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