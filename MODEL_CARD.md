# Model Card — SignSpeak AI v1.0.0

## Model Details

### Model Summary

This model performs isolated Indian Sign Language (ISL) recognition using hand landmark features extracted by MediaPipe.

**Model Type:** Multi-class classifier (Random Forest or SVM)
**Input:** Normalized hand landmarks (126 dimensions)
**Output:** ISL sign class (A-Z)
**Task:** Isolated sign recognition

### Version Information

- **Version:** 1.0.0
- **Created:** {Timestamp will be added during training}
- **Framework:** scikit-learn
- **Algorithm:** Random Forest (fallback: SVM)
- **Feature Dimension:** 126 (2 hands × 21 landmarks × 3 coordinates)

## Intended Use

### Primary Use Case

Real-time recognition of isolated Indian Sign Language fingerspelling and basic signs for:
- Assistive communication technology
- Educational demonstrations
- Accessibility tools
- Sign language learning applications

### Intended Users

- Deaf/hard-of-hearing individuals
- Sign language educators
- Researchers
- Students
- Application developers

### Out-of-Scope Use Cases

❌ Do NOT use for:
- Continuous ISL-to-English sentence translation
- Real-time multi-person crowd signing
- Automatic video subtitling (requires temporal modeling)
- Clinical/medical diagnosis based on signing patterns
- Production systems without testing on your target population

## Data Sheet

### Training Data

#### Dataset Composition
- **Vocabulary:** {Will be documented during data preparation}
- **Data Type:** Hand landmarks (MediaPipe Hands)
- **Format:** Normalized 126D feature vectors
- **Collection Method:** Webcam capture with MediaPipe
- **Preprocessing:** Landmark normalization (translation/scale invariant)

#### Data Characteristics
- **Total Samples:** {Documented during training}
- **Train Samples:** {80% split}
- **Validation Samples:** {10% split}
- **Test Samples:** {10% split}
- **Class Balance:** Stratified split (all classes balanced)

#### Data Quality Considerations
- **Lighting:** Collected under varied lighting conditions
- **Background:** {Documented}
- **Hand Visibility:** 100% hand visibility required
- **Hand Orientation:** Frontal camera perspective
- **Age Diversity:** {Documented}
- **Gender Diversity:** {Documented}

### Validation Data

- **Held-Out:** Yes (10% of original data)
- **Stratified:** Yes
- **Temporal Separation:** None (same session data)

### Test Data

- **Held-Out:** Yes (final 10% of original data)
- **Previously Unseen:** By fold, but same session collection
- **Stratified:** Yes

## Performance

### Test Set Metrics

**Accuracy:** {Will be measured during training}
**Precision (weighted):** {Will be measured}
**Recall (weighted):** {Will be measured}
**F1-Score (weighted):** {Will be measured}
**F1-Score (macro):** {Will be measured}

### Per-Class Metrics

| Sign | Precision | Recall | F1-Score | Support |
|------|-----------|--------|----------|---------|
| A | {TBD} | {TBD} | {TBD} | {TBD} |
| B | {TBD} | {TBD} | {TBD} | {TBD} |
| ... | ... | ... | ... | ... |

*(Full confusion matrix available in reports/figures/confusion_matrix.png)*

### Performance Caveats

⚠️ **Known Limitations:**

1. **Lighting Sensitivity**
   - Performance may degrade under extreme lighting conditions
   - Trained primarily under indoor office lighting
   - Recommendation: Test with your target lighting conditions

2. **Hand Visibility**
   - Requires clear hand visibility in frame
   - Occlusion (fingers hidden) causes misclassification
   - Gloves/accessories may affect landmark detection

3. **Population Bias**
   - Trained on {documented user demographics}
   - Performance may vary for different ethnicities
   - Hand size distribution: {documented}
   - Age range: {documented}

4. **Static Classification**
   - Cannot recognize signs requiring movement
   - Temporal dynamics not modeled
   - Each frame classified independently
   - Temporal smoothing helps but isn't a substitute

5. **Similarity Confusion**
   - Similar hand shapes (D/O/Z) often confused
   - Requires visual inspection of confusion matrix
   - May need separate collection for problem pairs

## Ethical Considerations

### Fairness

- ⚠️ **Not evaluated** for fairness across demographics
- Likely contains biases from training data demographics
- **Recommendation:** Evaluate on diverse populations before production use
- Consider collecting additional data for under-represented groups

### Bias

- **Potential sources:**
  - Training data collection limited to specific geographic region/culture
  - Lighting conditions during collection
  - Camera angle/quality
  - Hand size and age distributions

- **Mitigation:**
  - Collect diverse training data
  - Evaluate on multiple demographic groups
  - Monitor model drift
  - Provide user calibration option

### Accessibility

✅ **Model supports:**
- Real-time inference (~100ms latency)
- Low-cost GPU-less inference (CPU only)
- Runs on consumer hardware

❌ **Not optimized for:**
- Edge devices (mobile/embedded) without optimization
- Very low-latency requirements (<30ms)
- Large-vocabulary ISL (requires different approach)

### Transparency

- Model decisions not interpretable without post-hoc analysis
- Confidence scores provided but not well-calibrated
- Feature importance via Random Forest feature_importances (if applicable)

## Failure Modes

### Common Misclassifications

1. **Hand occlusion**
   - Missing fingers → incorrect prediction
   - Partial hand visibility
   - *Mitigation:* Require full hand visibility

2. **Similar shapes**
   - D/O/Z confusion common
   - 2/B confusion possible
   - *Mitigation:* Context from temporal history

3. **Speed variation**
   - Slow hand movement may not be recognized
   - Quick gestures may be missed
   - *Mitigation:* Temporal smoothing

4. **Lighting/contrast changes**
   - Low light → poor landmark detection
   - High glare → washed out features
   - *Mitigation:* Adjust camera/lighting

### Recommended Testing

Before deployment, test:

✅ **Robustness Testing**
```python
# Evaluate on new users from target population
# Evaluate on different lighting conditions
# Evaluate on different hand sizes
# Evaluate on different ages
# Evaluate with gloves/accessories
```

✅ **Adversarial Testing**
```python
# Blur/noise robustness
# Extreme lighting
# Extreme hand positions
# Partially visible hands
```

## Training Process

### Methodology

1. **Data Preparation**
   - Landmark extraction via MediaPipe Hands
   - Normalization (translation & scale invariant)
   - Two-hand padding to 126D
   - Stratified train/val/test split

2. **Model Selection**
   - Candidate 1: Random Forest (n_estimators=100)
   - Candidate 2: SVM (kernel='rbf', probability=True)
   - Selection: Best validation accuracy
   - Hyperparameters: Fixed (not tuned on test set)

3. **Validation Strategy**
   - Validation set: 10% stratified sample
   - Evaluation metric: Accuracy
   - Model selection: Best validation accuracy
   - No hyperparameter tuning on test set (data leakage prevention)

4. **Training Details**
   - Random seed: 42 (reproducibility)
   - Feature scaling: StandardScaler (fitted on training data)
   - Class weights: Balanced via stratification
   - Training time: {Documented during training}

### Reproducibility

✅ **Reproducible:**
- Random seeds fixed
- Stratified splitting
- Deterministic preprocessing
- Fixed hyperparameters

🔧 **To reproduce:**
```bash
python ml/collect_data.py --label A --samples 300  # Repeat for all signs
python ml/prepare_dataset.py
python ml/train.py
python ml/evaluate.py
```

## Monitoring & Maintenance

### Recommended Monitoring

1. **Model Performance**
   - Track accuracy on new unseen users
   - Monitor confusion matrix drift
   - Alert if accuracy drops >5%

2. **Data Quality**
   - Monitor input feature distributions
   - Detect landmark detection failures
   - Track lighting condition changes

3. **User Demographics**
   - Log user characteristics when possible
   - Monitor for demographic shifts
   - Re-evaluate on new populations

### Maintenance

- ❓ Retraining frequency: Not determined (recommend quarterly review)
- ❓ Data versioning: Not currently tracked
- ❓ Model versioning: Currently manual

### Model Updates

Future versions should consider:
- [ ] Temporal modeling (LSTM/Transformer)
- [ ] Expanded vocabulary
- [ ] Facial expression integration
- [ ] Cross-user pre-training + personalization
- [ ] Two-hand coordinated modeling

## Technical Specifications

### Feature Extraction

**MediaPipe Configuration:**
- Model: Hand Landmarker (current version)
- Max hands: 2
- Detection confidence: 0.5
- Tracking confidence: 0.5

**Normalization:**
```python
def normalize_landmarks(landmarks):
    # landmarks: [21 points × 3 coords]
    wrist = landmarks[0]
    centered = landmarks - wrist
    scale = ||landmarks[12] - wrist||
    normalized = centered / scale
    return normalized.flatten()  # 63D
```

**Two-Hand Handling:**
```python
features = [
    *normalize(left_hand),    # 63D
    *normalize(right_hand),   # 63D (or zeros if missing)
]  # 126D total
```

### Model Architecture

**Random Forest:**
- Estimators: 100
- Max depth: None
- Min samples split: 2
- Random state: 42

**SVM (if selected):**
- Kernel: RBF
- C: 1.0
- Probability: True
- Random state: 42

**Preprocessing:**
- StandardScaler (fitted on training data)

## Deployment Considerations

### Inference Requirements

- **Latency:** ~100ms per frame
- **Memory:** ~500 MB (model + MediaPipe)
- **CPU:** Yes (GPU optional)
- **GPU:** Optional (inference slower but possible)

### Inference Setup

```python
from joblib import load
model = load('artifacts/signspeak_model.joblib')
features = normalize_and_pad_landmarks(...)  # 126D
prediction = model.predict([features])
confidence = max(model.predict_proba([features])[0])
```

### Confidence Calibration

⚠️ **Warning:** Confidence scores from classifier are not well-calibrated
- High confidence ≠ correct prediction
- Use empirical thresholds based on your data
- Recommend: threshold = 0.75

## Known Issues & Limitations

1. **Static vs. Dynamic Signs**
   - Current: Static per-frame classification
   - Issue: Cannot recognize signs requiring movement
   - Solution: Future LSTM/Transformer model

2. **Two-Handed Coordination**
   - Current: Treats hands independently
   - Issue: Cannot model coordinated two-hand signs
   - Solution: Spatial transformer or attention mechanism

3. **Facial Expressions**
   - Current: Ignored
   - Issue: ISL uses facial expressions critically
   - Solution: MediaPipe Face integration

4. **Continuous Recognition**
   - Current: Isolated signs only
   - Issue: Cannot recognize continuous signing
   - Solution: RNN/Transformer + word-level modeling

5. **Grammar & Context**
   - Current: No language model
   - Issue: Cannot correct for ISL grammar
   - Solution: Sequence-to-sequence model with attention

## Future Work

### Short-term (v1.1)
- [ ] Add facial expression features
- [ ] Expand vocabulary (50+ signs)
- [ ] Improve temporal modeling
- [ ] Cross-validation instead of single split

### Medium-term (v2.0)
- [ ] LSTM for dynamic signs
- [ ] Word-level recognition
- [ ] Multi-person support
- [ ] Production-ready fairness evaluation

### Long-term (v3.0)
- [ ] End-to-end ISL → English translation
- [ ] Grammar-aware translation
- [ ] Personalized user adaptation
- [ ] Multilingual output (Hindi/others)

## Contact

For questions, issues, or feedback on this model:

- GitHub Issues: [signspeak-ai/issues]
- Documentation: See README.md and ARCHITECTURE.md

---

**Model Card Version:** 1.0  
**Last Updated:** 2024
