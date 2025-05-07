import asyncio
import websockets
import json
import wave
import argparse
import os
import time

class WebSocketClient:
    def __init__(self, url, audio_file=None):
        self.url = url
        self.audio_file = audio_file
        self.client_id = f"test_client_{int(time.time())}"
        self.full_url = f"{url}/ws/audio/{self.client_id}"
        self.connected = False
        self.config = None
        self.received_audio = bytearray()
        
    async def connect(self):
        """Establish WebSocket connection."""
        try:
            self.ws = await websockets.connect(self.full_url)
            self.connected = True
            print(f"Connected to {self.full_url}")
            return True
        except Exception as e:
            print(f"Connection error: {str(e)}")
            return False
    
    async def receive_messages(self):
        """Receive and process messages."""
        try:
            while self.connected:
                message = await self.ws.recv()
                
                if isinstance(message, str):
                    # JSON message
                    data = json.loads(message)
                    if "event" in data and data["event"] == "connected":
                        self.config = data.get("config", {})
                        print(f"Received config: {self.config}")
                elif isinstance(message, bytes):
                    # Audio data
                    self.received_audio.extend(message)
                    print(f"Received {len(message)} bytes of audio")
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed")
            self.connected = False
        except Exception as e:
            print(f"Error receiving messages: {str(e)}")
            self.connected = False
    
    async def send_audio_file(self):
        """Send audio from file in chunks."""
        if not self.audio_file or not os.path.exists(self.audio_file):
            print(f"Audio file not found: {self.audio_file}")
            return False
        
        try:
            # Open the WAV file
            with wave.open(self.audio_file, 'rb') as wav:
                frame_rate = wav.getframerate()
                channels = wav.getnchannels()
                sample_width = wav.getsampwidth()
                
                print(f"Sending audio: {self.audio_file}")
                print(f"Frame rate: {frame_rate}Hz, Channels: {channels}, Sample width: {sample_width}")
                
                # Read in chunks of 30ms
                chunk_size = int(frame_rate * 0.03) * channels * sample_width
                
                while True:
                    chunk = wav.readframes(chunk_size)
                    if not chunk:
                        break
                    
                    if not self.connected:
                        break
                    
                    await self.ws.send(chunk)
                    # Simulate real-time playback
                    await asyncio.sleep(0.03)
                
                print("Finished sending audio")
                return True
                
        except Exception as e:
            print(f"Error sending audio: {str(e)}")
            return False
    
    async def send_text(self, text):
        """Send text message."""
        try:
            await self.ws.send(text)
            print(f"Sent text: {text}")
            return True
        except Exception as e:
            print(f"Error sending text: {str(e)}")
            return False
    
    async def disconnect(self):
        """Close the connection."""
        if self.connected:
            await self.ws.close()
            self.connected = False
            print("Disconnected")
    
    def save_received_audio(self, filename="received_audio.wav"):
        """Save received audio to a WAV file."""
        if not self.received_audio:
            print("No audio received to save")
            return False
        
        # Default parameters if no config was received
        sample_rate = 16000
        channels = 1
        sample_width = 2  # 16-bit
        
        if self.config:
            sample_rate = self.config.get("sample_rate", sample_rate)
            channels = self.config.get("channels", channels)
        
        try:
            with wave.open(filename, 'wb') as wav:
                wav.setnchannels(channels)
                wav.setsampwidth(sample_width)
                wav.setframerate(sample_rate)
                wav.writeframes(self.received_audio)
            
            print(f"Saved received audio to {filename}")
            return True
        except Exception as e:
            print(f"Error saving audio: {str(e)}")
            return False

async def main():
    parser = argparse.ArgumentParser(description="WebSocket client for audio streaming")
    parser.add_argument("--url", default="ws://localhost:8000", help="WebSocket server URL")
    parser.add_argument("--audio", help="Path to WAV file to send")
    args = parser.parse_args()
    
    client = WebSocketClient(args.url, args.audio)
    
    if await client.connect():
        # Start receive task
        receive_task = asyncio.create_task(client.receive_messages())
        
        # Send audio if specified
        if args.audio:
            await client.send_audio_file()
        
        # Wait for a while to receive responses
        await asyncio.sleep(5)
        
        # Close connection
        await client.disconnect()
        await receive_task
        
        # Save received audio
        client.save_received_audio()

if __name__ == "__main__":
    asyncio.run(main())