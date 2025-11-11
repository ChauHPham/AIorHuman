"""
Model inference utilities for the web application
"""
import torch
import torch.nn.functional as F
from PIL import Image
import torchvision.transforms as transforms
import io
import os
import logging

logger = logging.getLogger(__name__)

class ArtDetector:
    def __init__(self, checkpoint_path='models/detector.pth', device=None, hf_repo_id=None, hf_filename=None):
        """
        Initialize the AI Art Detector
        
        Args:
            checkpoint_path (str): Path to the trained model checkpoint (local path)
            device (str): Device to run inference on ('cuda' or 'cpu')
            hf_repo_id (str): Hugging Face repository ID (optional, uses env var if not provided)
            hf_filename (str): Filename in Hugging Face repo (optional, defaults to 'detector.pth')
        """
        self.device = device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.class_names = ['AI', 'Human']
        self.model = None
        self.transform = None
        
        # Get model path (downloads from HF if needed)
        from .model_loader import get_model_path
        model_path = get_model_path(
            local_path=checkpoint_path,
            hf_repo_id=hf_repo_id,
            hf_filename=hf_filename
        )
        
        self._load_model(model_path)
        self._setup_transforms()
    
    def _load_model(self, checkpoint_path):
        """Load the trained model"""
        from .model import get_model
        
        self.model = get_model(num_classes=2, pretrained=False).to(self.device)
        
        if os.path.exists(checkpoint_path):
            try:
                self.model.load_state_dict(torch.load(checkpoint_path, map_location=self.device))
                self.model.eval()
                logger.info(f"Model loaded from {checkpoint_path}")
            except Exception as e:
                logger.error(f"Error loading model from {checkpoint_path}: {e}")
                logger.warning("Using untrained model.")
        else:
            logger.warning(f"Checkpoint {checkpoint_path} not found. Using untrained model.")
    
    def _setup_transforms(self):
        """Setup image preprocessing transforms"""
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
    
    def preprocess_image(self, image_bytes):
        """
        Preprocess image bytes for model inference
        
        Args:
            image_bytes (bytes): Raw image bytes
            
        Returns:
            torch.Tensor: Preprocessed image tensor
        """
        # Load image from bytes
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        # Apply transforms and add batch dimension
        image_tensor = self.transform(image).unsqueeze(0).to(self.device)
        return image_tensor
    
    def predict(self, image_bytes):
        """
        Predict the class of an image
        
        Args:
            image_bytes (bytes): Raw image bytes
            
        Returns:
            dict: Prediction results with class, confidence, and probabilities
        """
        # Preprocess image
        image_tensor = self.preprocess_image(image_bytes)
        
        # Make prediction
        with torch.no_grad():
            logits = self.model(image_tensor)
            probabilities = F.softmax(logits, dim=1)
            predicted_class_idx = logits.argmax(1).item()
            confidence = probabilities[0][predicted_class_idx].item()
        
        # Prepare results
        result = {
            'predicted_class': self.class_names[predicted_class_idx],
            'confidence': float(confidence),
            'probabilities': {
                self.class_names[i]: float(probabilities[0][i]) 
                for i in range(len(self.class_names))
            }
        }
        
        return result
    
    def predict_from_file(self, file_path):
        """
        Predict the class of an image from file path
        
        Args:
            file_path (str): Path to the image file
            
        Returns:
            dict: Prediction results
        """
        with open(file_path, 'rb') as f:
            image_bytes = f.read()
        return self.predict(image_bytes)
    
    def predict_from_pil(self, pil_image):
        """
        Predict the class of a PIL Image
        
        Args:
            pil_image (PIL.Image): PIL Image object
            
        Returns:
            dict: Prediction results
        """
        # Convert PIL image to bytes
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format='JPEG')
        image_bytes = img_byte_arr.getvalue()
        
        return self.predict(image_bytes)

# Convenience function for quick inference
def quick_predict(image_bytes, checkpoint_path='models/detector.pth'):
    """
    Quick prediction function for one-off inference
    
    Args:
        image_bytes (bytes): Raw image bytes
        checkpoint_path (str): Path to model checkpoint
        
    Returns:
        dict: Prediction results
    """
    detector = ArtDetector(checkpoint_path)
    return detector.predict(image_bytes)
