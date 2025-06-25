"""
Configuration file for StoryTeller application
Contains predefined characters, voice settings, and story templates
"""

from dataclasses import dataclass
from typing import Dict, List, Any

# Rate limiting configuration
RATE_LIMITS = {
    "chat_rpm": 100,  # Requests per minute for chat completion (max 120)
    "tts_rpm": 50,  # Requests per minute for TTS (max 60)
    "retry_delay": 60,  # Seconds to wait before retry on rate limit
    "max_retries": 1,  # Maximum number of retries on rate limit
}

# Predefined voice IDs from MiniMax
VOICE_IDS = {
    # Female voices
    "wise_woman": "English_Wiselady",
    "young_female": "English_radiant_girl",
    "mature_female": "English_CalmWoman",
    # Male voices
    "young_male": "English_ReservedYoungMan",
    "mature_male": "English_Trustworth_Man",
    "deep_male": "English_ManWithDeepVoice",
    # Special voices
    "villain": "English_ManWithDeepVoice",
    "narrator": "English_expressive_narrator",
    "child": "English_PlayfulGirl",
    "elder": "English_WiseScholar",
}

# Predefined character templates
CHARACTER_TEMPLATES = {
    "hero": {
        "name": "Hero",
        "description": "A courageous protagonist with a heart of gold, facing inner doubts and external challenges with determination and growth",
        "voice_id": "English_magnetic_voiced_man",
        "speed": 1.0,
        "volume": 1.0,
        "pitch": 0.0,
        "emotion": "brave",
    },
    "villain": {
        "name": "Villain",
        "description": "A complex antagonist with layers of motivation, not purely evil but driven by pain, fear, or misguided beliefs",
        "voice_id": "English_ManWithDeepVoice",
        "speed": 0.8,
        "volume": 1.0,
        "pitch": -0.3,
        "emotion": "sinister",
    },
    "friend": {
        "name": "Friend",
        "description": "A loyal companion who provides emotional support, wisdom, and sometimes tough love when needed",
        "voice_id": "English_radiant_girl",
        "speed": 1.1,
        "volume": 1.0,
        "pitch": 0.2,
        "emotion": "friendly",
    },
    "wizard": {
        "name": "Wizard",
        "description": "A mysterious mentor figure with ancient wisdom, who guides others while carrying their own burdens and secrets",
        "voice_id": "English_WiseScholar",
        "speed": 0.9,
        "volume": 1.0,
        "pitch": 0.0,
        "emotion": "wise",
    },
    "narrator": {
        "name": "Narrator",
        "description": "A wise storyteller with a warm, engaging voice who brings the world to life with vivid descriptions",
        "voice_id": "English_expressive_narrator",
        "speed": 1.0,
        "volume": 1.0,
        "pitch": 0.0,
        "emotion": "calm",
    },
    "princess": {
        "name": "Princess",
        "description": "A strong-willed royal with hidden depths, balancing duty with personal desires and inner strength",
        "voice_id": "English_Graceful_Lady",
        "speed": 1.0,
        "volume": 1.0,
        "pitch": 0.1,
        "emotion": "noble",
    },
    "knight": {
        "name": "Knight",
        "description": "A honorable warrior bound by duty, struggling with the weight of responsibility and personal honor",
        "voice_id": "English_Trustworth_Man",
        "speed": 1.0,
        "volume": 1.0,
        "pitch": 0.1,
        "emotion": "honorable",
    },
    "dragon": {
        "name": "Dragon",
        "description": "A powerful being with ancient wisdom, often misunderstood but capable of great kindness or destruction",
        "voice_id": "English_ManWithDeepVoice",
        "speed": 0.7,
        "volume": 1.0,
        "pitch": -0.4,
        "emotion": "mysterious",
    },
    "detective": {
        "name": "Detective",
        "description": "A sharp-minded investigator with a troubled past, driven by justice but haunted by personal demons",
        "voice_id": "English_Diligent_Man",
        "speed": 0.9,
        "volume": 1.0,
        "pitch": -0.1,
        "emotion": "determined",
    },
    "elder": {
        "name": "Elder",
        "description": "A wise figure with years of experience, offering guidance while dealing with their own mortality and regrets",
        "voice_id": "English_WiseScholar",
        "speed": 0.8,
        "volume": 1.0,
        "pitch": -0.1,
        "emotion": "wise",
    },
    "child": {
        "name": "Child",
        "description": "An innocent soul with pure heart and boundless imagination, often seeing truth that adults miss",
        "voice_id": "English_PlayfulGirl",
        "speed": 1.3,
        "volume": 1.0,
        "pitch": 0.3,
        "emotion": "innocent",
    },
    "mentor": {
        "name": "Mentor",
        "description": "A guiding figure who teaches through experience, balancing tough lessons with compassion and understanding",
        "voice_id": "English_WiseScholar",
        "speed": 0.9,
        "volume": 1.0,
        "pitch": 0.0,
        "emotion": "wise",
    },
    "outcast": {
        "name": "Outcast",
        "description": "A misunderstood soul with hidden talents, seeking acceptance while maintaining their unique identity",
        "voice_id": "English_ReservedYoungMan",
        "speed": 1.0,
        "volume": 1.0,
        "pitch": -0.2,
        "emotion": "lonely",
    },
    "guardian": {
        "name": "Guardian",
        "description": "A protective figure with fierce loyalty, willing to sacrifice everything for those they love",
        "voice_id": "English_Trustworth_Man",
        "speed": 1.0,
        "volume": 1.0,
        "pitch": 0.0,
        "emotion": "protective",
    },
}

# Story genre templates
STORY_GENRES = {
    "fantasy": {
        "description": "Magical worlds with mythical creatures and epic quests, where ordinary people discover extraordinary powers within themselves",
        "common_characters": ["hero", "wizard", "knight", "dragon", "princess"],
        "themes": [
            "discovering inner strength",
            "friendship and loyalty",
            "magical transformation",
            "epic quest",
            "finding one's true identity",
        ],
    },
    "adventure": {
        "description": "Exciting journeys with challenges and discoveries, where characters grow through facing their fears and overcoming obstacles",
        "common_characters": ["hero", "friend", "villain", "guide"],
        "themes": [
            "overcoming fear and doubt",
            "journey to unknown lands",
            "treasure hunting",
            "survival and resilience",
            "finding courage within",
        ],
    },
    "mystery": {
        "description": "Puzzling stories with clues and revelations, where characters must solve complex problems while dealing with personal demons",
        "common_characters": ["detective", "suspect", "witness", "victim"],
        "themes": [
            "solving a crime",
            "hidden secrets",
            "uncovering the truth",
            "suspense and intrigue",
            "justice and redemption",
        ],
    },
    "sci-fi": {
        "description": "Futuristic stories with technology and space, exploring what it means to be human in an increasingly complex world",
        "common_characters": ["scientist", "hero", "robot", "alien"],
        "themes": [
            "space exploration",
            "technological advancement",
            "alien contact",
            "time travel",
            "humanity and identity",
        ],
    },
    "romance": {
        "description": "Stories of love and relationships, where characters learn about themselves through connection with others",
        "common_characters": ["hero", "princess", "friend", "rival"],
        "themes": [
            "finding true love",
            "overcoming obstacles",
            "second chances",
            "destiny",
            "self-discovery through love",
        ],
    },
    "comedy": {
        "description": "Humorous stories with funny situations, where laughter helps characters overcome challenges and find joy",
        "common_characters": ["hero", "friend", "comedian", "fool"],
        "themes": [
            "misadventures",
            "funny misunderstandings",
            "pranks",
            "humor",
            "finding joy in chaos",
        ],
    },
    "fairy_tale": {
        "description": "Traditional fairy tales with magical elements, where characters learn important life lessons through magical experiences",
        "common_characters": ["princess", "knight", "wizard", "villain"],
        "themes": [
            "magical transformation",
            "true love",
            "good vs evil",
            "wishes come true",
            "learning life lessons",
        ],
    },
}


def create_character_from_template(
    template_name: str, custom_name: str = None
) -> "Character":
    """Create a character from a predefined template"""
    if template_name not in CHARACTER_TEMPLATES:
        raise ValueError(f"Unknown character template: {template_name}")

    template = CHARACTER_TEMPLATES[template_name]
    voice_id = VOICE_IDS.get(template["voice_id"], template["voice_id"])

    # Ensure proper capitalization for custom names
    if custom_name:
        # Convert to title case (first letter uppercase, rest lowercase)
        custom_name = custom_name.title()

    # Import Character here to avoid circular import
    from main import Character

    return Character(
        name=custom_name or template["name"],
        description=template["description"],
        voice_id=voice_id,
        speed=template["speed"],
        volume=template["volume"],
        pitch=template["pitch"],
        emotion=template.get(
            "emotion", "neutral"
        ),  # Default to neutral if not specified
    )


def get_available_characters() -> List[str]:
    """Get list of available character templates"""
    return list(CHARACTER_TEMPLATES.keys())


def get_available_voices() -> List[str]:
    """Get list of available voice IDs"""
    return list(VOICE_IDS.keys())


def get_available_genres() -> List[str]:
    """Get list of available story genres"""
    return list(STORY_GENRES.keys())


def get_genre_info(genre: str) -> Dict[str, Any]:
    """Get information about a specific genre"""
    if genre not in STORY_GENRES:
        raise ValueError(f"Unknown genre: {genre}")
    return STORY_GENRES[genre]


def create_story_prompt(
    genre: str, theme: str, characters: List[str], length: str = "medium"
) -> str:
    """Create a story prompt based on genre and theme"""
    genre_info = get_genre_info(genre)

    prompt = f"""Create an emotionally engaging {genre} story with the theme of "{theme}".

Genre: {genre_info['description']}

Characters to include: {', '.join(characters)}

Story Requirements:
- Give each character a memorable, realistic name that fits their personality
- Create emotional depth and character development
- Include meaningful dialogue that reveals character traits
- Build tension and conflict that drives the plot
- Create moments of vulnerability and growth
- End with a satisfying resolution that shows character growth
- Make readers care about what happens to the characters
- Include vivid descriptions that bring the world to life

Length: {length} (approximately 100 words for medium)

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

Make this a compelling story that readers will remember and care about. Focus on character relationships, emotional stakes, and meaningful growth. Create characters that feel real and relatable, with hopes, fears, and dreams that readers can connect with. Give each character a distinct voice and personality that comes through in their dialogue."""

    return prompt


# Example usage functions
def create_fantasy_story_setup():
    """Create a typical fantasy story setup"""
    characters = [
        create_character_from_template("hero", "Alex"),
        create_character_from_template("wizard", "Merlin"),
        create_character_from_template("princess", "Elena"),
        create_character_from_template("villain", "Dark Lord"),
    ]

    return {
        "genre": "fantasy",
        "theme": "friendship and courage",
        "characters": characters,
        "length": "medium",
    }


def create_mystery_story_setup():
    """Create a typical mystery story setup"""
    characters = [
        create_character_from_template("detective", "Sherlock"),
        create_character_from_template("friend", "Watson"),
        create_character_from_template("villain", "Criminal"),
        create_character_from_template("narrator"),
    ]

    return {
        "genre": "mystery",
        "theme": "solving a puzzling crime",
        "characters": characters,
        "length": "medium",
    }


def create_adventure_story_setup():
    """Create a typical adventure story setup"""
    characters = [
        create_character_from_template("hero", "Explorer"),
        create_character_from_template("friend", "Guide"),
        create_character_from_template("elder", "Wise One"),
        create_character_from_template("villain", "Rival"),
    ]

    return {
        "genre": "adventure",
        "theme": "journey to a magical land",
        "characters": characters,
        "length": "medium",
    }
