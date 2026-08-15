#!/bin/bash
# Git Push Script for Zero-Day Attack Detection System

echo "🚀 Pushing Zero-Day Attack Detection System to GitHub"
echo "======================================================="
echo ""

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed or not in PATH"
    exit 1
fi

# Check git status
echo "📋 Checking git status..."
git status

echo ""
echo "📁 Staging all files..."
git add .

echo ""
echo "📝 Creating commit..."
git commit -m "Add Zero-Day Network Attack Detection System

Features:
- ML-based detection (Isolation Forest, Autoencoder, Random Forest, XGBoost)
- Real-time Streamlit dashboard with alerts and analytics
- SHAP explainability for transparent AI decisions
- Ensemble voting for robust detection
- Support for DoS, Probe, R2L, U2R attack detection
- Comprehensive documentation and setup scripts
- 87% requirements coverage (13/15 requirements)

Components:
- Feature extraction and normalization
- Anomaly detection with dual models
- Attack classification with dual classifiers
- Weighted ensemble voting
- SHAP-based explanations
- Real-time visualization dashboard
- Model training pipeline with checksums
- Synthetic data generation for testing

Documentation:
- Complete README with usage instructions
- Quick start guide for immediate setup
- Requirements checklist with traceability
- Project summary and architecture overview
- GitHub setup guide for deployment"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Commit created successfully!"
    echo ""
    echo "🌐 Pushing to GitHub..."
    git push
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "======================================================="
        echo "✅ Successfully pushed to GitHub!"
        echo "======================================================="
        echo ""
        echo "📍 Your code is now on GitHub!"
        echo "🔗 Check your repository to see the changes"
        echo ""
        echo "Next steps:"
        echo "1. View your repo on GitHub"
        echo "2. Install dependencies: pip install -r requirements.txt"
        echo "3. Train models: python train_models.py"
        echo "4. Run dashboard: streamlit run app.py"
        echo ""
    else
        echo ""
        echo "❌ Push failed. Error details above."
        echo ""
        echo "Try manually:"
        echo "  git push"
        exit 1
    fi
else
    echo ""
    echo "⚠️  No changes to commit or commit failed"
    echo ""
    echo "Check 'git status' to see current state"
fi

echo "======================================================="
