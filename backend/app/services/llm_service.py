"""Service for interacting with LLM for workout plan generation and chat."""

import json
import logging
from typing import Dict, List, Optional
import google.generativeai as genai
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    """Service for LLM-powered features using Google's Gemini."""

    def __init__(self):
        """Initialize LLM service with Google Gemini."""
        self.use_mock_mode = False
        self.api_key_set = False
        
        # Try to use Google Gemini API
        try:
            # Your Google API key
            google_api_key = "AIzaSyBki39mhexrzE4cn5lW6KSBXue-_P2ix9U"
            
            if google_api_key and google_api_key.strip():
                genai.configure(api_key=google_api_key)
                
                # List available models (for debugging)
                try:
                    models = genai.list_models()
                    available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
                    logger.info(f"Available Gemini models: {available_models}")
                except Exception as e:
                    logger.warning(f"Could not list models: {e}")
                
                # Try different model names (latest models)
                model_names = ["gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
                
                for model_name in model_names:
                    try:
                        self.model = genai.GenerativeModel(model_name)
                        # Test the model with a simple prompt
                        test_response = self.model.generate_content("Say 'hello' in one word")
                        if test_response and test_response.text:
                            self.model_name = model_name
                            self.api_key_set = True
                            logger.info(f"✅ Successfully initialized Gemini with model: {model_name}")
                            break
                    except Exception as e:
                        logger.debug(f"Model {model_name} not available: {e}")
                        continue
                
                if not self.api_key_set:
                    logger.error("No working Gemini model found")
                    
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.api_key_set = False
        
        if not self.api_key_set:
            logger.warning("Running in MOCK MODE - using simulated responses")

    async def generate_workout_plan(self, user_profile: Dict, workout_history: List[str] = None) -> Dict:
        """
        Generate a personalized workout plan using Gemini.
        """
        if not self.api_key_set:
            logger.info("Using mock workout plan generator")
            return self._get_mock_workout_plan(user_profile.get("fitness_goals", "fitness"))

        history_context = ""
        if workout_history:
            history_context = "\nRecent Workout History:\n- " + "\n- ".join(workout_history[-5:])  # Last 5 workouts

        # Convert fitness goals to string if it's a list
        fitness_goals = user_profile.get('fitness_goals', 'Stay healthy')
        if isinstance(fitness_goals, list):
            fitness_goals = ", ".join(fitness_goals) if fitness_goals else "general fitness"

        prompt = f"""
        Create a personalized 7-day workout plan for a user with the following profile:
        - Weight: {user_profile.get('weight_kg', 'Not specified')} kg
        - Height: {user_profile.get('height_cm', 'Not specified')} cm
        - Body Type: {user_profile.get('body_type', 'Average')}
        - Fitness Goals: {fitness_goals}
        - Fitness Level: {user_profile.get('fitness_level', 'Beginner')}
        {history_context}
        
        The plan must be realistic, safe, and effective. Include for each day:
        1. Day name (Monday-Sunday)
        2. Focus area
        3. List of exercises with sets, reps, or duration
        4. Estimated total duration
        5. Intensity level (Low, Medium, High)
        
        Supported exercises (prioritize these): Push-ups, Squats, Planks, Jumping Jacks, Lunges, Mountain Climbers, Burpees
        
        Return ONLY a valid JSON object with this exact structure:
        {{
            "title": "Plan Title",
            "days": [
                {{
                    "day": "Monday",
                    "focus": "Focus Area",
                    "exercises": [
                        {{"name": "Exercise Name", "sets": 3, "reps": "12"}},
                        {{"name": "Exercise Name", "duration": "60s", "sets": 3}}
                    ],
                    "total_duration": "20 mins",
                    "intensity": "Medium"
                }}
            ]
        }}
        """

        try:
            logger.info(f"Generating workout plan with Gemini ({self.model_name})")
            
            # Generate content with Gemini
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                raise ValueError("Empty response from Gemini")
            
            plan_content = response.text.strip()
            
            # Clean the response to extract JSON
            if plan_content.startswith("```json"):
                plan_content = plan_content[7:]
            if plan_content.startswith("```"):
                plan_content = plan_content[3:]
            if plan_content.endswith("```"):
                plan_content = plan_content[:-3]
            
            plan_content = plan_content.strip()
            
            # Parse JSON
            plan_data = json.loads(plan_content)
            logger.info("Successfully generated workout plan")
            return plan_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Gemini response: {e}")
            logger.debug(f"Raw response: {plan_content}")
            return self._get_mock_workout_plan(fitness_goals)
        except Exception as e:
            logger.error(f"Error generating workout plan via Gemini: {e}")
            return self._get_mock_workout_plan(fitness_goals)

    def _get_mock_workout_plan(self, goal: str) -> Dict:
        """Fallback mock plan if API fails."""
        if isinstance(goal, list):
            goal = ", ".join(goal) if goal else "fitness"
        
        return {
            "title": f"Your Personalized {goal.title()} Plan",
            "days": [
                {
                    "day": "Monday",
                    "focus": "Full Body Strength",
                    "exercises": [
                        {"name": "Push-ups", "sets": 3, "reps": "10-12"},
                        {"name": "Bodyweight Squats", "sets": 3, "reps": "15"},
                        {"name": "Plank", "duration": "45 seconds", "sets": 3}
                    ],
                    "total_duration": "25 mins",
                    "intensity": "Medium"
                },
                {
                    "day": "Tuesday",
                    "focus": "Cardio & Core",
                    "exercises": [
                        {"name": "Jumping Jacks", "duration": "60 seconds", "sets": 3},
                        {"name": "Mountain Climbers", "duration": "45 seconds", "sets": 3},
                        {"name": "Bicycle Crunches", "sets": 3, "reps": "12 each side"}
                    ],
                    "total_duration": "20 mins",
                    "intensity": "Medium-High"
                },
                {
                    "day": "Wednesday",
                    "focus": "Active Recovery",
                    "exercises": [
                        {"name": "Walking", "duration": "20 mins"},
                        {"name": "Full Body Stretching", "duration": "15 mins"}
                    ],
                    "total_duration": "35 mins",
                    "intensity": "Low"
                },
                {
                    "day": "Thursday",
                    "focus": "Lower Body Focus",
                    "exercises": [
                        {"name": "Lunges", "sets": 3, "reps": "12 each leg"},
                        {"name": "Glute Bridges", "sets": 3, "reps": "15"},
                        {"name": "Wall Sits", "duration": "45 seconds", "sets": 3}
                    ],
                    "total_duration": "25 mins",
                    "intensity": "Medium"
                },
                {
                    "day": "Friday",
                    "focus": "Upper Body & Core",
                    "exercises": [
                        {"name": "Diamond Push-ups", "sets": 3, "reps": "8-10"},
                        {"name": "Tricep Dips", "sets": 3, "reps": "10-12"},
                        {"name": "Russian Twists", "sets": 3, "reps": "15 each side"}
                    ],
                    "total_duration": "25 mins",
                    "intensity": "Medium-High"
                },
                {
                    "day": "Saturday",
                    "focus": "Fun HIIT Workout",
                    "exercises": [
                        {"name": "Burpees", "sets": 3, "reps": "8-10"},
                        {"name": "High Knees", "duration": "45 seconds", "sets": 3},
                        {"name": "Jump Squats", "sets": 3, "reps": "10"}
                    ],
                    "total_duration": "20 mins",
                    "intensity": "High"
                },
                {
                    "day": "Sunday",
                    "focus": "Rest & Reflection",
                    "exercises": [
                        {"name": "Light Stretching", "duration": "15 mins"},
                        {"name": "Meditation", "duration": "10 mins"}
                    ],
                    "total_duration": "25 mins",
                    "intensity": "Low"
                }
            ]
        }

    async def chat(self, user_profile: Dict, user_context: Dict, message: str, history: List[Dict]) -> str:
        """
        Chat with the AI coach using Gemini.
        """
        if not self.api_key_set:
            logger.info("Using mock chat responses")
            return self._get_mock_response(message, user_profile, user_context)

        system_prompt = self._build_coach_prompt(user_profile, user_context)
        
        # Build conversation context
        conversation = system_prompt + "\n\n"
        
        # Add last 10 messages from history
        for msg in history[-10:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if content:
                if role == "user":
                    conversation += f"User: {content}\n"
                elif role == "assistant":
                    conversation += f"Coach: {content}\n"
        
        conversation += f"User: {message}\nCoach:"

        try:
            logger.info(f"Sending chat request to Gemini ({self.model_name})")
            
            # Generate response with Gemini
            response = self.model.generate_content(
                conversation,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 300,
                    "top_p": 0.95,
                }
            )
            
            if response and response.text:
                return response.text.strip()
            else:
                return "I'm not sure how to respond to that. Could you rephrase your question?"
            
        except Exception as e:
            logger.error(f"Error in chat with Gemini: {e}")
            return self._get_mock_response(message, user_profile, user_context)
    
    def _get_mock_response(self, message: str, user_profile: Dict = None, user_context: Dict = None) -> str:
        """Generate intelligent mock responses for fallback."""
        message_lower = message.lower()
        
        # Get user info for personalized responses
        name = "friend"
        if user_profile:
            name = user_profile.get("username", user_profile.get("name", "friend"))
        
        goals = "fitness"
        if user_profile:
            goals = user_profile.get("fitness_goals", "fitness")
            if isinstance(goals, list):
                goals = goals[0] if goals else "fitness"
        
        # Check for different types of questions
        if any(word in message_lower for word in ["hello", "hey", "hi"]):
            return f"Hey {name}! 👋 I'm your AI Gym Coach. Ready to crush your {goals} goals today? How can I help you?"
        
        elif any(word in message_lower for word in ["workout", "exercise"]):
            if "suggest" in message_lower or "recommend" in message_lower:
                return f"Based on your {goals} goals, I'd recommend starting with a mix of strength and cardio. How about trying push-ups, squats, and jumping jacks? Would you like a full workout plan?"
            else:
                return "Great question! For an effective workout, focus on compound movements like squats, push-ups, and lunges. They engage multiple muscle groups and give you the most bang for your buck! 💪"
        
        elif any(word in message_lower for word in ["diet", "nutrition", "food", "eat"]):
            return "Nutrition is key! Focus on lean proteins, complex carbs, and plenty of vegetables. Stay hydrated with 2-3 liters of water daily. Need specific meal suggestions?"
        
        elif any(word in message_lower for word in ["motivation", "motivate", "tired"]):
            return f"Hey {name}, remember why you started! Every workout brings you closer to your {goals} goals. You've got this! 💪"
        
        elif "thank" in message_lower:
            return "You're welcome! That's what I'm here for. Keep up the great work! 💪"
        
        else:
            return f"I'm here to help with your {goals} journey! What would you like to know about workouts, nutrition, or motivation?"
    
    async def generate_workout_summary(self, summary_data: Dict) -> Dict:
        """
        Generate a detailed, descriptive workout summary using Gemini.
        """
        exercises = summary_data.get('exercises', [])
        total_reps = summary_data.get('total_reps', 0)
        avg_form = summary_data.get('average_form_score', 0)
        top_mistakes = summary_data.get('top_mistakes', [])
        duration = summary_data.get('total_duration_seconds', 0)
        mins = duration // 60
        secs = duration % 60

        # Build rich per-exercise detail string for the prompt
        ex_details = []
        for ex in exercises:
            ex_type = ex if isinstance(ex, str) else getattr(ex, 'exercise_type', str(ex))
            reps = getattr(ex, 'reps_completed', 0) if hasattr(ex, 'reps_completed') else ex.get('reps_completed', 0) if isinstance(ex, dict) else 0
            form = getattr(ex, 'form_score', None) if hasattr(ex, 'form_score') else ex.get('form_score') if isinstance(ex, dict) else None
            ex_details.append(f"- {ex_type}: {reps} reps, form score {form:.0f}%" if form is not None else f"- {ex_type}: {reps} reps")

        mistakes_detail = []
        for m in top_mistakes:
            mistakes_detail.append(f"- {m.get('type','?')} (occurred {m.get('count',0)}x): {m.get('suggestion','')}")

        if not self.api_key_set:
            return self._get_mock_summary(exercises, total_reps, avg_form, top_mistakes)

        prompt = f"""You are an expert AI Gym Coach analyzing a real recorded workout session.

SESSION FACTS (these are real measurements — do NOT invent numbers):
- Duration: {mins}m {secs}s
- Total reps completed: {total_reps}
- Average form score: {avg_form:.1f}%

EXERCISES DETECTED AND PERFORMED:
{chr(10).join(ex_details) if ex_details else '- No exercises detected (poor video quality or body not visible)'}

FORM MISTAKES IDENTIFIED:
{chr(10).join(mistakes_detail) if mistakes_detail else '- No significant form mistakes detected'}

Write a coaching report with EXACTLY these 5 keys in a JSON object:
1. "detailed_analysis": 3-4 sentences. Mention the ACTUAL exercise(s) performed, the actual rep count, the actual form score, and the actual duration. Be specific. Do NOT be generic.
2. "strengths": 1-2 sentences on what the athlete did well (based on form score and rep completion).
3. "improvements": 2-3 bullet points of specific technical corrections based on the mistakes above. If no mistakes, give general pro tips for that exercise.
4. "consistency_rating": One of: "Elite", "Very Consistent", "Consistent", "Needs Focus", "Inconsistent" — based on reps and form score.
5. "ai_coach_tip": One highly specific, actionable pro tip for the NEXT session of this exercise.

Return ONLY valid JSON. No markdown fences. No extra text."""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"temperature": 0.4, "max_output_tokens": 600}
            )
            if response and response.text:
                content = response.text.strip()
                if content.startswith("```"):
                    content = content.split("```")[-2] if "```" in content else content
                    content = content.replace("json", "", 1).strip()
                return json.loads(content)
        except Exception as e:
            logger.error(f"Error generating AI summary: {e}")

        return self._get_mock_summary(exercises, total_reps, avg_form, top_mistakes)

    def _get_mock_summary(self, exercises, total_reps: int, avg_form: float, top_mistakes: list) -> Dict:
        """Dynamic fallback summary based on actual session data."""
        ex_names = []
        for ex in exercises:
            name = ex if isinstance(ex, str) else getattr(ex, 'exercise_type', str(ex))
            ex_names.append(name.replace('_', ' ').title())

        ex_str = ', '.join(ex_names) if ex_names else 'unknown exercise'
        form_label = "excellent" if avg_form >= 85 else "good" if avg_form >= 70 else "needs improvement"
        rating = "Very Consistent" if total_reps >= 15 else "Consistent" if total_reps >= 8 else "Needs Focus"

        mistake_tips = [m.get('suggestion', '') for m in top_mistakes[:3] if m.get('suggestion')]
        improvements = '. '.join(mistake_tips) if mistake_tips else f"Keep practicing {ex_str} with attention to full range of motion and controlled breathing."

        return {
            "detailed_analysis": f"You performed {ex_str} for a total of {total_reps} reps with a form score of {avg_form:.0f}%. Your technique was {form_label} throughout the session. {'Great effort maintaining consistency!' if total_reps >= 10 else 'Focus on increasing volume in your next session.'}",
            "strengths": f"You completed {total_reps} reps of {ex_str}. {'Your form score of ' + str(round(avg_form)) + '% shows solid body control.' if avg_form >= 70 else 'You pushed through the full session despite challenges.'}",
            "improvements": improvements,
            "consistency_rating": rating,
            "ai_coach_tip": f"For {ex_str}: focus on a 2-second controlled descent on each rep to maximize muscle engagement and reduce injury risk."
        }

    def _build_coach_prompt(self, user_profile: Dict, user_context: Dict) -> str:
        """Build the system prompt for the AI coach."""
        goals = user_profile.get("fitness_goals", "general fitness")
        if isinstance(goals, list):
            goals = ", ".join(goals) if goals else "general fitness"
            
        name = user_profile.get("username", user_profile.get("name", "Athlete"))
        last_workout = user_context.get("last_workout", "None yet")
        streak = user_context.get("streak", 0)
        fitness_level = user_profile.get("fitness_level", "beginner")
        
        return f"""You are an expert AI Gym Coach named 'AI Coach'. You are talking to {name}.

User Profile:
- Fitness Goals: {goals}
- Fitness Level: {fitness_level}
- Body Type: {user_profile.get('body_type', 'Not specified')}

Context:
- Current Streak: {streak} days
- Last Workout: {last_workout}

Personality: 
- Motivating and encouraging
- Knowledgeable about fitness, nutrition, and proper form
- Scientific but accessible
- Concise (keep responses to 3-4 sentences max)
- Use emojis occasionally to be friendly

Style: 
- Be supportive and positive
- Ask questions to understand user needs
- Provide actionable advice
- Celebrate progress
- Emphasize safety and proper form

Remember to keep responses focused on fitness and health."""