from core.dmlp_predictor import model, mlb, LABEL_MAP
from core.preprocessing_utils import apply_style_predictions_single
from sqlalchemy.orm import Session
from models.clothes import Clothes
from collections import defaultdict

# 카테고리 → mainCategory 매핑 함수
def conver_to_main_category(category):
    if category in ['베스트', '티셔츠', '셔츠', '블라우스', '니트웨어']:
        return '상의'
    elif category in ['점퍼', '재킷', '코트', '가디건']:
        return '아우터'
    elif category in ['청바지', '조거팬츠', '슬랙스', '스커트', '팬츠', '래깅스']:
        return '하의'
    elif category in ['원피스', '점프수트']:
        return '원피스'
    return category

# 사용자 옷 전체 불러오기 (추천용)
def get_user_clothes(db: Session) -> dict:
    clothes_list = db.query(Clothes).all()

    user_clothes = defaultdict(list)
    for item in clothes_list:
        item_id = str(item.id)
        category = item.category
        main_category = conver_to_main_category(category)
        style_probs = item.style_probs or {}

        features = [
            f"{main_category}_색상_{item.color}" if item.color else None,
            f"{main_category}_핏_{item.fit}" if item.fit else None,
            f"{main_category}_기장_{item.length}" if item.length else None,
            f"{main_category}_소재_{item.material}" if item.material else None,
            f"{main_category}_소매기장_{item.sleeve_length}" if item.sleeve_length else None,
            f"{main_category}_옷깃_{item.collar}" if item.collar else None
        ]
        features = [f for f in features if f]
        user_clothes[main_category].append([item_id, style_probs] + features)

    return dict(user_clothes)

# 선택된 옷 1개 가져오기 (추천 대상)
def get_selected_clothing(selected_item_id: int, db: Session) -> dict | None:
    try:
        item_id = int(selected_item_id) if "_" not in selected_item_id else int(selected_item_id.split("_")[1])
    except ValueError:
        return None

    item = db.query(Clothes).filter(Clothes.id == item_id).first()
    if item is None:
        return None
    
    main_category = conver_to_main_category(item.category)

    features = [
        f"{main_category}_색상_{item.color}" if item.color else None,
        f"{main_category}_핏_{item.fit}" if item.fit else None,
        f"{main_category}_기장_{item.length}" if item.length else None,
        f"{main_category}_소재_{item.material}" if item.material else None,
        f"{main_category}_소매기장_{item.sleeve_length}" if item.sleeve_length else None,
        f"{main_category}_옷깃_{item.collar}" if item.collar else None
    ]
    features = [f for f in features if f]

    # ✅ DMLP style 예측용 features도 mainCategory 포함 버전 사용
    style_probs = apply_style_predictions_single(features, model, mlb, LABEL_MAP) #출력값 상위 3개만


    # resultresult=[]
    # resultresult.append(int(item.id))
    # resultresult.append(style_probs)
    # for iii in features:
    #     resultresult.append(iii)

    # return resultresult
    return {
        "id": str(item.id),
        "style_probs": style_probs,
        "features": features,
        "category": item.category,
        "mainCategory": main_category
    }

def get_selected_clothing2(selected_item_id: int, db: Session) -> dict | None:
    try:
        item_id = int(selected_item_id) if "_" not in selected_item_id else int(selected_item_id.split("_")[1])
    except ValueError:
        return None

    item = db.query(Clothes).filter(Clothes.id == item_id).first()
    if item is None:
        return None
    
    main_category = conver_to_main_category(item.category)

    features = [
        f"{main_category}_색상_{item.color}" if item.color else None,
        f"{main_category}_핏_{item.fit}" if item.fit else None,
        f"{main_category}_기장_{item.length}" if item.length else None,
        f"{main_category}_소재_{item.material}" if item.material else None,
        f"{main_category}_소매기장_{item.sleeve_length}" if item.sleeve_length else None,
        f"{main_category}_옷깃_{item.collar}" if item.collar else None
    ]
    features = [f for f in features if f]

    # ✅ DMLP style 예측용 features도 mainCategory 포함 버전 사용
    style_probs = apply_style_predictions_single(features, model, mlb, LABEL_MAP)


    resultresult=[]
    resultresult.append(int(item.id))
    resultresult.append(style_probs)
    for iii in features:
        resultresult.append(iii)

    return resultresult