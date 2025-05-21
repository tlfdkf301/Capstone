# 연관 규칙 파일 (csv) 읽고 dict로 변환

import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler

def load_rules_with_score():
    # CSV 파일 경로
    color_rule = pd.read_csv("data/rules_c_v11(str).csv", encoding="utf-8")
    feature_rule = pd.read_csv("data/rules_f_v12(str).csv", encoding="utf-8")

    # log_lift 계산
    color_rule['log_lift'] = np.log(color_rule['lift'])
    feature_rule['log_lift'] = np.log(feature_rule['lift'])

    # 정규화
    metrics = ['confidence', 'log_lift', 'leverage']
    scaler = RobustScaler()
    color_rule[metrics] = scaler.fit_transform(color_rule[metrics])
    feature_rule[metrics] = scaler.fit_transform(feature_rule[metrics])

    # score 계산
    color_rule['score'] = (
        0.3 * color_rule['confidence'] +
        0.6 * color_rule['log_lift'] +
        0.1 * color_rule['leverage']
    )
    feature_rule['score'] = (
        0.3 * feature_rule['confidence'] +
        0.6 * feature_rule['log_lift'] +
        0.1 * feature_rule['leverage']
    )

    # 필요한 컬럼만 추출
    color_rule = color_rule[['antecedents', 'consequents', 'score']]
    feature_rule = feature_rule[['antecedents', 'consequents', 'score']]

    return color_rule, feature_rule

def rules_to_dict_sorted_key(rules_df, is_color=False):
    """
    연관 규칙 DataFrame을 딕셔너리로 변환
    """
    rules = {}
    for _, row in rules_df.iterrows():
        a = str(row['antecedents']).strip()
        b = str(row['consequents']).strip()

        if is_color:
            a = a.split('_')[-1]
            b = b.split('_')[-1]

        key = tuple(sorted([a, b]))
        rules[key] = float(row['score'])

    return rules