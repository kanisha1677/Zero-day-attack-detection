# 🔗 GitHub Setup Guide

## Push Your Zero-Day Attack Detection System to GitHub

Since you're working in a GitHub Codespace, here's how to commit and push your code to a repository.

---

## Option 1: Using the Codespace Terminal

### Step 1: Initialize Git Repository (if not already initialized)
```bash
git init
```

### Step 2: Add All Files
```bash
git add .
```

### Step 3: Commit Your Changes
```bash
git commit -m "Initial commit: Zero-Day Network Attack Detection System

- Implemented ML-based detection (Isolation Forest, Autoencoder, Random Forest, XGBoost)
- Added Streamlit dashboard with real-time alerts
- Included SHAP explainability
- Added training scripts and documentation
- 87% requirements coverage"
```

### Step 4: Create a New Repository on GitHub
1. Go to https://github.com/new
2. Name: `zero-day-attack-detection` (or your preferred name)
3. Description: "AI-powered network attack detection system"
4. Choose: Public or Private
5. **DO NOT** initialize with README (you already have one)
6. Click "Create repository"

### Step 5: Link to Remote Repository
Replace `YOUR_USERNAME` with your GitHub username:
```bash
git remote add origin https://github.com/YOUR_USERNAME/zero-day-attack-detection.git
```

### Step 6: Push to GitHub
```bash
git branch -M main
git push -u origin main
```

---

## Option 2: Using VS Code Source Control

### Step 1: Open Source Control Panel
- Click the **Source Control** icon in the left sidebar (looks like a branch)
- Or press `Ctrl+Shift+G` (Windows/Linux) or `Cmd+Shift+G` (Mac)

### Step 2: Initialize Repository
- Click "Initialize Repository" if not already done

### Step 3: Stage All Files
- Click the **+** icon next to "Changes" to stage all files
- Or click **+** next to individual files

### Step 4: Commit Changes
- Enter commit message in the text box at the top:
  ```
  Initial commit: Zero-Day Network Attack Detection System
  ```
- Click the **✓** checkmark icon or press `Ctrl+Enter`

### Step 5: Publish to GitHub
- Click "Publish Branch" button
- Choose repository name: `zero-day-attack-detection`
- Choose: Public or Private
- Click "Publish"

---

## Option 3: GitHub CLI (if available in Codespace)

```bash
# Login to GitHub
gh auth login

# Create repository and push
gh repo create zero-day-attack-detection --public --source=. --remote=origin --push
```

---

## What Gets Pushed to GitHub

### ✅ Will be committed:
- All source code (`src/`, `app.py`, etc.)
- Configuration files (`config/`, `requirements.txt`)
- Documentation (`README.md`, `QUICKSTART.md`, etc.)
- Setup scripts (`setup.sh`, `setup.bat`)

### ❌ Will be ignored (via `.gitignore`):
- Python cache (`__pycache__/`, `*.pyc`)
- Virtual environments (`venv/`, `env/`)
- Trained models (`models/*.joblib`, `models/*.h5`)
- Generated data (`data/*.csv`)
- Logs (`*.log`)
- IDE files (`.vscode/`, `.idea/`)

**Note**: Models and data are excluded because they're large and can be regenerated using `train_models.py`

---

## After Pushing to GitHub

### 1. Add Repository Description
- Go to your repository on GitHub
- Click the ⚙️ icon next to "About"
- Add description: "AI-powered zero-day network attack detection using ML ensemble (Isolation Forest, Autoencoder, Random Forest, XGBoost) with SHAP explainability"
- Add topics: `machine-learning`, `cybersecurity`, `intrusion-detection`, `streamlit`, `xgboost`, `shap`

### 2. Enable GitHub Pages (Optional)
If you want to host documentation:
- Go to Settings → Pages
- Source: Deploy from branch `main`
- Folder: `/docs` (you'd need to create this)

### 3. Add Repository Badge
Add this to the top of your README.md:
```markdown
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
```

### 4. Set Up GitHub Actions (Optional)
Create `.github/workflows/test.yml` for automated testing:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run verification
        run: python verify_system.py
```

---

## Verifying Your Push

After pushing, verify on GitHub:
1. Go to `https://github.com/YOUR_USERNAME/zero-day-attack-detection`
2. Check that all files are visible
3. Verify README.md displays correctly
4. Check that .gitignore is working (no model files should be there)

---

## Cloning on Another Machine

Anyone (or you on another machine) can clone and run:

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/zero-day-attack-detection.git
cd zero-day-attack-detection

# Install dependencies
pip install -r requirements.txt

# Train models
python train_models.py

# Run dashboard
streamlit run app.py
```

---

## Updating Your Repository

When you make changes:

```bash
# Check what changed
git status

# Stage changes
git add .

# Commit with message
git commit -m "Description of changes"

# Push to GitHub
git push
```

---

## Sharing Your Project

Once on GitHub, share your project:
- Repository URL: `https://github.com/YOUR_USERNAME/zero-day-attack-detection`
- Live demo: Deploy to Streamlit Cloud (see below)

---

## Deploy to Streamlit Cloud (Optional)

Make your dashboard publicly accessible:

1. Go to https://streamlit.io/cloud
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `zero-day-attack-detection`
5. Main file: `app.py`
6. Click "Deploy"

**Note**: You'll need to add model training to the deployment or upload pre-trained models.

---

## Troubleshooting

### "Permission denied (publickey)"
```bash
# Use HTTPS instead of SSH
git remote set-url origin https://github.com/YOUR_USERNAME/zero-day-attack-detection.git
```

### "Remote already exists"
```bash
# Remove and re-add
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/zero-day-attack-detection.git
```

### "Large files detected"
If models were accidentally staged:
```bash
git rm --cached models/*.joblib models/*.h5
git commit -m "Remove model files"
```

---

## Next Steps

1. ✅ Push code to GitHub
2. ✅ Add repository description and topics
3. ✅ Write a brief project summary in Issues or Wiki
4. ✅ Consider adding GitHub Actions for CI/CD
5. ✅ Deploy to Streamlit Cloud for live demo
6. ✅ Share with the community!

---

**Ready to push your code to GitHub!** 🚀

If you need help with any step, let me know!
