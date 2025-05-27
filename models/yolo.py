from ultralytics import YOLO

class_names = [
    "coat", "jacket", "jumper", "cardigan", "blouse", "t-shirt", "sweater",
    "shirt", "vest", "onepiece(dress)", "onepiece(jumpsuit)",
    "pants", "skirt", "jeans", "leggings", "jogger"
]
main_category_map = {
    "coat": "outer",
    "jacket": "outer",
    "jumper": "outer",
    "cardigan": "outer",
    "blouse": "top",
    "t-shirt": "top",
    "sweater": "top",
    "shirt": "top",
    "vest": "top",
    "onepiece(dress)": "dress",
    "onepiece(jumpsuit)": "dress",
    "pants": "bottom",
    "skirt": "bottom",
    "jeans": "bottom",
    "leggings": "bottom",
    "jogger": "bottom"
}


YOLO_MODEL_PATH = "models/weights/YOLO_best_model.pt"

def run_yolo(image_path: str) -> str:
    model = YOLO(YOLO_MODEL_PATH)
    results = model.predict(source=image_path, task='segment', save=False)
    cls_id = int(results[0].boxes.cls[0])
    subcategory = class_names[cls_id]
    main_category = main_category_map.get(subcategory, "unknown")
    return {
        "mainCategory": main_category,
        "category": subcategory
    }
