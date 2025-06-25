#!/usr/bin/env python3
"""
Test script to verify StoryTeller installation and API connectivity
"""

import os
import sys

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Install with: pip install python-dotenv")


def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")

    try:
        import requests

        print("✅ requests - OK")
    except ImportError:
        print("❌ requests - Missing")
        return False

    try:
        import websockets

        print("✅ websockets - OK")
    except ImportError:
        print("❌ websockets - Missing")
        return False

    try:
        from main import MiniMaxStoryTeller, Character

        print("✅ main module - OK")
    except ImportError as e:
        print(f"❌ main module - Error: {e}")
        return False

    try:
        from config import create_character_from_template

        print("✅ config module - OK")
    except ImportError as e:
        print(f"❌ config module - Error: {e}")
        return False

    return True


def test_api_credentials():
    """Test if API credentials are set"""
    print("\n🔑 Testing API credentials...")

    api_key = os.getenv("mini")
    group_id = os.getenv("group")

    if not api_key:
        print("❌ 'mini' not set in .env file")
        return False

    if not group_id:
        print("❌ 'group' not set in .env file")
        return False

    print("✅ API credentials found")
    print(f"   API Key: {api_key[:10]}...")
    print(f"   Group ID: {group_id}")

    return True


def test_api_connection():
    """Test API connection with a simple request"""
    print("\n🌐 Testing API connection...")

    api_key = os.getenv("mini")
    group_id = os.getenv("group")

    if not api_key or not group_id:
        print("❌ API credentials not available")
        return False

    try:
        from main import MiniMaxStoryTeller

        # Create storyteller instance
        storyteller = MiniMaxStoryTeller(api_key, group_id)

        # Test with a simple story generation
        print("⏳ Testing story generation (this may take a moment)...")
        story = storyteller.generate_story(
            genre="fantasy",
            theme="friendship",
            characters=["hero", "friend"],
            length="short",
        )

        if story:
            print("✅ Story generation successful")
            print(f"   Generated {len(story)} characters")
            return True
        else:
            print("❌ Story generation failed")
            return False

    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False


def test_character_creation():
    """Test character creation functionality"""
    print("\n👥 Testing character creation...")

    try:
        from config import create_character_from_template

        # Test creating a character
        character = create_character_from_template("hero", "TestHero")

        if character.name == "TestHero" and character.voice_id:
            print("✅ Character creation successful")
            print(f"   Name: {character.name}")
            print(f"   Voice: {character.voice_id}")
            return True
        else:
            print("❌ Character creation failed")
            return False

    except Exception as e:
        print(f"❌ Character creation failed: {e}")
        return False


def test_audio_libraries():
    """Test audio playback libraries"""
    print("\n🎵 Testing audio libraries...")

    try:
        from pydub import AudioSegment

        print("✅ pydub - OK")
    except ImportError:
        print("❌ pydub - Missing (audio playback will not work)")
        print("   Install with: pip install pydub simpleaudio")

    try:
        import simpleaudio

        print("✅ simpleaudio - OK")
    except ImportError:
        print("❌ simpleaudio - Missing (audio playback will not work)")
        print("   Install with: pip install simpleaudio")

    return True


def main():
    """Run all tests"""
    print("🧪 StoryTeller Setup Test")
    print("=" * 40)

    tests = [
        ("Imports", test_imports),
        ("API Credentials", test_api_credentials),
        ("Character Creation", test_character_creation),
        ("Audio Libraries", test_audio_libraries),
    ]

    # Only test API connection if credentials are available
    if os.getenv("mini") and os.getenv("group"):
        tests.append(("API Connection", test_api_connection))

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")

    print(f"\n{'='*50}")
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! StoryTeller is ready to use.")
        print("\n🚀 You can now run:")
        print("   python main.py          # Basic story generation")
        print("   python example_usage.py # Various examples")
        print("   python interactive_storyteller.py # Interactive interface")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")

        if not os.getenv("mini"):
            print("\n🔧 To fix API issues:")
            print("   Add to your .env file:")
            print("   mini=your_api_key_here")
            print("   group=your_group_id_here")

        if passed < 2:  # If imports failed
            print("\n🔧 To fix import issues:")
            print("   pip install -r requirements.txt")


if __name__ == "__main__":
    main()
