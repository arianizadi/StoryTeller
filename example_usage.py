#!/usr/bin/env python3
"""
Example usage of the StoryTeller application
Demonstrates different ways to generate stories and audio
"""

import os
import asyncio
from main import MiniMaxStoryTeller, Character
from config import (
    create_character_from_template,
    get_available_characters,
    get_available_genres,
    get_genre_info,
    create_fantasy_story_setup,
    create_mystery_story_setup,
    create_adventure_story_setup,
)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Install with: pip install python-dotenv")


def example_basic_story():
    """Basic story generation example"""
    print("=== Basic Story Generation ===")

    # Get API credentials
    api_key = os.getenv("mini")
    group_id = os.getenv("group")

    if not api_key or not group_id:
        print("Please set MINIMAX_API_KEY and MINIMAX_GROUP_ID environment variables")
        print("Or add them to your .env file:")
        print("mini=your_api_key_here")
        print("group=your_group_id_here")
        return

    # Create storyteller
    storyteller = MiniMaxStoryTeller(api_key, group_id)

    # Generate a simple story
    story = storyteller.generate_story(
        genre="adventure",
        theme="overcoming fear",
        characters=["hero", "friend"],
        length="short",
    )

    if story:
        print("Generated Story:")
        print(story)
        print("\n" + "=" * 50)

        # Parse and generate audio
        segments = storyteller.parse_story_into_segments(story)
        audio_files = storyteller.generate_full_story_audio("example_audio")

        print(f"Generated {len(audio_files)} audio files")
        storyteller.create_story_script("example_script.txt")


def example_custom_characters():
    """Example with custom character definitions"""
    print("\n=== Custom Characters Example ===")

    api_key = os.getenv("mini")
    group_id = os.getenv("group")

    storyteller = MiniMaxStoryTeller(api_key, group_id)

    # Add custom characters
    storyteller.add_character(
        Character(
            "Dragon",
            "A wise ancient dragon who guards ancient knowledge",
            "Grinch",
            0.8,
            1.2,
            -0.3,
            "mysterious",
        )
    )

    storyteller.add_character(
        Character(
            "Princess",
            "A brave princess who seeks adventure",
            "Spanish_SereneWoman",
            1.1,
            1.0,
            0.2,
            "confident",
        )
    )

    storyteller.add_character(
        Character(
            "Knight",
            "A loyal knight with a noble heart",
            "Spanish_DeterminedManager",
            1.0,
            1.0,
            0.0,
            "brave",
        )
    )

    # Generate story with custom characters
    story = storyteller.generate_story(
        genre="fantasy",
        theme="friendship and loyalty",
        characters=["dragon", "princess", "knight"],
        length="medium",
    )

    if story:
        print("Generated Story with Custom Characters:")
        print(story)
        print("\n" + "=" * 50)

        segments = storyteller.parse_story_into_segments(story)
        audio_files = storyteller.generate_full_story_audio("custom_audio")

        print(f"Generated {len(audio_files)} audio files")
        storyteller.create_story_script("custom_script.txt")


def example_different_genres():
    """Example generating stories in different genres"""
    print("\n=== Different Genres Example ===")

    api_key = os.getenv("mini")
    group_id = os.getenv("group")

    storyteller = MiniMaxStoryTeller(api_key, group_id)

    genres_and_themes = [
        ("sci-fi", "space exploration and discovery"),
        ("mystery", "solving a puzzling crime"),
        ("romance", "finding true love"),
        ("comedy", "misadventures and humor"),
    ]

    for genre, theme in genres_and_themes:
        print(f"\nGenerating {genre} story about {theme}...")

        story = storyteller.generate_story(
            genre=genre, theme=theme, characters=["hero", "friend"], length="short"
        )

        if story:
            print(f"Generated {genre} story:")
            print(story[:200] + "..." if len(story) > 200 else story)
            print("-" * 30)


async def example_streaming_audio():
    """Example using streaming audio generation"""
    print("\n=== Streaming Audio Example ===")

    api_key = os.getenv("mini")
    group_id = os.getenv("group")

    storyteller = MiniMaxStoryTeller(api_key, group_id)

    # Generate a story
    story = storyteller.generate_story(
        genre="adventure",
        theme="journey to a magical land",
        characters=["hero", "friend", "villain"],
        length="medium",
    )

    if story:
        print("Generated Story for Streaming:")
        print(story)
        print("\n" + "=" * 50)

        # Parse story
        segments = storyteller.parse_story_into_segments(story)

        # Generate audio using streaming
        print("Generating audio using WebSocket streaming...")
        audio_files = await storyteller.generate_full_story_audio_streaming(
            "streaming_audio"
        )

        print(f"Generated {len(audio_files)} audio files using streaming")
        storyteller.create_story_script("streaming_script.txt")


def example_character_voice_experiments():
    """Example experimenting with different voice settings"""
    print("\n=== Voice Experimentation Example ===")

    api_key = os.getenv("mini")
    group_id = os.getenv("group")

    storyteller = MiniMaxStoryTeller(api_key, group_id)

    # Create characters with different voice settings
    voice_experiments = [
        Character(
            "Fast_Talker",
            "Speaks very quickly",
            "Spanish_ThoughtfulMan",
            1.5,
            1.0,
            0.0,
            "excited",
        ),
        Character(
            "Slow_Thinker",
            "Speaks slowly and thoughtfully",
            "Spanish_WiseScholar",
            0.6,
            1.0,
            0.0,
            "calm",
        ),
        Character(
            "Loud_Leader",
            "Speaks loudly and confidently",
            "Spanish_DeterminedManager",
            1.0,
            1.5,
            0.2,
            "confident",
        ),
        Character(
            "Whisperer",
            "Speaks quietly and mysteriously",
            "Spanish_SereneWoman",
            0.8,
            0.7,
            -0.1,
            "mysterious",
        ),
    ]

    for char in voice_experiments:
        storyteller.add_character(char)

    # Generate a story to test different voices
    story = storyteller.generate_story(
        genre="fantasy",
        theme="a council meeting of different personalities",
        characters=["fast_talker", "slow_thinker", "loud_leader", "whisperer"],
        length="short",
    )

    if story:
        print("Generated Story with Voice Experiments:")
        print(story)
        print("\n" + "=" * 50)

        segments = storyteller.parse_story_into_segments(story)
        audio_files = storyteller.generate_full_story_audio("voice_experiments")

        print(f"Generated {len(audio_files)} audio files with different voice settings")
        storyteller.create_story_script("voice_experiments_script.txt")


def example_playback_demo():
    """Example demonstrating audio playback"""
    print("\n=== Audio Playback Demo ===")

    api_key = os.getenv("mini")
    group_id = os.getenv("group")

    storyteller = MiniMaxStoryTeller(api_key, group_id)

    # Generate a short story
    story = storyteller.generate_story(
        genre="fairy tale",
        theme="a magical transformation",
        characters=["hero", "friend"],
        length="short",
    )

    if story:
        segments = storyteller.parse_story_into_segments(story)
        audio_files = storyteller.generate_full_story_audio("playback_demo")

        print("Playing generated audio files...")
        for i, segment in enumerate(segments):
            if segment.audio_file:
                print(f"Playing segment {i+1}: {segment.character.name}")
                print(f"Text: {segment.text}")
                storyteller.play_audio_file(segment.audio_file)
                print("-" * 30)


def main():
    """Run all examples"""
    print("StoryTeller Examples")
    print("=" * 50)

    # Check if API credentials are available
    api_key = os.getenv("mini")
    group_id = os.getenv("group")

    if not api_key or not group_id:
        print("Please set your MiniMax API credentials in your .env file:")
        print("mini=your_api_key_here")
        print("group=your_group_id_here")
        return

    try:
        # Run basic example
        example_basic_story()

        # Run custom characters example
        example_custom_characters()

        # Run different genres example
        example_different_genres()

        # Run voice experimentation example
        example_character_voice_experiments()

        # Run streaming audio example
        asyncio.run(example_streaming_audio())

        # Run playback demo (optional)
        # example_playback_demo()

        print("\n" + "=" * 50)
        print("All examples completed!")
        print("Check the generated directories for audio files and scripts:")
        print("- example_audio/")
        print("- custom_audio/")
        print("- streaming_audio/")
        print("- voice_experiments/")
        print("- playback_demo/")

    except Exception as e:
        print(f"Error running examples: {e}")


if __name__ == "__main__":
    main()
