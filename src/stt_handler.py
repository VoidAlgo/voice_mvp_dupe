#stt_handler.py
from datetime import datetime
import logging
import asyncio
import warnings
import concurrent.futures
from RealtimeSTT import AudioToTextRecorder

# Suppress specific warnings to reduce noise
warnings.filterwarnings("ignore", category=DeprecationWarning, message="pkg_resources is deprecated")

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
            # Initialize with timeout to prevent hanging
            def init_recorder():
                return AudioToTextRecorder(
                    model="base", 
                    language="en",
                    compute_type="int8",
                    # Enable real-time transcription
                    enable_realtime_transcription=True,
                    # Use smaller model for real-time processing
                    realtime_model_type="base",
                    # Longer pause for processing to reduce CPU load
                    realtime_processing_pause=0.3,
                    # Start recording immediately
                    init_realtime_after_seconds=0.1,
                    # Longer post-speech silence detection
                    post_speech_silence_duration=0.8,
                    # Minimum recording length
                    min_length_of_recording=0.5,
                    # Minimum gap between recordings
                    min_gap_between_recordings=0.1,
                    # Use microphone
                    use_microphone=True
                )
            
            # Run initialization in a separate thread with timeout
            with concurrent.futures.ThreadPoolExecutor() as executor:
                try:
                    # Run the blocking initialization in a separate thread
                    future = executor.submit(init_recorder)
                    self.recorder = await asyncio.wait_for(
                        asyncio.wrap_future(future), 
                        timeout=30.0  # 30 second timeout
                    )
                    self.is_listening = True
                    logger.info("🎤 Started continuous listening with voice activation.")
                except asyncio.TimeoutError:
                    logger.error("❌ STT initialization timed out after 30 seconds")
                    raise TimeoutError("STT initialization timed out")
                except Exception as e:
                    logger.error(f"❌ Error starting continuous listening: {e}")
                    raise
        except Exception as e:
            logger.error(f"❌ Error in start_listening: {e}")
            raise
    
    async def get_transcription(self) -> str:
        """Get transcription from the recorder with error correction."""
        try:
            if not self.recorder:
                raise ValueError("Recorder not initialized")
            
            # Get the transcription
            text = self.recorder.text()
            
            # Post-process to fix common transcription errors
            if text:
                # Fix common errors
                text = text.replace("Shambla Tech", "Shamla Tech")
                text = text.replace("Shambla", "Shamla")
                text = text.replace("blocked", "about")  # Common misrecognition
                text = text.strip()
                
                logger.info(f"📝 Transcription: {text}")
                return text
            else:
                logger.warning("⚠️ No transcription received")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Error getting transcription: {e}")
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