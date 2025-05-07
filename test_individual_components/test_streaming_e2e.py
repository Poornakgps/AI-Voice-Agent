import unittest
import asyncio
import os
import wave
import time
import tempfile
import subprocess
from websocket_client import WebSocketClient

class TestStreamingE2E(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.server_url = "ws://localhost:8000"
        self.test_audio_path = self.create_test_audio()
    
    def create_test_audio(self):
        """Create a test audio file with silence and 'speech'."""
        # Create a temporary WAV file
        fd, path = tempfile.mkstemp(suffix='.wav')
        os.close(fd)
        
        # Generate 3 seconds of audio
        # 1s silence + 1s 'speech' + 1s silence
        sample_rate = 16000
        duration = 3
        
        with wave.open(path, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)  # 16-bit
            wav.setframerate(sample_rate)
            
            # 1s silence
            silence = bytes([0, 0] * sample_rate)
            wav.writeframes(silence)
            
            # 1s 'speech' (sine wave)
            import math
            speech = bytearray()
            for i in range(sample_rate):
                value = int(32767 * 0.5 * math.sin(2 * math.pi * 440 * i / sample_rate))
                speech.extend([value & 0xFF, (value >> 8) & 0xFF])
            wav.writeframes(speech)
            
            # 1s silence
            wav.writeframes(silence)
        
        return path
    
    def tearDown(self):
        # Clean up test audio file
        if hasattr(self, 'test_audio_path') and os.path.exists(self.test_audio_path):
            os.remove(self.test_audio_path)
    
    def is_server_running(self):
        """Check if the server is running on port 8000."""
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(('localhost', 8000))
            s.close()
            return True
        except:
            return False
    
    async def test_audio_streaming(self):
        """Test the full audio streaming cycle."""
        # Skip if server is not running
        if not self.is_server_running():
            self.skipTest("Server is not running on localhost:8000")
        
        client = WebSocketClient(self.server_url, self.test_audio_path)
        
        # Connect to server
        connected = await client.connect()
        self.assertTrue(connected, "Failed to connect to server")
        
        # Start receiving messages
        receive_task = asyncio.create_task(client.receive_messages())
        
        # Wait a moment for connection setup
        await asyncio.sleep(1)
        
        # Send audio file
        sent = await client.send_audio_file()
        self.assertTrue(sent, "Failed to send audio file")
        
        # Wait for processing and response
        await asyncio.sleep(3)
        
        # Disconnect
        await client.disconnect()
        await receive_task
        
        # Verify we received audio back
        self.assertTrue(len(client.received_audio) > 0, "No audio response received")
        
        # Save received audio for inspection
        saved = client.save_received_audio("e2e_response.wav")
        self.assertTrue(saved, "Failed to save received audio")
        
        # Clean up
        if os.path.exists("e2e_response.wav"):
            os.remove("e2e_response.wav")

if __name__ == '__main__':
    unittest.main()