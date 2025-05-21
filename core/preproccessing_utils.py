# user_clothes에 style 확률 삽입


from core.dmlp_predictor import predict_top3_tpo

def apply_style_predictions(user_clothes, model, mlb, label_to_idx, device='cpu'):
    """
    user_clothes에 스타일 확률 예측 결과 삽입
    """
    for category, clothes_list in user_clothes.items():
        for i, item in enumerate(clothes_list):
            item_features = item[1:]  # feature만 추출
            prediction = predict_top3_tpo(
                items=item_features,
                model=model,
                mlb=mlb,
                label_to_idx=label_to_idx,
                device=device
            )
            # [id, style_probs, feature1, feature2, ...] 형식으로 변환
            user_clothes[category][i] = [item[0], prediction] + item[1:]
    return user_clothes