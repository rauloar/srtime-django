"""
Tests for Timeline Integrity
TimelineNormalizer and TimelineValidator
"""
from datetime import time
from django.test import TestCase

from core.services.timeline_integrity import (
    TimelineNormalizer,
    TimelineValidator,
    TimelineIntegrityError
)
from core.models_timeline import BlockType


class TestTimelineValidator(TestCase):
    """Test temporal integrity validation."""
    
    def setUp(self):
        self.validator = TimelineValidator()
    
    def test_valid_timeline_passes(self):
        """Valid timeline should not raise errors."""
        blocks = [
            {
                'block_type': BlockType.WORK,
                'start_time': time(8, 0),
                'end_time': time(12, 0),
                'duration_minutes': 240,
            },
            {
                'block_type': BlockType.WORK,
                'start_time': time(13, 0),
                'end_time': time(17, 0),
                'duration_minutes': 240,
            },
        ]
        
        # Should not raise
        self.validator.validate(blocks)
    
    def test_overlapping_blocks_detected(self):
        """Overlapping blocks should raise error."""
        blocks = [
            {
                'block_type': BlockType.WORK,
                'start_time': time(8, 0),
                'end_time': time(12, 30),  # Overlaps next
                'duration_minutes': 270,
            },
            {
                'block_type': BlockType.WORK,
                'start_time': time(12, 0),  # Starts before previous ends
                'end_time': time(17, 0),
                'duration_minutes': 300,
            },
        ]
        
        with self.assertRaises(TimelineIntegrityError) as ctx:
            self.validator.validate(blocks)
        
        self.assertIn('overlap', str(ctx.exception).lower())
    
    def test_negative_duration_detected(self):
        """Negative duration should raise error."""
        blocks = [
            {
                'block_type': BlockType.WORK,
                'start_time': time(8, 0),
                'end_time': time(7, 0),  # End before start
                'duration_minutes': 60,
            },
        ]
        
        with self.assertRaises(TimelineIntegrityError) as ctx:
            self.validator.validate(blocks)
        
        self.assertIn('before', str(ctx.exception).lower())
    
    def test_zero_duration_detected(self):
        """Zero duration should raise error."""
        blocks = [
            {
                'block_type': BlockType.WORK,
                'start_time': time(8, 0),
                'end_time': time(8, 0),
                'duration_minutes': 0,
            },
        ]
        
        with self.assertRaises(TimelineIntegrityError)  as ctx:
            self.validator.validate(blocks)
        
        self.assertIn('positive', str(ctx.exception).lower())


class TestTimelineNormalizer(TestCase):
    """Test timeline normalization."""
    
    def setUp(self):
        self.normalizer = TimelineNormalizer()
    
    def test_sorts_blocks_by_time(self):
        """Normalizer should sort blocks by start_time."""
        blocks = [
            {
                'block_type': BlockType.WORK,
                'start_time': time(13, 0),
                'end_time': time(17, 0),
                'duration_minutes': 240,
            },
            {
                'block_type': BlockType.WORK,
                'start_time': time(8, 0),
                'end_time': time(12, 0),
                'duration_minutes': 240,
            },
        ]
        
        normalized = self.normalizer.normalize(blocks)
        
        # Should be sorted
        self.assertEqual(normalized[0]['start_time'], time(8, 0))
        self.assertEqual(normalized[1]['start_time'], time(13, 0))
    
    def test_fixes_overlapping_blocks(self):
        """Normalizer should trim overlapping blocks."""
        blocks = [
            {
                'block_type': BlockType.SCHEDULE,
                'start_time': time(8, 0),
                'end_time': time(17, 0),
                'duration_minutes': 540,
                'related_rule': '',
                'anomaly_code': '',
            },
            {
                'block_type': BlockType.WORK,
                'start_time': time(8, 5),  # Overlaps with schedule
                'end_time': time(12, 0),
                'duration_minutes': 235,
                'related_rule': '',
                'anomaly_code': '',
            },
        ]
        
        normalized = self.normalizer.normalize(blocks)
        
        # Second block should be trimmed
        self.assertGreaterEqual(
            normalized[1]['start_time'],
            normalized[0]['end_time']
        )
    
    def test_fills_gaps_with_unclassified(self):
        """Normalizer should fill gaps with GAP_UNCLASSIFIED."""
        blocks = [
            {
                'block_type': BlockType.WORK,
                'start_time': time(8, 0),
                'end_time': time(12, 0),
                'duration_minutes': 240,
                'related_rule': '',
                'anomaly_code': '',
            },
            {
                'block_type': BlockType.WORK,
                'start_time': time(13, 0),  # 1 hour gap
                'end_time': time(17, 0),
                'duration_minutes': 240,
                'related_rule': '',
                'anomaly_code': '',
            },
        ]
        
        normalized = self.normalizer.normalize(blocks)
        
        # Should have 3 blocks (work, gap, work)
        self.assertEqual(len(normalized), 3)
        
        # Middle block should be GAP_UNCLASSIFIED
        self.assertEqual(normalized[1]['block_type'], BlockType.GAP_UNCLASSIFIED)
        self.assertEqual(normalized[1]['start_time'], time(12, 0))
        self.assertEqual(normalized[1]['end_time'], time(13, 0))
    
    def test_recalculates_durations(self):
        """Normalizer should recalculate durations correctly."""
        blocks = [
            {
                'block_type': BlockType.WORK,
                'start_time': time(8, 0),
                'end_time': time(12, 30),
                'duration_minutes': 999,  # Wrong duration
                'related_rule': '',
                'anomaly_code': '',
            },
        ]
        
        normalized = self.normalizer.normalize(blocks)
        
        # Duration should be corrected to 270 minutes (4.5 hours)
        self.assertEqual(normalized[0]['duration_minutes'], 270)
    
    def test_handles_empty_blocks(self):
        """Normalizer should handle empty input."""
        normalized = self.normalizer.normalize([])
        self.assertEqual(normalized, [])
    
    def test_full_normalization_workflow(self):
        """Test complete normalization: sort, fix overlaps, fill gaps, recalculate."""
        # Messy input: out of order, overlapping, gaps, wrong durations
        blocks = [
            {
                'block_type': BlockType.WORK,
                'start_time': time(13, 0),
                'end_time': time(15, 0),
                'duration_minutes': 100,  # Wrong
                'related_rule': '',
                'anomaly_code': '',
            },
            {
                'block_type': BlockType.WORK,
                'start_time': time(8, 0),
                'end_time': time(10, 0),
                'duration_minutes': 120,
                'related_rule': '',
                'anomaly_code': '',
            },
            {
                'block_type': BlockType.WORK,
                'start_time': time(9, 30),  # Overlaps previous
                'end_time': time(11, 0),
                'duration_minutes': 90,
                'related_rule': '',
                'anomaly_code': '',
            },
        ]
        
        normalized = self.normalizer.normalize(blocks)
        
        # Should be sorted
        self.assertLessEqual(
            normalized[0]['start_time'],
            normalized[1]['start_time']
        )
        
        # Should have no overlaps
        for i in range(len(normalized) - 1):
            self.assertLessEqual(
                normalized[i]['end_time'],
                normalized[i + 1]['start_time'],
                f"Block {i} overlaps with block {i+1}"
            )
        
        # Should fill gap between 11:00 and 13:00
        gap_blocks = [b for b in normalized if b['block_type'] == BlockType.GAP_UNCLASSIFIED]
        self.assertGreater(len(gap_blocks), 0, "Should have filled gap")
        
        # Durations should be correct
        for block in normalized:
            expected_duration = self._calc_duration(
                block['start_time'],
                block['end_time']
            )
            self.assertAlmostEqual(
                block['duration_minutes'],
                expected_duration,
                delta=1,  # Allow 1 minute rounding
                msg=f"Duration mismatch for block {block}"
            )
    
    def _calc_duration(self, start: time, end: time) -> int:
        """Helper to calculate expected duration."""
        from datetime import datetime, timedelta
        today = datetime.today().date()
        start_dt = datetime.combine(today, start)
        end_dt = datetime.combine(today, end)
        if end < start:
            end_dt += timedelta(days=1)
        return int((end_dt - start_dt).total_seconds() / 60)
