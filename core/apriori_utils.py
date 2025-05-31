# 연관 규칙 유사도 점수 계산
category_to_prefix_map = {
    '베스트': '상의',
    '티셔츠': '상의',
    '셔츠': '상의',
    '블라우스' : '상의',
    '니트웨어' : '상의',
    # '가디건': '상의',
    '점퍼': '아우터',
    '재킷': '아우터',
    '코트': '아우터',
    '가디건' : '아우터',
    '청바지': '하의',
    '조거팬츠': '하의',
    '슬랙스': '하의',
    '스커트': '하의',
    '원피스': '원피스',
    '점프수트' : '원피스',
    '팬츠' : '하의',
    '래깅스' : '하의'
}
# core/score_utils.py 또는 해당 위치에서 사용 중인 추천 함수 내
VALID_FEATURES = {
    '상의': ['핏', '소매기장', '소재', '옷깃'],
    '하의': ['핏', '기장', '소재'],
    '아우터': ['핏', '기장', '소매기장'],
    '원피스': ['핏', '기장', '소매기장', '소재', '옷깃']
}

def get_feature_type(f):
    try:
        return f.split('_')[1]
    except IndexError:
        return None

def score_recommendation_dict_sorted_key(item, cat, color_dict, feature_dict, user_clothes, color_rate=1):
    current_id = item[0]
    current_features = set(item[2:])

    if not current_features:
        return {'input_ID': current_id, 'input_cat': cat, 'recommendation': {}}

    compare_categories = ['상의', '하의', '아우터', '원피스']
    if cat in compare_categories:
        compare_categories.remove(cat)

    recommend_dict = {}

    for category in compare_categories:
        item_scores = {}

        for user_item in user_clothes.get(category, []):
            item_raw_id = user_item[0]
            features = user_item[2:]
            item_id = f"{category}_{item_raw_id}"

            score = 0
            for input_feature in current_features:
                input_type = input_feature.split('_')[1]

                for user_feature in features:
                    user_type = user_feature.split('_')[1]

                    if input_type != user_type:
                        continue

                    if input_type == '색상':
                        color1 = input_feature.split('_')[-1]
                        color2 = user_feature.split('_')[-1]
                        key=[color1,color2]
                        key=tuple(sorted(key))
                        raw_score = color_dict.get(key, 0)
                        score += raw_score * color_rate
                    else:
                        key=[input_feature,user_feature]
                        key=tuple(sorted(key))
                        raw_score = feature_dict.get(key, 0)
                        score += raw_score

            item_scores[item_id] = score

        recommend_dict[category] = dict(sorted(item_scores.items(), key=lambda x: x[1], reverse=True))

    return {
        'input_ID': current_id,
        'input_cat': cat,
        'recommendation': recommend_dict
    }