#!/usr/bin/env python3
"""
Audio Creator Script
Combines individual character audio files into a single story MP3
"""

import os
import glob
import re
from typing import List, Tuple
from pydub import AudioSegment
import argparse


class AudioCreator:
    def __init__(self, audio_dir: str = "audio_output"):
        self.audio_dir = audio_dir
        self.combined_audio = None

    def get_audio_files_in_order(self) -> List[str]:
        """Get audio files sorted by their segment order from story_script.txt"""
        print(f"🔧 DEBUG: Looking for audio files in {self.audio_dir}")

        # First, try to get order from story_script.txt
        script_order = self.get_order_from_script()
        if script_order:
            print(f"🔧 DEBUG: Found {len(script_order)} segments in script")
            return script_order

        # Fallback: get all mp3 files and sort by timestamp
        print(f"🔧 DEBUG: No script found, using file timestamp order")
        audio_files = glob.glob(os.path.join(self.audio_dir, "*.mp3"))
        if not audio_files:
            print(f"❌ No audio files found in {self.audio_dir}")
            return []

        # Sort by timestamp in filename (format: Character_timestamp.mp3)
        def extract_timestamp(filename):
            match = re.search(r"_(\d+)\.mp3$", filename)
            return int(match.group(1)) if match else 0

        audio_files.sort(key=extract_timestamp)
        return audio_files

    def get_order_from_script(self) -> List[str]:
        """Extract audio file order from story_script.txt"""
        script_file = "story_script.txt"
        if not os.path.exists(script_file):
            return []

        audio_files = []
        try:
            with open(script_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract audio file paths from script
            audio_pattern = r"Audio: (audio_output/[^\n]+)"
            matches = re.findall(audio_pattern, content)

            # Verify files exist
            for audio_path in matches:
                if os.path.exists(audio_path):
                    audio_files.append(audio_path)
                else:
                    print(f"⚠️ Warning: Audio file not found: {audio_path}")

            print(f"🔧 DEBUG: Found {len(audio_files)} audio files from script")
            return audio_files

        except Exception as e:
            print(f"❌ Error reading script file: {e}")
            return []

    def combine_audio_files(
        self, audio_files: List[str], output_file: str = "complete_story.mp3"
    ) -> bool:
        """Combine multiple audio files into one"""
        if not audio_files:
            print("❌ No audio files to combine")
            return False

        print(f"🔧 DEBUG: Starting audio combination")
        print(f"🔧 DEBUG: Number of files to combine: {len(audio_files)}")

        try:
            # Start with the first audio file
            print(f"🔧 DEBUG: Loading first file: {audio_files[0]}")
            combined = AudioSegment.from_mp3(audio_files[0])

            # Add each subsequent file
            for i, audio_file in enumerate(audio_files[1:], 1):
                print(f"🔧 DEBUG: Adding file {i+1}/{len(audio_files)}: {audio_file}")
                audio_segment = AudioSegment.from_mp3(audio_file)

                # Add a small pause between segments (0.5 seconds)
                pause = AudioSegment.silent(duration=500)
                combined += pause + audio_segment

                print(f"🔧 DEBUG: Combined duration so far: {len(combined)}ms")

            # Export the combined audio
            print(f"🔧 DEBUG: Exporting combined audio to {output_file}")
            combined.export(output_file, format="mp3")

            print(f"✅ Successfully created: {output_file}")
            print(f"📊 Total duration: {len(combined)/1000:.2f} seconds")
            print(f"📊 Total size: {os.path.getsize(output_file)/1024/1024:.2f} MB")

            self.combined_audio = combined
            return True

        except Exception as e:
            print(f"❌ Error combining audio files: {e}")
            return False

    def play_combined_audio(self, audio_file: str = "complete_story.mp3"):
        """Play the combined audio file"""
        if not os.path.exists(audio_file):
            print(f"❌ Audio file not found: {audio_file}")
            return

        try:
            from pydub.playback import play

            print(f"🔧 DEBUG: Playing combined audio: {audio_file}")
            audio = AudioSegment.from_mp3(audio_file)
            print(f"🎵 Playing complete story ({len(audio)/1000:.2f} seconds)...")
            play(audio)
            print("✅ Playback completed")
        except ImportError:
            print("❌ pydub.playback not available. Install simpleaudio for playback.")
            print(f"📁 Audio file saved: {audio_file}")
        except Exception as e:
            print(f"❌ Error playing audio: {e}")

    def create_story_with_pauses(
        self,
        audio_files: List[str],
        output_file: str = "complete_story.mp3",
        pause_duration: int = 1000,
    ) -> bool:
        """Create combined audio with custom pause durations"""
        if not audio_files:
            print("❌ No audio files to combine")
            return False

        print(f"🔧 DEBUG: Creating story with {pause_duration}ms pauses")

        try:
            combined = AudioSegment.from_mp3(audio_files[0])
            pause = AudioSegment.silent(duration=pause_duration)

            for i, audio_file in enumerate(audio_files[1:], 1):
                print(f"🔧 DEBUG: Adding segment {i+1}/{len(audio_files)}")
                audio_segment = AudioSegment.from_mp3(audio_file)
                combined += pause + audio_segment

            combined.export(output_file, format="mp3")
            print(f"✅ Created: {output_file} with {pause_duration}ms pauses")
            return True

        except Exception as e:
            print(f"❌ Error: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Combine audio files into a single story"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default="audio_output",
        help="Directory containing audio files (default: audio_output)",
    )
    parser.add_argument(
        "--output", default="complete_story.mp3", help="Output file name"
    )
    parser.add_argument(
        "--pause", type=int, default=500, help="Pause duration between segments (ms)"
    )
    parser.add_argument(
        "--play", action="store_true", help="Play the combined audio after creation"
    )
    parser.add_argument(
        "--list", action="store_true", help="List available audio files"
    )

    args = parser.parse_args()

    # Use the directory argument
    audio_dir = args.directory

    # Check if directory exists
    if not os.path.exists(audio_dir):
        print(f"❌ Directory not found: {audio_dir}")
        print(f"💡 Available directories:")
        for item in os.listdir("."):
            if os.path.isdir(item) and any(
                f.endswith(".mp3")
                for f in os.listdir(item)
                if os.path.isfile(os.path.join(item, f))
            ):
                print(f"   - {item}/")
        return

    # Create audio creator
    creator = AudioCreator(audio_dir)

    # List files if requested
    if args.list:
        audio_files = creator.get_audio_files_in_order()
        if audio_files:
            print(f"\n📁 Available audio files in {audio_dir}/ ({len(audio_files)}):")
            for i, file in enumerate(audio_files, 1):
                duration = len(AudioSegment.from_mp3(file)) / 1000
                print(f"  {i:2d}. {os.path.basename(file)} ({duration:.1f}s)")
        else:
            print(f"❌ No audio files found in {audio_dir}/")
        return

    # Get audio files in order
    audio_files = creator.get_audio_files_in_order()
    if not audio_files:
        print(f"❌ No audio files found in {audio_dir}/")
        print("💡 Make sure the directory contains .mp3 files")
        return

    print(f"🎵 Found {len(audio_files)} audio files in {audio_dir}/")

    # Combine audio files
    success = creator.combine_audio_files(audio_files, args.output)

    if success and args.play:
        creator.play_combined_audio(args.output)


if __name__ == "__main__":
    main()
