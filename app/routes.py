
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]
from flask import Flask, request, render_template, jsonify, session
from werkzeug.utils import secure_filename
import torch
from torchvision import models, transforms
from torch import nn
from PIL import Image
import os
from app.dialogflow_bot import detect_intent_text
import uuid
import re
import numpy as np

# Load environment variables
load_dotenv()
app = Flask(__name__)

# Set a unique secret key (keep it secret in production!)
app.secret_key = os.getenv("SECRET_KEY", b'e\xafk\xe6N\x90\xe7\xf1\xbefi\xfd\x19\t\x9f\x1f\xdd\\\xec&\x00\xe5Af')

project_id = os.getenv("PROJECT_ID")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

app.config['UPLOAD_PATH'] = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg','webp'}

os.makedirs(app.config['UPLOAD_PATH'], exist_ok=True)

# Label mappings
label_map = {
    'akiec': 'Actinic Keratoses',
    'bcc': 'Basal Cell Carcinoma',
    'bkl': 'Benign Keratosis',
    'df': 'Dermatofibroma',
    'mel': 'Melanoma',
    'nv': 'Melanocytic Nevi',
    'vasc': 'Vascular Lesions'
}
class_keys = list(label_map.keys())

# Image preprocessing
def get_transforms():
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor()
    ])

# File type check
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Load model
def load_model(path):
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, len(class_keys))
    model.load_state_dict(torch.load(path, map_location='cpu'))
    model.eval()
    return model

# Predict
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



#image validation
def estimate_skin_ratio(pil_image):
    """Estimate proportion of skin-like pixels using YCbCr thresholding.
    Returns a float in [0,1].
    """
    # Ensure RGB
    rgb = pil_image.convert("RGB")
    # Convert to YCbCr and split channels
    ycbcr = rgb.convert("YCbCr")
    y, cb, cr = ycbcr.split()
    cb = np.array(cb, dtype=np.uint8)
    cr = np.array(cr, dtype=np.uint8)
    # Classic skin thresholds (tolerant):
    # 77<=Cb<=127 and 133<=Cr<=173
    skin_mask = (cb >= 77) & (cb <= 127) & (cr >= 133) & (cr <= 173)
    skin_pixels = int(np.count_nonzero(skin_mask))
    total_pixels = int(cb.size)
    if total_pixels == 0:
        return 0.0
    return skin_pixels / total_pixels






from flask import Flask, request, render_template, jsonify, session, redirect, url_for

@app.route('/', methods=['GET', 'POST'])
def home_page():
    scroll_to = "check"

    if request.method == 'POST':
        uploaded_file = request.files.get('file')

        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = secure_filename(uploaded_file.filename)
            filepath = os.path.join(app.config['UPLOAD_PATH'], filename)
            uploaded_file.save(filepath)

            try:
                model = load_model('./skin_disease_model.pth')
                transform = get_transforms()
                image = Image.open(filepath).convert("RGB")

                # Simple guardrail: reject if image likely doesn't contain skin
                skin_ratio = estimate_skin_ratio(image)
                if skin_ratio < 0.15:  # ~15% of pixels look like skin
                    session['res'] = "❌ No skin detected in the image. Please upload a clear close‑up of skin."
                    session['uploaded_image'] = filename
                    session['confidence'] = None
                    session['dermatologist_note'] = None
                    return redirect(url_for('home_page'))

                predicted_class, confidence_score = predict(model, image, transform, return_confidence=True)
                prediction_label = label_map[class_keys[predicted_class]]

                # Optional dermatologist note
                high_risk_classes = ['mel', 'bcc', 'akiec']
                dermatologist_note = None
                if class_keys[predicted_class] in high_risk_classes:
                    dermatologist_note = "⚠️ This skin condition may be high risk. Consult a dermatologist."

                # Store in session
                session['res'] = prediction_label
                session['uploaded_image'] = filename
                session['confidence'] = confidence_score
                session['dermatologist_note'] = dermatologist_note

            except Exception as e:
                session['res'] = f"Prediction error: {str(e)}"

        else:
            session['res'] = "❌ Invalid file format. Please upload a valid image."

        # Redirect to clear POST data
        return redirect(url_for('home_page'))

    # GET request — read and clear session
    res = session.pop('res', None)
    uploaded_image = session.pop('uploaded_image', None)
    confidence = session.pop('confidence', None)
    dermatologist_note = session.pop('dermatologist_note', None)

    return render_template('index.html',
                           res=res,
                           uploaded_image=uploaded_image,
                           confidence=confidence,
                           scroll_to=scroll_to,
                           dermatologist_note=dermatologist_note)








# Chatbot route
@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message')
    if not user_msg:
        return jsonify({'response': "Please ask a question."}), 400

    try:
        # Quick greeting handling without calling Dialogflow
        text = user_msg.strip().lower()
        if re.match(r'^(hi|hello|hey)\b', text):
            return jsonify({'response': 'Hello! Welcome to SkinCare Bot. How can I help you today?'}), 200

        session_id = str(uuid.uuid4())
        response = detect_intent_text(
            project_id='skinbot-onqi',  # Replace with your actual ID
            session_id=session_id,
            text=user_msg
        )
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'response': f"Error: {str(e)}"}), 500




@app.route("/contact")
def contact():
    return render_template("contact.html")


