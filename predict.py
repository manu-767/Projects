import torch
import torch.nn as nn
from PIL import Image
import torchvision.transforms as T
import torchvision.models as models
import argparse

# Disease label map
label_map = {
    0: 'Melanoma (mel)',
    1: 'Melanocytic Nevi (nv)',
    2: 'Benign Keratosis (bkl)',
    3: 'Basal Cell Carcinoma (bcc)',
    4: 'Actinic Keratoses (akiec)',
    5: 'Vascular Lesions (vasc)',
    6: 'Dermatofibroma (df)'
}

# Get image transform
def get_transforms():
    return T.Compose([
        T.Resize((224, 224)),
        T.ToTensor(),
        T.Normalize(mean=[0.5, 0.5, 0.5],
                    std=[0.5, 0.5, 0.5])
    ])



import torch

def predict(model, image, transform, return_confidence=False):
    img_tensor = transform(image).unsqueeze(0)  # image is already a PIL.Image
    model.eval()

    with torch.no_grad():
        output = model(img_tensor)
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        predicted_class = torch.argmax(probabilities).item()
        confidence = probabilities[predicted_class].item()

    if return_confidence:
        return predicted_class, confidence  # e.g., (3, 0.9456)
    else:
        return predicted_class


# Main
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", required=True, help="Path to the trained model (.pth)")
    parser.add_argument("-i", "--image", required=True, help="Path to the input image")
    args = parser.parse_args()

    # Load base model
    model = models.resnet18(pretrained=False)
    model.fc = nn.Linear(model.fc.in_features, 7)  # 7 classes
    model.load_state_dict(torch.load(args.model, map_location='cpu'))

    # Make prediction
    transform = get_transforms()
    pred_idx = predict(model, args.image, transform)
    pred_label = label_map.get(pred_idx, "Unknown")

    print(f"✅ The model predicts: {pred_label}")














