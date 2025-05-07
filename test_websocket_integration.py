import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from starlette.websockets import WebSocket, WebSocketDisconnect
from app.routes.websocket import websocket_audio_endpoint
from app.main import app

class TestWebSocketIntegration(unittest.IsolatedAsyncioTestCase):
    
    async def asyncSetUp(self):
        self.client = TestClient(app)
        self.test_audio_chunk = b'test_audio_data'
    
    # Using context manager approach instead of decorators to avoid parameter order issues
    async def test_websocket_connection(self):
        # Using context manager instead of decorators makes the order clear
        with patch('app.routes.websocket.handle_agent_responses') as mock_response_handler, \
             patch('app.routes.websocket.StreamingAgent') as mock_agent_class, \
             patch('app.routes.websocket.stream_manager') as mock_manager, \
             patch('app.routes.websocket.streaming_agents', {}):
            
            # Setup manager mock
            mock_manager.connect = AsyncMock()
            mock_manager.disconnect = MagicMock()
            mock_manager.receive_audio = AsyncMock()
            mock_manager.get_input_buffer = MagicMock(return_value=MagicMock())
            mock_manager.get_input_buffer().get_all = MagicMock(return_value=b'test_audio_data')
            mock_manager.register_interrupt_handler = MagicMock()
            
            # Setup agent mock
            mock_agent = MagicMock()
            mock_agent.process_audio = AsyncMock(return_value="Test transcript")
            mock_agent.close = AsyncMock()
            mock_agent_class.return_value = mock_agent
            
            mock_response_handler.return_value = None
            
            # Setup WebSocket mock
            mock_ws = AsyncMock()
            mock_ws.receive = AsyncMock(side_effect=[
                {"bytes": self.test_audio_chunk},
                WebSocketDisconnect()
            ])
            
            # Call the endpoint
            await websocket_audio_endpoint(mock_ws, "test_client", MagicMock())
            
            # Verify expected calls
            mock_manager.connect.assert_called_once_with(mock_ws, "test_client")
            mock_manager.receive_audio.assert_called_once_with("test_client", self.test_audio_chunk)
            mock_agent.process_audio.assert_called_once()
            mock_manager.disconnect.assert_called_once_with("test_client")
            mock_agent.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()