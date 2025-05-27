from core.ai_label_to_kfashion import color_map, fiber_map, fit_map, sleeve_map, top_length_map
from core.feature_prefix_map import prefix_map

def map_ai_attributes_to_features(attributes: dict) -> list[str]:
    result = []

    if "color" in attributes:
        val = color_map.get(attributes["color"])
        if val: result.append(f"{prefix_map['color']}_{val}")

    if "fiber" in attributes:
        val = fiber_map.get(attributes["fiber"])
        if val: result.append(f"{prefix_map['fiber']}_{val}")

    if "pants_silhouette" in attributes:
        val = fit_map.get(attributes["pants_silhouette"])
        if val: result.append(f"{prefix_map['pants_silhouette']}_{val}")

    if "sleeve_length" in attributes:
        val = sleeve_map.get(attributes["sleeve_length"])
        if val: result.append(f"{prefix_map['sleeve_length']}_{val}")

    if "top_length" in attributes:
        val = top_length_map.get(attributes["top_length"])
        if val: result.append(f"{prefix_map['top_length']}_{val}")

    return result
