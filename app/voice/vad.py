"""
Voice Activity Detection module using WebRTC VAD.
"""
import webrtcvad
import numpy as np
from collections import deque
import logging
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

class InterruptionDetector:
    """Detects speech and interruptions using WebRTC VAD."""
    
    def __init__(self, 
                 sample_rate: int = 16000, 
                 frame_duration_ms: int = 30,
                 aggressiveness: int = 3,
                 speech_window: int = 5,
                 silence_window: int = 10,
                 speech_threshold: float = 0.5,
                 interruption_duration_ms: int = 300):
        """
        Initialize the interruption detector.
        
        Args:
            sample_rate: Audio sample rate (must be 8000, 16000, 32000, or 48000 Hz)
            frame_duration_ms: Frame duration in ms (must be 10, 20, or 30 ms)
            aggressiveness: VAD aggressiveness (0-3, higher is more aggressive)
            speech_window: Number of frames to consider for speech detection
            silence_window: Number of frames to consider for silence detection
            speech_threshold: Ratio of speech frames needed in window to count as speech
            interruption_duration_ms: Minimum duration of speech to count as interruption
        """
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.frame_size = int(sample_rate * frame_duration_ms / 1000)
        self.vad = webrtcvad.Vad(aggressiveness)
        self._frame_buffer = bytearray()
        
        self.speech_window = speech_window
        self.silence_window = silence_window
        self.speech_threshold = speech_threshold
        
        self.interruption_frames = max(1, int(interruption_duration_ms / frame_duration_ms))
        
        # State tracking
        self.is_speaking = False
        self.speech_frames = deque(maxlen=speech_window)
        self.consecutive_speech = 0
        self.consecutive_silence = 0
        
        logger.info(f"Initialized VAD with sample_rate={sample_rate}, "
                    f"frame_duration_ms={frame_duration_ms}, "
                    f"aggressiveness={aggressiveness}")
    
    def process_frame(self, audio_frame: bytes) -> Tuple[bool, bool]:
        """Process audio frames of variable sizes."""
        expected_size = self.frame_size * 2  # 16-bit = 2 bytes per sample
        
        # Handle variable frame sizes
        if len(audio_frame) != expected_size:
            # For larger frames, split into multiple WebRTC VAD-compatible frames
            if len(audio_frame) > expected_size:
                results = []
                # Process multiple frames
                for i in range(0, len(audio_frame), expected_size):
                    frame_chunk = audio_frame[i:i+expected_size]
                    if len(frame_chunk) == expected_size:
                        speech, interrupt = self._process_standard_frame(frame_chunk)
                        results.append((speech, interrupt))
                
                # Return True for interruption if any frame detected it
                return any(r[0] for r in results), any(r[1] for r in results)
            else:
                # For smaller frames, buffer until we have enough data
                self._frame_buffer += audio_frame
                if len(self._frame_buffer) >= expected_size:
                    frame_to_process = self._frame_buffer[:expected_size]
                    self._frame_buffer = self._frame_buffer[expected_size:]
                    return self._process_standard_frame(frame_to_process)
                return False, False
        
        return self._process_standard_frame(audio_frame)

    def _process_standard_frame(self, frame: bytes) -> Tuple[bool, bool]:
        """Process a standard-sized frame."""
        try:
            is_speech = self.vad.is_speech(frame, self.sample_rate)
        except Exception as e:
            logger.error(f"VAD error: {str(e)}")
            return False, False
        
        self.speech_frames.append(is_speech)
        
        # Calculate speech ratio in the window
        if len(self.speech_frames) >= self.speech_window:
            speech_ratio = sum(self.speech_frames) / len(self.speech_frames)
            current_speech = speech_ratio >= self.speech_threshold
            
            if current_speech:
                self.consecutive_speech += 1
                self.consecutive_silence = 0
            else:
                self.consecutive_silence += 1
                self.consecutive_speech = 0
            
            # State transition: not speaking -> speaking
            interruption_detected = False
            if not self.is_speaking and self.consecutive_speech >= self.interruption_frames:
                logger.debug("Interruption detected")
                self.is_speaking = True
                interruption_detected = True
            
            # State transition: speaking -> not speaking
            elif self.is_speaking and self.consecutive_silence >= self.silence_window:
                logger.debug("End of speech detected")
                self.is_speaking = False
            
            return current_speech, interruption_detected
        
        return is_speech, False
    
    def reset(self):
        """Reset the detector state."""
        self.is_speaking = False
        self.speech_frames.clear()
        self.consecutive_speech = 0
        self.consecutive_silence = 0
        self._frame_buffer = bytearray()  # Also reset the buffer