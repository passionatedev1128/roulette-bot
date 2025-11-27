"""
Analyze Roulette Bot Test Results
Reads JSON result file and calculates accuracy metrics.
"""

import json
import sys
from pathlib import Path
from collections import Counter
from datetime import datetime


def analyze_results(json_file):
    """
    Analyze test results and calculate accuracy metrics.
    
    Args:
        json_file: Path to JSON results file
        
    Returns:
        Dictionary with analysis results
    """
    # Load JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = data.get('results', [])
    total_frames = data.get('total_frames', 0)
    processed_frames = data.get('processed_frames', 0)
    successful_detections = data.get('successful_detections', 0)
    
    # Calculate detection rate
    detection_rate = (successful_detections / processed_frames * 100) if processed_frames > 0 else 0
    
    # Analyze successful detections
    successful_results = [r for r in results if r.get('result', {}).get('number') is not None]
    
    # Extract metrics
    numbers_detected = []
    colors_detected = []
    methods_used = []
    confidences = []
    frame_numbers = []
    
    for result in successful_results:
        res = result.get('result', {})
        numbers_detected.append(res.get('number'))
        colors_detected.append(res.get('color'))
        methods_used.append(res.get('method'))
        confidences.append(res.get('confidence', 0))
        frame_numbers.append(result.get('frame_number'))
    
    # Count statistics
    number_counts = Counter(numbers_detected)
    color_counts = Counter(colors_detected)
    method_counts = Counter(methods_used)
    
    # Calculate confidence statistics
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    min_confidence = min(confidences) if confidences else 0
    max_confidence = max(confidences) if confidences else 0
    
    # Detection intervals (how often detection succeeds)
    if successful_results:
        intervals = []
        for i in range(1, len(successful_results)):
            interval = successful_results[i]['frame_number'] - successful_results[i-1]['frame_number']
            intervals.append(interval)
        avg_interval = sum(intervals) / len(intervals) if intervals else 0
    else:
        avg_interval = 0
    
    # Build analysis
    analysis = {
        'file_info': {
            'json_file': str(json_file),
            'video_path': data.get('video_path', 'Unknown'),
            'analysis_date': datetime.now().isoformat()
        },
        'overall_metrics': {
            'total_frames': total_frames,
            'processed_frames': processed_frames,
            'successful_detections': successful_detections,
            'failed_detections': processed_frames - successful_detections,
            'detection_rate': round(detection_rate, 2),
            'detection_percentage': f"{detection_rate:.2f}%"
        },
        'detection_quality': {
            'average_confidence': round(avg_confidence, 3),
            'min_confidence': round(min_confidence, 3),
            'max_confidence': round(max_confidence, 3),
            'high_confidence_detections': len([c for c in confidences if c >= 0.8]),
            'medium_confidence_detections': len([c for c in confidences if 0.5 <= c < 0.8]),
            'low_confidence_detections': len([c for c in confidences if c < 0.5])
        },
        'detection_methods': {
            'method_counts': dict(method_counts),
            'method_percentages': {
                method: round(count / len(methods_used) * 100, 2) 
                for method, count in method_counts.items()
            } if methods_used else {}
        },
        'detected_numbers': {
            'total_unique_numbers': len(set(numbers_detected)),
            'number_range': {
                'min': min(numbers_detected) if numbers_detected else None,
                'max': max(numbers_detected) if numbers_detected else None
            },
            'most_common_numbers': dict(number_counts.most_common(10))
        },
        'detected_colors': {
            'color_counts': dict(color_counts),
            'color_percentages': {
                color: round(count / len(colors_detected) * 100, 2)
                for color, count in color_counts.items()
            } if colors_detected else {}
        },
        'detection_intervals': {
            'average_frames_between_detections': round(avg_interval, 2) if avg_interval > 0 else None,
            'first_detection_frame': successful_results[0]['frame_number'] if successful_results else None,
            'last_detection_frame': successful_results[-1]['frame_number'] if successful_results else None
        },
        'accuracy_assessment': {
            'rating': get_accuracy_rating(detection_rate, avg_confidence),
            'ready_for_production': detection_rate >= 90 and avg_confidence >= 0.7,
            'recommendations': get_recommendations(detection_rate, avg_confidence, method_counts)
        }
    }
    
    return analysis


def get_accuracy_rating(detection_rate, avg_confidence):
    """Get human-readable accuracy rating."""
    if detection_rate >= 90 and avg_confidence >= 0.8:
        return "Excellent"
    elif detection_rate >= 80 and avg_confidence >= 0.7:
        return "Good"
    elif detection_rate >= 70 and avg_confidence >= 0.6:
        return "Fair"
    elif detection_rate >= 50:
        return "Poor"
    else:
        return "Very Poor"


def get_recommendations(detection_rate, avg_confidence, method_counts):
    """Get recommendations based on results."""
    recommendations = []
    
    if detection_rate < 70:
        recommendations.append(" Detection rate is too low (<70%). Consider:")
        recommendations.append("   - Creating number templates for better accuracy")
        recommendations.append("   - Adjusting color ranges in configuration")
        recommendations.append("   - Improving video quality")
    
    if avg_confidence < 0.7:
        recommendations.append("  Average confidence is low. Consider:")
        recommendations.append("   - Using template matching instead of OCR")
        recommendations.append("   - Calibrating detection settings")
    
    if method_counts.get('ocr', 0) > method_counts.get('template', 0):
        recommendations.append(" Most detections use OCR. For better accuracy:")
        recommendations.append("   - Create number templates (0-36)")
        recommendations.append("   - Template matching is more reliable than OCR")
    
    if detection_rate >= 90 and avg_confidence >= 0.7:
        recommendations.append(" Excellent results! Bot is ready for testing.")
    
    return recommendations


def print_analysis(analysis):
    """Print formatted analysis results."""
    print("=" * 70)
    print("ROULETTE BOT - TEST RESULTS ANALYSIS")
    print("=" * 70)
    
    # File info
    print("\n📁 FILE INFORMATION")
    print(f"   Video: {analysis['file_info']['video_path']}")
    print(f"   Analyzed: {analysis['file_info']['analysis_date']}")
    
    # Overall metrics
    print("\n📊 OVERALL METRICS")
    metrics = analysis['overall_metrics']
    print(f"   Total frames: {metrics['total_frames']}")
    print(f"   Processed frames: {metrics['processed_frames']}")
    print(f"   Successful detections: {metrics['successful_detections']}")
    print(f"   Failed detections: {metrics['failed_detections']}")
    print(f"   Detection Rate: {metrics['detection_percentage']}")
    
    # Accuracy assessment
    print("\n ACCURACY ASSESSMENT")
    assessment = analysis['accuracy_assessment']
    print(f"   Rating: {assessment['rating']}")
    print(f"   Ready for Production: {' YES' if assessment['ready_for_production'] else ' NO'}")
    
    # Detection quality
    print("\n🔍 DETECTION QUALITY")
    quality = analysis['detection_quality']
    print(f"   Average Confidence: {quality['average_confidence']:.3f}")
    print(f"   Confidence Range: {quality['min_confidence']:.3f} - {quality['max_confidence']:.3f}")
    print(f"   High Confidence (≥0.8): {quality['high_confidence_detections']}")
    print(f"   Medium Confidence (0.5-0.8): {quality['medium_confidence_detections']}")
    print(f"   Low Confidence (<0.5): {quality['low_confidence_detections']}")
    
    # Detection methods
    print("\n🔧 DETECTION METHODS")
    methods = analysis['detection_methods']
    print("   Method Usage:")
    for method, count in methods['method_counts'].items():
        percentage = methods['method_percentages'].get(method, 0)
        print(f"     - {method}: {count} ({percentage}%)")
    
    # Detected numbers
    print("\n🎲 DETECTED NUMBERS")
    numbers = analysis['detected_numbers']
    print(f"   Unique numbers detected: {numbers['total_unique_numbers']}")
    if numbers['number_range']['min'] is not None:
        print(f"   Range: {numbers['number_range']['min']} - {numbers['number_range']['max']}")
    print("   Most common numbers:")
    for number, count in list(numbers['most_common_numbers'].items())[:5]:
        print(f"     - {number}: {count} times")
    
    # Detected colors
    print("\n🎨 DETECTED COLORS")
    colors = analysis['detected_colors']
    for color, count in colors['color_counts'].items():
        percentage = colors['color_percentages'].get(color, 0)
        print(f"   {color.capitalize()}: {count} ({percentage}%)")
    
    # Recommendations
    print("\n RECOMMENDATIONS")
    for rec in assessment['recommendations']:
        print(f"   {rec}")
    
    print("\n" + "=" * 70)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python analyze_results.py <json_file>")
        print("\nExample:")
        print("  python analyze_results.py test_results/results_20231103_143022.json")
        sys.exit(1)
    
    json_file = Path(sys.argv[1])
    
    if not json_file.exists():
        print(f"Error: File not found: {json_file}")
        sys.exit(1)
    
    try:
        # Analyze results
        analysis = analyze_results(json_file)
        
        # Print analysis
        print_analysis(analysis)
        
        # Save detailed analysis
        output_file = json_file.parent / f"analysis_{json_file.stem}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Detailed analysis saved to: {output_file}")
        
    except Exception as e:
        print(f"Error analyzing results: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

