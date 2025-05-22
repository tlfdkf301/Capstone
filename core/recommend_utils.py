from core.preprocessing_utils import apply_style_predictions
from core.score_utils import calculate_tpo_scores, merge_scores_global_standardization, sort_items_by_score, tpo_score_table
from core.apriori_utils import score_recommendation_dict_sorted_key

def run_recommendation(
    selected_tpo: str,
    selected_clothing: list,
    color_dict: dict,
    feature_dict: dict,
    user_clothes: dict,
    top_n: int = 1
) -> dict:
    """
    선택된 옷 1벌과 TPO를 기준으로
    나머지 카테고리(상의, 하의, 아우터, 원피스 중 선택된 카테고리 제외)에 대해
    각 카테고리별로 top-N 추천 옷 ID를 반환
    """
    # 선택된 옷 ID에서 카테고리 추출
    selected_id = selected_clothing[0]
    selected_category = None
    for cat in user_clothes:
        for item in user_clothes[cat]:
            if item[0] == selected_id:
                selected_category = cat
                break
        if selected_category:
            break

    if selected_category is None:
        raise ValueError("선택된 아이템의 카테고리를 찾을 수 없습니다")

    # 스타일 예측 붙이기
    user_clothes = apply_style_predictions(user_clothes)

    # TPO 점수 계산
    tpo_scores = calculate_tpo_scores(user_clothes, tpo_score_table, selected_tpo)

    # 유사도 계산
    similarity_result = score_recommendation_dict_sorted_key(
        selected_clothing, selected_category, color_dict, feature_dict, user_clothes
    )

    # 점수 정규화 + 합산
    merged_score = merge_scores_global_standardization(similarity_result['recommendation'], tpo_scores)
    sorted_items = sort_items_by_score(merged_score)

    # 추천 결과에서 선택된 카테고리를 제외하고, top-N씩 추출
    result_by_category = {cat: [] for cat in user_clothes if cat != selected_category}
    for item_id, score in sorted_items:
        cat_prefix = item_id.split('_')[0]
        for cat in result_by_category:
            if cat.startswith(cat_prefix) and len(result_by_category[cat]) < top_n:
                result_by_category[cat].append(item_id)

    return result_by_category
