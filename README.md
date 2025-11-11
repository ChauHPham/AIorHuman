# AI Art Detector Quiz (PyTorch + Web App)

**Test your knowledge on AI images vs human!** Can you tell the difference between AI-generated art and human-made art? Take the quiz and see how well you can identify them!

## Features
- **🎮 Interactive Quiz**: Test your knowledge with 10, 20, or 30 questions
- **📊 Score Tracking**: See your accuracy and track your progress
- **🤖 AI Model Comparison**: See how the AI model predicts each image
- **🎨 Random Images**: Get a fresh set of randomized images each game
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices
- PyTorch + torchvision baseline (ResNet-50) for model predictions
- Clean dataset loader with train/val splits
- Ready-to-run CLI (`train.py`, `evaluate.py`)
- **🐳 Docker deployment** ready

## Folder Layout
```
ai_art_detector/
├─ data/
│  ├─ train/
│  │  ├─ AI/            # put AI-generated images here
│  │  └─ Human/         # put human-made images here
│  └─ val/
│     ├─ AI/
│     └─ Human/
├─ src/
│  ├─ datasets.py
│  ├─ model.py
│  ├─ train.py
│  ├─ evaluate.py
│  └─ inference.py      # model inference utilities
├─ templates/
│  └─ index.html        # web application frontend
├─ notebooks/
│  └─ quickstart.ipynb
├─ app.py               # Flask web application
├─ run_web.py           # web app startup script
├─ requirements.txt
├─ environment.yml
├─ Dockerfile
├─ docker-compose.yml
└─ README.md
```

## Quickstart
1. **Create environment**
   ```bash
   # Option A: conda
   conda env create -f environment.yml
   conda activate ai-art-detector

   # Option B: pip
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Add data**
   Place your images inside the `data/train/*` and `data/val/*` folders as shown above.

3. **Train**
   ```bash
   python -m src.train --data_dir data --epochs 10 --batch_size 32 --lr 1e-4 --num_classes 2
   ```

4. **Evaluate**
   ```bash
   python -m src.evaluate --data_dir data --checkpoint models/detector.pth --num_classes 2
   ```

## 🌐 Web Application - Quiz Mode

### Quick Start
1. **Install dependencies** (includes Flask and web dependencies)
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the web application**
   ```bash
   python run_web.py
   ```

3. **Open your browser** and go to `http://localhost:5000`

### Quiz Features
- **Choose Your Challenge**: Select 10, 20, or 30 questions
- **Random Images**: Each game shows you a fresh set of randomized images
- **Instant Feedback**: See if you're correct immediately after answering
- **AI Model Comparison**: See how the AI model predicts each image and compare with your answer
- **Score Tracking**: Track your score, correct answers, and accuracy percentage
- **Progress Indicator**: See which question you're on (e.g., "Question 5 of 20")
- **Completion Screen**: View your final results when you finish the quiz

### API Endpoints
- `GET /` - Main quiz interface
- `GET /quiz/image` - Get a random quiz image
- `GET /quiz/image/<id>` - Serve quiz image file
- `POST /quiz/check` - Check user's answer and return results
- `GET /health` - Health check endpoint

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t ai-art-detector .
docker run -p 5000:5000 ai-art-detector
```

## 📥 Download Dataset

You can download the dataset using either method:

### Option 1: Using KaggleHub (Recommended)
```python
import kagglehub

# Download latest version
path = kagglehub.dataset_download("alessandrasala79/ai-vs-human-generated-dataset")
print("Path to dataset files:", path)
```

**Pros:**
- Clean, programmatic download
- Easy to update to latest version
- Handles authentication automatically

**Requirements:**
- Install: `pip install kagglehub`
- Set up Kaggle API credentials (kaggle.json in ~/.kaggle/)

### Option 2: Manual Download
1. Go to: https://www.kaggle.com/datasets/alessandrasala79/ai-vs-human-generated-dataset
2. Click "Download" button
3. Extract the zip file
4. Organize images into `data/train/AI/`, `data/train/Human/`, `data/val/AI/`, `data/val/Human/`

**Pros:**
- No API setup needed
- Can preview dataset before downloading

## 🌐 Deploy to Production

Want to make this a live website? See the deployment guides:

- **Quick Start**: See `DEPLOY_QUICKSTART.md` for the fastest way to deploy
- **Full Guide**: See `DEPLOYMENT.md` for detailed deployment options

**Recommended platforms:**
- **Render** (Free tier available) - Easiest
- **Railway** (Free $5 credit) - Very simple
- **Heroku** (Free tier with limitations) - Classic choice

## How to Play

1. **Start the Quiz**: Click "Start Quiz" on the home screen
2. **Choose Questions**: Select how many questions you want (10, 20, or 30)
3. **View Image**: Each question shows you an image
4. **Make Your Guess**: Click "🤖 AI" or "👤 Human"
5. **See Results**: Find out if you're correct and see the AI model's prediction
6. **Track Progress**: Watch your score update in real-time
7. **Complete Quiz**: View your final results and accuracy!

## Notes
- This is a baseline; for real-world robustness, consider:
  - multiple generators in the AI class
  - augmentations (jpeg, resize, blur) to avoid overfitting to trivial cues
- GPU recommended but not required.
- Web app works with or without a trained model (will use untrained weights if no checkpoint found)
- **Disclaimer**: Predictions may not be accurate due to model limitations, potential overfitting, and limited training data. This quiz is for educational and entertainment purposes only.
