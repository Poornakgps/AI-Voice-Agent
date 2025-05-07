import unittest
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio
from app.voice.streaming import AudioBuffer, StreamManager

class TestAudioBuffer(unittest.TestCase):
    def setUp(self):
        self.buffer = AudioBuffer(max_size=1000)
    
    def test_add(self):
        self.buffer.add(b'test data')
        self.assertEqual(len(self.buffer.buffer), 1)
        self.assertEqual(self.buffer.current_size, 9)
    
    def test_get_all(self):
        self.buffer.add(b'test1')
        self.buffer.add(b'test2')
        result = self.buffer.get_all()
        self.assertEqual(result, b'test1test2')
        self.assertEqual(len(self.buffer.buffer), 0)
    
    def test_clear(self):
        self.buffer.add(b'test data')
        self.buffer.clear()
        self.assertEqual(len(self.buffer.buffer), 0)
        self.assertEqual(self.buffer.current_size, 0)
    
    def test_overflow(self):
        small_buffer = AudioBuffer(max_size=15)
        small_buffer.add(b'test1')
        small_buffer.add(b'test2')
        small_buffer.add(b'overflow')
        # First chunk should be removed due to overflow
        self.assertEqual(len(small_buffer.buffer), 2)
        self.assertEqual(small_buffer.buffer[0], b'test2')

class TestStreamManager(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.stream_manager = StreamManager()
        
    async def test_connect(self):
        mock_ws = AsyncMock()
        client_id = "test_client"
        
        await self.stream_manager.connect(mock_ws, client_id)
        
        # No longer expect accept() to be called
        self.assertIn(client_id, self.stream_manager.active_connections)
        self.assertIn(client_id, self.stream_manager.vad_detectors)
        self.assertIn(client_id, self.stream_manager.input_buffers)
    
    def test_disconnect(self):
        client_id = "test_client"
        self.stream_manager.active_connections[client_id] = MagicMock()
        self.stream_manager.vad_detectors[client_id] = MagicMock()
        self.stream_manager.input_buffers[client_id] = MagicMock()
        
        self.stream_manager.disconnect(client_id)
        
        self.assertNotIn(client_id, self.stream_manager.active_connections)
        self.assertNotIn(client_id, self.stream_manager.vad_detectors)
        self.assertNotIn(client_id, self.stream_manager.input_buffers)
    
    async def test_receive_audio(self):
        client_id = "test_client"
        self.stream_manager.active_connections[client_id] = MagicMock()
        self.stream_manager.input_buffers[client_id] = AudioBuffer()
        self.stream_manager.vad_detectors[client_id] = MagicMock()
        self.stream_manager.vad_detectors[client_id].process_frame = MagicMock(return_value=(False, False))
        
        await self.stream_manager.receive_audio(client_id, b'test_audio')
        
        self.assertEqual(self.stream_manager.input_buffers[client_id].get_all(), b'test_audio')
        self.stream_manager.vad_detectors[client_id].process_frame.assert_called_once()
    
    async def test_send_audio(self):
        client_id = "test_client"
        mock_ws = AsyncMock()
        self.stream_manager.active_connections[client_id] = mock_ws
        
        await self.stream_manager.send_audio(client_id, b'test_audio')
        
        mock_ws.send_bytes.assert_called_once_with(b'test_audio')

if __name__ == '__main__':
    unittest.main()