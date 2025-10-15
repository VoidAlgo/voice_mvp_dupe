from stt_handler import STTHandler
from llm_handler import LLMHandler
from tts_handler import TTSHandler
import asyncio
import logging
import warnings

# Suppress specific warnings to reduce noise
warnings.filterwarnings("ignore", category=DeprecationWarning, message="pkg_resources is deprecated")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def handle_conversation_turn(stt_handler, llm_handler, tts_handler, conversation_history):
    """Handle a single turn in the conversation."""
    try:
        logger.info("🎤 Waiting for your speech...")
        print("\n🎤 Speak now... (The system is listening)")
        
        # Get the transcription (this will wait for speech)
        user_text = await stt_handler.get_transcription()
        
        if not user_text:
            logger.warning("⚠️ No speech detected.")
            print("❌ No speech detected. Please try again.")
            return False
        
        print(f"📝 You said: {user_text}")
        
        # Add to conversation history
        conversation_history.append(f"User: {user_text}")
        
        # Exit if user says quit/exit
        if user_text.strip().lower() in ['quit', 'exit', 'q']:
            return True
        
        # Process with LLM
        logger.info("🤖 AI is thinking...")
        response = await llm_handler.process_text_with_history(user_text, conversation_history)
        
        print(f"🤖 Shamla Tech Agent: {response}")
        
        # Add to conversation history
        conversation_history.append(f"Agent: {response}")
        
        # Speak the response with barge-in enabled
        logger.info("🗣 Agent is speaking...")
        tts_handler.speak(response, voice="default", emotive_tags="", enable_barge_in=True)
        
        # Wait for completion or barge-in
        completed = tts_handler.wait_for_completion(timeout=30.0)
        
        if tts_handler.is_barge_in_detected():
            print("🎤 Barge-in detected! You interrupted the AI.")
            # Add the interruption to conversation history
            conversation_history.append("User: [Interrupted AI]")
            # Immediately start next turn (recursive call)
            return await handle_conversation_turn(stt_handler, llm_handler, tts_handler, conversation_history)
        
        return completed
        
    except Exception as e:
        logger.error(f"❌ Error in conversation turn: {e}")
        print(f"❌ An error occurred: {e}")
        return False

async def main():
    """Main function to run the conversational voice processing pipeline."""
    logger.info("🚀 Starting conversational voice processing pipeline...")
    
    try:
        # Initialize the handlers
        logger.info("🔧 Initializing handlers...")
        stt_handler = STTHandler()
        llm_handler = LLMHandler()
        tts_handler = TTSHandler()
        # Start continuous STT listening in background
        await stt_handler.start_listening()
        
        # Initialize conversation history
        conversation_history = [
            "System: You are an AI voice calling agent for Shamla Tech. Shamla Tech provides AI, blockchain, and cryptocurrency services. Be professional, helpful, and informative. Ask clarifying questions to better assist customers."
        ]
        
        # Welcome message
        welcome_message = "Hello! Thank you for calling Shamla Tech! I'm your AI assistant. How can I help you today?"
        print(f"🤖 Shamla Tech Agent: {welcome_message}")
        conversation_history.append(f"Agent: {welcome_message}")
        
        # Speak the welcome message
        logger.info("🗣 Speaking welcome message...")
        tts_handler.speak(welcome_message, voice="default", emotive_tags="")
        
        # Main conversation loop
        print("\n💡 Conversation Tips:")
        print("- Speak clearly and pause briefly between sentences")
        print("- Say 'quit' or 'exit' to end the conversation")
        print("- Say 'help' for assistance")
        print()
        
        while True:
            # Voice-driven loop: handle a conversation turn
            result = await handle_conversation_turn(stt_handler, llm_handler, tts_handler, conversation_history)
            
            # If user said quit/exit, break
            if result is True and conversation_history[-1].lower().startswith("user: "):
                last_user = conversation_history[-1][6:].strip().lower()
                if last_user in ['quit', 'exit', 'q']:
                    print("👋 Thank you for calling Shamla Tech! Have a great day!")
                    break
            
            if not result:
                print("❌ There was an error processing your input. Please try again.")
                continue
        
        logger.info("✅ Conversation completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error in conversation pipeline: {e}")
        print(f"❌ An error occurred: {e}")
    
    finally:
        # Cleanup
        logger.info("🧹 Cleaning up...")
        if 'tts_handler' in locals():
            tts_handler.shutdown()
        if 'stt_handler' in locals():
            # stop_listening is async
            try:
                await stt_handler.stop_listening()
            except Exception:
                # best-effort cleanup
                pass

if __name__ == "__main__":
    print("🎙 Shamla Tech AI Voice Assistant")
    print("=" * 50)
    print("Professional AI Voice Calling Agent")
    print("Services: AI, Blockchain, Cryptocurrency")
    print("=" * 50)
    print("Make sure you have:")
    print("1. Microphone access")
    print("2. GEMINI_API_KEY set in your .env file")
    print("3. Required dependencies installed")
    print("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Voice processing interrupted by user.")
    except Exception as e:
        print(f"❌ Fatal error: {e}")