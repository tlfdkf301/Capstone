# user_clothes에 style 확률 삽입


from core.dmlp_predictor import predict_top3_tpo
import torch
# def apply_style_predictions(user_clothes, model, mlb, label_to_idx, device='cpu'):
#     """
#     user_clothes에 스타일 확률 예측 결과 삽입
#     """
#     for category, clothes_list in user_clothes.items():
#         for i, item in enumerate(clothes_list):
#             item_features = item[2:]  # feature만 추출
#             prediction = predict_top3_tpo(
#                 items=item_features,
#                 device=device
#                 )
#             # [id, style_probs, feature1, feature2, ...] 형식으로 변환
#             user_clothes[category][i] = [item[0], prediction] + item[1:]
#     return user_clothes

def apply_style_predictions(user_clothes, model, mlb, label_to_idx, device='cpu'):
    """
    user_clothes에 스타일 확률 예측 결과 삽입
    """
    for category, clothes_list in user_clothes.items():
        for i, item in enumerate(clothes_list):
            item_features = item[2:]  # ✅ style_probs(dict) 건너뜀
            prediction = predict_top3_tpo(
                items=item_features,
                model=model,
                mlb=mlb,
                label_to_idx=label_to_idx,
                device=device
            )
            # [id, style_probs, feature1, ...]
            user_clothes[category][i] = [item[0], prediction] + item[2:]
    return user_clothes

def apply_style_predictions_single(features, model, mlb, label_map):
    """
    단일 아이템 스타일 예측
    """
    import numpy as np

    encoded = mlb.transform([features])
    input_tensor = torch.tensor(encoded).float()
    model.eval()
    with torch.no_grad():
        logits = model(input_tensor)
        probs = torch.softmax(logits, dim=1).squeeze().cpu().numpy()
    label_probs = {label: float(prob) for label, prob in zip(label_map.keys(), probs)}
    top3 = dict(sorted(label_probs.items(), key=lambda x: x[1], reverse=True)[:3])
    return top3