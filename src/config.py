# Configuration settings for the voice-to-text with LLM integration system

import os

class Config:
    """Configuration class for the voice processing pipeline"""
    
    # Model settings
    STT_MODEL_SIZE: str = "base"  # Options: "tiny", "base", "small", "medium", "large"
    STT_REALTIME_MODEL_SIZE: str = "small"  # Smaller model for real-time processing
    STT_DEVICE: str = "auto"  # Device for processing (auto, cpu, cuda)
    STT_REALTIME_PROCESSING_PAUSE: float = 0.2  # Pause for real-time processing
    STT_BEAM_SIZE: int = 3  # Beam size for STT
    
    # LLM settings
    LLM_MODEL: str = "gemini-2.0-flash-lite"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2048
    LLM_RATE_LIMIT_DELAY: float = 0.2  # Seconds between requests
    LLM_MAX_RETRIES: int = 3
    LLM_RETRY_DELAY: float = 1.0
    
    # TTS settings
    TTS_MODEL: str = "orpheus"  # Orpheus model for TTS
    TTS_VOICE: str = "default"  # Default voice for TTS
    TTS_EMOTIVE_TAGS: bool = True  # Enable emotive tags for TTS
    
    # Buffer settings
    BUFFER_THRESHOLD: int = 5  # Characters before batching
    BUFFER_TIMEOUT: float = 0.5  # Seconds before flushing buffer
    MAX_BUFFER_SIZE: int = 100  # Maximum characters in buffer
    
    # Performance settings
    SESSION_KEEPALIVE_TIMEOUT: int = 30  # Seconds
    REQUEST_TIMEOUT: float = 30.0  # Seconds
    CONNECT_TIMEOUT: float = 5.0  # Seconds
    ENQUEUE_TIMEOUT: float = 5.0  # Seconds
    
    # Logging settings
    LOG_LEVEL: str = "INFO"  # Options: "DEBUG", "INFO", "WARNING", "ERROR"
    LOG_FORMAT: str = "%(asctime)s [%(levelname)s] %(message)s"
    
    # File settings
    RESPONSES_DIR: str = "./responses"
    TRANSCRIPT_PREFIX: str = "transcript"
    RESPONSE_PREFIX: str = "response"
    
    # Memory management
    MAX_AUDIO_DURATION: int = 3600  # Maximum recording time in seconds (1 hour)
    CLEANUP_INTERVAL: int = 300  # Cleanup interval in seconds (5 minutes)
    
    @classmethod
    def get_env_settings(cls):
        """Get settings from environment variables with fallbacks"""
        env_settings = {
            'STT_MODEL_SIZE': os.getenv('STT_MODEL_SIZE', cls.STT_MODEL_SIZE),
            'STT_REALTIME_MODEL_SIZE': os.getenv('STT_REALTIME_MODEL_SIZE', cls.STT_REALTIME_MODEL_SIZE),
            'STT_DEVICE': os.getenv('STT_DEVICE', cls.STT_DEVICE),
            'STT_REALTIME_PROCESSING_PAUSE': float(os.getenv('STT_REALTIME_PROCESSING_PAUSE', cls.STT_REALTIME_PROCESSING_PAUSE)),
            'STT_BEAM_SIZE': int(os.getenv('STT_BEAM_SIZE', cls.STT_BEAM_SIZE)),
            'LLM_RATE_LIMIT_DELAY': float(os.getenv('LLM_RATE_LIMIT_DELAY', cls.LLM_RATE_LIMIT_DELAY)),
            'LLM_MAX_RETRIES': int(os.getenv('LLM_MAX_RETRIES', cls.LLM_MAX_RETRIES)),
            'LLM_RETRY_DELAY': float(os.getenv('LLM_RETRY_DELAY', cls.LLM_RETRY_DELAY)),
            'BUFFER_THRESHOLD': int(os.getenv('BUFFER_THRESHOLD', cls.BUFFER_THRESHOLD)),
            'BUFFER_TIMEOUT': float(os.getenv('BUFFER_TIMEOUT', cls.BUFFER_TIMEOUT)),
            'LOG_LEVEL': os.getenv('LOG_LEVEL', cls.LOG_LEVEL),
            'MAX_AUDIO_DURATION': int(os.getenv('MAX_AUDIO_DURATION', cls.MAX_AUDIO_DURATION)),
        }
        return env_settings
    
    @classmethod
    def apply_settings(cls, settings):
        """Apply configuration settings to the class"""
        for key, value in settings.items():
            if hasattr(cls, key):
                setattr(cls, key, value)
    
    @classmethod
    def validate_settings(cls):
        """Validate configuration settings"""
        errors = []
        
        # Validate model sizes
        valid_sizes = ["tiny", "base", "small", "medium", "large"]
        if cls.STT_MODEL_SIZE not in valid_sizes:
            errors.append(f"Invalid STT_MODEL_SIZE: {cls.STT_MODEL_SIZE}")
        if cls.STT_REALTIME_MODEL_SIZE not in valid_sizes:
            errors.append(f"Invalid STT_REALTIME_MODEL_SIZE: {cls.STT_REALTIME_MODEL_SIZE}")
        
        # Validate device
        valid_devices = ["auto", "cuda", "cpu"]
        if cls.STT_DEVICE not in valid_devices:
            errors.append(f"Invalid STT_DEVICE: {cls.STT_DEVICE}")
        
        # Validate timeouts and delays
        if cls.STT_REALTIME_PROCESSING_PAUSE <= 0:
            errors.append("STT_REALTIME_PROCESSING_PAUSE must be positive")
        if cls.LLM_RATE_LIMIT_DELAY <= 0:
            errors.append("LLM_RATE_LIMIT_DELAY must be positive")
        if cls.BUFFER_TIMEOUT <= 0:
            errors.append("BUFFER_TIMEOUT must be positive")
        
        # Validate thresholds
        if cls.BUFFER_THRESHOLD <= 0:
            errors.append("BUFFER_THRESHOLD must be positive")
        if cls.BUFFER_THRESHOLD > cls.MAX_BUFFER_SIZE:
            errors.append("BUFFER_THRESHOLD cannot exceed MAX_BUFFER_SIZE")
        
        if errors:
            logger = logging.getLogger(__name__)
            logger.error("Configuration validation failed:")
            for error in errors:
                logger.error(f"  - {error}")
            return False
        
        return True