from core.preprocessing_utils import apply_style_predictions
from core.score_utils import calculate_tpo_scores, merge_scores_global_standardization, sort_items_by_score, tpo_score_table
from core.apriori_utils import score_recommendation_dict_sorted_key

def run_recommendation(
    selected_tpo: str,
    selected_clothing: dict,  # dict로 받음
    color_dict: dict,
    feature_dict: dict,
    user_clothes: dict,
    top_n: int = 1
) -> dict:
    """
    선택된 옷(dict)과 TPO를 기준으로
    나머지 카테고리에 대해 top-N 추천 (dict 형태로 반환)
    """

    selected_id = selected_clothing["id"]
    selected_category = selected_clothing["category"]

    # 스타일 예측 붙이기
    user_clothes = apply_style_predictions(user_clothes)

    # TPO 점수 계산
    tpo_scores = calculate_tpo_scores(user_clothes, tpo_score_table, selected_tpo)

    # 유사도 계산 (기존 함수는 리스트로 받으니 감싸줌)
    similarity_result = score_recommendation_dict_sorted_key(
        selected_clothing_list=[selected_clothing],
        selected_category=selected_category,
        color_dict=color_dict,
        feature_dict=feature_dict,
        user_clothes=user_clothes
    )

    # 점수 병합 및 정렬
    merged_score = merge_scores_global_standardization(similarity_result["recommendation"], tpo_scores)
    sorted_items = sort_items_by_score(merged_score)

    # 추천 결과 변환 (ID 리스트 → dict 리스트)
    result_by_category = {cat: [] for cat in user_clothes if cat != selected_category}

    for item_id, score in sorted_items:
        cat_prefix = item_id.split('_')[0]

        for cat in result_by_category:
            if cat.startswith(cat_prefix) and len(result_by_category[cat]) < top_n:
                # 해당 아이템의 feature dict 찾아서 반환
                for item in user_clothes[cat]:
                    if item[0] == item_id:
                        feature_dict = item[2]  # [id, style_probs, feature_dict]
                        result_by_category[cat].append({
                            "id": item_id,
                            **feature_dict
                        })

    return result_by_category
