#!/usr/bin/env python3
"""
Demo script to showcase the text segmentation functionality
for the SummarizationModel when handling long transcriptions.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.pipeline_services.summarization_service import SummarizationModel
from unittest.mock import Mock

def create_long_transcription_text():
    """Create a sample long transcription text that exceeds model capacity"""
    
    # Sample sentences about AI and machine learning
    sentences = [
        "Artificial intelligence represents one of the most significant technological advances of the 21st century.",
        "Machine learning algorithms enable computers to learn patterns from data without explicit programming.",
        "Deep learning networks use multiple layers to process information in ways that mimic the human brain.",
        "Natural language processing allows computers to understand and generate human language.",
        "Computer vision systems can analyze and interpret visual information from images and videos.",
        "Reinforcement learning teaches AI systems to make decisions through trial and error.",
        "Neural networks consist of interconnected nodes that process information in parallel.",
        "Data preprocessing is crucial for training effective machine learning models.",
        "Feature engineering involves selecting and transforming input variables for better model performance.",
        "Cross-validation helps evaluate model performance and prevent overfitting.",
        "Transfer learning leverages pre-trained models to solve new related problems.",
        "Ensemble methods combine multiple models to improve prediction accuracy.",
        "Regularization techniques prevent models from becoming too complex and overfitting.",
        "Hyperparameter tuning optimizes model configuration for best performance.",
        "Big data technologies enable processing of massive datasets for AI applications."
    ]
    
    # Repeat sentences to create a very long text (simulating a long lecture transcription)
    long_text = ""
    for i in range(200):  # This will create ~3000 words
        sentence_idx = i % len(sentences)
        long_text += sentences[sentence_idx] + " "
        
        # Add some variation
        if i % 10 == 0:
            long_text += "The speaker pauses to emphasize this important point. "
        if i % 25 == 0:
            long_text += "Moving on to the next topic, we need to understand that "
    
    return long_text.strip()

def demo_segmentation():
    """Demonstrate the segmentation functionality"""
    
    print("=== Text Segmentation Demo ===")
    print()
    
    # Create mock services (since we're just demonstrating segmentation logic)
    mock_summary_services = Mock()
    mock_translator = Mock()
    mock_job_services = Mock()
    mock_transcription_services = Mock()
    
    # Create the summarization service
    summarization_service = SummarizationModel(
        summary_services=mock_summary_services,
        translator=mock_translator,
        job_services=mock_job_services,
        transcription_services=mock_transcription_services
    )
    
    # Create long transcription text
    long_text = create_long_transcription_text()
    word_count = len(long_text.split())
    
    print(f"Original text length: {word_count} words")
    print(f"Model capacity: {summarization_service.max_input_length} words")
    print(f"Segmentation needed: {'Yes' if word_count > summarization_service.max_input_length else 'No'}")
    print()
    
    # Demonstrate segmentation
    print("=== Segmentation Process ===")
    segments = summarization_service._segment_text(long_text)
    
    print(f"Text segmented into {len(segments)} chunks:")
    print()
    
    for i, segment in enumerate(segments, 1):
        segment_words = len(segment.split())
        preview = segment[:100] + "..." if len(segment) > 100 else segment
        print(f"Segment {i}: {segment_words} words")
        print(f"Preview: {preview}")
        print()
    
    # Demonstrate configuration
    print("=== Configuration Demo ===")
    print(f"Current settings:")
    print(f"  Max input length: {summarization_service.max_input_length}")
    print(f"  Segment overlap: {summarization_service.segment_overlap}")
    print(f"  Min segment length: {summarization_service.min_segment_length}")
    print()
    
    # Configure for smaller segments
    summarization_service.configure_segmentation(
        max_input_length=512,
        segment_overlap=50,
        min_segment_length=100
    )
    
    print("After reconfiguration:")
    print(f"  Max input length: {summarization_service.max_input_length}")
    print(f"  Segment overlap: {summarization_service.segment_overlap}")
    print(f"  Min segment length: {summarization_service.min_segment_length}")
    print()
    
    # Re-segment with new configuration
    new_segments = summarization_service._segment_text(long_text)
    print(f"Text re-segmented into {len(new_segments)} chunks with new configuration")
    
    for i, segment in enumerate(new_segments, 1):
        segment_words = len(segment.split())
        print(f"Segment {i}: {segment_words} words")
    
    print()
    print("=== Key Features ===")
    print("✓ Automatic segmentation for texts exceeding model capacity")
    print("✓ Sentence boundary preservation for coherent segments")
    print("✓ Configurable overlap between segments to maintain context")
    print("✓ Configurable segment sizes based on model requirements")
    print("✓ Recursive summarization for combining segment summaries")
    print("✓ Comprehensive error handling and logging")

if __name__ == "__main__":
    demo_segmentation()
