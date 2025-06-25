#!/usr/bin/env python3
"""
Script to query MiniMax API for available voice IDs
Uses the official get_voice API endpoint
"""

import os
import requests
import json
from typing import Dict, List, Any
from dotenv import load_dotenv


def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()
    api_key = os.getenv("mini")
    group_id = os.getenv("group")

    if not api_key:
        print("❌ Error: API key not found in environment variables")
        print("Please set your MiniMax API key in the .env file:")
        print("mini=your_api_key_here")
        return None, None

    if not group_id:
        print("⚠️ Warning: Group ID not found in environment variables")
        print("This script doesn't require Group ID, but other parts of the app do")

    return api_key, group_id


def get_available_voices(api_key: str, voice_type: str = "all") -> Dict[str, Any]:
    """
    Query MiniMax API for available voice IDs

    Args:
        api_key: MiniMax API key
        voice_type: Type of voices to query ("system", "voice_cloning", "voice_generation", "music_generation", "all")

    Returns:
        Dictionary containing available voices
    """
    url = "https://api.minimax.io/v1/get_voice"
    headers = {
        "authority": "api.minimax.io",
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {"voice_type": voice_type}

    print(f"🔍 Querying MiniMax API for {voice_type} voices...")
    print(f"🔧 URL: {url}")
    print(f"🔧 Voice type: {voice_type}")

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()
        print(f"✅ Successfully retrieved voice data")
        print(f"🔧 Response status: {response.status_code}")

        return result

    except requests.exceptions.RequestException as e:
        print(f"❌ Error making API request: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON response: {e}")
        return None


def display_voices(voices_data: Dict[str, Any]):
    """Display available voices in a user-friendly format"""
    if not voices_data:
        print("❌ No voice data to display")
        return

    print("\n" + "=" * 60)
    print("🎤 AVAILABLE MINIMAX VOICES")
    print("=" * 60)

    # System voices
    if "system_voice" in voices_data and voices_data["system_voice"]:
        print(f"\n📢 SYSTEM VOICES ({len(voices_data['system_voice'])} available):")
        print("-" * 40)
        for voice in voices_data["system_voice"]:
            voice_id = voice.get("voice_id", "Unknown")
            voice_name = voice.get("voice_name", "No name")
            description = voice.get("description", [])

            print(f"🎵 Voice ID: {voice_id}")
            print(f"   Name: {voice_name}")
            if description:
                print(f"   Description: {', '.join(description)}")
            print()

    # Voice cloning voices
    if "voice_cloning" in voices_data and voices_data["voice_cloning"]:
        print(
            f"\n🎭 VOICE CLONING VOICES ({len(voices_data['voice_cloning'])} available):"
        )
        print("-" * 40)
        for voice in voices_data["voice_cloning"]:
            voice_id = voice.get("voice_id", "Unknown")
            description = voice.get("description", [])
            created_time = voice.get("created_time", "Unknown")

            print(f"🎵 Voice ID: {voice_id}")
            if description:
                print(f"   Description: {', '.join(description)}")
            print(f"   Created: {created_time}")
            print()

    # Voice generation voices
    if "voice_generation" in voices_data and voices_data["voice_generation"]:
        print(
            f"\n🎨 VOICE GENERATION VOICES ({len(voices_data['voice_generation'])} available):"
        )
        print("-" * 40)
        for voice in voices_data["voice_generation"]:
            voice_id = voice.get("voice_id", "Unknown")
            description = voice.get("description", [])
            created_time = voice.get("created_time", "Unknown")

            print(f"🎵 Voice ID: {voice_id}")
            if description:
                print(f"   Description: {', '.join(description)}")
            print(f"   Created: {created_time}")
            print()

    # Music generation voices
    if "music_generation" in voices_data and voices_data["music_generation"]:
        print(
            f"\n🎼 MUSIC GENERATION VOICES ({len(voices_data['music_generation'])} available):"
        )
        print("-" * 40)
        for voice in voices_data["music_generation"]:
            voice_id = voice.get("voice_id", "Unknown")
            instrumental_id = voice.get("instrumental_id", "Unknown")
            created_time = voice.get("created_time", "Unknown")

            print(f"🎵 Voice ID: {voice_id}")
            print(f"   Instrumental ID: {instrumental_id}")
            print(f"   Created: {created_time}")
            print()

    # Voice slots
    if "voice_slots" in voices_data and voices_data["voice_slots"]:
        print(f"\n📦 VOICE SLOTS ({len(voices_data['voice_slots'])} available):")
        print("-" * 40)
        for voice in voices_data["voice_slots"]:
            voice_id = voice.get("voice_id", "Unknown")
            voice_name = voice.get("voice_name", "No name")
            description = voice.get("description", [])

            print(f"🎵 Voice ID: {voice_id}")
            print(f"   Name: {voice_name}")
            if description:
                print(f"   Description: {', '.join(description)}")
            print()


def extract_voice_ids(voices_data: Dict[str, Any]) -> List[str]:
    """Extract all available voice IDs from the response"""
    voice_ids = []

    for category in [
        "system_voice",
        "voice_cloning",
        "voice_generation",
        "music_generation",
        "voice_slots",
    ]:
        if category in voices_data and voices_data[category]:
            for voice in voices_data[category]:
                voice_id = voice.get("voice_id")
                if voice_id:
                    voice_ids.append(voice_id)

    return sorted(list(set(voice_ids)))  # Remove duplicates and sort


def suggest_voice_mapping(voices_data: Dict[str, Any]) -> Dict[str, str]:
    """Suggest voice mappings for different character types"""
    suggestions = {}

    # Get system voices for suggestions
    system_voices = voices_data.get("system_voice", [])

    # Look for common voice patterns
    for voice in system_voices:
        voice_id = voice.get("voice_id", "").lower()
        voice_name = voice.get("voice_name", "").lower()

        # Female voices
        if any(
            keyword in voice_id or keyword in voice_name
            for keyword in ["female", "woman", "girl", "lady"]
        ):
            if "narrator" not in voice_id and "narrator" not in voice_name:
                suggestions["female"] = voice.get("voice_id")

        # Male voices
        if any(
            keyword in voice_id or keyword in voice_name
            for keyword in ["male", "man", "boy", "guy"]
        ):
            suggestions["male"] = voice.get("voice_id")

        # Narrator voices
        if any(
            keyword in voice_id or keyword in voice_name
            for keyword in ["narrator", "wise", "story"]
        ):
            suggestions["narrator"] = voice.get("voice_id")

        # Villain voices
        if any(
            keyword in voice_id or keyword in voice_name
            for keyword in ["villain", "evil", "dark", "grinch"]
        ):
            suggestions["villain"] = voice.get("voice_id")

    return suggestions


def main():
    """Main function"""
    print("🎤 MiniMax Voice ID Query Tool")
    print("=" * 40)

    # Load environment
    api_key, group_id = load_environment()
    if not api_key:
        return

    # Query for all voice types
    voices_data = get_available_voices(api_key, "all")

    if not voices_data:
        print("❌ Failed to retrieve voice data")
        return

    # Display voices
    display_voices(voices_data)

    # Extract all voice IDs
    all_voice_ids = extract_voice_ids(voices_data)
    print(f"\n📊 SUMMARY:")
    print(f"Total unique voice IDs available: {len(all_voice_ids)}")

    # Suggest voice mappings
    suggestions = suggest_voice_mapping(voices_data)
    if suggestions:
        print(f"\n💡 SUGGESTED VOICE MAPPINGS:")
        print("-" * 30)
        for character_type, voice_id in suggestions.items():
            print(f"{character_type.capitalize()}: {voice_id}")

    # Save to file
    output_file = "available_voices.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(voices_data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Voice data saved to: {output_file}")
    print(
        f"📝 You can use this data to update your config.py file with the correct voice IDs"
    )


if __name__ == "__main__":
    main()
