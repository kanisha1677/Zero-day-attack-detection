"""
Ensemble Voter Component
Combines predictions from multiple models through voting
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class EnsembleVoter:
    """Combines predictions from multiple models using ensemble voting"""
    
    def __init__(self, model_weights: Dict[str, float]):
        # Requirement 6, AC2, AC5: Weights in range 0.0 to 1.0, normalized to sum to 1.0
        self.model_weights = self._normalize_weights(model_weights)
        logger.info(f"Ensemble voter initialized with weights: {self.model_weights}")
    
    def _normalize_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """Normalize weights to sum to 1.0"""
        total = sum(weights.values())
        if total == 0:
            logger.warning("Total weight is 0, using equal weights")
            return {k: 1.0/len(weights) for k in weights}
        return {k: v/total for k, v in weights.items()}
    
    def vote(self, predictions: Dict[str, Optional[Dict]]) -> Tuple[str, float]:
        """
        Combine predictions using weighted voting
        
        Args:
            predictions: Dictionary of model predictions
                         Format: {'model_name': {'class': str, 'confidence': float}}
        
        Returns:
            Tuple of (final_decision, confidence_score)
        """
        # Filter out None predictions
        valid_predictions = {k: v for k, v in predictions.items() if v is not None}
        
        # Requirement 6, AC6: Handle single prediction
        if len(valid_predictions) == 0:
            logger.error("No valid predictions available")
            return "Normal", 0.0
        
        if len(valid_predictions) == 1:
            logger.info(f"Only one model prediction available: {list(valid_predictions.keys())[0]}")
            single_pred = list(valid_predictions.values())[0]
            decision = "Attack" if single_pred['class'] != 'Normal' else "Normal"
            return decision, float(single_pred['confidence'])
        
        # Requirement 6, AC1: Combine predictions from at least 2 models
        if len(valid_predictions) < 2:
            logger.warning(f"Less than 2 predictions available: {len(valid_predictions)}")
        
        # Collect votes with weights
        votes = {'Attack': 0.0, 'Normal': 0.0}
        confidences = []
        
        for model_name, prediction in valid_predictions.items():
            weight = self.model_weights.get(model_name, 0.0)
            predicted_class = prediction['class']
            confidence = prediction['confidence']
            
            # Binary decision: Attack or Normal
            decision = "Attack" if predicted_class != 'Normal' else "Normal"
            votes[decision] += weight
            confidences.append((confidence, weight))
        
        # Requirement 6, AC7: Handle tie-breaking
        if votes['Attack'] == votes['Normal']:
            logger.info("Voting tie detected, using highest confidence as tie-breaker")
            # Find prediction with highest confidence
            max_confidence_pred = max(valid_predictions.items(), 
                                     key=lambda x: x[1]['confidence'])
            final_decision = "Attack" if max_confidence_pred[1]['class'] != 'Normal' else "Normal"
        else:
            # Requirement 6, AC3: Produce final binary decision
            final_decision = max(votes, key=votes.get)
        
        # Requirement 6, AC4: Compute overall confidence by weighted averaging
        if confidences:
            total_weight = sum(w for _, w in confidences)
            if total_weight > 0:
                confidence_score = sum(c * w for c, w in confidences) / total_weight
            else:
                confidence_score = 0.0
        else:
            confidence_score = 0.0
        
        logger.info(f"Ensemble decision: {final_decision} with confidence {confidence_score:.2f}")
        logger.debug(f"Vote distribution: {votes}")
        
        return final_decision, float(confidence_score)
    
    def vote_with_anomaly_scores(self, 
                                 anomaly_scores: Dict[str, Optional[float]],
                                 classifications: Dict[str, Optional[Dict]],
                                 threshold: float = 0.5) -> Tuple[str, float]:
        """
        Combine anomaly scores and classifications
        
        Args:
            anomaly_scores: Anomaly scores from detectors
            classifications: Classifications from classifiers
            threshold: Detection threshold
            
        Returns:
            Tuple of (final_decision, confidence_score)
        """
        # Convert anomaly scores to binary predictions
        anomaly_predictions = {}
        
        # Isolation Forest: scores < -0.5 indicate anomaly
        if anomaly_scores.get('isolation_forest_score') is not None:
            if_score = anomaly_scores['isolation_forest_score']
            is_anomaly = if_score < -0.5
            confidence = abs(if_score)  # Higher absolute value = more confident
            anomaly_predictions['isolation_forest'] = {
                'class': 'Attack' if is_anomaly else 'Normal',
                'confidence': confidence
            }
        
        # Autoencoder: higher scores indicate anomaly
        if anomaly_scores.get('autoencoder_score') is not None:
            ae_score = anomaly_scores['autoencoder_score']
            is_anomaly = ae_score > threshold
            anomaly_predictions['autoencoder'] = {
                'class': 'Attack' if is_anomaly else 'Normal',
                'confidence': ae_score if is_anomaly else (1 - ae_score)
            }
        
        # Combine with classifier predictions
        all_predictions = {**anomaly_predictions}
        if classifications.get('random_forest'):
            all_predictions['random_forest'] = classifications['random_forest']
        if classifications.get('xgboost'):
            all_predictions['xgboost'] = classifications['xgboost']
        
        return self.vote(all_predictions)
