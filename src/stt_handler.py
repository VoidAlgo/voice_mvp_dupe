from datetime import datetime
import os
import logging
import asyncio
from RealtimeSTT import AudioToTextRecorder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

class STTHandler:
    """Handles speech-to-text functionality using RealTimeSTT with voice activation."""
    
    def __init__(self):
        self.recorder = None
        self.is_listening = False
        logger.info("🎤 STT Handler initialized.")
    
    async def start_listening(self):
        """Start continuous audio recording with voice activation."""
        try:
            self.recorder = AudioToTextRecorder(
                model="base", 
                language="en",
                compute_type="int8",
                # Enable real-time transcription
                enable_realtime_transcription=True,
                # Use smaller model for real-time processing
                realtime_model_type="tiny",
                # Pause for processing
                realtime_processing_pause=0.2,
                # Start recording immediately
                init_realtime_after_seconds=0.2,
                # Post-speech silence detection
                post_speech_silence_duration=0.6,
                # Minimum recording length
                min_length_of_recording=0.5,
                # Minimum gap between recordings
                min_gap_between_recordings=0,
                # Use microphone
                use_microphone=True
            )
            self.is_listening = True
            logger.info("🎤 Started continuous listening with voice activation.")
        except Exception as e:
            logger.error(f"❌ Error starting continuous listening: {e}")
            raise
    
    async def get_transcription(self) -> str:
        """Get transcription from the recorded audio with timeout."""
        try:
            if not self.recorder or not self.is_listening:
                raise ValueError("Listening not started. Call start_listening() first.")
            
            logger.info("🎤 Listening for speech...")
            
            # Wait for speech with timeout
            text = ""
            max_wait_time = 10  # seconds
            start_time = asyncio.get_event_loop().time()
            
            while asyncio.get_event_loop().time() - start_time < max_wait_time:
                if self.recorder:
                    text = self.recorder.text()
                    if text and text.strip():
                        logger.info(f"📝 Transcription: {text}")
                        return text.strip()
                
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
            
            logger.warning("⚠️ No speech detected within timeout period.")
            return ""
            
        except Exception as e:
            logger.error(f"❌ Error during transcription: {e}")
            return ""
    
    async def stop_listening(self):
        """Stop continuous audio recording."""
        try:
            if self.recorder:
                self.recorder = None
            self.is_listening = False
            logger.info("🎤 Stopped continuous listening.")
        except Exception as e:
            logger.error(f"❌ Error stopping listening: {e}")

async def main():
    """Main function to test STT functionality."""
    stt_handler = STTHandler()
    await stt_handler.start_listening()
    
    # Simulate recording for a few seconds
    print("Speak now... (Press Enter when done)")
    input()
    
    text = await stt_handler.get_transcription()
    print(f"Transcribed text: {text}")
    
    await stt_handler.stop_listening()

if __name__ == "__main__":
    asyncio.run(main())