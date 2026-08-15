"""
Explainability Engine Component
Provides SHAP-based explanations for detection decisions
"""

import numpy as np
import shap
import logging
import time
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ExplainabilityEngine:
    """Provides SHAP-based explanations for detection decisions"""
    
    def __init__(self):
        self.explainer = None
        self.feature_names = [
            'packet_size', 'byte_count', 'duration_seconds',
            'protocol_type', 'flag_status', 'service_type'
        ]
        
    def initialize_explainer(self, model, background_data: np.ndarray):
        """
        Initialize SHAP explainer
        
        Args:
            model: Trained model for explanation
            background_data: Background dataset for SHAP
        """
        try:
            # Use KernelExplainer for model-agnostic explanations
            self.explainer = shap.KernelExplainer(
                model.predict_proba if hasattr(model, 'predict_proba') else model.predict,
                background_data[:100]  # Use subset for efficiency
            )
            logger.info("SHAP explainer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SHAP explainer: {e}")
            self.explainer = None
    
    def explain(self, feature_vector: np.ndarray, model=None) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Generate SHAP explanations for a detection
        
        Args:
            feature_vector: Feature vector to explain
            model: Optional model to use for explanation
            
        Returns:
            Tuple of (explanation dict, error message)
        """
        # Requirement 7, AC5: Handle SHAP computation failures
        if self.explainer is None and model is None:
            error_msg = "SHAP explainer not initialized and no model provided"
            logger.error(error_msg)
            return self._default_explanation(), None
        
        if feature_vector.ndim == 1:
            feature_vector = feature_vector.reshape(1, -1)
        
        # Requirement 7, AC4, AC6: Complete within 500ms or timeout
        start_time = time.time()
        timeout_ms = 500
        
        try:
            # Requirement 7, AC1: Compute SHAP values
            if self.explainer:
                shap_values = self.explainer.shap_values(feature_vector)
            else:
                # Quick TreeExplainer for tree-based models
                if hasattr(model, 'predict_proba'):
                    explainer = shap.TreeExplainer(model)
                    shap_values = explainer.shap_values(feature_vector)
                else:
                    return self._default_explanation(), "Model not compatible with SHAP"
            
            # Handle multi-class output (take first class for binary interpretation)
            if isinstance(shap_values, list):
                shap_values = shap_values[0]
            
            if shap_values.ndim > 1:
                shap_values = shap_values[0]
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            # Check timeout
            if elapsed_ms > timeout_ms:
                logger.warning(f"SHAP analysis took {elapsed_ms:.2f}ms (>{timeout_ms}ms timeout)")
                return None, f"SHAP timeout: {elapsed_ms:.2f}ms"
            
            # Requirement 7, AC2: Identify top 10 features with highest absolute SHAP values
            abs_shap_values = np.abs(shap_values)
            top_indices = np.argsort(abs_shap_values)[-10:][::-1]
            
            top_features = []
            positive_features = []
            negative_features = []
            
            for idx in top_indices:
                feature_name = self.feature_names[idx] if idx < len(self.feature_names) else f"feature_{idx}"
                shap_value = float(shap_values[idx])
                
                feature_info = {
                    'feature': feature_name,
                    'shap_value': round(shap_value, 4),
                    'importance': round(abs(shap_value), 4)
                }
                
                top_features.append(feature_info)
                
                # Requirement 7, AC3: Separate positive and negative contributions
                if shap_value > 0:
                    positive_features.append(feature_info)
                elif shap_value < 0:
                    negative_features.append(feature_info)
            
            # Requirement 7, AC7: Structured format with feature names, SHAP values, and rankings
            explanation = {
                'top_features': top_features,
                'positive_contributions': positive_features,
                'negative_contributions': negative_features,
                'computation_time_ms': round(elapsed_ms, 2)
            }
            
            logger.debug(f"SHAP explanation generated in {elapsed_ms:.2f}ms")
            return explanation, None
            
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            error_msg = f"SHAP computation failed: {str(e)}"
            logger.error(error_msg)
            
            if elapsed_ms > timeout_ms:
                return None, f"SHAP timeout: {elapsed_ms:.2f}ms"
            
            return self._default_explanation(), error_msg
    
    def _default_explanation(self) -> Dict:
        """
        Return default explanation when SHAP is unavailable
        
        Returns:
            Default explanation dictionary
        """
        return {
            'top_features': [],
            'positive_contributions': [],
            'negative_contributions': [],
            'message': 'SHAP explanation unavailable',
            'computation_time_ms': 0
        }
    
    def explain_batch(self, feature_vectors: np.ndarray, model=None) -> List[Dict]:
        """
        Generate SHAP explanations for a batch of detections
        
        Args:
            feature_vectors: Batch of feature vectors
            model: Optional model to use for explanation
            
        Returns:
            List of explanation dictionaries
        """
        explanations = []
        
        for i, feature_vector in enumerate(feature_vectors):
            explanation, error = self.explain(feature_vector, model)
            
            if error:
                logger.warning(f"Sample {i}: {error}")
            
            explanations.append(explanation if explanation else self._default_explanation())
        
        return explanations
