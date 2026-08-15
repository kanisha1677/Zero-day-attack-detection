#!/bin/bash
# Setup script for Zero-Day Network Attack Detection System

echo "🛡️  Zero-Day Network Attack Detection System Setup"
echo "=================================================="
echo ""

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p models
mkdir -p data
mkdir -p logs

# Create .gitkeep files
touch models/.gitkeep
touch data/.gitkeep
touch logs/.gitkeep

echo "✅ Directories created"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""

# Train models
echo "🔬 Training machine learning models..."
echo "This may take a few minutes..."
python train_models.py

if [ $? -eq 0 ]; then
    echo "✅ Models trained successfully"
else
    echo "❌ Model training failed"
    exit 1
fi

echo ""
echo "=================================================="
echo "✅ Setup complete!"
echo ""
echo "🚀 To start the dashboard, run:"
echo "   streamlit run app.py"
echo ""
echo "📊 The dashboard will be available at:"
echo "   http://localhost:8501"
echo "=================================================="
