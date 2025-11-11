#!/usr/bin/env python3
"""
Startup script for the AI Art Detector web application
"""
import os
import sys
import argparse
from app import app, load_detector

def main():
    parser = argparse.ArgumentParser(description='AI Art Detector Web Application')
    parser.add_argument('--checkpoint', type=str, default='models/detector.pth',
                       help='Path to the trained model checkpoint')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                       help='Host to bind the server to')
    parser.add_argument('--port', type=int, default=5000,
                       help='Port to bind the server to')
    parser.add_argument('--debug', action='store_true',
                       help='Run in debug mode')
    parser.add_argument('--workers', type=int, default=1,
                       help='Number of worker processes (for production)')
    
    args = parser.parse_args()
    
    # Check if checkpoint exists
    if not os.path.exists(args.checkpoint):
        print(f"Warning: Checkpoint {args.checkpoint} not found.")
        print("The application will run with an untrained model.")
        print("To train a model, run: python -m src.train")
        print()
    
    # Load the detector
    print("Loading AI Art Detector...")
    try:
        detector = load_detector(args.checkpoint)
        print(f"✓ Detector loaded successfully on {detector.device}")
    except Exception as e:
        print(f"✗ Failed to load detector: {e}")
        sys.exit(1)
    
    # Load quiz dataset
    from app import load_quiz_dataset
    print("Loading quiz dataset...")
    load_quiz_dataset()
    
    # Start the application
    print(f"Starting web server on {args.host}:{args.port}")
    print("Open your browser and go to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print()
    
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
        threaded=True
    )

if __name__ == '__main__':
    main()
