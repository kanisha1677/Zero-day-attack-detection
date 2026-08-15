# Requirements Document

## Introduction

The Zero-Day Network Attack Detection System is an AI-powered intrusion detection system designed to identify previously unknown network attacks through advanced machine learning techniques. Unlike traditional signature-based IDS, this system analyzes network traffic patterns using multiple anomaly detection and classification algorithms to detect zero-day attacks in real-time, providing security analysts with explainable alerts through a visual dashboard.

## Glossary

- **Detection_System**: The complete AI-powered zero-day network attack detection system
- **Traffic_Analyzer**: Component responsible for analyzing network traffic patterns
- **Feature_Extractor**: Component that extracts relevant features from raw network traffic data
- **Anomaly_Detector**: ML component combining Isolation Forest and Autoencoder for identifying anomalous patterns
- **Attack_Classifier**: ML component using Random Forest and XGBoost for classifying detected anomalies
- **Ensemble_Voter**: Component that combines predictions from multiple models through voting
- **Explainability_Engine**: Component using SHAP to provide explanations for detection decisions
- **Alert_Dashboard**: Web-based interface displaying real-time alerts and explanations
- **Network_Traffic**: Incoming data stream representing network activity to be analyzed
- **Zero_Day_Attack**: Previously unknown attack with no existing signature
- **Anomaly_Score**: Numerical value indicating the degree of abnormality in traffic patterns
- **Attack_Classification**: Categorization of detected anomaly into attack types
- **SHAP_Values**: SHapley Additive exPlanations values showing feature importance
- **Detection_Threshold**: Configurable value determining when an anomaly triggers an alert

## Requirements

### Requirement 1: Network Traffic Feature Extraction

**User Story:** As a security analyst, I want the system to extract relevant features from network traffic, so that ML models can effectively analyze traffic patterns.

#### Acceptance Criteria

1. WHEN Network_Traffic is received, THE Feature_Extractor SHALL extract numerical features (packet_size, byte_count, duration_seconds) and categorical features (protocol_type, flag_status, service_type) from the traffic data
2. THE Feature_Extractor SHALL normalize extracted numerical features to the range 0 to 1 using min-max scaling
3. IF Network_Traffic contains null values for any required field, THEN THE Feature_Extractor SHALL apply default values (0 for numerical features, "unknown" for categorical features)
4. IF Network_Traffic fails validation (missing required fields packet_size, protocol_type, or timestamp), THEN THE Feature_Extractor SHALL reject the traffic data and output an error indication
5. THE Feature_Extractor SHALL produce a feature vector as a fixed-length numerical array of 6 elements (3 normalized numerical features followed by 3 encoded categorical features)

### Requirement 2: Anomaly Detection Using Isolation Forest

**User Story:** As a security analyst, I want the system to detect anomalies using Isolation Forest, so that unusual network patterns can be identified.

#### Acceptance Criteria

1. WHEN a feature vector is received, THE Anomaly_Detector SHALL compute an Isolation Forest anomaly score in the range -1.0 to 1.0
2. WHEN the Anomaly_Detector computes an anomaly score, THE Anomaly_Detector SHALL assign scores below -0.5 to patterns indicating higher anomaly likelihood
3. WHERE Isolation Forest is configured, THE Anomaly_Detector SHALL use the specified contamination parameter in the range 0.0 to 0.5
4. THE Anomaly_Detector SHALL complete Isolation Forest scoring within 100 milliseconds per sample measured as the 95th percentile response time
5. WHEN the Anomaly_Detector receives a feature vector, THE feature vector SHALL contain numerical values matching the dimensionality of the trained Isolation Forest model
6. IF a feature vector has incompatible dimensionality or contains non-numerical values, THEN THE Anomaly_Detector SHALL reject the input and return an error message indicating the validation failure
7. THE Anomaly_Detector SHALL use a pre-trained Isolation Forest model fitted on historical normal network traffic data before performing anomaly scoring

### Requirement 3: Anomaly Detection Using Autoencoder

**User Story:** As a security analyst, I want the system to detect anomalies using an Autoencoder, so that complex non-linear patterns can be identified.

#### Acceptance Criteria

1. WHEN a feature vector is received, THE Anomaly_Detector SHALL compute reconstruction error as the mean squared error between the input feature vector and the Autoencoder output
2. WHEN reconstruction error is computed, THE Anomaly_Detector SHALL assign an anomaly score in the range 0.0 to 1.0 by normalizing the reconstruction error against the maximum observed error during training
3. THE Anomaly_Detector SHALL use a trained Autoencoder model loaded from persistent storage
4. IF the Autoencoder model file is missing or fails model validation, THEN THE Anomaly_Detector SHALL log an error message indicating the failure reason and return a null anomaly score
5. IF a feature vector with incompatible dimensions is received, THEN THE Anomaly_Detector SHALL log an error message indicating dimension mismatch and return a null anomaly score

### Requirement 4: Attack Classification Using Random Forest

**User Story:** As a security analyst, I want detected anomalies to be classified using Random Forest, so that attack types can be identified.

#### Acceptance Criteria

1. WHEN an anomaly is detected, THE Attack_Classifier SHALL predict attack classification from the set {DoS, Probe, R2L, U2R, Normal} using Random Forest
2. THE Attack_Classifier SHALL output predicted class and confidence probability in the range 0.00 to 1.00 with 2 decimal places
3. THE Attack_Classifier SHALL return the predicted class and confidence probability as a structured output containing "class" and "confidence" fields
4. THE Attack_Classifier SHALL use a trained Random Forest model with at least 100 decision trees
5. THE Attack_Classifier SHALL complete classification within 50 milliseconds per sample measured as the 95th percentile response time
6. IF a feature vector with incompatible dimensionality is received, THEN THE Attack_Classifier SHALL return an error indication specifying dimension mismatch
7. IF the Random Forest model is unavailable or fails to load, THEN THE Attack_Classifier SHALL return an error indication specifying model unavailability
8. IF classification exceeds the 50 millisecond timeout, THEN THE Attack_Classifier SHALL terminate the operation and return a timeout error indication

### Requirement 5: Attack Classification Using XGBoost

**User Story:** As a security analyst, I want detected anomalies to be classified using XGBoost, so that accurate attack type predictions can be obtained.

#### Acceptance Criteria

1. WHEN an anomaly is detected with feature vector as input, THE Attack_Classifier SHALL predict attack classification from the set {DoS, Probe, R2L, U2R, Normal} using XGBoost and return predicted class and confidence probability
2. THE Attack_Classifier SHALL output confidence probability as a numerical value in the range 0.0 to 1.0
3. THE Attack_Classifier SHALL use a trained XGBoost model loaded from persistent storage
4. IF the XGBoost model file is missing or fails model validation, THEN THE Attack_Classifier SHALL log an error message indicating the failure reason and use fallback classification (Random Forest if available)
5. IF a feature vector with incompatible dimensionality is received, THEN THE Attack_Classifier SHALL reject the input and return an error indication specifying dimension mismatch

### Requirement 6: Ensemble Voting for Final Detection

**User Story:** As a security analyst, I want multiple model predictions to be combined through ensemble voting, so that detection accuracy is maximized.

#### Acceptance Criteria

1. WHEN predictions are available from at least 2 models, THE Ensemble_Voter SHALL combine them using majority voting
2. THE Ensemble_Voter SHALL assign weights in the range 0.0 to 1.0 to each model based on configured importance
3. THE Ensemble_Voter SHALL produce a final binary decision from the set {Attack, Normal} indicating attack or normal traffic
4. THE Ensemble_Voter SHALL compute an overall confidence score for the final decision in the range 0.0 to 1.0 by weighted averaging of individual model confidence scores
5. WHERE weighted voting is configured, THE Ensemble_Voter SHALL apply specified model weights normalized to sum to 1.0
6. IF predictions are available from fewer than 2 models, THEN THE Ensemble_Voter SHALL use the single available prediction as the final decision
7. IF a voting tie occurs with an even number of models, THEN THE Ensemble_Voter SHALL select the prediction with the highest confidence score as the tie-breaker

### Requirement 7: SHAP-Based Explainability

**User Story:** As a security analyst, I want explanations for why traffic was flagged as an attack, so that I can understand and validate detections.

#### Acceptance Criteria

1. WHEN an attack is detected by the Ensemble_Voter, THE Explainability_Engine SHALL compute SHAP values for the detection using the ensemble model
2. WHEN SHAP values are computed, THE Explainability_Engine SHALL identify the top 10 features with the highest absolute SHAP values
3. WHEN feature contributions are identified, THE Explainability_Engine SHALL provide feature contributions with both positive SHAP values (supporting attack classification) and negative SHAP values (opposing attack classification)
4. WHEN SHAP analysis is initiated, THE Explainability_Engine SHALL complete SHAP analysis within 500 milliseconds or timeout
5. IF SHAP computation fails due to model incompatibility or errors, THEN THE Explainability_Engine SHALL log the error and return a default explanation indicating SHAP unavailable
6. IF SHAP analysis exceeds the 500 millisecond timeout, THEN THE Explainability_Engine SHALL terminate the computation and return a timeout indication
7. THE Explainability_Engine SHALL output SHAP explanations as a structured format containing feature names, SHAP values, and feature rankings

### Requirement 8: Real-Time Alert Dashboard

**User Story:** As a security analyst, I want a visual dashboard displaying real-time alerts, so that I can monitor and respond to detected attacks.

#### Acceptance Criteria

1. WHEN an attack is detected, THE Alert_Dashboard SHALL render the alert in the user interface within 1 second of detection
2. WHEN an alert is rendered, THE Alert_Dashboard SHALL display attack classification from the set {DoS, Probe, R2L, U2R}, confidence score in the range 0.00 to 1.00 with 2 decimal places, and timestamp in ISO 8601 format
3. WHEN SHAP explanations are available, THE Alert_Dashboard SHALL render feature importance visualizations showing the top 10 features with their SHAP values as a horizontal bar chart
4. THE Alert_Dashboard SHALL provide filtering UI controls allowing users to filter alerts by attack type and time range (last 1 hour, 24 hours, 7 days, or custom range)
5. THE Alert_Dashboard SHALL update detection statistics (total detections count, detection rate per minute, false positive rate percentage) within 5 seconds of new detections

### Requirement 9: Model Training and Persistence

**User Story:** As a system administrator, I want ML models to be trainable and persistable, so that the system can be updated with new training data.

#### Acceptance Criteria

1. THE Detection_System SHALL provide a training mode accepting labeled training datasets as input for Isolation Forest, Autoencoder, Random Forest, and XGBoost models
2. WHEN training completes successfully with training loss below configured threshold, THE Detection_System SHALL persist trained models to disk in serialized format with model metadata (training date, version, accuracy metrics)
3. THE Detection_System SHALL load persisted models during initialization from the configured model directory
4. THE Detection_System SHALL validate model integrity by computing and verifying SHA-256 checksums stored alongside model files before loading
5. IF checksum validation fails for any model file, THEN THE Detection_System SHALL log an error indicating checksum mismatch and skip loading that model
6. IF model loading fails due to file corruption or missing files, THEN THE Detection_System SHALL log an error specifying the failure reason and enter degraded mode (operating with remaining successfully loaded models only)
7. IF model training fails to converge within the configured maximum epochs, THEN THE Detection_System SHALL log a warning and persist the best available model from training iterations
8. IF model persistence fails due to insufficient disk space or write permissions, THEN THE Detection_System SHALL log an error and continue operating with in-memory models

### Requirement 10: Configuration Management

**User Story:** As a system administrator, I want to configure detection thresholds and model parameters, so that the system can be tuned for different environments.

#### Acceptance Criteria

1. THE Detection_System SHALL load configuration from a JSON or YAML file located at the path specified by environment variable CONFIG_PATH or default path ./config/detection_config.yaml
2. THE Detection_System SHALL support configurable Detection_Threshold values in the range 0.0 to 1.0
3. THE Detection_System SHALL support configurable model weights for ensemble voting in the range 0.0 to 1.0 with weights summing to 1.0 across all models
4. THE Detection_System SHALL support configurable contamination parameters for Isolation Forest in the range 0.0 to 0.5
5. IF configuration file parsing fails due to invalid JSON or YAML syntax, THEN THE Detection_System SHALL log an error with the parsing failure details and terminate startup
6. IF Detection_Threshold is outside the range 0.0 to 1.0, THEN THE Detection_System SHALL log a warning and use default value 0.5
7. IF model weights do not sum to 1.0, THEN THE Detection_System SHALL log a warning and normalize weights to sum to 1.0
8. IF contamination parameter is outside the range 0.0 to 0.5, THEN THE Detection_System SHALL log a warning and use default value 0.1
9. THE Detection_System SHALL complete configuration loading within 5 seconds of startup

### Requirement 11: Data Processing Pipeline

**User Story:** As a developer, I want a clear data processing pipeline, so that traffic flows consistently through all detection stages.

#### Acceptance Criteria

1. THE Detection_System SHALL process Network_Traffic through stages where each stage consumes the output of the previous stage: Feature_Extractor (produces feature vector) → Anomaly_Detector (produces anomaly scores) → Attack_Classifier (produces attack classification) → Ensemble_Voter (produces final decision) → Explainability_Engine (produces SHAP explanations) → Alert_Dashboard (displays alert)
2. IF Anomaly_Detector or Attack_Classifier cannot execute due to missing models, THEN THE Detection_System SHALL skip that stage and pass available data to the next stage
3. THE Detection_System SHALL log processing time for each pipeline stage in milliseconds precision with stage name and sample identifier
4. IF any pipeline stage fails with an error, THEN THE Detection_System SHALL log the error with stage name and sample identifier, discard that sample, and continue processing the next sample in the queue
5. IF Ensemble_Voter receives predictions from fewer than 2 models, THEN THE Ensemble_Voter SHALL use the single available prediction as the final decision
6. IF Explainability_Engine fails to generate SHAP explanations, THEN THE Detection_System SHALL generate an alert without explanations and log the failure

### Requirement 12: Performance and Scalability

**User Story:** As a system administrator, I want the system to handle high traffic volumes, so that real-time detection remains effective under load.

#### Acceptance Criteria

1. THE Detection_System SHALL process at least 1000 traffic samples per second sustained for a continuous 60-second window with successful completion of all pipeline stages for at least 95% of samples
2. THE Detection_System SHALL maintain end-to-end latency below 2 seconds per sample measured as the 95th percentile latency from traffic input to alert generation
3. THE Detection_System SHALL handle concurrent processing of 100 traffic samples simultaneously with successful completion of all pipeline stages for at least 95% of samples
4. THE Detection_System SHALL process traffic samples under normal load (100-799 samples per second) with detection accuracy within 5% of baseline accuracy (measured on 100 samples per second with no concurrent load)
5. WHILE under high load (≥800 samples per second), THE Detection_System SHALL maintain detection accuracy within 5% of baseline accuracy
6. IF the incoming traffic rate exceeds 1500 samples per second, THEN THE Detection_System SHALL log an overload warning and apply rate limiting by queuing excess samples

### Requirement 13: Logging and Monitoring

**User Story:** As a system administrator, I want comprehensive logging and monitoring, so that I can troubleshoot issues and track system health.

#### Acceptance Criteria

1. WHEN an attack is detected, THE Detection_System SHALL log the detection event as a structured JSON log entry containing timestamp (ISO 8601 format), attack classification, confidence score, feature vector, and SHAP explanation summary
2. THE Detection_System SHALL log model loading, training, and persistence operations as structured log entries containing operation type, model name, timestamp, and success/failure status
3. THE Detection_System SHALL log pipeline errors with structured log entries containing error message, exception type, stack trace, timestamp, and affected sample identifier
4. THE Detection_System SHALL expose metrics as numerical values in Prometheus format including detection_rate (detections per minute), false_positive_rate (percentage), and processing_latency_milliseconds (95th percentile)
5. THE Detection_System SHALL support configurable log levels from the set {DEBUG, INFO, WARNING, ERROR} selectable via LOG_LEVEL environment variable

### Requirement 14: Data Format Support

**User Story:** As a developer, I want to support standard network traffic data formats, so that the system integrates with existing data sources.

#### Acceptance Criteria

1. THE Detection_System SHALL accept network traffic data in CSV format with columns {timestamp, packet_size, byte_count, duration_seconds, protocol_type, flag_status, service_type}
2. THE Detection_System SHALL accept network traffic data in JSON format with fields {timestamp, packet_size, byte_count, duration_seconds, protocol_type, flag_status, service_type}
3. WHERE Pandas DataFrame format is provided, THE Detection_System SHALL validate the DataFrame contains required columns {timestamp, packet_size, byte_count, duration_seconds, protocol_type, flag_status, service_type} and process it directly
4. THE Detection_System SHALL validate input data schema by checking presence of required fields and data types (numerical for packet_size, byte_count, duration_seconds; string for protocol_type, flag_status, service_type; datetime for timestamp) before processing
5. IF CSV data is missing required columns, THEN THE Detection_System SHALL return error message "Invalid CSV format: missing required columns [list of missing columns]"
6. IF JSON data is missing required fields, THEN THE Detection_System SHALL return error message "Invalid JSON format: missing required fields [list of missing fields]"
7. IF input data contains invalid data types for required fields, THEN THE Detection_System SHALL return error message "Invalid data types: [field name] expected [expected type] but got [actual type]"
8. THE Detection_System SHALL parse CSV files with comma delimiter and support both quoted and unquoted string values

### Requirement 15: Model Evaluation and Metrics

**User Story:** As a data scientist, I want to evaluate model performance using standard metrics, so that I can assess detection effectiveness.

#### Acceptance Criteria

1. THE Detection_System SHALL compute precision, recall, and F1-score for each model
2. THE Detection_System SHALL compute confusion matrix for classification results
3. THE Detection_System SHALL compute ROC-AUC scores for anomaly detection models
4. THE Detection_System SHALL provide a model evaluation report comparing all models
5. THE Detection_System SHALL support evaluation on labeled test datasets
