# 연관 규칙 유사도 점수 계산

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