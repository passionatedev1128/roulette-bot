# How to Analyze Bot Accuracy from JSON Results

## Quick Start

### Option 1: Use the Analysis Script (Recommended)

```bash
python analyze_results.py test_results/results_TIMESTAMP.json
```

This will show you:
-  Detection rate (accuracy percentage)
-  Confidence scores
-  Detection methods used
-  Numbers and colors detected
-  Recommendations

---

## Understanding JSON Results

### What's in the JSON File?

The JSON file contains:
```json
{
  "video_path": "roleta_brazileria.mp4",
  "total_frames": 1200,
  "processed_frames": 100,
  "successful_detections": 85,
  "detection_rate": 85.0,
  "results": [
    {
      "frame_number": 1,
      "timestamp": 0.033,
      "result": {
        "number": 17,
        "color": "black",
        "zero": false,
        "confidence": 0.95,
        "method": "template"
      }
    },
    ...
  ]
}
```

---

## Key Metrics to Check

### 1. Detection Rate (Accuracy)

**Location:** `detection_rate` field

**What it means:**
- Percentage of frames where a number was successfully detected
- Formula: `(successful_detections / processed_frames) * 100`

**Interpretation:**
- **>90%**:  Excellent - Ready for production
- **70-90%**:  Good - May need minor calibration
- **<70%**:  Poor - Needs improvement

### 2. Confidence Scores

**Location:** `results[].result.confidence`

**What it means:**
- How confident the bot is in each detection (0.0 to 1.0)

**Interpretation:**
- **0.9-1.0**:  Very confident - High reliability
- **0.7-0.9**:  Good - Reliable
- **0.5-0.7**:  Fair - May have errors
- **<0.5**:  Low - Likely incorrect

**Average Confidence:**
```python
confidences = [r['result']['confidence'] for r in results if r['result'].get('number')]
avg_confidence = sum(confidences) / len(confidences)
```

### 3. Detection Methods

**Location:** `results[].result.method`

**What it means:**
- Which method was used: `"template"`, `"ocr"`, or `"color_fallback"`

**Interpretation:**
- **Template**:  Best method - Most accurate
- **OCR**:  Fallback - Less reliable
- **Color Fallback**:  Last resort - Only color detected

**Ideal:** Most detections should use `"template"`

---

## Manual Analysis

### Calculate Detection Rate

```python
import json

# Load JSON file
with open('test_results/results_TIMESTAMP.json', 'r') as f:
    data = json.load(f)

# Get metrics
total_frames = data['total_frames']
processed_frames = data['processed_frames']
successful_detections = data['successful_detections']
detection_rate = data['detection_rate']

print(f"Detection Rate: {detection_rate}%")
print(f"Successful: {successful_detections}/{processed_frames}")
```

### Calculate Average Confidence

```python
results = data['results']
confidences = []

for r in results:
    if r.get('result', {}).get('number') is not None:
        confidences.append(r['result'].get('confidence', 0))

if confidences:
    avg_confidence = sum(confidences) / len(confidences)
    print(f"Average Confidence: {avg_confidence:.3f}")
    print(f"Min: {min(confidences):.3f}")
    print(f"Max: {max(confidences):.3f}")
```

### Count Detection Methods

```python
from collections import Counter

methods = [r['result'].get('method') for r in results if r.get('result', {}).get('number')]
method_counts = Counter(methods)

print("Detection Methods:")
for method, count in method_counts.items():
    percentage = (count / len(methods)) * 100
    print(f"  {method}: {count} ({percentage:.1f}%)")
```

### Analyze Detected Numbers

```python
numbers = [r['result']['number'] for r in results if r.get('result', {}).get('number') is not None]
unique_numbers = set(numbers)

print(f"Total detections: {len(numbers)}")
print(f"Unique numbers: {len(unique_numbers)}")
print(f"Range: {min(numbers)} - {max(numbers)}")

# Count occurrences
from collections import Counter
number_counts = Counter(numbers)
print("\nMost common numbers:")
for number, count in number_counts.most_common(10):
    print(f"  {number}: {count} times")
```

### Analyze Detected Colors

```python
colors = [r['result']['color'] for r in results if r.get('result', {}).get('color')]
color_counts = Counter(colors)

print("Colors detected:")
for color, count in color_counts.items():
    percentage = (count / len(colors)) * 100
    print(f"  {color}: {count} ({percentage:.1f}%)")
```

---

## Using the Analysis Script

### Basic Usage

```bash
python analyze_results.py test_results/results_20231103_143022.json
```

### Output Example

```
======================================================================
ROULETTE BOT - TEST RESULTS ANALYSIS
======================================================================

📁 FILE INFORMATION
   Video: roleta_brazileria.mp4
   Analyzed: 2025-11-03T14:30:22

📊 OVERALL METRICS
   Total frames: 1200
   Processed frames: 100
   Successful detections: 85
   Failed detections: 15
   Detection Rate: 85.00%

 ACCURACY ASSESSMENT
   Rating: Good
   Ready for Production:  NO

🔍 DETECTION QUALITY
   Average Confidence: 0.823
   Confidence Range: 0.650 - 0.980
   High Confidence (≥0.8): 65
   Medium Confidence (0.5-0.8): 20
   Low Confidence (<0.5): 0

🔧 DETECTION METHODS
   Method Usage:
     - template: 70 (82.4%)
     - ocr: 15 (17.6%)

🎲 DETECTED NUMBERS
   Unique numbers detected: 25
   Range: 0 - 36
   Most common numbers:
     - 17: 5 times
     - 3: 4 times
     - 25: 3 times

🎨 DETECTED COLORS
   Red: 42 (49.4%)
   Black: 38 (44.7%)
   Green: 5 (5.9%)

 RECOMMENDATIONS
     Average confidence is low. Consider:
      - Using template matching instead of OCR
      - Calibrating detection settings
```

---

## Accuracy Rating System

### Excellent (90%+ detection, 0.8+ confidence)
-  Ready for production
-  High reliability
-  Minimal errors expected

### Good (80-90% detection, 0.7+ confidence)
-  May need minor calibration
-  Generally reliable
-  Some false negatives possible

### Fair (70-80% detection, 0.6+ confidence)
-  Needs improvement
-  Significant errors likely
-  Calibration required

### Poor (<70% detection or <0.6 confidence)
-  Not ready for use
-  Major issues
-  Requires significant work

---

## What to Look For

### Good Results 
- Detection rate >90%
- Average confidence >0.8
- Most detections use "template" method
- Consistent confidence scores
- Numbers detected across full range (0-36)

### Warning Signs 
- Detection rate <70%
- Average confidence <0.7
- Many detections use "ocr" method
- Large gaps in detected numbers
- Inconsistent confidence scores

### Red Flags 
- Detection rate <50%
- Average confidence <0.5
- Many "color_fallback" detections
- No numbers detected
- All detections fail

---

## Improving Accuracy

### If Detection Rate is Low (<70%)
1. **Create number templates** (0-36)
2. **Adjust color ranges** in config
3. **Improve video quality**
4. **Set screen region** to focus on table

### If Confidence is Low (<0.7)
1. **Use template matching** (more reliable)
2. **Calibrate detection settings**
3. **Check video lighting**
4. **Verify number templates match game font**

### If Too Many OCR Detections
1. **Create templates** - Much more accurate
2. **Use template matching as primary method**
3. **OCR should only be fallback**

---

## Quick Analysis Checklist

- [ ] Detection rate >90%?
- [ ] Average confidence >0.8?
- [ ] Most detections use "template"?
- [ ] Numbers detected across full range?
- [ ] Consistent confidence scores?
- [ ] Ready for production?

---

## Summary

**Key Metrics:**
1. **Detection Rate** - Should be >90%
2. **Average Confidence** - Should be >0.8
3. **Method Used** - Prefer "template" over "ocr"
4. **Number Range** - Should cover 0-36
5. **Consistency** - Confidence should be stable

**Use the analysis script for detailed metrics:**
```bash
python analyze_results.py your_results.json
```

