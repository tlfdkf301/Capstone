# 스타일 예측 모델 로딩, 예측
import torch
import torch.nn as nn
import pickle
import numpy as np
from torch.serialization import add_safe_globals

# DMLP 클래스 정의
class DMLP(nn.Module):
    def __init__(self, input_size, num_classes):
        super(DMLP, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        return self.net(x)

import __main__
__main__.DMLP = DMLP

add_safe_globals({'DMLP': DMLP})

# 모델 및 인코더 불러오기
MODEL_PATH = "models/style_dmlp.pth"
MLB_PATH = "models/mlb.pkl"
LABEL_MAP = {
    '스트리트': 0, '페미닌': 1, '모던': 2, '클래식': 3, '로맨틱': 4, '아방가르드': 5,
    '리조트': 6, '소피스트케이티드': 7, '웨스턴': 8, '키치': 9, '톰보이': 10, '매니시': 11,
    '레트로': 12, '컨트리': 13, '힙합': 14, '스포티': 15, '젠더리스': 16, '프레피': 17,
    '밀리터리': 18, '히피': 19, '섹시': 20, '펑크': 21, '오리엔탈': 22
}
IDX_TO_LABEL = {v: k for k, v in LABEL_MAP.items()}

with open(MLB_PATH, 'rb') as f:
    mlb = pickle.load(f)

input_size = len(mlb.classes_)
num_classes = len(LABEL_MAP)

#model = DMLP(input_size, num_classes)
#model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu'), weights_only=False))
model = torch.load(MODEL_PATH, map_location=torch.device('cpu'), weights_only=False)
model.eval()

# 예측 함수
# def predict_top3_tpo(items, device='cpu'):
#     sample_X = mlb.transform([items])
#     sample_X = torch.tensor(sample_X, dtype=torch.float32).to(device)

#     model.eval()
#     with torch.no_grad():
#         output = model(sample_X)
#         probs = torch.softmax(output, dim=1).cpu().numpy()[0]

#     top3_indices = probs.argsort()[-3:][::-1]
#     top3_labels = {IDX_TO_LABEL[i]: round(probs[i], 4) for i in top3_indices}

#     return top3_labels
def predict_top3_tpo(items, model, mlb, label_to_idx=None, device='cpu'):
    if isinstance(items, dict):
        items = [f"{k}_{v}" for k, v in items.items() if v]

    sample_X = mlb.transform([items])
    sample_X = torch.tensor(sample_X, dtype=torch.float32).to(device)

    model.eval()
    with torch.no_grad():
        output = model(sample_X)
        probs = torch.softmax(output, dim=1).cpu().numpy()[0]

    top3_indices = probs.argsort()[-3:][::-1]
    top3_labels = {IDX_TO_LABEL[i]: round(probs[i], 4) for i in top3_indices}
    return top3_labels