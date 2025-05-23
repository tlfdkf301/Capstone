# TPO 점수계산, 정규화, 합산, 정렬
import numpy as np

tpo_score_table = {'데일리': {
  '스트리트': 0.52858794,
  '클래식': 0.29832992,
  '로맨틱': 0.530706,
  '펑크': 0.25430354,
  '페미닌': 0.4762796,
  '스포티': 0.46903458,
  '힙합': 0.32017642,
  '모던': 0.61891097,
  '프레피': 0.59357345,
  '톰보이': 0.4324854,
  '레트로': 0.56764644,
  '키치': 0.47647268,
  '아방가르드': 0.22979008,
  '오리엔탈': 0.32786918,
  '웨스턴': 0.23968673,
  '히피': 0.44711334,
  '젠더리스': 0.35417756,
  '밀리터리': 0.17381348,
  '매니시': 0.5283391,
  '컨트리': 0.3614927,
  '리조트': 0.32551143,
  '소피스트케이티드': 0.5927358,
  '섹시': 0.5265901},
 '직장': {'스트리트': 0.2307991,
  '클래식': 0.277169,
  '로맨틱': 0.373245,
  '펑크': 0.110792525,
  '페미닌': 0.34261927,
  '스포티': 0.19779,
  '힙합': 0.15050335,
  '모던': 0.47148114,
  '프레피': 0.30647242,
  '톰보이': 0.19858037,
  '레트로': 0.32886535,
  '키치': 0.3238792,
  '아방가르드': 0.1940976,
  '오리엔탈': 0.28934458,
  '웨스턴': 0.15596609,
  '히피': 0.2015844,
  '젠더리스': 0.28316513,
  '밀리터리': 0.07486073,
  '매니시': 0.4094499,
  '컨트리': 0.22943243,
  '리조트': 0.16133589,
  '소피스트케이티드': 0.47308594,
  '섹시': 0.31044325},
 '데이트': {'스트리트': 0.35422868,
  '클래식': 0.24003245,
  '로맨틱': 0.69649774,
  '펑크': 0.21289736,
  '페미닌': 0.5060767,
  '스포티': 0.35738122,
  '힙합': 0.26824525,
  '모던': 0.4868198,
  '프레피': 0.53625184,
  '톰보이': 0.38813046,
  '레트로': 0.46007064,
  '키치': 0.5099761,
  '아방가르드': 0.24406748,
  '오리엔탈': 0.26468188,
  '웨스턴': 0.14807768,
  '히피': 0.3811553,
  '젠더리스': 0.352549,
  '밀리터리': 0.050598018,
  '매니시': 0.4704031,
  '컨트리': 0.30839613,
  '리조트': 0.2530147,
  '소피스트케이티드': 0.65943706,
  '섹시': 0.5963634},
 '경조사': {'스트리트': 0.36375412,
  '클래식': 0.30381358,
  '로맨틱': 0.52054816,
  '펑크': 0.14737882,
  '페미닌': 0.36699504,
  '스포티': 0.37927377,
  '힙합': 0.18956085,
  '모던': 0.5019663,
  '프레피': 0.40365452,
  '톰보이': 0.26966545,
  '레트로': 0.52741235,
  '키치': 0.4126282,
  '아방가르드': 0.1792833,
  '오리엔탈': 0.3156517,
  '웨스턴': 0.23063555,
  '히피': 0.3652409,
  '젠더리스': 0.26723626,
  '밀리터리': 0.0898062,
  '매니시': 0.3378259,
  '컨트리': 0.3745199,
  '리조트': 0.3581507,
  '소피스트케이티드': 0.51044554,
  '섹시': 0.39378038},
 '여행': {'스트리트': 0.5842646,
  '클래식': 0.15974745,
  '로맨틱': 0.39738858,
  '펑크': 0.3726854,
  '페미닌': 0.28424317,
  '스포티': 0.5145872,
  '힙합': 0.41938052,
  '모던': 0.44138741,
  '프레피': 0.5156857,
  '톰보이': 0.39823353,
  '레트로': 0.56900585,
  '키치': 0.4954515,
  '아방가르드': 0.3834904,
  '오리엔탈': 0.408062,
  '웨스턴': 0.41594252,
  '히피': 0.5748364,
  '젠더리스': 0.27390137,
  '밀리터리': 0.16488421,
  '매니시': 0.37509647,
  '컨트리': 0.46930322,
  '리조트': 0.70026326,
  '소피스트케이티드': 0.48646387,
  '섹시': 0.4108982},
 '파티': {'스트리트': 0.4990375,
  '클래식': 0.22124353,
  '로맨틱': 0.4567237,
  '펑크': 0.446158,
  '페미닌': 0.42028332,
  '스포티': 0.51005644,
  '힙합': 0.4711032,
  '모던': 0.4456517,
  '프레피': 0.5910596,
  '톰보이': 0.45082673,
  '레트로': 0.58568376,
  '키치': 0.55756074,
  '아방가르드': 0.40107894,
  '오리엔탈': 0.3259839,
  '웨스턴': 0.19204624,
  '히피': 0.5364033,
  '젠더리스': 0.3558746,
  '밀리터리': 0.098348536,
  '매니시': 0.44707882,
  '컨트리': 0.40599796,
  '리조트': 0.42181265,
  '소피스트케이티드': 0.65604776,
  '섹시': 0.56462836},
 '운동': {'스트리트': 0.379994,
  '클래식': 0.043412022,
  '로맨틱': 0.16206,
  '펑크': 0.24390033,
  '페미닌': 0.1992781,
  '스포티': 0.62818235,
  '힙합': 0.5319789,
  '모던': 0.29742286,
  '프레피': 0.3966062,
  '톰보이': 0.6161824,
  '레트로': 0.314254,
  '키치': 0.2673113,
  '아방가르드': 0.2065803,
  '오리엔탈': 0.25593814,
  '웨스턴': 0.12673365,
  '히피': 0.3309636,
  '젠더리스': 0.1496136,
  '밀리터리': 0.124842584,
  '매니시': 0.34297353,
  '컨트리': 0.2250949,
  '리조트': 0.28023916,
  '소피스트케이티드': 0.27504063,
  '섹시': 0.3095897}}



def calculate_tpo_scores(user_clothes, tpo_score_table, selected_tpo):
    """
    스타일 확률 기반 TPO 점수 계산

    Args:
        user_clothes (dict): {카테고리: [[id, style_probs, feature1, ...], ...]}
        tpo_score_table (dict): TPO별 스타일 점수표
        selected_tpo (str): 사용자가 선택한 TPO

    Returns:
        dict: {카테고리: {item_id: tpo_score, ...}}
    """
    final_scores = {}
    style_score_table = tpo_score_table[selected_tpo]

    for category, items in user_clothes.items():
        category_scores = {}
        for item in items:
            item_id = item[0]
            style_probs = item[1]

            score = sum(float(prob) * float(style_score_table.get(style, 0))
                        for style, prob in style_probs.items())

            key = f"{category}_{item_id}"
            category_scores[key] = score

        final_scores[category] = category_scores

    return final_scores


def flatten_scores(score_dict):
    """
    {카테고리: {item_id: score}} → {item_id: score}
    """
    flat = {}
    for category in score_dict:
        flat.update(score_dict[category])
    return flat


def standardize_all_items(score_dict):
    """
    전체 아이템 기준 Z-score 정규화
    """
    flat = flatten_scores(score_dict)
    values = np.array(list(flat.values()))
    mean = values.mean()
    std = values.std() if values.std() > 0 else 1e-8
    standardized = {k: (v - mean) / std for k, v in flat.items()}
    return standardized


def merge_scores_global_standardization(score_dict1, score_dict2, weight1=0.5, weight2=0.5):
    """
    정규화된 두 점수를 합산하여 최종 점수 계산

    Returns:
        dict: {item_id: final_score}
    """
    norm1 = standardize_all_items(score_dict1)
    norm2 = standardize_all_items(score_dict2)

    common_keys = set(norm1.keys()) & set(norm2.keys())
    merged = {
        key: weight1 * norm1[key] + weight2 * norm2[key]
        for key in common_keys
    }
    return merged


def sort_items_by_score(score_dict, descending=True):
    """
    점수순 정렬 결과 반환

    Returns:
        list of (item_id, score)
    """
    return sorted(score_dict.items(), key=lambda x: x[1], reverse=descending)