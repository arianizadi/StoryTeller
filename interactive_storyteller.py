#!/usr/bin/env python3
"""
Interactive StoryTeller - Command-line interface for creating stories
"""

import os
import sys
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


class InteractiveStoryTeller:
    """Interactive command-line interface for story creation"""

    def __init__(self):
        self.api_key = os.getenv("mini")
        self.group_id = os.getenv("group")

        if not self.api_key or not self.group_id:
            print("❌ Error: MiniMax API credentials not found!")
            print("Please set your credentials in your .env file:")
            print("mini=your_api_key_here")
            print("group=your_group_id_here")
            print("\nOr set environment variables:")
            print("export mini='your_api_key'")
            print("export group='your_group_id'")
            sys.exit(1)

        self.storyteller = MiniMaxStoryTeller(self.api_key, self.group_id)
        self.current_story = None
        self.current_segments = []

    def clear_screen(self):
        """Clear the terminal screen"""
        os.system("cls" if os.name == "nt" else "clear")

    def print_header(self):
        """Print the application header"""
        print("🎭" + "=" * 50 + "🎭")
        print("           STORYTELLER - AI Story Creator")
        print("🎭" + "=" * 50 + "🎭")
        print()

    def print_menu(self, title, options):
        """Print a formatted menu"""
        print(f"\n📋 {title}")
        print("-" * 40)
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        print("0. Back/Exit")
        print("-" * 40)

    def get_user_choice(self, max_options):
        """Get user choice from menu"""
        while True:
            try:
                choice = input("\n🎯 Enter your choice (0-{}): ".format(max_options))
                choice = int(choice)
                if 0 <= choice <= max_options:
                    return choice
                else:
                    print("❌ Invalid choice. Please try again.")
            except ValueError:
                print("❌ Please enter a valid number.")

    def main_menu(self):
        """Main menu of the application"""
        while True:
            self.clear_screen()
            self.print_header()

            options = [
                "Create a Quick Story (Preset)",
                "Create a Custom Story",
                "Manage Characters",
                "View Available Genres",
                "Generate Audio for Existing Story",
                "Exit",
            ]

            self.print_menu("Main Menu", options)
            choice = self.get_user_choice(len(options))

            if choice == 0:
                print("👋 Goodbye!")
                break
            elif choice == 1:
                self.quick_story_menu()
            elif choice == 2:
                self.custom_story_menu()
            elif choice == 3:
                self.character_management_menu()
            elif choice == 4:
                self.view_genres()
            elif choice == 5:
                self.generate_audio_menu()

    def quick_story_menu(self):
        """Menu for creating quick stories with presets"""
        while True:
            self.clear_screen()
            self.print_header()

            options = [
                "Fantasy Adventure",
                "Mystery Detective",
                "Space Exploration",
                "Romantic Tale",
                "Comedy Adventure",
            ]

            self.print_menu("Quick Story Presets", options)
            choice = self.get_user_choice(len(options))

            if choice == 0:
                break
            elif choice == 1:
                self.create_preset_story("fantasy")
            elif choice == 2:
                self.create_preset_story("mystery")
            elif choice == 3:
                self.create_preset_story("sci-fi")
            elif choice == 4:
                self.create_preset_story("romance")
            elif choice == 5:
                self.create_preset_story("comedy")

    def create_preset_story(self, story_type):
        """Create a story using preset configurations"""
        self.clear_screen()
        self.print_header()

        print(f"🎬 Creating {story_type} story...")
        print("⏳ This may take a few moments...")

        # Reset storyteller characters
        self.storyteller = MiniMaxStoryTeller(self.api_key, self.group_id)

        if story_type == "fantasy":
            setup = create_fantasy_story_setup()
        elif story_type == "mystery":
            setup = create_mystery_story_setup()
        elif story_type == "sci-fi":
            setup = create_adventure_story_setup()
            setup["genre"] = "sci-fi"
            setup["theme"] = "space exploration and discovery"
        elif story_type == "romance":
            setup = create_adventure_story_setup()
            setup["genre"] = "romance"
            setup["theme"] = "finding true love"
        elif story_type == "comedy":
            setup = create_adventure_story_setup()
            setup["genre"] = "comedy"
            setup["theme"] = "funny misadventures"

        # Add characters to storyteller
        for char in setup["characters"]:
            self.storyteller.add_character(char)

        # Generate story
        character_names = [char.name.lower() for char in setup["characters"]]
        story = self.storyteller.generate_story(
            genre=setup["genre"],
            theme=setup["theme"],
            characters=character_names,
            length=setup["length"],
        )

        if story:
            self.current_story = story
            self.current_segments = self.storyteller.parse_story_into_segments(story)

            self.clear_screen()
            self.print_header()
            print("✅ Story generated successfully!")
            print(f"📖 Genre: {setup['genre'].title()}")
            print(f"🎯 Theme: {setup['theme']}")
            print(f"👥 Characters: {len(setup['characters'])}")
            print(f"📝 Segments: {len(self.current_segments)}")

            self.story_actions_menu()
        else:
            print("❌ Failed to generate story. Please try again.")
            input("\nPress Enter to continue...")

    def story_actions_menu(self):
        """Menu for actions after story generation"""
        while True:
            print("\n🎭 Story Actions:")
            print("-" * 30)
            print("1. 📖 View Story")
            print("2. 🎵 Generate Audio")
            print("3. 💾 Save Story Script")
            print("4. 🎧 Play Audio Sample")
            print("5. 🔄 Create New Story")
            print("0. Back to Main Menu")
            print("-" * 30)

            choice = self.get_user_choice(5)

            if choice == 0:
                break
            elif choice == 1:
                self.view_story()
            elif choice == 2:
                self.generate_audio()
            elif choice == 3:
                self.save_story_script()
            elif choice == 4:
                self.play_audio_sample()
            elif choice == 5:
                return  # Go back to main menu

    def view_story(self):
        """Display the generated story"""
        self.clear_screen()
        self.print_header()
        print("📖 Generated Story")
        print("=" * 50)
        print(self.current_story)
        print("=" * 50)
        input("\nPress Enter to continue...")

    def generate_audio(self):
        """Generate audio for the story"""
        self.clear_screen()
        self.print_header()
        print("🎵 Generating Audio...")
        print("⏳ This may take several minutes...")

        audio_files = self.storyteller.generate_full_story_audio("interactive_audio")

        print(f"\n✅ Generated {len(audio_files)} audio files!")
        print("📁 Check the 'interactive_audio' directory for audio files.")

        input("\nPress Enter to continue...")

    def save_story_script(self):
        """Save the story script to file"""
        filename = "interactive_story_script.txt"
        self.storyteller.create_story_script(filename)
        print(f"✅ Story script saved to: {filename}")
        input("\nPress Enter to continue...")

    def play_audio_sample(self):
        """Play a sample audio file"""
        if not self.current_segments:
            print("❌ No story segments available.")
            input("\nPress Enter to continue...")
            return

        # Find first segment with audio
        for segment in self.current_segments:
            if segment.audio_file and os.path.exists(segment.audio_file):
                print(f"🎧 Playing: {segment.character.name}")
                print(f"📝 Text: {segment.text}")
                self.storyteller.play_audio_file(segment.audio_file)
                break
        else:
            print("❌ No audio files found. Generate audio first.")

        input("\nPress Enter to continue...")

    def custom_story_menu(self):
        """Menu for creating custom stories"""
        self.clear_screen()
        self.print_header()

        print("🎨 Custom Story Creation")
        print("=" * 40)

        # Get genre
        genres = get_available_genres()
        print("\n📚 Available Genres:")
        for i, genre in enumerate(genres, 1):
            info = get_genre_info(genre)
            print(f"{i}. {genre.title()} - {info['description']}")

        genre_choice = self.get_user_choice(len(genres))
        if genre_choice == 0:
            return

        selected_genre = genres[genre_choice - 1]

        # Get theme
        print(f"\n🎯 Enter a theme for your {selected_genre} story:")
        theme = input("Theme: ").strip()
        if not theme:
            theme = "adventure and discovery"

        # Get characters
        print(f"\n👥 Select characters for your story:")
        available_chars = get_available_characters()

        selected_characters = []
        while True:
            print(
                f"\nCurrent characters: {[c.name for c in selected_characters] if selected_characters else 'None'}"
            )
            print("\nAvailable character templates:")
            for i, char in enumerate(available_chars, 1):
                print(f"{i}. {char.title()}")

            char_choice = self.get_user_choice(len(available_chars))
            if char_choice == 0:
                break

            char_name = available_chars[char_choice - 1]
            custom_name = input(
                f"Enter custom name for {char_name} (or press Enter to use default): "
            ).strip()

            character = create_character_from_template(char_name, custom_name)
            selected_characters.append(character)

            if len(selected_characters) >= 4:
                print("✅ Maximum 4 characters reached.")
                break

        if not selected_characters:
            print("❌ No characters selected. Using default characters.")
            selected_characters = [
                create_character_from_template("hero"),
                create_character_from_template("friend"),
            ]

        # Get story length
        print("\n📏 Select story length:")
        lengths = ["short", "medium", "long"]
        for i, length in enumerate(lengths, 1):
            print(f"{i}. {length.title()}")

        length_choice = self.get_user_choice(len(lengths))
        if length_choice == 0:
            return

        selected_length = lengths[length_choice - 1]

        # Generate story
        print(f"\n🎬 Generating {selected_genre} story...")
        print("⏳ This may take a few moments...")

        # Reset storyteller and add characters
        self.storyteller = MiniMaxStoryTeller(self.api_key, self.group_id)
        for char in selected_characters:
            self.storyteller.add_character(char)

        character_names = [char.name.lower() for char in selected_characters]
        story = self.storyteller.generate_story(
            genre=selected_genre,
            theme=theme,
            characters=character_names,
            length=selected_length,
        )

        if story:
            self.current_story = story
            self.current_segments = self.storyteller.parse_story_into_segments(story)

            self.clear_screen()
            self.print_header()
            print("✅ Custom story generated successfully!")
            print(f"📖 Genre: {selected_genre.title()}")
            print(f"🎯 Theme: {theme}")
            print(f"👥 Characters: {len(selected_characters)}")
            print(f"📝 Segments: {len(self.current_segments)}")

            self.story_actions_menu()
        else:
            print("❌ Failed to generate story. Please try again.")
            input("\nPress Enter to continue...")

    def character_management_menu(self):
        """Menu for managing characters"""
        while True:
            self.clear_screen()
            self.print_header()

            print("👥 Character Management")
            print("=" * 30)
            print("1. 📋 View Available Characters")
            print("2. 🎭 View Available Voices")
            print("3. ➕ Add Custom Character")
            print("0. Back to Main Menu")
            print("=" * 30)

            choice = self.get_user_choice(3)

            if choice == 0:
                break
            elif choice == 1:
                self.view_available_characters()
            elif choice == 2:
                self.view_available_voices()
            elif choice == 3:
                self.add_custom_character()

    def view_available_characters(self):
        """Display available character templates"""
        self.clear_screen()
        self.print_header()
        print("📋 Available Character Templates")
        print("=" * 50)

        characters = get_available_characters()
        for i, char_name in enumerate(characters, 1):
            char = create_character_from_template(char_name)
            print(f"{i}. {char.name}")
            print(f"   Description: {char.description}")
            print(f"   Voice: {char.voice_id}")
            print(f"   Speed: {char.speed}, Volume: {char.volume}, Pitch: {char.pitch}")
            print("-" * 30)

        input("\nPress Enter to continue...")

    def view_available_voices(self):
        """Display available voice options"""
        self.clear_screen()
        self.print_header()
        print("🎭 Available Voice Options")
        print("=" * 30)

        from config import VOICE_IDS

        for voice_key, voice_id in VOICE_IDS.items():
            print(f"• {voice_key}: {voice_id}")

        input("\nPress Enter to continue...")

    def add_custom_character(self):
        """Add a custom character"""
        self.clear_screen()
        self.print_header()
        print("➕ Add Custom Character")
        print("=" * 30)

        name = input("Character name: ").strip()
        if not name:
            print("❌ Name is required.")
            input("\nPress Enter to continue...")
            return

        # Ensure proper capitalization for character names
        name = name.title()

        description = input("Character description: ").strip()
        if not description:
            description = "A custom character"

        # Get voice settings
        print("\nVoice settings:")
        speed = float(input("Speed (0.5-2.0, default 1.0): ") or "1.0")
        volume = float(input("Volume (0.0-2.0, default 1.0): ") or "1.0")
        pitch = float(input("Pitch (-1.0 to 1.0, default 0.0): ") or "0.0")

        # Get voice ID
        from config import VOICE_IDS

        print("\nAvailable voices:")
        voice_keys = list(VOICE_IDS.keys())
        for i, voice_key in enumerate(voice_keys, 1):
            print(f"{i}. {voice_key}")

        voice_choice = self.get_user_choice(len(voice_keys))
        if voice_choice == 0:
            return

        voice_id = VOICE_IDS[voice_keys[voice_choice - 1]]

        # Create character
        character = Character(name, description, voice_id, speed, volume, pitch)
        self.storyteller.add_character(character)

        print(f"✅ Added character: {name}")
        input("\nPress Enter to continue...")

    def view_genres(self):
        """Display available genres"""
        self.clear_screen()
        self.print_header()
        print("📚 Available Story Genres")
        print("=" * 50)

        from config import STORY_GENRES

        for genre, info in STORY_GENRES.items():
            print(f"🎭 {genre.title()}")
            print(f"   Description: {info['description']}")
            print(f"   Common characters: {', '.join(info['common_characters'])}")
            print(f"   Themes: {', '.join(info['themes'])}")
            print("-" * 40)

        input("\nPress Enter to continue...")

    def generate_audio_menu(self):
        """Menu for generating audio for existing stories"""
        self.clear_screen()
        self.print_header()

        if not self.current_story:
            print("❌ No story available. Create a story first.")
            input("\nPress Enter to continue...")
            return

        print("🎵 Generate Audio for Current Story")
        print("=" * 40)
        print(f"📝 Story has {len(self.current_segments)} segments")

        print("\nAudio generation options:")
        print("1. 🎵 Standard Audio Generation")
        print("2. ⚡ Streaming Audio Generation (Faster)")
        print("0. Back")

        choice = self.get_user_choice(2)

        if choice == 1:
            self.generate_audio()
        elif choice == 2:
            self.generate_streaming_audio()

    def generate_streaming_audio(self):
        """Generate audio using streaming"""
        self.clear_screen()
        self.print_header()
        print("⚡ Generating Audio (Streaming)...")
        print("⏳ This may take several minutes...")

        import asyncio

        audio_files = asyncio.run(
            self.storyteller.generate_full_story_audio_streaming("interactive_audio")
        )

        print(f"\n✅ Generated {len(audio_files)} audio files using streaming!")
        print("📁 Check the 'interactive_audio' directory for audio files.")

        input("\nPress Enter to continue...")


def main():
    """Main function"""
    try:
        app = InteractiveStoryTeller()
        app.main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your API credentials and try again.")


if __name__ == "__main__":
    main()
