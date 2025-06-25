#!/usr/bin/env python3
"""
Simple Story Audio Creator
Easy-to-use script to combine story audio files into one MP3
"""

from audio_creator import AudioCreator
import os
import sys


def main():
    print("🎵 Story Audio Creator")
    print("=" * 40)

    # Check for directory argument
    audio_dir = "audio_output"
    if len(sys.argv) > 1:
        audio_dir = sys.argv[1]
        print(f"📁 Using directory: {audio_dir}")

    # Check if directory exists
    if not os.path.exists(audio_dir):
        print(f"❌ Directory not found: {audio_dir}")
        print("\n💡 Available directories with audio files:")
        found_dirs = []
        for item in os.listdir("."):
            if os.path.isdir(item):
                mp3_files = [f for f in os.listdir(item) if f.endswith(".mp3")]
                if mp3_files:
                    found_dirs.append(item)
                    print(f"   - {item}/ ({len(mp3_files)} files)")

        if not found_dirs:
            print("   No directories with .mp3 files found")
            print("   Run 'python main.py' first to generate audio files")
        return

    # Create audio creator
    creator = AudioCreator(audio_dir)

    # Get audio files
    audio_files = creator.get_audio_files_in_order()

    if not audio_files:
        print(f"❌ No audio files found in {audio_dir}/")
        print("💡 Make sure the directory contains .mp3 files")
        return

    print(f"🎵 Found {len(audio_files)} audio files in {audio_dir}/")

    # Show available files
    print("\n📁 Audio files to combine:")
    for i, file in enumerate(audio_files, 1):
        filename = os.path.basename(file)
        print(f"  {i:2d}. {filename}")

    # Ask user for preferences
    print("\n⚙️ Options:")
    print("1. Create with short pauses (0.5s) - Recommended")
    print("2. Create with long pauses (1.0s)")
    print("3. Create without pauses")

    choice = input("\nEnter your choice (1-3): ").strip()

    pause_duration = 500  # Default 0.5 seconds
    if choice == "2":
        pause_duration = 1000  # 1.0 seconds
    elif choice == "3":
        pause_duration = 0  # No pauses

    # Ask for output filename
    output_file = input(
        "\nEnter output filename (default: complete_story.mp3): "
    ).strip()
    if not output_file:
        output_file = "complete_story.mp3"

    if not output_file.endswith(".mp3"):
        output_file += ".mp3"

    print(f"\n🎵 Creating combined audio file: {output_file}")

    # Combine audio files
    if pause_duration == 0:
        success = creator.combine_audio_files(audio_files, output_file)
    else:
        success = creator.create_story_with_pauses(
            audio_files, output_file, pause_duration
        )

    if success:
        print(f"\n✅ Successfully created: {output_file}")

        # Ask if user wants to play it
        play_choice = input("\n🎵 Play the combined audio? (y/n): ").strip().lower()
        if play_choice in ["y", "yes"]:
            creator.play_combined_audio(output_file)
        else:
            print(f"📁 Audio file saved as: {output_file}")
    else:
        print("❌ Failed to create combined audio file")


if __name__ == "__main__":
    main()
