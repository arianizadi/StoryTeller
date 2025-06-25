import json
import requests
import asyncio
import websockets
import ssl
import os
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from io import BytesIO
import base64
from config import RATE_LIMITS

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
    print("🔧 DEBUG: Successfully loaded .env file")
except ImportError:
    print(
        "❌ DEBUG: python-dotenv not installed. Install with: pip install python-dotenv"
    )
    print("Or set environment variables manually.")

# Audio playback libraries (optional - for real-time playback)
try:
    from pydub import AudioSegment
    from pydub.playback import play

    AUDIO_AVAILABLE = True
    print("🔧 DEBUG: Audio playback libraries available")
except ImportError:
    AUDIO_AVAILABLE = False
    print(
        "⚠️ DEBUG: Audio playback not available. Install pydub and simpleaudio for audio playback."
    )


@dataclass
class Character:
    """Represents a character in the story with voice settings"""

    name: str
    description: str
    voice_id: str
    speed: float = 1.0
    volume: float = 1.0
    pitch: float = 0.0
    emotion: str = "neutral"  # Only used for WebSocket API


@dataclass
class StorySegment:
    """Represents a segment of the story with character dialogue"""

    character: Optional[Character]
    text: str
    audio_file: Optional[str] = None


class RateLimiter:
    """Simple rate limiter to prevent hitting API limits"""

    def __init__(self, requests_per_minute: int = 50):
        self.requests_per_minute = requests_per_minute
        self.request_times = []
        self.min_interval = (
            60.0 / requests_per_minute
        )  # Minimum seconds between requests

    def wait_if_needed(self):
        """Wait if we need to respect rate limits"""
        current_time = time.time()

        # Remove old requests (older than 1 minute)
        self.request_times = [t for t in self.request_times if current_time - t < 60.0]

        # If we've made too many requests recently, wait
        if len(self.request_times) >= self.requests_per_minute:
            oldest_request = min(self.request_times)
            wait_time = (
                60.0 - (current_time - oldest_request) + 1.0
            )  # Add 1 second buffer
            if wait_time > 0:
                print(f"⏳ Rate limit protection: Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
                current_time = time.time()

        # Add current request
        self.request_times.append(current_time)

        # Ensure minimum interval between requests
        if self.request_times and len(self.request_times) > 1:
            time_since_last = current_time - self.request_times[-2]
            if time_since_last < self.min_interval:
                wait_time = self.min_interval - time_since_last
                print(
                    f"⏳ Rate limit protection: Waiting {wait_time:.1f} seconds between requests..."
                )
                time.sleep(wait_time)


class MiniMaxStoryTeller:
    """Main class for generating stories and audio using MiniMax API"""

    # Model configuration for cost optimization
    MODELS = {
        "story_generation": "MiniMax-M1",  # Thinking model for creative story generation
        "name_analysis": "MiniMax-Text-01",  # Faster, cheaper model for name analysis
        "simple_tasks": "MiniMax-Text-01",  # For any other simple AI tasks
    }

    # Cost tracking (official MiniMax pricing per 1M tokens)
    MODEL_COSTS = {
        "MiniMax-M1": {
            "input": 0.4,  # $0.4 per 1M tokens (if input ≤200K tokens)
            "output": 2.2,  # $2.2 per 1M tokens
            "description": "Top-Tier Model: 80K CoT Length x 1M Input",
        },
        "MiniMax-Text-01": {
            "input": 0.2,  # $0.2 per 1M tokens
            "output": 1.1,  # $1.1 per 1M tokens
            "description": "Text model, new model architecture, 1000k content length",
        },
        "speech-02-hd": {
            "per_character": 0.0001,  # $100/M characters = $0.0001 per character
            "description": "HD model with superior rhythm and stability",
        },
        "speech-02-turbo": {
            "per_character": 0.00006,  # $60/M characters = $0.00006 per character
            "description": "Turbo model with enhanced multilingual capabilities",
        },
    }

    def __init__(self, api_key: str, group_id: str):
        print(f"🔧 DEBUG: Initializing MiniMaxStoryTeller")
        print(f"🔧 DEBUG: API Key length: {len(api_key) if api_key else 0}")
        print(f"🔧 DEBUG: Group ID: {group_id}")

        self.api_key = api_key
        self.group_id = group_id
        self.chat_url = "https://api.minimax.io/v1/text/chatcompletion_v2"
        self.tts_url = f"https://api.minimax.io/v1/t2a_v2?GroupId={group_id}"
        self.ws_url = "wss://api.minimax.io/ws/v1/t2a_v2"

        print(f"🔧 DEBUG: Chat URL: {self.chat_url}")
        print(f"🔧 DEBUG: TTS URL: {self.tts_url}")
        print(f"🔧 DEBUG: WebSocket URL: {self.ws_url}")

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        print(
            f"🔧 DEBUG: Headers configured with Authorization: Bearer {api_key[:10]}..."
        )

        # Initialize rate limiters
        self.chat_limiter = RateLimiter(requests_per_minute=RATE_LIMITS["chat_rpm"])
        self.tts_limiter = RateLimiter(requests_per_minute=RATE_LIMITS["tts_rpm"])
        self.retry_delay = RATE_LIMITS["retry_delay"]
        self.max_retries = RATE_LIMITS["max_retries"]

        # Default characters with rich personalities and unique voices
        self.characters = {
            "narrator": Character(
                "Narrator",
                "A wise storyteller with a warm, engaging voice who brings the world to life with vivid descriptions",
                "English_expressive_narrator",
                1.0,
                1.0,
                0.0,
                "calm",
            ),
            "hero": Character(
                "Hero",
                "A courageous protagonist with a heart of gold, facing inner doubts and external challenges with determination and growth",
                "English_magnetic_voiced_man",
                1.0,
                1.0,
                0.0,
                "brave",
            ),
            "villain": Character(
                "Villain",
                "A complex antagonist with layers of motivation, not purely evil but driven by pain, fear, or misguided beliefs",
                "English_ManWithDeepVoice",
                0.8,
                1.0,
                -0.3,
                "sinister",
            ),
            "friend": Character(
                "Friend",
                "A loyal companion who provides emotional support, wisdom, and sometimes tough love when needed",
                "English_radiant_girl",
                1.1,
                1.0,
                0.2,
                "friendly",
            ),
        }

        print(f"🔧 DEBUG: Initialized {len(self.characters)} default characters")
        for name, char in self.characters.items():
            print(f"   - {name}: {char.name} (voice: {char.voice_id})")

        self.story_segments = []
        self.current_story = ""

        # Initialize voice mapping cache
        self.name_voice_cache = {}

        print("🔧 DEBUG: MiniMaxStoryTeller initialization complete")

    def add_character(self, character: Character):
        """Add a new character to the story"""
        print(f"🔧 DEBUG: Adding character: {character.name}")
        print(
            f"🔧 DEBUG: Character details - Voice: {character.voice_id}, Speed: {character.speed}, Volume: {character.volume}, Pitch: {character.pitch}"
        )

        self.characters[character.name.lower()] = character
        print(f"✅ Added character: {character.name}")
        print(f"🔧 DEBUG: Total characters now: {len(self.characters)}")

    def generate_story_prompt(
        self, genre: str, theme: str, characters: List[str], length: str = "medium"
    ) -> str:
        """Generate a story prompt for the AI"""
        print(f"🔧 DEBUG: Generating story prompt")
        print(f"🔧 DEBUG: Genre: {genre}")
        print(f"🔧 DEBUG: Theme: {theme}")
        print(f"🔧 DEBUG: Characters: {characters}")
        print(f"🔧 DEBUG: Length: {length}")

        character_descriptions = []
        for char_name in characters:
            if char_name.lower() in self.characters:
                char = self.characters[char_name.lower()]
                character_descriptions.append(f"{char.name}: {char.description}")
                print(f"🔧 DEBUG: Added character description for {char.name}")
            else:
                print(
                    f"⚠️ DEBUG: Character '{char_name}' not found in available characters"
                )

        # For engaging stories, use 100 words
        word_limit = 100 if length == "medium" else 100  # Reduced for shorter stories

        prompt = f"""Create an engaging {genre} story about {theme} with approximately {word_limit} words.

Characters: {', '.join(character_descriptions)}

Story Requirements:
- Give each character a memorable, realistic name that fits their personality
- Create emotional depth and character development
- Include meaningful dialogue that reveals character traits
- Build tension and conflict that drives the plot
- Create moments of vulnerability and growth
- End with a satisfying resolution that shows character growth
- Make readers care about what happens to the characters

**CRITICAL FORMATTING RULES:**
- Each line must start with the character's name followed by a colon and a space
- Give characters realistic names (like "Kael", "Elara", "Marcus", "Luna", etc.)
- Use "Narrator" for narrative descriptions
- Do NOT use parentheses, stage directions, or any formatting
- Do NOT embed dialogue inside narration
- Do NOT use bold, italics, or markdown
- Example format:
Narrator: The sun rose over the valley.
Kael: I must find the ancient treasure!
Elara: Be careful, Kael!
Voryn: The treasure belongs to me!

Make this a compelling story that readers will remember and care about. Focus on character relationships, emotional stakes, and meaningful growth. Give each character a distinct voice and personality that comes through in their dialogue."""

        print(f"🔧 DEBUG: Generated prompt length: {len(prompt)} characters")
        print(f"🔧 DEBUG: Prompt preview: {prompt[:200]}...")

        return prompt

    def make_api_call(
        self,
        model_type: str,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> dict:
        """Make an API call with the specified model type"""
        model = self.MODELS.get(model_type, self.MODELS["simple_tasks"])

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

        print(f"🔧 DEBUG: Making API call with model: {model} (type: {model_type})")
        print(
            f"🔧 DEBUG: Cost optimization: Using {'thinking model' if model_type == 'story_generation' else 'faster/cheaper model'}"
        )

        # Initialize cost tracking if not exists
        if not hasattr(self, "api_usage_stats"):
            self.api_usage_stats = {
                "total_calls": 0,
                "total_tokens": 0,
                "estimated_cost": 0.0,
                "calls_by_model": {},
                "tokens_by_model": {},
            }

        # Apply rate limiting for chat completion
        self.chat_limiter.wait_if_needed()

        response = requests.post(self.chat_url, headers=self.headers, json=payload)

        # Check for rate limit errors
        if response.status_code == 429:
            print(
                f"⚠️ Rate limit exceeded. Waiting {self.retry_delay} seconds before retry..."
            )
            time.sleep(self.retry_delay)
            # Retry once
            self.chat_limiter.wait_if_needed()
            response = requests.post(self.chat_url, headers=self.headers, json=payload)
            print(f"🔧 DEBUG: Retry response status code: {response.status_code}")

        response.raise_for_status()
        result = response.json()

        # Track usage and costs
        self.api_usage_stats["total_calls"] += 1
        self.api_usage_stats["calls_by_model"][model] = (
            self.api_usage_stats["calls_by_model"].get(model, 0) + 1
        )

        if "usage" in result:
            prompt_tokens = result["usage"].get("prompt_tokens", 0)
            completion_tokens = result["usage"].get("completion_tokens", 0)
            total_tokens = result["usage"].get("total_tokens", 0)

            self.api_usage_stats["total_tokens"] += total_tokens
            self.api_usage_stats["tokens_by_model"][model] = (
                self.api_usage_stats["tokens_by_model"].get(model, 0) + total_tokens
            )

            # Calculate estimated cost based on new pricing structure
            estimated_cost = 0.0
            if model in self.MODEL_COSTS and isinstance(self.MODEL_COSTS[model], dict):
                model_costs = self.MODEL_COSTS[model]
                if "input" in model_costs and "output" in model_costs:
                    # Text model pricing (per 1M tokens)
                    input_cost = (prompt_tokens / 1_000_000) * model_costs["input"]
                    output_cost = (completion_tokens / 1_000_000) * model_costs[
                        "output"
                    ]
                    estimated_cost = input_cost + output_cost
                elif "per_character" in model_costs:
                    # TTS pricing (per character)
                    estimated_cost = total_tokens * model_costs["per_character"]
            else:
                # Fallback for unknown models
                estimated_cost = (
                    total_tokens / 1_000_000
                ) * 0.5  # Default $0.5 per 1M tokens

            self.api_usage_stats["estimated_cost"] += estimated_cost

            print(
                f"🔧 DEBUG: Tokens used: {total_tokens} (prompt: {prompt_tokens}, completion: {completion_tokens})"
            )
            print(f"🔧 DEBUG: Estimated cost: ${estimated_cost:.6f}")
            print(
                f"🔧 DEBUG: Total usage - Calls: {self.api_usage_stats['total_calls']}, Tokens: {self.api_usage_stats['total_tokens']}, Cost: ${self.api_usage_stats['estimated_cost']:.6f}"
            )

        return result

    def get_usage_statistics(self) -> dict:
        """Get current API usage statistics and cost breakdown"""
        if not hasattr(self, "api_usage_stats"):
            return {
                "total_calls": 0,
                "total_tokens": 0,
                "estimated_cost": 0.0,
                "calls_by_model": {},
                "tokens_by_model": {},
                "cost_breakdown": {},
            }

        # Calculate cost breakdown by model
        cost_breakdown = {}
        for model, tokens in self.api_usage_stats["tokens_by_model"].items():
            if model in self.MODEL_COSTS and isinstance(self.MODEL_COSTS[model], dict):
                model_costs = self.MODEL_COSTS[model]
                if "input" in model_costs and "output" in model_costs:
                    # Text model pricing - estimate 70% input, 30% output
                    input_tokens = int(tokens * 0.7)
                    output_tokens = tokens - input_tokens
                    input_cost = (input_tokens / 1_000_000) * model_costs["input"]
                    output_cost = (output_tokens / 1_000_000) * model_costs["output"]
                    cost = input_cost + output_cost
                    cost_breakdown[model] = {
                        "tokens": tokens,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "cost": cost,
                        "input_cost_per_1m": model_costs["input"],
                        "output_cost_per_1m": model_costs["output"],
                        "description": model_costs.get("description", "Unknown model"),
                    }
                elif "per_character" in model_costs:
                    # TTS pricing
                    cost = tokens * model_costs["per_character"]
                    cost_breakdown[model] = {
                        "characters": tokens,
                        "cost": cost,
                        "cost_per_character": model_costs["per_character"],
                        "description": model_costs.get(
                            "description", "Unknown TTS model"
                        ),
                    }
            else:
                # Fallback for unknown models
                cost = (tokens / 1_000_000) * 0.5
                cost_breakdown[model] = {
                    "tokens": tokens,
                    "cost": cost,
                    "cost_per_1m": 0.5,
                    "description": "Unknown model (estimated pricing)",
                }

        stats = self.api_usage_stats.copy()
        stats["cost_breakdown"] = cost_breakdown
        return stats

    def print_usage_summary(self):
        """Print a summary of API usage and costs"""
        stats = self.get_usage_statistics()

        print("\n" + "=" * 60)
        print("📊 API USAGE SUMMARY")
        print("=" * 60)
        print(f"Total API calls: {stats['total_calls']}")
        print(f"Total tokens used: {stats['total_tokens']:,}")
        print(f"Estimated total cost: ${stats['estimated_cost']:.4f}")
        print("\n📈 Breakdown by Model:")

        for model, breakdown in stats["cost_breakdown"].items():
            calls = stats["calls_by_model"].get(model, 0)
            print(f"  {model}:")
            print(f"    Calls: {calls}")
            print(f"    Description: {breakdown.get('description', 'Unknown')}")

            if "tokens" in breakdown:
                print(f"    Tokens: {breakdown['tokens']:,}")
                if "input_tokens" in breakdown and "output_tokens" in breakdown:
                    print(f"      Input: {breakdown['input_tokens']:,} tokens")
                    print(f"      Output: {breakdown['output_tokens']:,} tokens")
                print(f"    Cost: ${breakdown['cost']:.6f}")
                if "input_cost_per_1m" in breakdown:
                    print(
                        f"    Input cost: ${breakdown['input_cost_per_1m']:.3f}/1M tokens"
                    )
                    print(
                        f"    Output cost: ${breakdown['output_cost_per_1m']:.3f}/1M tokens"
                    )
            elif "characters" in breakdown:
                print(f"    Characters: {breakdown['characters']:,}")
                print(f"    Cost: ${breakdown['cost']:.6f}")
                print(f"    Cost per character: ${breakdown['cost_per_character']:.6f}")

        print("\n💰 Cost Optimization:")
        if stats["cost_breakdown"]:
            most_expensive = max(
                stats["cost_breakdown"].items(), key=lambda x: x[1]["cost"]
            )
            most_used = max(stats["calls_by_model"].items(), key=lambda x: x[1])

            print(
                f"  Most expensive model: {most_expensive[0]} (${most_expensive[1]['cost']:.6f})"
            )
            print(f"  Most used model: {most_used[0]} ({most_used[1]} calls)")

            # Calculate savings if using cheaper models
            if "MiniMax-M1" in stats["cost_breakdown"]:
                m1_cost = stats["cost_breakdown"]["MiniMax-M1"]["cost"]
                m1_tokens = stats["cost_breakdown"]["MiniMax-M1"]["tokens"]
                # Estimate savings using MiniMax-Text-01
                cheaper_input_cost = (m1_tokens * 0.7 / 1_000_000) * self.MODEL_COSTS[
                    "MiniMax-Text-01"
                ]["input"]
                cheaper_output_cost = (m1_tokens * 0.3 / 1_000_000) * self.MODEL_COSTS[
                    "MiniMax-Text-01"
                ]["output"]
                cheaper_cost = cheaper_input_cost + cheaper_output_cost
                savings = m1_cost - cheaper_cost
                print(f"  Potential savings using MiniMax-Text-01: ${savings:.6f}")

        print("=" * 60)

    def generate_story(
        self, genre: str, theme: str, characters: List[str], length: str = "medium"
    ) -> str:
        """Generate a story using MiniMax chat completion"""
        print(f"🔧 DEBUG: Starting story generation")
        print(
            f"🔧 DEBUG: Parameters - Genre: {genre}, Theme: {theme}, Characters: {characters}, Length: {length}"
        )

        prompt = self.generate_story_prompt(genre, theme, characters, length)

        messages = [
            {
                "role": "system",
                "content": "You are a master storyteller who creates emotionally engaging, character-driven stories with deep plots, memorable characters, and meaningful growth. Your stories make readers care deeply about the characters and their journeys.",
            },
            {"role": "user", "content": prompt},
        ]

        try:
            result = self.make_api_call(
                "story_generation", messages, temperature=0.8, max_tokens=8000
            )

            print(
                f"🔧 DEBUG: API response keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}"
            )
            print(
                f"🔧 DEBUG: Full API response structure: {json.dumps(result, indent=2)}"
            )

            if "choices" in result and len(result["choices"]) > 0:
                choice = result["choices"][0]
                print(
                    f"🔧 DEBUG: First choice keys: {list(choice.keys()) if isinstance(choice, dict) else 'Not a dict'}"
                )

                if "message" in choice:
                    message = choice["message"]
                    print(
                        f"🔧 DEBUG: Message keys: {list(message.keys()) if isinstance(message, dict) else 'Not a dict'}"
                    )

                    # Check if we hit token limit
                    finish_reason = choice.get("finish_reason", "")
                    print(f"🔧 DEBUG: Finish reason: {finish_reason}")

                    if "content" in message:
                        story = message["content"]
                        print(f"🔧 DEBUG: Story extracted from message.content")
                        print(f"🔧 DEBUG: Story length: {len(story)} characters")
                        print(f"🔧 DEBUG: Story word count: {len(story.split())} words")
                        print(f"🔧 DEBUG: Story preview: {story[:200]}...")

                        if story.strip():  # Check if story is not empty
                            self.current_story = story
                            return story
                        else:
                            print(
                                f"❌ DEBUG: Story content is empty or whitespace only"
                            )
                            print(f"🔧 DEBUG: Raw story content: '{story}'")

                            # Try to extract from reasoning_content as fallback
                            if "reasoning_content" in message:
                                reasoning = message["reasoning_content"]
                                print(
                                    f"🔧 DEBUG: Found reasoning_content, length: {len(reasoning)}"
                                )
                                print(
                                    f"🔧 DEBUG: Reasoning preview: {reasoning[:200]}..."
                                )

                                # Look for the final story in reasoning content
                                if "NARRATOR:" in reasoning or "HERO:" in reasoning:
                                    # Extract the story part from reasoning
                                    story_start = max(
                                        reasoning.find("NARRATOR:"),
                                        reasoning.find("HERO:"),
                                        reasoning.find("VILLAIN:"),
                                        reasoning.find("FRIEND:"),
                                        reasoning.find("WIZARD:"),
                                    )
                                    if story_start != -1:
                                        extracted_story = reasoning[
                                            story_start:
                                        ].strip()
                                        print(
                                            f"🔧 DEBUG: Extracted story from reasoning_content"
                                        )
                                        print(
                                            f"🔧 DEBUG: Extracted story length: {len(extracted_story)}"
                                        )
                                        self.current_story = extracted_story
                                        return extracted_story

                            if finish_reason == "length":
                                print(
                                    f"❌ DEBUG: Hit token limit before completing story"
                                )
                                raise Exception(
                                    "Story generation hit token limit - try reducing story length or simplifying prompt"
                                )
                            else:
                                raise Exception("Story content is empty")
                    else:
                        print(f"❌ DEBUG: No 'content' key in message")
                        print(f"🔧 DEBUG: Message content: {message}")
                        raise Exception("No content in message")
                else:
                    print(f"❌ DEBUG: No 'message' key in choice")
                    print(f"🔧 DEBUG: Choice content: {choice}")
                    raise Exception("No message in choice")
            else:
                print(f"❌ DEBUG: No choices in API response")
                print(f"🔧 DEBUG: Full API response: {result}")
                raise Exception("No story generated")

        except requests.exceptions.RequestException as e:
            print(f"❌ DEBUG: Request error: {e}")
            print(
                f"🔧 DEBUG: Response content: {getattr(e.response, 'content', 'No response content')}"
            )
            return None
        except Exception as e:
            print(f"❌ DEBUG: Error generating story: {e}")
            print(f"🔧 DEBUG: Exception type: {type(e)}")
            return None

    def analyze_character_name_with_ai(self, char_name: str) -> dict:
        """Use AI to analyze a character name and determine its characteristics"""
        print(f"🔧 DEBUG: Analyzing character name '{char_name}' with AI")

        # Check if we've already analyzed this name
        if not hasattr(self, "name_analysis_cache"):
            self.name_analysis_cache = {}

        if char_name.lower() in self.name_analysis_cache:
            print(f"🔧 DEBUG: Using cached analysis for '{char_name}'")
            return self.name_analysis_cache[char_name.lower()]

        # Create analysis prompt
        analysis_prompt = f"""Analyze the character name "{char_name}" and provide the following information in JSON format:

{{
    "gender": "male/female/neutral/unknown",
    "age_group": "child/young_adult/adult/elder/unknown", 
    "personality_trait": "heroic/friendly/villainous/wise/mysterious/neutral",
    "voice_type": "masculine/feminine/neutral/deep/soft/wise",
    "confidence": 0.0-1.0
}}

Consider:
- Name origins and cultural associations
- Sound patterns and phonetics
- Common name associations
- Fantasy/sci-fi naming conventions

Respond with ONLY the JSON object, no additional text."""

        messages = [
            {
                "role": "system",
                "content": "You are a name analysis expert. Analyze character names and provide structured information about their likely characteristics. Respond only with valid JSON.",
            },
            {"role": "user", "content": analysis_prompt},
        ]

        try:
            result = self.make_api_call(
                "name_analysis", messages, temperature=0.3, max_tokens=200
            )

            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                print(f"🔧 DEBUG: AI analysis response: {content}")

                # Parse JSON response
                try:
                    import json

                    analysis = json.loads(content.strip())

                    # Validate required fields
                    required_fields = [
                        "gender",
                        "age_group",
                        "personality_trait",
                        "voice_type",
                        "confidence",
                    ]
                    for field in required_fields:
                        if field not in analysis:
                            analysis[field] = (
                                "unknown" if field != "confidence" else 0.5
                            )

                    # Cache the result
                    self.name_analysis_cache[char_name.lower()] = analysis

                    print(
                        f"🔧 DEBUG: AI analysis complete for '{char_name}': {analysis}"
                    )
                    return analysis

                except json.JSONDecodeError as e:
                    print(f"⚠️ DEBUG: Failed to parse AI analysis JSON: {e}")
                    print(f"🔧 DEBUG: Raw response: {content}")
                    return self.fallback_name_analysis(char_name)
            else:
                print(f"⚠️ DEBUG: No choices in AI analysis response")
                return self.fallback_name_analysis(char_name)

        except Exception as e:
            print(f"⚠️ DEBUG: Error during AI name analysis: {e}")
            return self.fallback_name_analysis(char_name)

    def fallback_name_analysis(self, char_name: str) -> dict:
        """Fallback name analysis using pattern matching when AI is unavailable"""
        char_name_lower = char_name.lower()

        # Simple pattern-based analysis
        analysis = {
            "gender": "unknown",
            "age_group": "adult",
            "personality_trait": "neutral",
            "voice_type": "neutral",
            "confidence": 0.3,
        }

        # Gender patterns
        if any(pattern in char_name_lower for pattern in ["a", "e", "i", "o", "u"]):
            if char_name_lower.endswith(("a", "e", "i")):
                analysis["gender"] = "female"
                analysis["voice_type"] = "feminine"
            elif char_name_lower.endswith(("o", "u", "n", "r")):
                analysis["gender"] = "male"
                analysis["voice_type"] = "masculine"

        # Personality patterns
        if any(
            pattern in char_name_lower
            for pattern in ["shadow", "dark", "grim", "vex", "mal"]
        ):
            analysis["personality_trait"] = "villainous"
        elif any(
            pattern in char_name_lower for pattern in ["light", "bright", "sun", "star"]
        ):
            analysis["personality_trait"] = "heroic"
        elif any(
            pattern in char_name_lower
            for pattern in ["wise", "sage", "elder", "merlin"]
        ):
            analysis["personality_trait"] = "wise"
            analysis["voice_type"] = "wise"

        return analysis

    def map_character_name_to_voice(self, char_name: str) -> Character:
        """Map a character name to an appropriate voice using AI analysis"""
        print(f"🔧 DEBUG: AI-mapping '{char_name}' to voice profile")

        # First, check if we already have a mapping for this name
        if char_name in self.name_voice_cache:
            cached_voice = self.name_voice_cache[char_name]
            print(
                f"🔧 DEBUG: Using cached voice mapping for '{char_name}': {cached_voice}"
            )
            return cached_voice

        # Analyze the character name to understand their traits
        analysis = self.analyze_character_name_with_ai(char_name)
        print(f"🔧 DEBUG: AI analysis complete for '{char_name}': {analysis}")

        # Available English voices for different character types
        english_voices = {
            # Narrator voices
            "narrator": [
                "English_expressive_narrator",
                "English_CaptivatingStoryteller",
                "English_WiseScholar",
            ],
            # Female voices
            "female": [
                "English_radiant_girl",
                "English_compelling_lady1",
                "English_captivating_female1",
                "English_Upbeat_Woman",
                "English_CalmWoman",
                "English_Graceful_Lady",
                "English_PlayfulGirl",
                "English_LovelyGirl",
                "English_Wiselady",
                "English_SentimentalLady",
                "English_Soft-spokenGirl",
            ],
            # Male voices
            "male": [
                "English_magnetic_voiced_man",
                "English_Aussie_Bloke",
                "English_Trustworth_Man",
                "English_Gentle-voiced_man",
                "English_Diligent_Man",
                "English_ReservedYoungMan",
                "English_ManWithDeepVoice",
                "English_FriendlyPerson",
                "English_Debator",
                "English_Steadymentor",
                "English_Deep-VoicedGentleman",
                "English_DecentYoungMan",
                "English_PassionateWarrior",
            ],
            # Villain voices
            "villain": [
                "English_ManWithDeepVoice",
                "English_Deep-VoicedGentleman",
                "English_ImposingManner",
            ],
            # Child voices
            "child": [
                "English_radiant_girl",
                "English_PlayfulGirl",
                "English_LovelyGirl",
                "English_Soft-spokenGirl",
            ],
            # Elder voices
            "elder": [
                "English_WiseScholar",
                "English_Wiselady",
                "English_MaturePartner",
                "English_Steadymentor",
            ],
        }

        # Determine character type based on AI analysis
        gender = analysis.get("gender", "unknown")
        age_group = analysis.get("age_group", "unknown")
        personality = analysis.get("personality_trait", "unknown")

        # Select appropriate voice category
        voice_category = "male"  # default

        if gender == "female":
            if age_group == "child":
                voice_category = "child"
            elif age_group == "elder":
                voice_category = "elder"
            else:
                voice_category = "female"
        elif gender == "male":
            if age_group == "child":
                voice_category = "child"
            elif age_group == "elder":
                voice_category = "elder"
            else:
                voice_category = "male"

        # Special cases based on personality
        if personality in ["villainous", "sinister", "evil"]:
            voice_category = "villain"
        elif personality in ["wise", "scholarly", "mentor"]:
            voice_category = "elder"

        # Get available voices for this category
        available_voices = english_voices.get(voice_category, english_voices["male"])

        # Select a voice (simple round-robin for variety)
        if not hasattr(self, "voice_selection_index"):
            self.voice_selection_index = {}

        if voice_category not in self.voice_selection_index:
            self.voice_selection_index[voice_category] = 0

        selected_voice = available_voices[
            self.voice_selection_index[voice_category] % len(available_voices)
        ]
        self.voice_selection_index[voice_category] += 1

        # Create character with selected voice
        character = Character(
            name=char_name,
            description=f"AI-generated character with {gender} voice, {age_group} age group, {personality} personality",
            voice_id=selected_voice,
            speed=1.0,
            volume=1.0,
            pitch=0.0,
            emotion="neutral",
        )

        # Cache the mapping
        self.name_voice_cache[char_name] = character

        print(
            f"🔧 DEBUG: AI-mapped '{char_name}' to voice profile of '{selected_voice}'"
        )
        return character

    def parse_story_into_segments(self, story: str) -> List[StorySegment]:
        """Parse the story into segments with character dialogue"""
        print(f"🔧 DEBUG: Parsing story into segments")
        print(f"🔧 DEBUG: Story length: {len(story)} characters")

        segments = []
        lines = story.split("\n")
        print(f"🔧 DEBUG: Story has {len(lines)} lines")

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                print(f"🔧 DEBUG: Line {i+1}: Empty line, skipping")
                continue

            print(f"🔧 DEBUG: Processing line {i+1}: {line[:50]}...")

            # Check if line contains character dialogue
            if ":" in line:
                # Extract character name and dialogue
                parts = line.split(":", 1)
                if len(parts) == 2:
                    char_name_part = parts[0].strip()
                    dialogue = parts[1].strip()

                    # Clean up character name (remove parentheses and stage directions)
                    char_name = char_name_part.split("(")[0].strip()

                    print(f"🔧 DEBUG: Processing line - Raw: '{line[:50]}...'")
                    print(f"🔧 DEBUG: Extracted character name: '{char_name}'")
                    print(f"🔧 DEBUG: Dialogue: '{dialogue[:30]}...'")

                    # Map the character name to a voice profile
                    mapped_character = self.map_character_name_to_voice(char_name)

                    segments.append(
                        StorySegment(character=mapped_character, text=dialogue)
                    )
                    print(
                        f"🔧 DEBUG: Added segment for {mapped_character.name} (voice: {mapped_character.voice_id})"
                    )
                else:
                    # No colon found, treat as narrative text
                    print(f"🔧 DEBUG: No colon found, treating as narrative text")
                    segments.append(
                        StorySegment(character=self.characters["narrator"], text=line)
                    )
            else:
                # No colon in line, treat as narrative text
                print(f"🔧 DEBUG: No colon in line, treating as narrative text")
                segments.append(
                    StorySegment(character=self.characters["narrator"], text=line)
                )

        self.story_segments = segments
        print(f"🔧 DEBUG: Parsed {len(segments)} segments")
        for i, segment in enumerate(segments):
            print(
                f"🔧 DEBUG: Segment {i+1}: {segment.character.name} - {segment.text[:30]}..."
            )

        return segments

    def generate_audio_for_segment(
        self, segment: StorySegment, output_dir: str = "audio_output"
    ) -> str:
        """Generate audio for a story segment using MiniMax TTS"""
        print(f"🔧 DEBUG: Generating audio for segment")
        print(f"🔧 DEBUG: Character: {segment.character.name}")
        print(f"🔧 DEBUG: Text: {segment.text}")
        print(f"🔧 DEBUG: Output directory: {output_dir}")

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"🔧 DEBUG: Created output directory: {output_dir}")

        char = segment.character
        timestamp = int(time.time())
        filename = f"{output_dir}/{char.name}_{timestamp}.mp3"
        print(f"🔧 DEBUG: Target filename: {filename}")

        payload = {
            "model": "speech-02-hd",
            "text": segment.text,
            "stream": False,
            "voice_setting": {
                "voice_id": char.voice_id,
                "speed": int(char.speed * 100),  # Convert to integer percentage
                "vol": int(char.volume * 100),  # Convert to integer percentage
                "pitch": int(char.pitch * 100),  # Convert to integer percentage
            },
            "audio_setting": {
                "sample_rate": 32000,
                "bitrate": 128000,
                "format": "mp3",
                "channel": 1,
            },
        }

        print(f"🔧 DEBUG: TTS payload prepared")
        print(f"🔧 DEBUG: Voice settings: {payload['voice_setting']}")
        print(f"🔧 DEBUG: Audio settings: {payload['audio_setting']}")

        try:
            # Apply rate limiting for TTS
            self.tts_limiter.wait_if_needed()

            print(f"🔧 DEBUG: Making TTS API request to {self.tts_url}")
            print(f"🔧 DEBUG: Request headers: {dict(self.headers)}")

            response = requests.post(self.tts_url, headers=self.headers, json=payload)
            print(f"🔧 DEBUG: TTS API response status code: {response.status_code}")
            print(f"🔧 DEBUG: TTS API response headers: {dict(response.headers)}")

            # Check for rate limit errors
            if response.status_code == 429:
                print(
                    f"⚠️ TTS Rate limit exceeded. Waiting {self.retry_delay} seconds before retry..."
                )
                time.sleep(self.retry_delay)
                # Retry once
                self.tts_limiter.wait_if_needed()
                response = requests.post(
                    self.tts_url, headers=self.headers, json=payload
                )
                print(
                    f"🔧 DEBUG: TTS retry response status code: {response.status_code}"
                )

            response.raise_for_status()

            result = response.json()
            print(
                f"🔧 DEBUG: TTS API response keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}"
            )

            if "data" in result and "audio" in result["data"]:
                audio_hex = result["data"]["audio"]
                print(
                    f"🔧 DEBUG: Received audio hex data, length: {len(audio_hex)} characters"
                )

                try:
                    audio_bytes = bytes.fromhex(audio_hex)
                    print(
                        f"🔧 DEBUG: Converted hex to bytes, size: {len(audio_bytes)} bytes"
                    )

                    with open(filename, "wb") as f:
                        f.write(audio_bytes)

                    print(f"🔧 DEBUG: Audio file saved successfully: {filename}")

                    segment.audio_file = filename
                    print(f"✅ Generated audio for {char.name}: {filename}")
                    return filename
                except ValueError as e:
                    print(f"❌ DEBUG: Error converting hex to bytes: {e}")
                    print(f"🔧 DEBUG: Audio hex data preview: {audio_hex[:50]}...")
                    return None
            else:
                print(f"❌ DEBUG: No audio data in TTS response")
                print(f"🔧 DEBUG: Full TTS response: {result}")
                print(f"Failed to generate audio for {char.name}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ DEBUG: TTS request error: {e}")
            print(
                f"🔧 DEBUG: Response content: {getattr(e.response, 'content', 'No response content')}"
            )
            return None
        except Exception as e:
            print(f"❌ DEBUG: Error generating audio for {char.name}: {e}")
            print(f"🔧 DEBUG: Exception type: {type(e)}")
            return None

    def generate_full_story_audio(self, output_dir: str = "audio_output") -> List[str]:
        """Generate audio for all story segments"""
        print(f"🔧 DEBUG: Generating audio for all story segments")
        print(f"🔧 DEBUG: Number of segments: {len(self.story_segments)}")
        print(f"🔧 DEBUG: Output directory: {output_dir}")

        audio_files = []

        for i, segment in enumerate(self.story_segments):
            print(f"🔧 DEBUG: Processing segment {i+1}/{len(self.story_segments)}")
            print(
                f"Generating audio for segment {i+1}/{len(self.story_segments)}: {segment.character.name}"
            )
            audio_file = self.generate_audio_for_segment(segment, output_dir)
            if audio_file:
                audio_files.append(audio_file)
                print(f"🔧 DEBUG: Successfully generated audio for segment {i+1}")
            else:
                print(f"❌ DEBUG: Failed to generate audio for segment {i+1}")

        print(
            f"🔧 DEBUG: Audio generation complete. Generated {len(audio_files)} files"
        )
        return audio_files

    def play_audio_file(self, audio_file: str):
        """Play an audio file if audio libraries are available"""
        print(f"🔧 DEBUG: Attempting to play audio file: {audio_file}")

        if not AUDIO_AVAILABLE:
            print(f"🔧 DEBUG: Audio libraries not available")
            print(f"Audio file saved: {audio_file}")
            print("Install pydub and simpleaudio for audio playback")
            return

        try:
            print(f"🔧 DEBUG: Loading audio file with pydub")
            audio = AudioSegment.from_file(audio_file, format="mp3")
            print(f"🔧 DEBUG: Audio loaded successfully, duration: {len(audio)}ms")
            print(f"Playing: {audio_file}")
            play(audio)
            print(f"🔧 DEBUG: Audio playback completed")
        except Exception as e:
            print(f"❌ DEBUG: Error playing audio: {e}")
            print(f"🔧 DEBUG: Exception type: {type(e)}")

    def create_story_script(self, output_file: str = "story_script.txt"):
        """Create a script file with all story segments and audio file references"""
        print(f"🔧 DEBUG: Creating story script file: {output_file}")
        print(f"🔧 DEBUG: Number of segments to write: {len(self.story_segments)}")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("STORY SCRIPT\n")
            f.write("=" * 50 + "\n\n")

            for i, segment in enumerate(self.story_segments, 1):
                print(f"🔧 DEBUG: Writing segment {i} to script")
                f.write(f"Segment {i}:\n")
                f.write(f"Character: {segment.character.name}\n")
                f.write(f"Voice: {segment.character.voice_id}\n")
                f.write(f"Text: {segment.text}\n")
                if segment.audio_file:
                    f.write(f"Audio: {segment.audio_file}\n")
                f.write("-" * 30 + "\n\n")

        print(f"✅ Story script saved to: {output_file}")


def main():
    """Main function to demonstrate the story telling app"""
    print("🔧 DEBUG: Starting main function")

    # Configuration - Use your specific environment variable names
    API_KEY = os.getenv("mini")
    GROUP_ID = os.getenv("group")

    print(f"🔧 DEBUG: Environment variables loaded")
    print(f"🔧 DEBUG: API_KEY present: {bool(API_KEY)}")
    print(f"🔧 DEBUG: GROUP_ID present: {bool(GROUP_ID)}")

    if not API_KEY or not GROUP_ID:
        print("❌ DEBUG: Missing API credentials")
        print("Please set your MiniMax API credentials in your .env file:")
        print("mini=your_api_key_here")
        print("group=your_group_id_here")
        print("\nOr set environment variables:")
        print("export mini='your_api_key'")
        print("export group='your_group_id'")
        return

    print(f"🔧 DEBUG: API credentials found, creating storyteller instance")

    # Create story teller instance
    storyteller = MiniMaxStoryTeller(API_KEY, GROUP_ID)

    # Add custom characters if needed
    print(f"🔧 DEBUG: Adding custom wizard character")
    storyteller.add_character(
        Character(
            "Wizard",
            "A mysterious mentor figure with ancient wisdom, who guides others while carrying their own burdens and secrets",
            "English_WiseScholar",
            0.9,
            1.0,
            0.0,
            "wise",
        )
    )

    # Generate a story
    print(f"🔧 DEBUG: Starting story generation")
    print("Generating story...")
    story = storyteller.generate_story(
        genre="fantasy",
        theme="discovering inner strength and the power of friendship",
        characters=["hero", "friend", "villain", "wizard"],
        length="medium",
    )

    if story:
        print(f"🔧 DEBUG: Story generated successfully")
        print("\n" + "=" * 50)
        print("GENERATED STORY:")
        print("=" * 50)
        print(story)
        print("=" * 50)

        # Parse story into segments
        print(f"🔧 DEBUG: Parsing story into segments")
        print("\nParsing story into segments...")
        segments = storyteller.parse_story_into_segments(story)

        # Generate audio for all segments
        print(f"🔧 DEBUG: Starting audio generation")
        print("\nGenerating audio files...")
        audio_files = storyteller.generate_full_story_audio()

        # Create story script
        print(f"🔧 DEBUG: Creating story script")
        storyteller.create_story_script()

        print(f"\n🔧 DEBUG: Story generation process complete")
        print(f"Story generation complete!")
        print(f"Generated {len(audio_files)} audio files")
        print("Check the 'audio_output' directory for audio files")
        print("Check 'story_script.txt' for the complete script")

        # Optionally play the first audio file as a sample
        if audio_files:
            print(f"🔧 DEBUG: Playing sample audio file")
            print(f"\nPlaying sample audio: {audio_files[0]}")
            storyteller.play_audio_file(audio_files[0])
        else:
            print(f"⚠️ DEBUG: No audio files generated to play")

        # Display usage statistics and cost optimization results
        print(f"\n🔧 DEBUG: Displaying usage statistics")
        storyteller.print_usage_summary()
    else:
        print(f"❌ DEBUG: Story generation failed")
        print("Failed to generate story")

        # Still show usage statistics even if story generation failed
        if hasattr(storyteller, "api_usage_stats"):
            print(f"\n🔧 DEBUG: Displaying usage statistics despite failure")
            storyteller.print_usage_summary()


if __name__ == "__main__":
    print("🔧 DEBUG: Script started")
    main()
    print("🔧 DEBUG: Script completed")
