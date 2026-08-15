"""
Anomaly Detector Component
Combines Isolation Forest and Autoencoder for anomaly detection
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from tensorflow import keras
from keras import layers
import joblib
import logging
import time
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Detects anomalies using Isolation Forest and Autoencoder"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.isolation_forest = None
        self.autoencoder = None
        self.max_reconstruction_error = None
        
    def train_isolation_forest(self, X_train: np.ndarray) -> IsolationForest:
        """
        Train Isolation Forest model
        
        Args:
            X_train: Training data
            
        Returns:
            Trained Isolation Forest model
        """
        # Requirement 2, AC3: Use configured contamination parameter
        contamination = self.config['isolation_forest']['contamination']
        n_estimators = self.config['isolation_forest']['n_estimators']
        
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            max_samples=self.config['isolation_forest']['max_samples'],
            random_state=self.config['isolation_forest']['random_state']
        )
        
        # Requirement 2, AC7: Fit on historical normal network traffic data
        self.isolation_forest.fit(X_train)
        logger.info("Isolation Forest trained successfully")
        return self.isolation_forest
    
    def train_autoencoder(self, X_train: np.ndarray) -> keras.Model:
        """
        Train Autoencoder model
        
        Args:
            X_train: Training data
            
        Returns:
            Trained Autoencoder model
        """
        input_dim = X_train.shape[1]
        encoding_dim = self.config['autoencoder']['encoding_dim']
        
        # Build autoencoder architecture
        input_layer = layers.Input(shape=(input_dim,))
        encoded = layers.Dense(encoding_dim, activation='relu')(input_layer)
        decoded = layers.Dense(input_dim, activation='sigmoid')(encoded)
        
        self.autoencoder = keras.Model(input_layer, decoded)
        self.autoencoder.compile(optimizer='adam', loss='mse')
        
        # Train autoencoder
        self.autoencoder.fit(
            X_train, X_train,
            epochs=self.config['autoencoder']['epochs'],
            batch_size=self.config['autoencoder']['batch_size'],
            validation_split=self.config['autoencoder']['validation_split'],
            verbose=0
        )
        
        # Compute max reconstruction error for normalization
        reconstructions = self.autoencoder.predict(X_train, verbose=0)
        reconstruction_errors = np.mean(np.square(X_train - reconstructions), axis=1)
        self.max_reconstruction_error = np.max(reconstruction_errors)
        
        logger.info("Autoencoder trained successfully")
        return self.autoencoder
    
    def detect_isolation_forest(self, feature_vector: np.ndarray) -> Tuple[Optional[float], Optional[str]]:
        """
        Detect anomalies using Isolation Forest
        
        Args:
            feature_vector: Feature vector to analyze
            
        Returns:
            Tuple of (anomaly_score, error_message)
        """
        if self.isolation_forest is None:
            error_msg = "Isolation Forest model not loaded"
            logger.error(error_msg)
            return None, error_msg
        
        # Requirement 2, AC5, AC6: Validate feature vector
        if not isinstance(feature_vector, np.ndarray):
            error_msg = "Feature vector must be numpy array"
            logger.error(error_msg)
            return None, error_msg
        
        if feature_vector.ndim == 1:
            feature_vector = feature_vector.reshape(1, -1)
        
        expected_dim = self.isolation_forest.n_features_in_
        if feature_vector.shape[1] != expected_dim:
            error_msg = f"Dimension mismatch: expected {expected_dim}, got {feature_vector.shape[1]}"
            logger.error(error_msg)
            return None, error_msg
        
        if not np.issubdtype(feature_vector.dtype, np.number):
            error_msg = "Feature vector contains non-numerical values"
            logger.error(error_msg)
            return None, error_msg
        
        # Requirement 2, AC4: Complete within 100ms (95th percentile)
        start_time = time.time()
        
        # Requirement 2, AC1: Compute anomaly score in range -1.0 to 1.0
        anomaly_score = self.isolation_forest.score_samples(feature_vector)[0]
        
        elapsed_ms = (time.time() - start_time) * 1000
        if elapsed_ms > 100:
            logger.warning(f"Isolation Forest scoring took {elapsed_ms:.2f}ms (>100ms threshold)")
        
        # Requirement 2, AC2: Scores below -0.5 indicate higher anomaly likelihood
        logger.debug(f"Isolation Forest anomaly score: {anomaly_score:.4f}")
        return float(anomaly_score), None
    
    def detect_autoencoder(self, feature_vector: np.ndarray) -> Tuple[Optional[float], Optional[str]]:
        """
        Detect anomalies using Autoencoder
        
        Args:
            feature_vector: Feature vector to analyze
            
        Returns:
            Tuple of (anomaly_score, error_message)
        """
        # Requirement 3, AC4: Handle missing model
        if self.autoencoder is None:
            error_msg = "Autoencoder model not loaded"
            logger.error(error_msg)
            return None, error_msg
        
        if feature_vector.ndim == 1:
            feature_vector = feature_vector.reshape(1, -1)
        
        # Requirement 3, AC5: Handle incompatible dimensions
        expected_dim = self.autoencoder.input_shape[1]
        if feature_vector.shape[1] != expected_dim:
            error_msg = f"Dimension mismatch: expected {expected_dim}, got {feature_vector.shape[1]}"
            logger.error(error_msg)
            return None, error_msg
        
        # Requirement 3, AC1: Compute reconstruction error (MSE)
        reconstruction = self.autoencoder.predict(feature_vector, verbose=0)
        reconstruction_error = np.mean(np.square(feature_vector - reconstruction))
        
        # Requirement 3, AC2: Normalize to range 0.0 to 1.0
        if self.max_reconstruction_error and self.max_reconstruction_error > 0:
            anomaly_score = min(reconstruction_error / self.max_reconstruction_error, 1.0)
        else:
            anomaly_score = reconstruction_error
        
        logger.debug(f"Autoencoder anomaly score: {anomaly_score:.4f}")
        return float(anomaly_score), None
    
    def detect(self, feature_vector: np.ndarray) -> Dict[str, Optional[float]]:
        """
        Detect anomalies using both models
        
        Args:
            feature_vector: Feature vector to analyze
            
        Returns:
            Dictionary with anomaly scores from both models
        """
        results = {
            'isolation_forest_score': None,
            'autoencoder_score': None,
            'errors': []
        }
        
        # Isolation Forest detection
        if_score, if_error = self.detect_isolation_forest(feature_vector)
        results['isolation_forest_score'] = if_score
        if if_error:
            results['errors'].append(f"Isolation Forest: {if_error}")
        
        # Autoencoder detection
        ae_score, ae_error = self.detect_autoencoder(feature_vector)
        results['autoencoder_score'] = ae_score
        if ae_error:
            results['errors'].append(f"Autoencoder: {ae_error}")
        
        return results
    
    def save_models(self, if_path: str, ae_path: str):
        """Save trained models"""
        if self.isolation_forest:
            joblib.dump(self.isolation_forest, if_path)
            logger.info(f"Isolation Forest saved to {if_path}")
        
        if self.autoencoder:
            self.autoencoder.save(ae_path)
            # Save max reconstruction error
            joblib.dump(self.max_reconstruction_error, ae_path.replace('.h5', '_max_error.joblib'))
            logger.info(f"Autoencoder saved to {ae_path}")
    
    def load_models(self, if_path: str, ae_path: str):
        """Load trained models"""
        try:
            self.isolation_forest = joblib.load(if_path)
            logger.info(f"Isolation Forest loaded from {if_path}")
        except Exception as e:
            logger.error(f"Failed to load Isolation Forest: {e}")
        
        try:
            # Requirement 3, AC3: Load from persistent storage
            self.autoencoder = keras.models.load_model(ae_path)
            self.max_reconstruction_error = joblib.load(ae_path.replace('.h5', '_max_error.joblib'))
            logger.info(f"Autoencoder loaded from {ae_path}")
        except Exception as e:
            logger.error(f"Failed to load Autoencoder: {e}")
