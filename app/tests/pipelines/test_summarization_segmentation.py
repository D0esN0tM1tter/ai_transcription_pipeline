import unittest
from unittest.mock import Mock, patch
from app.services.pipeline_services.summarization_service import SummarizationModel


class TestSummarizationSegmentation(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_summary_services = Mock()
        self.mock_translator = Mock()
        self.mock_job_services = Mock()
        self.mock_transcription_services = Mock()
        
        self.summarization_service = SummarizationModel(
            summary_services=self.mock_summary_services,
            translator=self.mock_translator,
            job_services=self.mock_job_services,
            transcription_services=self.mock_transcription_services
        )
    
    def test_segment_short_text(self):
        """Test that short text is not segmented"""
        short_text = "This is a short text. It should not be segmented."
        
        segments = self.summarization_service._segment_text(short_text)
        
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0], short_text)
    
    def test_segment_long_text(self):
        """Test that long text is properly segmented"""
        # Create a long text that exceeds the default max_input_length (1024 words)
        long_sentence = "This is a very long sentence that will be repeated many times to create a text that exceeds the model's capacity. "
        long_text = long_sentence * 200  # This will create a text with ~2000 words
        
        segments = self.summarization_service._segment_text(long_text)
        
        # Should be segmented into multiple parts
        self.assertGreater(len(segments), 1)
        
        # Each segment should be within the limit
        for segment in segments:
            word_count = len(segment.split())
            self.assertLessEqual(word_count, self.summarization_service.max_input_length)
    
    def test_segment_with_sentences(self):
        """Test segmentation respects sentence boundaries"""
        # Create text with clear sentence boundaries
        sentences = [
            "First sentence.",
            "Second sentence.",
            "Third sentence.",
            "Fourth sentence.",
            "Fifth sentence."
        ]
        
        # Make each sentence long enough to force segmentation
        long_sentences = [sentence + " " + "Word " * 250 for sentence in sentences]
        text = " ".join(long_sentences)
        
        segments = self.summarization_service._segment_text(text)
        
        # Should create multiple segments
        self.assertGreater(len(segments), 1)
        
        # Each segment should contain complete sentences (at least one period)
        for segment in segments:
            self.assertIn('.', segment)
    
    def test_combine_segment_summaries_single(self):
        """Test combining a single summary"""
        summaries = ["This is a single summary."]
        
        result = self.summarization_service._combine_segment_summaries(summaries)
        
        self.assertEqual(result, summaries[0])
    
    @patch.object(SummarizationModel, 'summarize_text')
    def test_combine_segment_summaries_multiple_short(self, mock_summarize_text):
        """Test combining multiple short summaries"""
        mock_summarize_text.return_value = "Combined summary."
        
        summaries = [
            "First summary.",
            "Second summary.",
            "Third summary."
        ]
        
        result = self.summarization_service._combine_segment_summaries(summaries)
        
        # Should have called summarize_text to combine the summaries
        mock_summarize_text.assert_called_once()
        self.assertEqual(result, "Combined summary.")
    
    def test_configure_segmentation(self):
        """Test segmentation configuration"""
        original_max_length = self.summarization_service.max_input_length
        original_overlap = self.summarization_service.segment_overlap
        original_min_length = self.summarization_service.min_segment_length
        
        # Configure new values
        new_max_length = 512
        new_overlap = 50
        new_min_length = 100
        
        self.summarization_service.configure_segmentation(
            max_input_length=new_max_length,
            segment_overlap=new_overlap,
            min_segment_length=new_min_length
        )
        
        # Check values were updated
        self.assertEqual(self.summarization_service.max_input_length, new_max_length)
        self.assertEqual(self.summarization_service.segment_overlap, new_overlap)
        self.assertEqual(self.summarization_service.min_segment_length, new_min_length)
        
        # Test partial configuration
        self.summarization_service.configure_segmentation(max_input_length=256)
        self.assertEqual(self.summarization_service.max_input_length, 256)
        self.assertEqual(self.summarization_service.segment_overlap, new_overlap)  # Should remain unchanged
    
    @patch.object(SummarizationModel, 'summarize_text')
    def test_summarize_with_segmentation_short_text(self, mock_summarize_text):
        """Test that short text bypasses segmentation"""
        mock_summarize_text.return_value = "Short summary."
        
        short_text = "This is a short text."
        result = self.summarization_service._summarize_with_segmentation(short_text)
        
        mock_summarize_text.assert_called_once_with(short_text, "medium")
        self.assertEqual(result, "Short summary.")
    
    @patch.object(SummarizationModel, 'summarize_text')
    @patch.object(SummarizationModel, '_segment_text')
    def test_summarize_with_segmentation_long_text(self, mock_segment_text, mock_summarize_text):
        """Test that long text uses segmentation"""
        # Mock segmentation to return multiple segments
        mock_segment_text.return_value = ["Segment 1.", "Segment 2.", "Segment 3."]
        
        # Mock individual segment summarization
        mock_summarize_text.side_effect = ["Summary 1.", "Summary 2.", "Summary 3.", "Final summary."]
        
        long_text = "This is a very long text. " * 1000
        result = self.summarization_service._summarize_with_segmentation(long_text)
        
        # Should have called segment_text
        mock_segment_text.assert_called_once_with(long_text)
        
        # Should have summarized each segment plus the final combination
        self.assertEqual(mock_summarize_text.call_count, 4)
        
        self.assertEqual(result, "Final summary.")


if __name__ == '__main__':
    unittest.main()
