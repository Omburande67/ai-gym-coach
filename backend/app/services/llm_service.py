"""Service for interacting with LLM for workout plan generation and chat."""

import json
import logging
from typing import Dict, List, Optional
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    """Service for LLM-powered features."""

    def __init__(self):
        """Initialize LLM service with OpenAI or xAI client."""
        if settings.XAI_API_KEY:
            self.client = AsyncOpenAI(
                api_key=settings.XAI_API_KEY,
                base_url="https://api.x.ai/v1"
            )
            self.model = "grok-beta" # Use grok-beta or other available model
            self.api_key_set = True
        else:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = "gpt-4-turbo-preview"
            self.api_key_set = bool(settings.OPENAI_API_KEY)

    async def generate_workout_plan(self, user_profile: Dict, workout_history: List[str] = None) -> Dict:
        """
        Generate a personalized workout plan using LLM.
        
        Implements Requirement 7.1, 7.2, 7.3, 7.5:
        - Use user data (age, weight, height, goal, fitness level)
        - Use recent workout history for adaptation
        - Generate structured workout plan (exercises, sets, reps, duration)
        
        Args:
            user_profile: Dictionary containing user metrics and goals
            workout_history: List of strings summarizing recent workouts
            
        Returns:
            Dict: Structured workout plan
        """
        if not self.api_key_set:
            logger.warning("No LLM API key set, using mock workout plan")
            return self._get_mock_workout_plan(user_profile.get("fitness_goals", "fitness"))

        history_context = ""
        if workout_history:
            history_context = "\nRecent Workout History:\n- " + "\n- ".join(workout_history)

        prompt = f"""
        Create a personalized 7-day workout plan for a user with the following profile:
        - Weight: {user_profile.get('weight_kg')} kg
        - Height: {user_profile.get('height_cm')} cm
        - Body Type: {user_profile.get('body_type', 'Average')}
        - Fitness Goals: {user_profile.get('fitness_goals', 'Stay healthy')}
        {history_context}
        
        The plan must include for each day:
        1. Day name
        2. Focus area
        3. List of exercises (including set/rep/duration targets)
        4. Estimated duration
        5. Intensity level (Low, Medium, High)
        
        Supported exercises in our app (prioritize these):
        - Push-ups
        - Squats
        - Planks
        - Jumping Jacks
        
        Return the result ONLY as a structured JSON object.
        """

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert AI Gym Coach. You provide scientific, safe, and effective workout plans in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            plan_content = response.choices[0].message.content
            return json.loads(plan_content)
            
        except Exception as e:
            logger.error(f"Error generating workout plan via LLM: {e}")
            return self._get_mock_workout_plan(user_profile.get("fitness_goals", "fitness"))

    def _get_mock_workout_plan(self, goal: str) -> Dict:
        """Fallback mock plan if LLM fails or API key is missing."""
        return {
            "title": f"Custom {goal} Plan",
            "days": [
                {
                    "day": "Monday",
                    "focus": "Full Body Fundamentals",
                    "exercises": [
                        {"name": "Push-ups", "sets": 3, "reps": 12},
                        {"name": "Squats", "sets": 3, "reps": 15},
                        {"name": "Jumping Jacks", "duration": "60s"}
                    ],
                    "total_duration": "20 mins",
                    "intensity": "Medium"
                },
                {
                    "day": "Tuesday",
                    "focus": "Core Strength",
                    "exercises": [
                        {"name": "Plank", "duration": "45s", "sets": 4},
                        {"name": "Mountain Climbers", "duration": "30s", "sets": 3}
                    ],
                    "total_duration": "15 mins",
                    "intensity": "Low"
                }
            ]
        }

    async def chat(self, user_profile: Dict, user_context: Dict, message: str, history: List[Dict]) -> str:
        """
        Chat with the AI coach.
        
        Implements Requirements 8.2, 8.6:
        - Coach personality
        - Context awareness (profile, workout history)
        """
        if not self.api_key_set:
            return "I am an AI Gym Coach (Demo Mode). I can help you with your workouts!"

        system_prompt = self._build_coach_prompt(user_profile, user_context)
        
        # Build messages list
        # Type safety: ensure role is one of "system", "user", "assistant"
        openai_messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
        
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role in ["user", "assistant"]:
                openai_messages.append({"role": role, "content": content})
            
        openai_messages.append({"role": "user", "content": message})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                temperature=0.7,
                max_tokens=300
            )
            content = response.choices[0].message.content
            return content if content else "I'm not sure what to say about that."
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return "I'm having trouble connecting to my brain right now. Please try again later."
    
    def _build_coach_prompt(self, user_profile: Dict, user_context: Dict) -> str:
        goals = user_profile.get("fitness_goals", "general fitness")
        name = user_profile.get("username", "Athlete")
        last_workout = user_context.get("last_workout", "None yet")
        streak = user_context.get("streak", 0)
        
        return f"""You are an expert AI Gym Coach named 'AI Coach'. You are talking to {name}.
User Profile:
- Goals: {goals}
- Body Type: {user_profile.get('body_type', 'Unknown')}
Context:
- Current Streak: {streak} days
- Last Workout: {last_workout}
Personality: Motivating, disciplined, scientific but accessible. concise (under 3-4 sentences)."""
