# Text Segmentation for Long Transcriptions

This feature adds intelligent text segmentation to handle transcriptions that exceed the model's token capacity. The implementation ensures that long transcriptions are properly processed without losing important content.

## Overview

The `SummarizationModel` now includes automatic segmentation logic that:

1. **Detects when text exceeds model capacity** (default: 1024 words)
2. **Segments text at sentence boundaries** to maintain coherence
3. **Applies overlap between segments** to preserve context
4. **Summarizes each segment individually**
5. **Combines segment summaries** into a final coherent summary

## Key Features

### Automatic Segmentation
- Automatically triggers when text exceeds the configured maximum input length
- Uses sentence-based segmentation for better coherence
- Maintains configurable overlap between segments

### Configurable Parameters
- `max_input_length`: Maximum words per segment (default: 1024)
- `segment_overlap`: Words to overlap between segments (default: 100)  
- `min_segment_length`: Minimum meaningful segment size (default: 200)

### Intelligent Processing
- Recursive summarization when combined summaries are still too long
- Comprehensive error handling with fallback strategies
- Detailed logging for monitoring and debugging

## Usage

### Basic Usage
The segmentation is completely automatic and transparent:

```python
# Long transcription text will be automatically segmented
summary = summarization_service.summarize(transcription_job)
```

### Configuration
You can customize segmentation behavior:

```python
# Configure segmentation parameters
summarization_service.configure_segmentation(
    max_input_length=512,  # Smaller segments
    segment_overlap=50,    # Less overlap
    min_segment_length=100 # Smaller minimum size
)
```

## Implementation Details

### Segmentation Algorithm

1. **Text Analysis**: Check if text length exceeds `max_input_length`
2. **Sentence Splitting**: Split text using sentence boundaries (`.`, `!`, `?`)
3. **Segment Building**: Build segments respecting the maximum length
4. **Overlap Management**: Add overlap from previous segment for context
5. **Quality Control**: Ensure segments meet minimum length requirements

### Processing Flow

```
Long Text Input
       ↓
[Length Check] → Short Text → Direct Summarization
       ↓
[Segmentation] → Multiple Segments
       ↓
[Individual Summarization] → Segment Summaries
       ↓
[Combination] → Final Summary
```

### Error Handling

- **Segment Failure**: If a segment fails to summarize, processing continues with remaining segments
- **Empty Results**: Validation ensures meaningful output is produced
- **Resource Limits**: Automatic cleanup and memory management

## Examples

### Example 1: Long Academic Lecture
```python
# 5000-word lecture transcription
long_lecture = "..." # Very long text

# Automatic segmentation and summarization
summary = summarization_service._summarize_with_segmentation(long_lecture)

# Result: Coherent summary combining insights from all segments
```

### Example 2: Custom Configuration for Different Models
```python
# For smaller models with 512 token limit
summarization_service.configure_segmentation(
    max_input_length=400,  # Leave buffer for model processing
    segment_overlap=75,    # Good context preservation
    min_segment_length=150 # Reasonable minimum
)

# For larger models with 2048 token limit  
summarization_service.configure_segmentation(
    max_input_length=1800, # Use most of available capacity
    segment_overlap=200,   # More context preservation
    min_segment_length=300 # Larger meaningful segments
)
```

## Testing

Comprehensive tests are included in `app/tests/pipelines/test_summarization_segmentation.py`:

```bash
# Run segmentation tests
python -m pytest app/tests/pipelines/test_summarization_segmentation.py -v
```

## Performance Considerations

### Memory Usage
- Segments are processed sequentially to manage memory
- Automatic cleanup after each segment
- GPU memory clearing when available

### Processing Time
- Longer texts take proportionally more time due to multiple segment processing
- Overlap processing adds slight overhead but improves quality
- Final combination step may require additional summarization

### Quality Trade-offs
- Segmentation maintains high summary quality for very long texts
- Some context may be lost at segment boundaries despite overlap
- Final combination step ensures coherent overall summary

## Monitoring and Debugging

The implementation includes comprehensive logging:

```python
# Enable debug logging to see segmentation details
import logging
logging.getLogger('app.services.pipeline_services.summarization_service').setLevel(logging.DEBUG)
```

Log messages include:
- Text length analysis and segmentation decisions
- Segment creation and processing progress
- Error handling and recovery actions
- Performance metrics and timing information

## Demo

Run the included demonstration script:

```bash
python demo_segmentation.py
```

This shows the segmentation process in action with a sample long text.
