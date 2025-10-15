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
    """Handles text processing using Gemini API."""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            logger.error("❌ GEMINI_API_KEY not found in environment variables.")
            raise ValueError("API key is required for LLM functionality.")
        
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent"
        logger.info("🤖 LLM Handler initialized with Gemini API.")
    
    async def process_text(self, text: str) -> str:
        """Process text using Gemini API and return response."""
        try:
            url = f"{self.base_url}?key={self.api_key}"
            
            # System prompt to define the AI voice calling agent role
            system_prompt = """You are an AI voice calling agent for Shamla Tech, a company that provides AI, blockchain, and cryptocurrency services. 
Your role is to:
1. Be professional, friendly, and helpful
2. Provide accurate information about Shamla Tech's services
3. Answer questions about AI, blockchain, and cryptocurrency solutions
4. Be concise and clear in your responses
5. Maintain a helpful and engaging tone
6. If you don't know something, be honest and offer to connect with a human representative

Remember: You are representing Shamla Tech, so maintain a professional and helpful demeanor at all times."""

            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"{system_prompt}\n\nUser: {text}\nAI Voice Agent:"
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 2048
                }
            }
            
            logger.info(f"🤖 Processing text: {text}")
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            response_text = result['candidates'][0]['content']['parts'][0]['text']
            
            logger.info(f"📝 LLM Response: {response_text}")
            return response_text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error processing text: {e}")
            return "Sorry, I encountered an error while processing your request."
        except KeyError as e:
            logger.error(f"❌ Error parsing response: {e}")
            return "Sorry, I received an unexpected response from the API."

    async def process_text_with_history(self, text: str, conversation_history: list) -> str:
        """Process text using Gemini API with conversation history."""
        try:
            # Create the conversation context
            context = "\n".join(conversation_history[-6:])  # Keep last 6 exchanges for context
            
            url = f"{self.base_url}?key={self.api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"""Context: {context}

User: {text}

Please respond as a professional AI voice calling agent for Shamla Tech. Shamla Tech provides AI, blockchain, and cryptocurrency services. Be helpful, informative, and professional. Ask clarifying questions if needed.

AI Response:"""
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 500
                }
            }
            
            logger.info(f"🤖 Processing text with history: {text}")
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            response_text = result['candidates'][0]['content']['parts'][0]['text']
            
            logger.info(f"📝 LLM Response: {response_text}")
            return response_text
            
        except Exception as e:
            logger.error(f"❌ Error processing text with history: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Could you please try again?"

async def main():
    """Example usage of LLMHandler"""
    llm_handler = LLMHandler()
    response = await llm_handler.process_text("Hello, this is a test message.")
    print(f"Response: {response}")

if __name__ == "__main__":
    asyncio.run(main())