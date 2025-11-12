import os
import random
import logging
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the inference module
from src.inference import ArtDetector
from src.datasets import ArtDataset
from src.quiz_dataset_loader import QuizDatasetLoader

app = Flask(__name__)
CORS(app)

# Global detector instance
detector = None
quiz_dataset = None
quiz_loader = None

# Initialize on import (for gunicorn)
def init_app():
    """Initialize the app - called on startup"""
    global detector, quiz_loader, quiz_dataset
    
    # Load detector
    try:
        load_detector()
    except Exception as e:
        logger.error(f"Failed to load detector: {e}")
    
    # Load quiz dataset
    try:
        load_quiz_dataset()
    except Exception as e:
        logger.error(f"Failed to load quiz dataset: {e}")

# Initialize when module is imported (works with gunicorn)
init_app()

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
    hf_repo = os.environ.get('HF_QUIZ_IMAGES_REPO', 'Not set')
    quiz_status = 'loaded' if (quiz_loader and len(quiz_loader) > 0) or (quiz_dataset and len(quiz_dataset) > 0) else 'not loaded'
    
    return jsonify({
        'status': 'healthy',
        'model_loaded': detector is not None,
        'device': str(detector.device) if detector else 'unknown',
        'quiz_loader_status': quiz_status,
        'quiz_loader_count': len(quiz_loader) if quiz_loader else 0,
        'quiz_dataset_count': len(quiz_dataset) if quiz_dataset else 0,
        'hf_quiz_repo': hf_repo,
        'quiz_loader_initialized': quiz_loader is not None
    })

@app.route('/quiz/image', methods=['GET'])
def get_quiz_image():
    """Get a random image from the quiz dataset"""
    try:
        # Use quiz_loader if available (preferred for production)
        if quiz_loader and len(quiz_loader) > 0:
            result = quiz_loader.get_random_sample()
            if result:
                idx, sample_data = result
                if sample_data:
                    image_path, true_label_idx = sample_data
                    true_label = quiz_loader.class_names[true_label_idx]
                    return jsonify({
                        'image_id': idx,
                        'image_path': image_path,
                        'true_label': true_label
                    })
                else:
                    logger.error(f"Failed to get sample data for index {idx}")
                    return jsonify({'error': 'Failed to load image data'}), 500
            else:
                logger.error("get_random_sample returned None")
                return jsonify({'error': 'No samples available'}), 500
        
        # Fallback to full dataset (for local development)
        if quiz_dataset is not None and len(quiz_dataset) > 0:
            idx = random.randint(0, len(quiz_dataset) - 1)
            image_path, true_label_idx = quiz_dataset.samples[idx]
            true_label = quiz_dataset.class_names[true_label_idx]
            return jsonify({
                'image_id': idx,
                'image_path': image_path,
                'true_label': true_label
            })
        
        error_msg = 'Quiz dataset not available. '
        if not quiz_loader:
            error_msg += 'Quiz loader not initialized. '
        elif len(quiz_loader) == 0:
            error_msg += 'Quiz loader has 0 images. '
        error_msg += 'Please check HF_QUIZ_IMAGES_REPO environment variable or create quiz_samples/ directory.'
        
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500
    except Exception as e:
        logger.error(f"Error getting quiz image: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/quiz/image/<int:image_id>', methods=['GET'])
def serve_quiz_image(image_id):
    """Serve the quiz image file"""
    try:
        # Try quiz_loader first
        if quiz_loader and image_id < len(quiz_loader):
            sample = quiz_loader.get_sample(image_id)
            if sample:
                image_path, _ = sample
                if image_path and os.path.exists(image_path):
                    return send_file(image_path)
                else:
                    logger.error(f"Image path does not exist: {image_path}")
                    return jsonify({'error': f'Image file not found: {image_path}'}), 404
        
        # Fallback to full dataset
        if quiz_dataset is not None and image_id < len(quiz_dataset):
            image_path, _ = quiz_dataset.samples[image_id]
            if os.path.exists(image_path):
                return send_file(image_path)
            else:
                logger.error(f"Image path does not exist: {image_path}")
                return jsonify({'error': f'Image file not found: {image_path}'}), 404
        
        return jsonify({'error': f'Invalid image ID: {image_id}'}), 404
    except Exception as e:
        logger.error(f"Error serving quiz image {image_id}: {e}")
        import traceback
        logger.error(traceback.format_exc())
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
        
        # Get image and label from quiz_loader or quiz_dataset
        image_path = None
        true_label = None
        
        if quiz_loader and image_id < len(quiz_loader):
            sample = quiz_loader.get_sample(image_id)
            if sample:
                image_path, true_label_idx = sample
                true_label = quiz_loader.class_names[true_label_idx]
        elif quiz_dataset is not None and image_id < len(quiz_dataset):
            image_path, true_label_idx = quiz_dataset.samples[image_id]
            true_label = quiz_dataset.class_names[true_label_idx]
        else:
            return jsonify({'error': 'Invalid image ID'}), 404
        
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
    """Load the quiz dataset from Hugging Face Hub or local directories"""
    global quiz_dataset, quiz_loader
    
    # Get Hugging Face repo from environment variable
    hf_repo_id = os.environ.get('HF_QUIZ_IMAGES_REPO', None)
    
    logger.info(f"Loading quiz dataset...")
    logger.info(f"  HF_QUIZ_IMAGES_REPO: {hf_repo_id if hf_repo_id else 'Not set'}")
    logger.info(f"  Checking quiz_samples/: {os.path.exists('quiz_samples')}")
    logger.info(f"  Checking data/val/: {os.path.exists(os.path.join(data_dir, 'val'))}")
    
    # Try to load from Hugging Face Hub or local directories
    try:
        logger.info("Attempting to create QuizDatasetLoader...")
        quiz_loader = QuizDatasetLoader(
            sample_data_dir='quiz_samples',
            full_data_dir=data_dir,
            hf_repo_id=hf_repo_id
        )
        logger.info(f"QuizDatasetLoader created, samples count: {len(quiz_loader)}")
        
        if len(quiz_loader) > 0:
            source = "Hugging Face Hub" if hf_repo_id and quiz_loader.hf_repo_id else "local directory"
            msg = f"✓ Quiz dataset loaded: {len(quiz_loader)} images from {source}"
            print(msg)
            logger.info(msg)
            return quiz_loader
        else:
            logger.warning("QuizDatasetLoader created but has 0 samples")
    except Exception as e:
        error_msg = f"Warning: Could not load quiz dataset: {e}"
        print(error_msg)
        logger.error(error_msg, exc_info=True)
        quiz_loader = None
    
    # Fallback to full dataset (for local development)
    try:
        logger.info("Attempting to load from full dataset...")
        quiz_dataset = ArtDataset(root_dir=data_dir, split='val', transform=None)
        if len(quiz_dataset) > 0:
            msg = f"✓ Quiz dataset loaded: {len(quiz_dataset)} images from full dataset"
            print(msg)
            logger.info(msg)
            return quiz_dataset
    except Exception as e:
        error_msg = f"Warning: Could not load full quiz dataset: {e}"
        print(error_msg)
        logger.warning(error_msg)
        quiz_dataset = None
    
    warning_msg = "⚠️  No quiz dataset available. Quiz will not work."
    print(warning_msg)
    logger.warning(warning_msg)
    print("   Options to fix:")
    print("   1. Upload images to Hugging Face Hub and set HF_QUIZ_IMAGES_REPO environment variable")
    print("   2. Create quiz_samples/ directory with AI/ and Human/ subdirectories")
    return None

if __name__ == '__main__':
    # Load detector on startup
    load_detector()
    # Load quiz dataset
    load_quiz_dataset()
    # Get port from environment variable (for deployment) or use default
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
