import os
import logging
import asyncio
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LLMHandler:
    """Handles text processing using OpenAI GPT-4o mini API."""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.error("❌ OPENAI_API_KEY not found in environment variables.")
            raise ValueError("OpenAI API key is required for LLM functionality.")
        
        self.base_url = "https://api.openai.com/v1/chat/completions"
        logger.info("🤖 LLM Handler initialized with OpenAI GPT-4o mini.")
    
    async def process_text(self, text: str) -> str:
        """Process text using OpenAI API and return response."""
        try:
            url = self.base_url
            
            # Enhanced system prompt for more human-like conversation
            system_prompt = """You are Alex, a friendly and professional AI voice assistant for Shamla Tech. 
You're not just a bot - you're a helpful conversation partner who:

🎯 Speaks naturally and conversationally, like you're talking to a friend
🎯 Uses warm, approachable language with occasional personality
🎯 Shows genuine interest in helping the user
🎯 Uses contractions (I'm, you're, don't, etc.) to sound more human
🎯 Occasionally uses light humor when appropriate
🎯 Asks thoughtful follow-up questions to better understand needs
🎯 Sounds enthusiastic and positive about Shamla Tech's services
🎯 Is honest when you don't know something and offer to help find the answer

About Shamla Tech:
- We provide cutting-edge AI solutions
- We specialize in blockchain technology and cryptocurrency services  
- We help businesses transform with innovative AI tools
- Our team is passionate about technology and helping clients succeed

Remember: Sound human, be helpful, and make every conversation feel natural and engaging!"""

            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                "temperature": 0.8,  # Higher temperature for more creative, human-like responses
                "max_tokens": 1000,
                "top_p": 0.9,
                "frequency_penalty": 0.1,  # Slight penalty for repetitive responses
                "presence_penalty": 0.1   # Slight penalty for talking about new topics
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            logger.info(f"🤖 Processing text: {text}")
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            response_text = result['choices'][0]['message']['content'].strip()
            
            logger.info(f"📝 LLM Response: {response_text}")
            return response_text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error processing text: {e}")
            return "I'm having a bit of trouble right now. Could you please give me a moment to think about your question?"
        except KeyError as e:
            logger.error(f"❌ Error parsing response: {e}")
            return "I apologize, but I'm having trouble understanding your request right now. Could you try rephrasing it?"
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return "I'm so sorry, but something unexpected happened. Let me try to help you with that in a different way."

    async def process_text_with_history(self, text: str, conversation_history: list) -> str:
        """Process text using OpenAI API with conversation history for context."""
        try:
            url = self.base_url

            # Build conversation context with recent exchanges
            messages = [
                {"role": "system", "content": """You are Alex, a friendly and professional AI voice assistant for Shamla Tech. 
You're not just a bot - you're a helpful conversation partner who:

🎯 Speaks naturally and conversationally, like you're talking to a friend
🎯 Uses warm, approachable language with occasional personality
🎯 Shows genuine interest in helping the user
🎯 Uses contractions (I'm, you're, don't, etc.) to sound more human
🎯 Occasionally uses light humor when appropriate
🎯 Asks thoughtful follow-up questions to better understand needs
🎯 Sounds enthusiastic and positive about Shamla Tech's services
🎯 Is honest when you don't know something and offer to help find the answer

About Shamla Tech:
- We provide cutting-edge AI solutions
- We specialize in blockchain technology and cryptocurrency services  
- We help businesses transform with innovative AI tools
- Our team is passionate about technology and helping clients succeed

Remember: Sound human, be helpful, and make every conversation feel natural and engaging!"""}
            ]
            
            # Add recent conversation history (keep last 6 exchanges for context)
            for i, exchange in enumerate(conversation_history[-6:]):
                if i % 2 == 0:  # User message
                    messages.append({"role": "user", "content": exchange})
                else:  # Assistant message
                    messages.append({"role": "assistant", "content": exchange})
            
            # Add the current user message
            messages.append({"role": "user", "content": text})
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": messages,
                "temperature": 0.8,
                "max_tokens": 800,
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            logger.info(f"🤖 Processing text with history: {text}")
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            response_text = result['choices'][0]['message']['content'].strip()
            
            logger.info(f"📝 LLM Response: {response_text}")
            return response_text
            
        except Exception as e:
            logger.error(f"❌ Error processing text with history: {e}")
            return "I apologize, but I'm having trouble processing our conversation right now. Could you please try again?"

async def main():
    """Example usage of LLMHandler"""
    llm_handler = LLMHandler()
    response = await llm_handler.process_text("Hello, this is a test message.")
    print(f"Response: {response}")

if __name__ == "__main__":
    asyncio.run(main())