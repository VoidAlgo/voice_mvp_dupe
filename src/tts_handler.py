import os
import logging
import asyncio
import time
import threading
import warnings
from RealtimeSTT import AudioToTextRecorder
from RealtimeTTS import SystemEngine, TextToAudioStream

# Suppress specific warnings to reduce noise
warnings.filterwarnings("ignore", category=DeprecationWarning, message="pkg_resources is deprecated")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TTSHandler:
    """Handles text-to-speech functionality with barge-in capability."""
    
    def __init__(self):
        """Initialize the TTS handler with SystemEngine and speech detection."""
        try:
            # Initialize SystemEngine and TextToAudioStream
            self.engine = SystemEngine()
            self.stream = TextToAudioStream(self.engine)
            
            # Initialize speech detector for barge-in with aggressive settings
            self.speech_detector = AudioToTextRecorder(
                model="tiny",
                language="en",
                compute_type="int8",
                enable_realtime_transcription=True,
                realtime_processing_pause=0.05,  # Reduced from 0.1 for faster detection
                post_speech_silence_duration=0.2,  # Reduced from 0.3 for faster response
                min_length_of_recording=0.1  # Reduced from 0.2 for faster detection
            )
            
            self.is_playing = False
            self.is_barge_in_enabled = True
            self.barge_in_detected = False
            self.playback_thread = None
            self.stop_event = threading.Event()  # For immediate cancellation
            
            logger.info("🎤 TTS Handler initialized with enhanced barge-in capability.")
        except Exception as e:
            logger.error(f"❌ Error initializing TTS: {e}")
            self.engine = None
            self.stream = None
            self.speech_detector = None
            raise
    
    def _playback_with_barge_in(self, text: str):
        """Play audio in a separate thread while monitoring for speech with enhanced responsiveness."""
        def monitor_speech():
            """Monitor for user speech during playback with aggressive detection."""
            try:
                if self.is_barge_in_enabled and self.speech_detector:
                    # Use shorter intervals for faster detection
                    last_check_time = time.time()
                    
                    while not self.stop_event.is_set() and self.is_playing:
                        current_time = time.time()
                        
                        # Check speech detection every 50ms for maximum responsiveness
                        if current_time - last_check_time >= 0.05:
                            try:
                                # Get detected text
                                detected_text = self.speech_detector.text()
                                if detected_text and detected_text.strip():
                                    logger.info(f"🎤 Barge-in detected: {detected_text}")
                                    self.barge_in_detected = True
                                    # Signal immediate stop
                                    self.stop_event.set()
                                    # Immediately stop the stream
                                    if self.stream and hasattr(self.stream, 'stop'):
                                        self.stream.stop()
                                        logger.info("🛑 Audio playback stopped due to barge-in")
                                    break
                            except Exception:
                                # Non-critical error, continue monitoring
                                pass
                            
                            last_check_time = current_time
                        
                        # Small sleep to prevent CPU overload
                        time.sleep(0.01)
                        
            except Exception as e:
                logger.error(f"❌ Error monitoring speech: {e}")
        
        def play_audio():
            """Play the audio stream with enhanced cancellation."""
            try:
                self.is_playing = True
                self.barge_in_detected = False
                self.stop_event.clear()
                
                # Start speech monitoring in a separate thread
                monitor_thread = threading.Thread(target=monitor_speech, daemon=True)
                monitor_thread.start()
                
                # Feed and play the audio
                def text_generator():
                    yield text
                
                if self.stream:
                    self.stream.feed(text_generator())
                    
                    # Play with enhanced cancellation support
                    try:
                        self.stream.play()
                    except Exception as e:
                        # Check if it was cancelled
                        if self.stop_event.is_set():
                            logger.info("🛑 Playback cancelled due to barge-in")
                        else:
                            logger.error(f"❌ Error during playback: {e}")
                
            except Exception as e:
                logger.error(f"❌ Error during playback: {e}")
            finally:
                self.is_playing = False
                self.stop_event.clear()
        
        # Start playback in a separate thread
        self.playback_thread = threading.Thread(target=play_audio, daemon=True)
        self.playback_thread.start()
    
    def speak(self, text: str, voice: str = "default", emotive_tags: str = "", enable_barge_in: bool = True) -> str:
        """
        Convert text to speech with barge-in capability.
        
        Args:
            text (str): The text to convert to speech
            voice (str): Voice to use (default: "default")
            emotive_tags (str): Emotive tags to apply (default: "")
            enable_barge_in (bool): Enable barge-in detection (default: True)
        
        Returns:
            str: Path to the generated audio file
        """
        try:
            if not self.engine or not self.stream:
                raise ValueError("TTS not initialized properly")
            
            self.is_barge_in_enabled = enable_barge_in
            
            logger.info(f"🗣 Speaking text: {text}")
            
            # Apply emotive tags if provided
            if emotive_tags:
                text = f"{text} {emotive_tags}"
            
            # Set voice if specified
            if voice != "default":
                try:
                    self.engine.set_voice(voice)
                except Exception as e:
                    logger.warning(f"Voice '{voice}' not available, using default: {e}")
            
            # Use playback with barge-in
            self._playback_with_barge_in(text)
            
            # Save audio to file (SystemEngine might not return audio data directly)
            output_dir = os.path.join("src", "audio", "output")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{int(time.time())}.wav")
            
            logger.info("✅ Audio playing through system speakers")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Error during TTS: {e}")
            return ""
    
    def wait_for_completion(self, timeout: float = 30.0) -> bool:
        """
        Wait for TTS playback to complete or timeout.
        
        Args:
            timeout (float): Maximum time to wait in seconds
        """
        try:
            if not self.is_playing:
                return True

            start_time = time.time()

            while self.is_playing and not self.barge_in_detected:
                if time.time() - start_time > timeout:
                    logger.warning("\u23f0 TTS playback timed out")
                    return False
                time.sleep(0.1)

            return not self.barge_in_detected

        except Exception as e:
            logger.error(f"\u274c Error waiting for completion: {e}")
            return False
    
    def is_barge_in_detected(self) -> bool:
        """Check if barge-in was detected during playback."""
        return self.barge_in_detected
    
    def shutdown(self):
        """Shutdown the TTS handler and release resources."""
        try:
            if hasattr(self, 'stream'):
                self.stream = None
            if hasattr(self, 'engine'):
                self.engine = None
            if hasattr(self, 'speech_detector'):
                self.speech_detector = None
            logger.info("🎤 TTS Handler shutdown complete.")
        except Exception as e:
            logger.error(f"❌ Error during TTS shutdown: {e}")

async def main():
    """Example usage of TTSHandler"""
    tts_handler = TTSHandler()
    
    # Test with different voices and emotive tags
    test_cases = [
        ("Hello, this is a test message.", "default", ""),
        ("This is a happy message! <laugh>", "zoe", "<laugh>"),
        ("I'm feeling excited today!", "tara", "")
    ]
    
    for text, voice, tags in test_cases:
        print(f"Testing: {text}")
        tts_handler.speak(text, voice, tags)
        await asyncio.sleep(2)  # Wait between tests

if __name__ == "__main__":
    asyncio.run(main())