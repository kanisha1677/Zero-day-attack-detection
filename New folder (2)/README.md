# 🛡️ Zero-Day Network Attack Detection System

An AI-powered intrusion detection system that identifies previously unknown network attacks through advanced machine learning techniques.

## 🌟 Features

- **Zero-Day Attack Detection**: Detects unknown attacks without relying on signatures
- **Multi-Model Ensemble**: Combines Isolation Forest, Autoencoder, Random Forest, and XGBoost
- **SHAP Explainability**: Provides interpretable explanations for each detection
- **Real-Time Dashboard**: Streamlit-based interface with live alerts and analytics
- **High Performance**: 1000+ samples/second throughput, <2s latency

## 🏗️ Architecture

```
Network Traffic → Feature Extraction → Anomaly Detection → Classification → 
Ensemble Voting → SHAP Explainability → Alert Dashboard
```

### Components

1. **Feature Extractor**: Extracts and normalizes network traffic features
2. **Anomaly Detector**: 
   - Isolation Forest for outlier detection
   - Autoencoder for complex pattern recognition
3. **Attack Classifier**:
   - Random Forest (100+ trees)
   - XGBoost for gradient boosting
4. **Ensemble Voter**: Combines predictions with weighted voting
5. **Explainability Engine**: SHAP-based feature importance
6. **Alert Dashboard**: Real-time Streamlit visualization

## 🎯 Attack Types Detected

- **DoS** (Denial of Service): Resource exhaustion attacks
- **Probe**: Network scanning and reconnaissance
- **R2L** (Remote to Local): Unauthorized access attempts
- **U2R** (User to Root): Privilege escalation

## 📋 Requirements

- Python 3.8+
- TensorFlow/Keras
- Scikit-learn
- XGBoost
- Streamlit
- SHAP
- See `requirements.txt` for full list

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Train Models

```bash
python train_models.py
```

This will:
- Generate synthetic training data
- Train all ML models (Isolation Forest, Autoencoder, Random Forest, XGBoost)
- Save models with SHA-256 checksums to `./models/`

### 3. Run Dashboard

```bash
streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`

## 📊 Dashboard Features

### Real-Time Alerts
- Live attack detection display
- Confidence scores and timestamps
- SHAP explanations with feature importance charts
- Filter by time range and attack type

### Analytics
- Detection trends over time
- Attack type distribution
- Confidence score histograms
- Performance metrics

### Manual Testing
- Test the system with custom network traffic data
- Instant analysis and visualization

## ⚙️ Configuration

Edit `config/detection_config.yaml` to customize:

```yaml
# Detection threshold (0.0 to 1.0)
detection_threshold: 0.5

# Model weights for ensemble voting
model_weights:
  isolation_forest: 0.25
  autoencoder: 0.25
  random_forest: 0.25
  xgboost: 0.25

# Isolation Forest contamination parameter
isolation_forest:
  contamination: 0.1
  n_estimators: 100
```

## 📁 Project Structure

```
.
├── app.py                      # Streamlit dashboard
├── train_models.py             # Model training script
├── requirements.txt            # Python dependencies
├── config/
│   └── detection_config.yaml   # System configuration
├── src/
│   ├── feature_extractor.py    # Feature extraction
│   ├── anomaly_detector.py     # Anomaly detection (IF + AE)
│   ├── attack_classifier.py    # Classification (RF + XGB)
│   ├── ensemble_voter.py       # Ensemble voting
│   ├── explainability_engine.py # SHAP explanations
│   ├── detection_system.py     # Main orchestrator
│   └── data_generator.py       # Synthetic data generation
├── models/                     # Trained models (generated)
└── data/                       # Training data (generated)
```

## 🔬 Technical Details

### Feature Extraction
- **Numerical Features**: packet_size, byte_count, duration_seconds
- **Categorical Features**: protocol_type, flag_status, service_type
- **Normalization**: Min-max scaling (0 to 1)
- **Encoding**: Label encoding for categorical variables

### Anomaly Detection
- **Isolation Forest**: Score range -1.0 to 1.0 (< -0.5 = anomaly)
- **Autoencoder**: MSE reconstruction error normalized to 0.0-1.0
- **Timeout**: 100ms per sample (95th percentile)

### Classification
- **Random Forest**: 100 trees, multi-class output
- **XGBoost**: Gradient boosting with 100 estimators
- **Output**: Class + confidence (0.00-1.00, 2 decimals)
- **Timeout**: 50ms per sample (95th percentile)

### Ensemble Voting
- **Strategy**: Weighted majority voting
- **Tie-breaking**: Highest confidence score
- **Binary Output**: Attack or Normal

### SHAP Explanations
- **Top Features**: 10 most important features
- **Contributions**: Positive (supporting) and negative (opposing)
- **Timeout**: 500ms per explanation

## 📈 Performance Metrics

- **Throughput**: 1000+ samples/second sustained
- **Latency**: <2 seconds (95th percentile)
- **Concurrent Processing**: 100 samples
- **Accuracy**: Within 5% of baseline under load

## 🧪 Testing

### Manual Testing via Dashboard
1. Navigate to the "Manual Test" tab
2. Enter network traffic parameters
3. Click "Analyze Traffic"
4. View detection results and explanations

### Programmatic Testing
```python
from detection_system import DetectionSystem

# Initialize system
system = DetectionSystem()
system.load_models()

# Test traffic
traffic_data = {
    'timestamp': '2024-01-01T12:00:00',
    'packet_size': 1200,
    'byte_count': 8000,
    'duration_seconds': 0.5,
    'protocol_type': 'tcp',
    'flag_status': 'S0',
    'service_type': 'http'
}

# Analyze
result = system.process_traffic(traffic_data)
print(f"Decision: {result['decision']}")
print(f"Confidence: {result['confidence']:.2f}")
```

## 📝 Data Format Support

### CSV Format
```csv
timestamp,packet_size,byte_count,duration_seconds,protocol_type,flag_status,service_type
2024-01-01T12:00:00,1000,5000,1.5,tcp,SF,http
```

### JSON Format
```json
{
  "timestamp": "2024-01-01T12:00:00",
  "packet_size": 1000,
  "byte_count": 5000,
  "duration_seconds": 1.5,
  "protocol_type": "tcp",
  "flag_status": "SF",
  "service_type": "http"
}
```

## 🔒 Security Considerations

- Models validated with SHA-256 checksums
- Degraded mode operation if models fail to load
- Input validation on all network traffic data
- Comprehensive error logging

## 📊 Logging

Configure logging level via environment variable:
```bash
export LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

Logs include:
- Detection events (JSON format)
- Model operations
- Pipeline errors with stack traces
- Performance metrics (Prometheus format)

## 🚧 Future Enhancements

- Real-time packet capture integration
- Cloud deployment support
- IoT device integration
- Automated response system
- Advanced threat intelligence feeds

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## 📞 Support

For issues or questions, please open a GitHub issue.

---

**Built with ❤️ using Python, Machine Learning, and Streamlit**
