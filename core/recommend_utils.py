from core.preprocessing_utils import apply_style_predictions
from core.score_utils import calculate_tpo_scores, merge_scores_global_standardization, sort_items_by_score, tpo_score_table
from core.apriori_utils import score_recommendation_dict_sorted_key
from core.dmlp_predictor import model, mlb, LABEL_MAP
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
from tqdm import tqdm
import pandas as pd

def get_top_items_by_category(sorted_result):
    """
    주어진 (아이템ID, 점수) 리스트에서 카테고리(상의, 하의 등)별 최고 점수 아이템 ID들을 추출.
    동점인 경우 모두 포함하여 반환.

    Args:
        sorted_result (List[Tuple[str, float]]): 예: [('상의_123', 1.2), ('하의_456', 2.3), ...]

    Returns:
        Dict[str, List[str]]: 각 카테고리별 최고 점수 아이템 ID 목록
    """
    # 카테고리별로 아이템 분류
    grouped = defaultdict(list)
    for item_id, score in sorted_result:
        category = item_id.split('_')[0]
        grouped[category].append((item_id, score))

    # 각 카테고리별 최고 점수 아이템 찾기
    top_items_by_category = {}
    for category, items in grouped.items():
        max_score = max(score for _, score in items)
        top_items = [item_id for item_id, score in items if score == max_score]
        top_items_by_category[category] = top_items

    return top_items_by_category

# feature 리스트를 dict로 바꾸는 함수
def parse_feature_list_to_dict(feature_list):
    result = {}
    for feature in feature_list:
        if "_" in feature:
            k, v = feature.split("_", 1)
            result[k] = v
    return result

def recommend_clothes_parallel_sorted(validation_input_dict, color_dict, feature_dict, user_clothes, color_rate=1):
    args = []

    for cat, items in validation_input_dict.items():
        for item in items:
            args.append((item, cat, color_dict, feature_dict, user_clothes, color_rate))

    results = []

    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        futures = [executor.submit(score_recommendation_dict_sorted_key, *arg) for arg in args]
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing recommendations"):
            results.append(future.result())

    return pd.DataFrame(results)

def run_recommendation(selected_tpo, selected_clothing, color_dict, feature_dict, user_clothes, tpo_score_table):
    # ✅ 선택된 옷 종류 추출
    clothing_type = selected_clothing[2].split('_')[0]

    # ✅ input 딕셔너리 구성
    input_dict = {clothing_type: [selected_clothing]}

    # 추천 점수 계산
    score_f = recommend_clothes_parallel_sorted(input_dict, color_dict, feature_dict, user_clothes)
    result_tpo = calculate_tpo_scores(user_clothes, tpo_score_table, selected_tpo)
    result = merge_scores_global_standardization(score_f['recommendation'].loc[0], result_tpo)
    sorted_result = sort_items_by_score(result)
    top_items_by_category = get_top_items_by_category(sorted_result)

    # ✅ 필터링 기준 정의
    category_filter_map = {
        "아우터": {"상의", "하의", "원피스"},
        "상의": {"아우터", "하의"},
        "하의": {"아우터", "상의"},
        "원피스": {"아우터"},
    }

    allowed_categories = category_filter_map.get(clothing_type, set())
    filtered_result = {
        cat: items for cat, items in top_items_by_category.items() if cat in allowed_categories
    }

    return filtered_result
