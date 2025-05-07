import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
from app.core.streaming_agent import StreamingAgent

class TestStreamingAgent(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db_session = MagicMock()
        with patch('app.core.streaming_agent.openai'):
            self.agent = StreamingAgent(self.db_session)
    
    def test_initialization(self):
        self.assertIsNotNone(self.agent.conversation_id)
        self.assertFalse(self.agent.is_speaking)
        self.assertFalse(self.agent.should_interrupt)
        self.assertEqual(self.agent.partial_transcript, "")
        self.assertEqual(len(self.agent.messages), 1)
        self.assertEqual(self.agent.messages[0]["role"], "system")
    
    async def test_process_audio(self):
        with patch('app.core.streaming_agent.transcribe_audio_stream', 
                  return_value="Hello, this is a test") as mock_transcribe, \
             patch.object(self.agent, '_generate_response') as mock_generate:
            
            result = await self.agent.process_audio(b'test_audio')
            
            mock_transcribe.assert_called_once_with(b'test_audio', self.agent.openai_client)
            self.assertEqual(result, "Hello, this is a test")
            self.assertEqual(self.agent.messages[-1]["role"], "user")
            self.assertEqual(self.agent.messages[-1]["content"], "Hello, this is a test")
            mock_generate.assert_called_once()
    
    async def test_handle_interruption(self):
        self.agent.is_speaking = True
        await self.agent.handle_interruption()
        self.assertTrue(self.agent.should_interrupt)
    
    async def test_get_response_stream(self):
        # Put some items in the queue
        await self.agent.response_queue.put(b'chunk1')
        await self.agent.response_queue.put(b'chunk2')
        await self.agent.response_queue.put(None)  # End signal
        
        chunks = []
        async for chunk in self.agent.get_response_stream():
            chunks.append(chunk)
        
        self.assertEqual(chunks, [b'chunk1', b'chunk2'])

if __name__ == '__main__':
    unittest.main()