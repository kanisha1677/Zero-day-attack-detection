"""
Feature Extractor Component
Extracts and normalizes features from network traffic data
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
import joblib
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Extracts relevant features from network traffic data"""
    
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.label_encoders = {}
        self.numerical_features = ['packet_size', 'byte_count', 'duration_seconds']
        self.categorical_features = ['protocol_type', 'flag_status', 'service_type']
        self.required_fields = ['packet_size', 'protocol_type', 'timestamp']
        self.is_fitted = False
        
    def fit(self, data: pd.DataFrame) -> 'FeatureExtractor':
        """
        Fit the feature extractor on training data
        
        Args:
            data: Training data DataFrame
            
        Returns:
            self
        """
        # Fit scaler on numerical features
        self.scaler.fit(data[self.numerical_features])
        
        # Fit label encoders on categorical features
        for feature in self.categorical_features:
            le = LabelEncoder()
            le.fit(data[feature].fillna('unknown'))
            self.label_encoders[feature] = le
            
        self.is_fitted = True
        logger.info("Feature extractor fitted successfully")
        return self
    
    def extract_features(self, traffic_data: Dict[str, Any]) -> Optional[np.ndarray]:
        """
        Extract and normalize features from network traffic data
        
        Args:
            traffic_data: Dictionary containing network traffic data
            
        Returns:
            Feature vector as numpy array of 6 elements, or None if validation fails
        """
        # Requirement 1, AC4: Validate required fields
        missing_fields = [field for field in self.required_fields 
                         if field not in traffic_data or traffic_data[field] is None]
        
        if missing_fields:
            logger.error(f"Validation failed: missing required fields {missing_fields}")
            return None
        
        # Requirement 1, AC3: Handle null values with defaults
        numerical_values = []
        for feature in self.numerical_features:
            value = traffic_data.get(feature, 0)
            if value is None or (isinstance(value, float) and np.isnan(value)):
                value = 0
            numerical_values.append(value)
        
        categorical_values = []
        for feature in self.categorical_features:
            value = traffic_data.get(feature, 'unknown')
            if value is None or value == '':
                value = 'unknown'
            categorical_values.append(value)
        
        # Requirement 1, AC2: Normalize numerical features to range 0 to 1
        numerical_array = np.array(numerical_values).reshape(1, -1)
        if self.is_fitted:
            normalized_numerical = self.scaler.transform(numerical_array)
        else:
            # If not fitted, use the raw values (for initial usage)
            normalized_numerical = numerical_array
        
        # Requirement 1, AC1: Encode categorical features
        encoded_categorical = []
        for i, feature in enumerate(self.categorical_features):
            value = categorical_values[i]
            if self.is_fitted and feature in self.label_encoders:
                le = self.label_encoders[feature]
                # Handle unknown categories
                if value not in le.classes_:
                    value = 'unknown'
                    if value not in le.classes_:
                        encoded_value = 0
                    else:
                        encoded_value = le.transform([value])[0]
                else:
                    encoded_value = le.transform([value])[0]
                encoded_categorical.append(encoded_value)
            else:
                encoded_categorical.append(0)
        
        # Requirement 1, AC5: Produce fixed-length array of 6 elements
        feature_vector = np.concatenate([
            normalized_numerical.flatten(),
            np.array(encoded_categorical)
        ])
        
        logger.debug(f"Extracted feature vector: {feature_vector}")
        return feature_vector
    
    def extract_features_batch(self, traffic_df: pd.DataFrame) -> Tuple[Optional[np.ndarray], list]:
        """
        Extract features from a batch of network traffic data
        
        Args:
            traffic_df: DataFrame containing network traffic data
            
        Returns:
            Tuple of (feature matrix, list of error messages)
        """
        feature_vectors = []
        errors = []
        
        for idx, row in traffic_df.iterrows():
            traffic_dict = row.to_dict()
            features = self.extract_features(traffic_dict)
            
            if features is not None:
                feature_vectors.append(features)
            else:
                errors.append(f"Row {idx}: Validation failed")
        
        if not feature_vectors:
            return None, errors
        
        return np.array(feature_vectors), errors
    
    def save(self, scaler_path: str, encoder_path: str):
        """Save fitted scaler and encoders"""
        if not self.is_fitted:
            raise ValueError("Feature extractor must be fitted before saving")
        
        joblib.dump(self.scaler, scaler_path)
        joblib.dump(self.label_encoders, encoder_path)
        logger.info(f"Feature extractor saved to {scaler_path} and {encoder_path}")
    
    def load(self, scaler_path: str, encoder_path: str):
        """Load fitted scaler and encoders"""
        self.scaler = joblib.load(scaler_path)
        self.label_encoders = joblib.load(encoder_path)
        self.is_fitted = True
        logger.info(f"Feature extractor loaded from {scaler_path} and {encoder_path}")
