import unittest
import webrtcvad
from app.voice.vad import InterruptionDetector
from unittest.mock import patch

class TestVAD(unittest.TestCase):
    def setUp(self):
        self.vad = InterruptionDetector(sample_rate=16000, frame_duration_ms=30)
        
        # Create test audio frames (mock speech and silence)
        self.silence_frame = b'\x00' * 960  # 30ms of silence
        # Create a simple pattern that stays within byte range (0-255)
        self.speech_frame = bytes([(i % 128) + 64 for i in range(960)])
    
    def test_process_frame_silence(self):
        is_speech, is_interruption = self.vad.process_frame(self.silence_frame)
        self.assertFalse(is_speech)
        self.assertFalse(is_interruption)
    
    def test_process_frame_speech(self):
        # First reset to ensure "not speaking" state
        self.vad.reset()

        # Fill the speech window first with silence to set initial state
        for _ in range(self.vad.speech_window):
            self.vad.process_frame(self.silence_frame)
        
        # Mock VAD to detect speech
        with patch.object(self.vad.vad, 'is_speech', return_value=True):
            # Capture the result of the last frame only
            for i in range(self.vad.interruption_frames + 2):
                is_speech, is_interruption = self.vad.process_frame(self.speech_frame)
                if i == self.vad.interruption_frames + 1:
                    # This should be the frame where interruption is detected
                    self.assertTrue(is_speech)
                    self.assertTrue(is_interruption)
    
    def test_reset(self):
        # Fill buffer with speech first
        for _ in range(5):
            self.vad.process_frame(self.speech_frame)
        
        # Reset detector
        self.vad.reset()
        
        # State should be cleared
        self.assertFalse(self.vad.is_speaking)
        self.assertEqual(0, self.vad.consecutive_speech)
        self.assertEqual(0, self.vad.consecutive_silence)

if __name__ == '__main__':
    unittest.main()