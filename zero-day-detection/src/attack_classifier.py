"""
Attack Classifier Component
Classifies detected anomalies using Random Forest and XGBoost
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import joblib
import logging
import time
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)


class AttackClassifier:
    """Classifies attacks using Random Forest and XGBoost"""
    
    # Requirement 4, AC1: Attack classification taxonomy
    ATTACK_CLASSES = ['DoS', 'Probe', 'R2L', 'U2R', 'Normal']
    
    def __init__(self, config: Dict):
        self.config = config
        self.random_forest = None
        self.xgboost = None
        
    def train_random_forest(self, X_train: np.ndarray, y_train: np.ndarray) -> RandomForestClassifier:
        """
        Train Random Forest classifier
        
        Args:
            X_train: Training features
            y_train: Training labels
            
        Returns:
            Trained Random Forest model
        """
        # Requirement 4, AC4: At least 100 decision trees
        self.random_forest = RandomForestClassifier(
            n_estimators=self.config['random_forest']['n_estimators'],
            max_depth=self.config['random_forest']['max_depth'],
            random_state=self.config['random_forest']['random_state'],
            n_jobs=-1
        )
        
        self.random_forest.fit(X_train, y_train)
        logger.info("Random Forest trained successfully")
        return self.random_forest
    
    def train_xgboost(self, X_train: np.ndarray, y_train: np.ndarray) -> xgb.XGBClassifier:
        """
        Train XGBoost classifier
        
        Args:
            X_train: Training features
            y_train: Training labels
            
        Returns:
            Trained XGBoost model
        """
        self.xgboost = xgb.XGBClassifier(
            n_estimators=self.config['xgboost']['n_estimators'],
            max_depth=self.config['xgboost']['max_depth'],
            learning_rate=self.config['xgboost']['learning_rate'],
            random_state=self.config['xgboost']['random_state'],
            n_jobs=-1
        )
        
        self.xgboost.fit(X_train, y_train)
        logger.info("XGBoost trained successfully")
        return self.xgboost
    
    def classify_random_forest(self, feature_vector: np.ndarray) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Classify using Random Forest
        
        Args:
            feature_vector: Feature vector to classify
            
        Returns:
            Tuple of (classification result dict, error message)
        """
        # Requirement 4, AC7: Handle model unavailability
        if self.random_forest is None:
            error_msg = "Random Forest model unavailable"
            logger.error(error_msg)
            return None, error_msg
        
        if feature_vector.ndim == 1:
            feature_vector = feature_vector.reshape(1, -1)
        
        # Requirement 4, AC6: Validate dimensionality
        expected_dim = self.random_forest.n_features_in_
        if feature_vector.shape[1] != expected_dim:
            error_msg = f"Dimension mismatch: expected {expected_dim}, got {feature_vector.shape[1]}"
            logger.error(error_msg)
            return None, error_msg
        
        # Requirement 4, AC5: Complete within 50ms (95th percentile)
        start_time = time.time()
        
        # Requirement 4, AC1, AC2: Predict class and confidence
        predicted_class = self.random_forest.predict(feature_vector)[0]
        confidence_probs = self.random_forest.predict_proba(feature_vector)[0]
        confidence = float(np.max(confidence_probs))
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Requirement 4, AC8: Handle timeout
        if elapsed_ms > 50:
            logger.warning(f"Random Forest classification took {elapsed_ms:.2f}ms (>50ms threshold)")
            if elapsed_ms > 100:  # Hard timeout
                error_msg = f"Classification timeout: {elapsed_ms:.2f}ms"
                logger.error(error_msg)
                return None, error_msg
        
        # Requirement 4, AC3: Structured output with class and confidence
        result = {
            'class': predicted_class,
            'confidence': round(confidence, 2)  # AC2: 2 decimal places
        }
        
        logger.debug(f"Random Forest prediction: {result}")
        return result, None
    
    def classify_xgboost(self, feature_vector: np.ndarray) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Classify using XGBoost
        
        Args:
            feature_vector: Feature vector to classify
            
        Returns:
            Tuple of (classification result dict, error message)
        """
        # Requirement 5, AC4: Handle model unavailability with fallback
        if self.xgboost is None:
            error_msg = "XGBoost model unavailable"
            logger.error(error_msg)
            
            # Fallback to Random Forest if available
            if self.random_forest is not None:
                logger.info("Using Random Forest as fallback")
                return self.classify_random_forest(feature_vector)
            
            return None, error_msg
        
        if feature_vector.ndim == 1:
            feature_vector = feature_vector.reshape(1, -1)
        
        # Requirement 5, AC5: Validate dimensionality
        expected_dim = self.xgboost.n_features_in_
        if feature_vector.shape[1] != expected_dim:
            error_msg = f"Dimension mismatch: expected {expected_dim}, got {feature_vector.shape[1]}"
            logger.error(error_msg)
            return None, error_msg
        
        # Requirement 5, AC1: Predict from attack taxonomy
        predicted_class = self.xgboost.predict(feature_vector)[0]
        
        # Requirement 5, AC2: Confidence in range 0.0 to 1.0
        confidence_probs = self.xgboost.predict_proba(feature_vector)[0]
        confidence = float(np.max(confidence_probs))
        
        result = {
            'class': predicted_class,
            'confidence': round(confidence, 2)
        }
        
        logger.debug(f"XGBoost prediction: {result}")
        return result, None
    
    def classify(self, feature_vector: np.ndarray) -> Dict:
        """
        Classify using both models
        
        Args:
            feature_vector: Feature vector to classify
            
        Returns:
            Dictionary with classifications from both models
        """
        results = {
            'random_forest': None,
            'xgboost': None,
            'errors': []
        }
        
        # Random Forest classification
        rf_result, rf_error = self.classify_random_forest(feature_vector)
        results['random_forest'] = rf_result
        if rf_error:
            results['errors'].append(f"Random Forest: {rf_error}")
        
        # XGBoost classification
        xgb_result, xgb_error = self.classify_xgboost(feature_vector)
        results['xgboost'] = xgb_result
        if xgb_error:
            results['errors'].append(f"XGBoost: {xgb_error}")
        
        return results
    
    def save_models(self, rf_path: str, xgb_path: str):
        """Save trained models"""
        if self.random_forest:
            joblib.dump(self.random_forest, rf_path)
            logger.info(f"Random Forest saved to {rf_path}")
        
        if self.xgboost:
            joblib.dump(self.xgboost, xgb_path)
            logger.info(f"XGBoost saved to {xgb_path}")
    
    def load_models(self, rf_path: str, xgb_path: str):
        """Load trained models"""
        try:
            self.random_forest = joblib.load(rf_path)
            logger.info(f"Random Forest loaded from {rf_path}")
        except Exception as e:
            logger.error(f"Failed to load Random Forest: {e}")
        
        try:
            # Requirement 5, AC3: Load from persistent storage
            self.xgboost = joblib.load(xgb_path)
            logger.info(f"XGBoost loaded from {xgb_path}")
        except Exception as e:
            logger.error(f"Failed to load XGBoost: {e}")
