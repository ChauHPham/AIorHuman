import os
import random
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS

# Import the inference module
from src.inference import ArtDetector
from src.datasets import ArtDataset

app = Flask(__name__)
CORS(app)

# Global detector instance
detector = None
quiz_dataset = None

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Predict image class"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        # Read image bytes
        image_bytes = file.read()
        
        # Make prediction using the detector
        result = detector.predict(image_bytes)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': detector is not None,
        'device': str(detector.device) if detector else 'unknown'
    })

@app.route('/quiz/image', methods=['GET'])
def get_quiz_image():
    """Get a random image from the validation set for quiz"""
    try:
        if quiz_dataset is None or len(quiz_dataset) == 0:
            return jsonify({'error': 'Quiz dataset not available'}), 500
        
        # Get random image
        idx = random.randint(0, len(quiz_dataset) - 1)
        image_path, true_label_idx = quiz_dataset.samples[idx]
        
        # Get true label name
        true_label = quiz_dataset.class_names[true_label_idx]
        
        # Return image path relative to data directory and true label
        # We'll serve the image from a static endpoint
        return jsonify({
            'image_id': idx,
            'image_path': image_path,
            'true_label': true_label
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/quiz/image/<int:image_id>', methods=['GET'])
def serve_quiz_image(image_id):
    """Serve the quiz image file"""
    try:
        if quiz_dataset is None or image_id >= len(quiz_dataset):
            return jsonify({'error': 'Invalid image ID'}), 404
        
        image_path, _ = quiz_dataset.samples[image_id]
        return send_file(image_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/quiz/check', methods=['POST'])
def check_quiz_answer():
    """Check user's answer and return result with model prediction"""
    try:
        data = request.json
        image_id = data.get('image_id')
        user_answer = data.get('answer')  # 'AI' or 'Human'
        
        if image_id is None or user_answer is None:
            return jsonify({'error': 'Missing image_id or answer'}), 400
        
        if quiz_dataset is None or image_id >= len(quiz_dataset):
            return jsonify({'error': 'Invalid image ID'}), 404
        
        # Get true label
        image_path, true_label_idx = quiz_dataset.samples[image_id]
        true_label = quiz_dataset.class_names[true_label_idx]
        
        # Get model prediction
        result = detector.predict_from_file(image_path)
        
        # Check if user is correct
        is_correct = user_answer == true_label
        
        return jsonify({
            'is_correct': is_correct,
            'user_answer': user_answer,
            'true_label': true_label,
            'model_prediction': result['predicted_class'],
            'model_confidence': result['confidence'],
            'model_probabilities': result['probabilities']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def load_detector(checkpoint_path='models/detector.pth'):
    """Load the AI Art Detector"""
    global detector
    # Get Hugging Face repo from environment variable if set
    hf_repo_id = os.environ.get('HF_MODEL_REPO', None)
    hf_filename = os.environ.get('HF_MODEL_FILENAME', None)
    
    detector = ArtDetector(
        checkpoint_path=checkpoint_path,
        hf_repo_id=hf_repo_id,
        hf_filename=hf_filename
    )
    return detector

def load_quiz_dataset(data_dir='data'):
    """Load the quiz dataset from validation set"""
    global quiz_dataset
    try:
        quiz_dataset = ArtDataset(root_dir=data_dir, split='val', transform=None)
        print(f"✓ Quiz dataset loaded: {len(quiz_dataset)} images")
        return quiz_dataset
    except Exception as e:
        print(f"Warning: Could not load quiz dataset: {e}")
        quiz_dataset = None
        return None

if __name__ == '__main__':
    # Load detector on startup
    load_detector()
    # Load quiz dataset
    load_quiz_dataset()
    # Get port from environment variable (for deployment) or use default
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
