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
            
            # Pre-process the input to handle common transcription variations
            processed_text = self._preprocess_transcription(text)
            
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

IMPORTANT TRANSCRIPTION GUIDELINES:
- If you hear variations of "Shamla Tech" like "Shambla Tech", "Shamla", "Shambla", etc., assume they mean Shamla Tech
- If you hear numbers that might be misheard words (like "blocked" instead of "about"), interpret based on context
- Be forgiving of minor pronunciation errors and focus on the user's intent
- If something sounds unclear, ask for clarification in a friendly way

Remember: Sound human, be helpful, and make every conversation feel natural and engaging!"""

            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": processed_text}
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
            
            # Post-process response to remove unwanted prefixes and clean up
            response_text = self._post_process_response(response_text)
            
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

            # Pre-process the input to handle common transcription variations
            processed_text = self._preprocess_transcription(text)
            
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

IMPORTANT TRANSCRIPTION GUIDELINES:
- If you hear variations of "Shamla Tech" like "Shambla Tech", "Shamla", "Shambla", etc., assume they mean Shamla Tech
- If you hear numbers that might be misheard words (like "blocked" instead of "about"), interpret based on context
- Be forgiving of minor pronunciation errors and focus on the user's intent
- If something sounds unclear, ask for clarification in a friendly way

Remember: Sound human, be helpful, and make every conversation feel natural and engaging!"""}
            ]
            
            # Add recent conversation history (keep last 6 exchanges for context)
            for i, exchange in enumerate(conversation_history[-6:]):
                if i % 2 == 0:  # User message
                    messages.append({"role": "user", "content": exchange})
                else:  # Assistant message
                    messages.append({"role": "assistant", "content": exchange})
            
            # Add the current user message (with pre-processing)
            messages.append({"role": "user", "content": processed_text})
            
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
            logger.info(f"🔧 Pre-processed text: {processed_text}")
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            response_text = result['choices'][0]['message']['content'].strip()
            
            # Post-process response to remove unwanted prefixes and clean up
            response_text = self._post_process_response(response_text)
            
            logger.info(f"📝 LLM Response: {response_text}")
            return response_text
            
        except Exception as e:
            logger.error(f"❌ Error processing text with history: {e}")
            return "I apologize, but I'm having trouble processing our conversation right now. Could you please try again?"

    def _preprocess_transcription(self, text: str) -> str:
        """Pre-process transcription to handle common variations and errors."""
        if not text:
            return text
        
        # Convert to lowercase for easier processing
        processed = text.lower()
        
        # Handle Shamla Tech variations
        shamla_variations = [
            "shambla tech", "shambla", "shamla tech", "shamla",
            "shambla technologies", "shamla technologies",
            "shambla", "shambla", "shambla", "shambla"  # Common mispronunciations
        ]
        
        for variation in shamla_variations:
            if variation in processed:
                processed = processed.replace(variation, "shamla tech")
                break
        
        # Handle common number/word confusions
        word_confusions = {
            "blocked": "about",
            "blacked": "about", 
            "blogged": "about",
            "wanna": "want to",
            "gonna": "going to",
            "sorta": "sort of",
            "lemme": "let me",
            "gimme": "give me",
            "hafta": "have to",
            "shoulda": "should have",
            "coulda": "could have",
            "woulda": "would have"
        }
        
        for wrong_word, correct_word in word_confusions.items():
            processed = processed.replace(wrong_word, correct_word)
        
        # Handle common company name variations
        company_variations = {
            "shambla": "shamla",
            "shambla tech": "shamla tech",
            "shambla technologies": "shamla tech"
        }
        
        for wrong, correct in company_variations.items():
            processed = processed.replace(wrong, correct)
        
        # Restore original casing while keeping the corrections
        # This is a simple approach - in production, you might want more sophisticated casing
        final_text = text
        for wrong, correct in company_variations.items():
            if wrong.lower() in text.lower():
                final_text = final_text.replace(wrong, correct)
        
        # Apply word confusions to original text
        for wrong_word, correct_word in word_confusions.items():
            if wrong_word in final_text.lower():
                final_text = final_text.replace(wrong_word, correct_word)
        
        return final_text.strip()

    def _post_process_response(self, response_text: str) -> str:
        """Post-process LLM response to remove unwanted prefixes and improve natural flow."""
        if not response_text:
            return response_text
        
        # Remove unwanted prefixes
        unwanted_prefixes = [
            "agent:",
            "agent: ",
            "agent - ",
            "assistant:",
            "assistant: ",
            "ai: ",
            "ai - ",
            "shamla tech agent:",
            "shamla tech agent: "
        ]
        
        cleaned_response = response_text
        for prefix in unwanted_prefixes:
            if cleaned_response.lower().startswith(prefix.lower()):
                cleaned_response = cleaned_response[len(prefix):].strip()
                break
        
        # Clean up multiple spaces and newlines
        cleaned_response = " ".join(cleaned_response.split())
        
        # Ensure the response starts with a capital letter
        if cleaned_response and cleaned_response[0].islower():
            cleaned_response = cleaned_response[0].upper() + cleaned_response[1:]
        
        return cleaned_response.strip()

async def main():
    """Example usage of LLMHandler"""
    llm_handler = LLMHandler()
    response = await llm_handler.process_text("Hello, this is a test message.")
    print(f"Response: {response}")

if __name__ == "__main__":
    asyncio.run(main())