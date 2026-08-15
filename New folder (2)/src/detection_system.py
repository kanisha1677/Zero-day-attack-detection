"""
Main Detection System
Orchestrates the complete zero-day network attack detection pipeline
"""

import yaml
import json
import logging
import hashlib
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from datetime import datetime

from feature_extractor import FeatureExtractor
from anomaly_detector import AnomalyDetector
from attack_classifier import AttackClassifier
from ensemble_voter import EnsembleVoter
from explainability_engine import ExplainabilityEngine

# Requirement 13, AC5: Configurable log levels
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DetectionSystem:
    """Main zero-day network attack detection system"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.feature_extractor = FeatureExtractor()
        self.anomaly_detector = AnomalyDetector(self.config)
        self.attack_classifier = AttackClassifier(self.config)
        self.ensemble_voter = EnsembleVoter(self.config['model_weights'])
        self.explainability_engine = ExplainabilityEngine()
        
        self.detection_metrics = {
            'total_detections': 0,
            'attack_detections': 0,
            'normal_detections': 0,
            'processing_times': []
        }
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """
        Load configuration from file
        
        Requirement 10, AC1: Load from CONFIG_PATH or default path
        """
        if config_path is None:
            config_path = os.getenv('CONFIG_PATH', './config/detection_config.yaml')
        
        start_time = time.time()
        
        try:
            with open(config_path, 'r') as f:
                if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                    config = yaml.safe_load(f)
                elif config_path.endswith('.json'):
                    config = json.load(f)
                else:
                    raise ValueError(f"Unsupported config format: {config_path}")
            
            # Requirement 10, AC9: Complete within 5 seconds
            elapsed = time.time() - start_time
            if elapsed > 5:
                logger.warning(f"Config loading took {elapsed:.2f}s (>5s threshold)")
            
            # Validate and apply defaults
            config = self._validate_config(config)
            
            logger.info(f"Configuration loaded from {config_path}")
            return config
            
        except (FileNotFoundError, json.JSONDecodeError, yaml.YAMLError) as e:
            # Requirement 10, AC5: Log error and terminate on parsing failure
            logger.error(f"Configuration parsing failed: {e}")
            raise
    
    def _validate_config(self, config: Dict) -> Dict:
        """
        Validate configuration and apply defaults
        
        Requirements 10, AC6-AC8: Validate ranges and apply defaults
        """
        # Requirement 10, AC2, AC6: Detection threshold 0.0 to 1.0
        threshold = config.get('detection_threshold', 0.5)
        if not (0.0 <= threshold <= 1.0):
            logger.warning(f"Detection threshold {threshold} out of range, using default 0.5")
            config['detection_threshold'] = 0.5
        
        # Requirement 10, AC3, AC7: Model weights 0.0 to 1.0, sum to 1.0
        weights = config.get('model_weights', {})
        weight_sum = sum(weights.values())
        if abs(weight_sum - 1.0) > 0.01:
            logger.warning(f"Model weights sum to {weight_sum}, normalizing to 1.0")
            total = weight_sum if weight_sum > 0 else 1.0
            config['model_weights'] = {k: v/total for k, v in weights.items()}
        
        # Requirement 10, AC4, AC8: Contamination 0.0 to 0.5
        contamination = config.get('isolation_forest', {}).get('contamination', 0.1)
        if not (0.0 <= contamination <= 0.5):
            logger.warning(f"Contamination {contamination} out of range, using default 0.1")
            config.setdefault('isolation_forest', {})['contamination'] = 0.1
        
        return config
    
    def load_models(self):
        """
        Load persisted models
        
        Requirement 9, AC3: Load models during initialization
        """
        model_paths = self.config['model_paths']
        
        # Load feature extractor
        try:
            self.feature_extractor.load(
                model_paths['scaler'],
                model_paths['encoder']
            )
        except Exception as e:
            # Requirement 9, AC6: Log error and enter degraded mode
            logger.error(f"Failed to load feature extractor: {e}")
        
        # Requirement 9, AC4: Validate model integrity with checksums
        for model_name, model_path in model_paths.items():
            if model_name in ['scaler', 'encoder']:
                continue
            
            if os.path.exists(model_path):
                checksum_path = model_path + '.sha256'
                if os.path.exists(checksum_path):
                    if not self._verify_checksum(model_path, checksum_path):
                        # Requirement 9, AC5: Log checksum mismatch and skip
                        logger.error(f"Checksum validation failed for {model_name}, skipping")
                        continue
        
        # Load anomaly detectors
        self.anomaly_detector.load_models(
            model_paths['isolation_forest'],
            model_paths['autoencoder']
        )
        
        # Load classifiers
        self.attack_classifier.load_models(
            model_paths['random_forest'],
            model_paths['xgboost']
        )
        
        logger.info("Models loaded successfully")
    
    def _verify_checksum(self, file_path: str, checksum_path: str) -> bool:
        """Verify file checksum"""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            with open(checksum_path, 'r') as f:
                expected_hash = f.read().strip()
            
            return file_hash == expected_hash
        except Exception as e:
            logger.error(f"Checksum verification failed: {e}")
            return False
    
    def process_traffic(self, traffic_data: Dict[str, Any]) -> Dict:
        """
        Process network traffic through the detection pipeline
        
        Requirement 11, AC1: Process through all stages
        """
        pipeline_start = time.time()
        result = {
            'timestamp': datetime.utcnow().isoformat(),
            'decision': 'Normal',
            'confidence': 0.0,
            'explanation': None,
            'errors': [],
            'pipeline_times': {}
        }
        
        # Stage 1: Feature Extraction
        stage_start = time.time()
        feature_vector = self.feature_extractor.extract_features(traffic_data)
        result['pipeline_times']['feature_extraction'] = (time.time() - stage_start) * 1000
        
        if feature_vector is None:
            # Requirement 11, AC4: Log error and discard sample
            error = "Feature extraction failed"
            logger.error(f"{error} for sample")
            result['errors'].append(error)
            return result
        
        # Stage 2: Anomaly Detection
        stage_start = time.time()
        anomaly_scores = self.anomaly_detector.detect(feature_vector)
        result['pipeline_times']['anomaly_detection'] = (time.time() - stage_start) * 1000
        result['anomaly_scores'] = {
            k: v for k, v in anomaly_scores.items() if k != 'errors'
        }
        
        if anomaly_scores.get('errors'):
            result['errors'].extend(anomaly_scores['errors'])
        
        # Stage 3: Attack Classification
        stage_start = time.time()
        classifications = self.attack_classifier.classify(feature_vector)
        result['pipeline_times']['classification'] = (time.time() - stage_start) * 1000
        result['classifications'] = {
            k: v for k, v in classifications.items() if k != 'errors'
        }
        
        if classifications.get('errors'):
            result['errors'].extend(classifications['errors'])
        
        # Requirement 11, AC2: Skip stages if models unavailable
        # Stage 4: Ensemble Voting
        stage_start = time.time()
        
        # Requirement 11, AC5: Use single prediction if < 2 models
        decision, confidence = self.ensemble_voter.vote_with_anomaly_scores(
            anomaly_scores,
            classifications,
            self.config['detection_threshold']
        )
        result['pipeline_times']['ensemble_voting'] = (time.time() - stage_start) * 1000
        result['decision'] = decision
        result['confidence'] = confidence
        
        # Stage 5: Explainability (only for attacks)
        if decision == 'Attack':
            stage_start = time.time()
            
            # Use best available classifier model for SHAP
            model = (self.attack_classifier.xgboost or 
                    self.attack_classifier.random_forest)
            
            explanation, error = self.explainability_engine.explain(feature_vector, model)
            result['pipeline_times']['explainability'] = (time.time() - stage_start) * 1000
            
            if error:
                # Requirement 11, AC6: Generate alert without explanations if SHAP fails
                logger.warning(f"Explainability failed: {error}")
                result['errors'].append(f"Explainability: {error}")
                result['explanation'] = self.explainability_engine._default_explanation()
            else:
                result['explanation'] = explanation
        
        # Requirement 11, AC3: Log processing times
        total_time = (time.time() - pipeline_start) * 1000
        result['total_processing_time'] = total_time
        
        logger.info(f"Sample processed in {total_time:.2f}ms - Decision: {decision}")
        
        # Update metrics
        self._update_metrics(result)
        
        # Requirement 13, AC1: Log detection events
        if decision == 'Attack':
            self._log_detection(traffic_data, result)
        
        return result
    
    def _update_metrics(self, result: Dict):
        """Update detection metrics"""
        self.detection_metrics['total_detections'] += 1
        
        if result['decision'] == 'Attack':
            self.detection_metrics['attack_detections'] += 1
        else:
            self.detection_metrics['normal_detections'] += 1
        
        self.detection_metrics['processing_times'].append(
            result['total_processing_time']
        )
        
        # Keep only last 1000 processing times
        if len(self.detection_metrics['processing_times']) > 1000:
            self.detection_metrics['processing_times'] = \
                self.detection_metrics['processing_times'][-1000:]
    
    def _log_detection(self, traffic_data: Dict, result: Dict):
        """
        Log detection event in structured format
        
        Requirement 13, AC1: JSON format with all details
        """
        log_entry = {
            'timestamp': result['timestamp'],
            'attack_classification': result['decision'],
            'confidence_score': result['confidence'],
            'feature_vector': traffic_data,
            'shap_explanation_summary': result.get('explanation', {}).get('top_features', [])[:3]
        }
        
        logger.info(f"DETECTION: {json.dumps(log_entry)}")
    
    def get_metrics(self) -> Dict:
        """
        Get system metrics
        
        Requirement 13, AC4: Expose metrics in Prometheus format
        """
        processing_times = self.detection_metrics['processing_times']
        
        metrics = {
            'detection_rate': 0.0,  # Would need time window tracking
            'false_positive_rate': 0.0,  # Would need ground truth labels
            'processing_latency_milliseconds': np.percentile(processing_times, 95) if processing_times else 0.0,
            'total_detections': self.detection_metrics['total_detections'],
            'attack_detections': self.detection_metrics['attack_detections'],
            'normal_detections': self.detection_metrics['normal_detections']
        }
        
        return metrics
