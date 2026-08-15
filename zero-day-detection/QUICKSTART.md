# 🚀 Quick Start Guide

Get your Zero-Day Network Attack Detection System running in 3 steps!

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- 2GB free disk space
- 4GB RAM recommended

## Installation

### Option 1: Automated Setup (Recommended)

**Windows:**
```bash
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Create directories:**
```bash
mkdir models data logs
```

3. **Train models:**
```bash
python train_models.py
```

4. **Start dashboard:**
```bash
streamlit run app.py
```

## First Run

1. Open your browser to `http://localhost:8501`
2. You should see the dashboard with 4 tabs:
   - 🚨 Real-Time Detection
   - 📊 Analytics
   - 🧪 Manual Test
   - 📖 About

## Testing the System

### Quick Test

1. Click on the **"Manual Test"** tab
2. Use the default values or customize:
   - Packet Size: 1000 bytes
   - Byte Count: 5000 bytes
   - Duration: 1.5 seconds
   - Protocol: tcp
   - Flag Status: SF
   - Service: http
3. Click **"Analyze Traffic"**
4. View the detection result!

### Test Attack Scenarios

**DoS Attack Pattern:**
- Packet Size: 1200
- Byte Count: 8000
- Duration: 0.5
- Protocol: udp
- Flag Status: S0
- Service: http

**Probe Attack Pattern:**
- Packet Size: 100
- Byte Count: 500
- Duration: 0.3
- Protocol: icmp
- Flag Status: REJ
- Service: other

**Normal Traffic Pattern:**
- Packet Size: 500
- Byte Count: 2000
- Duration: 2.0
- Protocol: tcp
- Flag Status: SF
- Service: http

## Dashboard Features

### Real-Time Alerts
- View recent detections
- See attack classifications
- Examine SHAP explanations
- Filter by time and attack type

### Analytics
- Detection trends over time
- Attack type distribution
- Confidence score analysis
- System performance metrics

## Troubleshooting

### Models Not Found
```bash
python train_models.py
```

### Import Errors
```bash
pip install -r requirements.txt --upgrade
```

### Port Already in Use
```bash
streamlit run app.py --server.port 8502
```

### Low Performance
- Reduce batch size in config
- Disable SHAP explanations temporarily
- Close other applications

## Configuration

Edit `config/detection_config.yaml` to customize:

```yaml
detection_threshold: 0.5  # Lower = more sensitive
model_weights:            # Adjust model importance
  isolation_forest: 0.25
  autoencoder: 0.25
  random_forest: 0.25
  xgboost: 0.25
```

## Next Steps

1. ✅ Test with various traffic patterns
2. ✅ Explore the Analytics dashboard
3. ✅ Review SHAP explanations
4. ✅ Adjust detection threshold
5. ✅ Integrate with your data sources

## Need Help?

- Check `README.md` for detailed documentation
- Review logs in the `logs/` directory
- Open an issue on GitHub

---

**Ready to detect zero-day attacks! 🛡️**
