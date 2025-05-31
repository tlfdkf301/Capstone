import torch
import numpy as np
import torch.nn as nn
from torchvision import models, transforms
from sklearn.preprocessing import LabelEncoder
from PIL import Image

WEIGHT_PATH = "models/weights/"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class ResNet18Classifier(nn.Module):
    def __init__(self, num_classes):
        super(ResNet18Classifier, self).__init__()
        self.resnet = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
        self.resnet.fc = nn.Linear(self.resnet.fc.in_features, num_classes)

    def forward(self, x):
        return self.resnet(x)

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])



# def predict_attribute(image_path, model, encoder):
#     image = Image.open(image_path).convert('RGB')
    
#     image = transform(image).unsqueeze(0).to(device)
#     model.to(device)
#     model.eval()
#     with torch.no_grad():
#         output = model(image)
#         pred_idx = torch.argmax(output, dim=1).item()
#         return encoder.inverse_transform([pred_idx])[0]
def predict_attribute(image_path, model, encoder):
    image = Image.open(image_path).convert('RGB')
    image = transform(image).unsqueeze(0).to(device)
    model.eval()
    with torch.no_grad():
        output = model(image)
        pred_idx = torch.argmax(output, dim=1).item()
        return encoder.inverse_transform([pred_idx])[0]




# def load_model_and_encoder(name, classes):
#     encoder = LabelEncoder()
#     encoder.classes_ = classes
#     model = ResNet18Classifier(len(classes))
#     device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
#     model.load_state_dict(torch.load(f"{WEIGHT_PATH}best_model_{name}.pth", map_location=device))
#     model = model.to(device)
#     return model, encoder
def load_model_and_encoder(name, classes):
    encoder = LabelEncoder()
    encoder.classes_ = np.array(classes)  # ✅ 반드시 ndarray로!
    model = ResNet18Classifier(len(classes))
    model.load_state_dict(torch.load(f"{WEIGHT_PATH}best_model_{name}.pth", map_location=device))
    return model.to(device), encoder

# 모델들 로딩
model_color, encoder_color = load_model_and_encoder("color", [
    'black', 'white', 'beige', 'gray', 'blue', 'brown', 'green',
    'pink', 'purple', 'red', 'yellow', 'orange'])

model_fiber, encoder_fiber = load_model_and_encoder("fiber", [
    'cotton', 'synthetic fiber others', 'hemp', 'cellulose fiber others', 'silk', 'wool', 'viscos rayon',
    'polyester', 'nylon', 'polyurethane', 'protein fiber others', 'regenerated fiber others'])

model_pants, encoder_pants = load_model_and_encoder("pants_silhouette", [
    'null', 'normal', 'loose', 'skinny', 'others', 'bell-bottom', 'wide'])

model_season, encoder_season = load_model_and_encoder("season", [
    'spring&fall', 'winter', 'summer'])

model_sleeve, encoder_sleeve = load_model_and_encoder("sleeve_length_type", [
    'long sleeves', 'null', 'short sleeves', 'sleeveless'])

model_top, encoder_top = load_model_and_encoder("top_length_type", [
    'long', 'normal', 'midi', 'short', 'crop'])

model_transparency, encoder_transparency = load_model_and_encoder("transparency", [
    'none at all', 'none', 'contain', 'contain little', 'contain a lot'])

def run_resnet(image_path: str) -> dict:
    return {
        "color": predict_attribute(image_path, model_color, encoder_color),
        "fiber": predict_attribute(image_path, model_fiber, encoder_fiber),
        "pants_silhouette": predict_attribute(image_path, model_pants, encoder_pants),
        "season": predict_attribute(image_path, model_season, encoder_season),
        "sleeve_length": predict_attribute(image_path, model_sleeve, encoder_sleeve),
        "top_length": predict_attribute(image_path, model_top, encoder_top),
        "transparency": predict_attribute(image_path, model_transparency, encoder_transparency)
    }
