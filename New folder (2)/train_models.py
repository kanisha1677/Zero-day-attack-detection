"""
Model Training Script
Train all ML models for the detection system
"""

import os
import sys
import hashlib
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_generator import DataGenerator
from feature_extractor import FeatureExtractor
from anomaly_detector import AnomalyDetector
from attack_classifier import AttackClassifier
import yaml
import joblib
from sklearn.preprocessing import LabelEncoder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def compute_checksum(filepath: str) -> str:
    """Compute SHA-256 checksum of file"""
    with open(filepath, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    return file_hash


def save_with_checksum(model, filepath: str):
    """Save model and compute checksum"""
    # Create directory if it doesn't exist
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    # Save model
    if filepath.endswith('.h5'):
        model.save(filepath)
    else:
        joblib.dump(model, filepath)
    
    # Compute and save checksum
    checksum = compute_checksum(filepath)
    with open(filepath + '.sha256', 'w') as f:
        f.write(checksum)
    
    logger.info(f"Model saved: {filepath}")
    logger.info(f"Checksum: {checksum}")


def main():
    """Main training function"""
    logger.info("Starting model training...")
    
    # Load configuration
    with open('config/detection_config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Generate training data
    logger.info("Generating training data...")
    train_df = DataGenerator.generate_dataset(
        normal=2000,
        dos=400,
        probe=300,
        r2l=200,
        u2r=100
    )
    
    logger.info(f"Generated {len(train_df)} training samples")
    logger.info(f"Class distribution:\n{train_df['label'].value_counts()}")
    
    # Save dataset
    os.makedirs('data', exist_ok=True)
    train_df.to_csv('data/training_data.csv', index=False)
    logger.info("Training data saved to data/training_data.csv")
    
    # Initialize and fit feature extractor
    logger.info("Training feature extractor...")
    feature_extractor = FeatureExtractor()
    feature_extractor.fit(train_df)
    
    # Extract features
    X_train, errors = feature_extractor.extract_features_batch(train_df)
    if errors:
        logger.warning(f"Feature extraction errors: {len(errors)}")
    
    y_train = train_df['label'].values[:len(X_train)]
    
    # Encode labels for XGBoost
    label_encoder = LabelEncoder()
    y_train_encoded = label_encoder.fit_transform(y_train)
    
    logger.info(f"Feature matrix shape: {X_train.shape}")
    
    # Save feature extractor
    model_paths = config['model_paths']
    feature_extractor.save(model_paths['scaler'], model_paths['encoder'])
    
    # Train Isolation Forest
    logger.info("Training Isolation Forest...")
    anomaly_detector = AnomalyDetector(config)
    
    # Train on normal data only
    normal_indices = train_df['label'] == 'Normal'
    X_normal = X_train[normal_indices[:len(X_train)]]
    
    isolation_forest = anomaly_detector.train_isolation_forest(X_normal)
    save_with_checksum(isolation_forest, model_paths['isolation_forest'])
    
    # Train Autoencoder
    logger.info("Training Autoencoder...")
    autoencoder = anomaly_detector.train_autoencoder(X_normal)
    autoencoder.save(model_paths['autoencoder'])
    
    # Save max reconstruction error
    joblib.dump(
        anomaly_detector.max_reconstruction_error,
        model_paths['autoencoder'].replace('.h5', '_max_error.joblib')
    )
    
    # Compute checksum for autoencoder
    checksum = compute_checksum(model_paths['autoencoder'])
    with open(model_paths['autoencoder'] + '.sha256', 'w') as f:
        f.write(checksum)
    
    # Train Random Forest
    logger.info("Training Random Forest...")
    attack_classifier = AttackClassifier(config)
    random_forest = attack_classifier.train_random_forest(X_train, y_train)
    save_with_checksum(random_forest, model_paths['random_forest'])
    
    # Train XGBoost
    logger.info("Training XGBoost...")
    xgboost = attack_classifier.train_xgboost(X_train, y_train_encoded)
    save_with_checksum(xgboost, model_paths['xgboost'])
    
    # Save label encoder
    logger.info("Saving label encoder...")
    joblib.dump(label_encoder, model_paths['xgboost'].replace('.joblib', '_label_encoder.joblib'))
    
    # Evaluate models
    logger.info("\n" + "="*50)
    logger.info("Model Training Complete!")
    logger.info("="*50)
    
    # Test predictions
    logger.info("\nTesting models on sample data...")
    
    # Load models
    anomaly_detector.load_models(
        model_paths['isolation_forest'],
        model_paths['autoencoder']
    )
    attack_classifier.load_models(
        model_paths['random_forest'],
        model_paths['xgboost']
    )
    
    # Test on a few samples
    test_samples = X_train[:5]
    test_labels = y_train[:5]
    
    for i, (sample, label) in enumerate(zip(test_samples, test_labels)):
        logger.info(f"\nSample {i+1} (True label: {label}):")
        
        # Anomaly detection
        anomaly_scores = anomaly_detector.detect(sample)
        logger.info(f"  IF Score: {anomaly_scores.get('isolation_forest_score', 'N/A'):.4f}")
        logger.info(f"  AE Score: {anomaly_scores.get('autoencoder_score', 'N/A'):.4f}")
        
        # Classification
        classifications = attack_classifier.classify(sample)
        if classifications['random_forest']:
            logger.info(f"  RF: {classifications['random_forest']}")
        if classifications['xgboost']:
            logger.info(f"  XGB: {classifications['xgboost']}")
    
    logger.info("\n" + "="*50)
    logger.info("All models trained and saved successfully!")
    logger.info("="*50)
    logger.info("\nModel files:")
    for name, path in model_paths.items():
        if os.path.exists(path):
            logger.info(f"  ✓ {name}: {path}")
        else:
            logger.warning(f"  ✗ {name}: {path} (not found)")
    
    logger.info("\nYou can now run the dashboard with: streamlit run app.py")


if __name__ == "__main__":
    main()
