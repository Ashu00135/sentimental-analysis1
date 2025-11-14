# Machine Learning Package Installation Guide

## Problem: SSL Certificate Issues with MSYS64 Python

Your Python environment (MSYS64/mingw64) has SSL certificate verification issues preventing numpy and scikit-learn installation.

## Solutions

### ✅ Option 1: Use Regular Windows Python (Recommended)

Check if you have system Python installed:
```powershell
# Check for Python
where.exe python
python --version

# If available, install packages:
pip install numpy scikit-learn

# Then train model:
python D:\PROJECTS\sentiment_analysis\train_model.py
```

### ✅ Option 2: Create New Virtual Environment with System Python

```powershell
cd D:\PROJECTS\sentiment_analysis

# Create venv with system Python
python -m venv venv_ml

# Activate
.\venv_ml\Scripts\activate

# Install
pip install numpy scikit-learn

# Train
python train_model.py
```

### ✅ Option 3: Download Pre-built Wheels

Visit: https://www.lfd.uci.edu/~gohlke/pythonlibs/ (unofficial Windows binaries)

Download for Python 3.12 64-bit:
- `numpy-1.26.4+mkl-cp312-cp312-win_amd64.whl`
- `scikit_learn-1.4.2-cp312-cp312-win_amd64.whl`

Install:
```powershell
pip install path\to\numpy-1.26.4+mkl-cp312-cp312-win_amd64.whl
pip install path\to\scikit_learn-1.4.2-cp312-cp312-win_amd64.whl
```

### ✅ Option 4: Use Anaconda/Miniconda

If you have conda:
```bash
conda create -n sentiment python=3.12
conda activate sentiment
conda install numpy scikit-learn
```

### ✅ Option 5: Train on Google Colab (Free)

1. Upload `sentiment_tweets.db` to Google Drive
2. Use Colab notebook with free GPU
3. Train model faster
4. Download trained model files

### ✅ Option 6: Skip ML Training - Build GUI First

We can:
- Build the GUI interface now
- Display database statistics
- Add manual sentiment labeling
- Train model later

## What Would You Like To Do?

1. **Try system Python** (if available)
2. **Download wheels manually** 
3. **Use Google Colab** for training
4. **Skip to GUI development**
5. **Install Anaconda** (clean Python environment)

Let me know your preference!
