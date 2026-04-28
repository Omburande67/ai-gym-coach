# app/api/chat.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from groq import Groq
import os
from dotenv import load_dotenv
from typing import List, Dict, Any

# Load environment variables from .env file
load_dotenv()

router = APIRouter()

# Initialize the Groq client
# It will automatically read your key from the GROQ_API_KEY environment variable
client = Groq()

# Define the request and response models for your API
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@router.post("/message", response_model=ChatResponse)
async def chat_message(chat_request: ChatRequest):
    """
    Receives a user's message and returns a response from the Groq AI model.
    """
    user_message = chat_request.message

    # --- Optional: Create a system prompt to guide the AI ---
    # This helps the AI act as a fitness coach.
    system_prompt = {
        "role": "system",
        "content": "You are 'AI Coach', an enthusiastic and knowledgeable personal trainer. \
                    You provide helpful, concise, and safe advice on exercise, form, \
                    and fitness motivation. Keep your answers under 100 words."
    }

    user_prompt = {
        "role": "user",
        "content": user_message
    }

    try:
        # Send the conversation to Groq
        # The 'llama-3.3-70b-versatile' model is a great, fast, free option [citation:5][citation:9]
        chat_completion = client.chat.completions.create(
            messages=[system_prompt, user_prompt],
            model="llama-3.3-70b-versatile",  # You can also try "llama-3.1-8b-instant" for even faster responses
            temperature=0.7,  # Controls creativity (0-2, lower is more deterministic)
            max_tokens=200,   # Limits the length of the response
        )

        # Extract the AI's response
        ai_response = chat_completion.choices[0].message.content

        return ChatResponse(response=ai_response)

    except Exception as e:
        print(f"Error calling Groq API: {e}")
        # Return a friendly fallback message to the user if the API call fails
        return ChatResponse(response="I'm having trouble connecting right now. Please try again in a moment.")
