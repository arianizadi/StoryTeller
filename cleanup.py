#!/usr/bin/env python3
"""
Cleanup script for StoryTeller application
Deletes all generated files and directories
"""

import os
import shutil
import glob


def cleanup_generated_files():
    """Delete all generated files and directories"""
    print("🧹 StoryTeller Cleanup Script")
    print("=" * 40)

    # Files and directories to delete
    items_to_delete = [
        "audio_output/",
        "interactive_audio/",
        "story_script.txt",
        "complete_story.mp3",
        "example_script.txt",
        "custom_script.txt",
        "streaming_script.txt",
        "example_audio/",
        "custom_audio/",
        "streaming_audio/",
    ]

    # Also delete any .mp3 files in the root directory
    mp3_files = glob.glob("*.mp3")
    items_to_delete.extend(mp3_files)

    # Also delete any script files in the root directory
    script_files = glob.glob("*_script.txt")
    items_to_delete.extend(script_files)

    deleted_count = 0
    skipped_count = 0

    for item in items_to_delete:
        if os.path.exists(item):
            try:
                if os.path.isdir(item):
                    shutil.rmtree(item)
                    print(f"🗑️  Deleted directory: {item}")
                else:
                    os.remove(item)
                    print(f"🗑️  Deleted file: {item}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Error deleting {item}: {e}")
                skipped_count += 1
        else:
            print(f"⏭️  Skipped (not found): {item}")
            skipped_count += 1

    print("\n" + "=" * 40)
    print(f"✅ Cleanup complete!")
    print(f"   Deleted: {deleted_count} items")
    print(f"   Skipped: {skipped_count} items")

    # Check if there are any remaining generated files
    remaining_files = []
    for pattern in ["*.mp3", "*_script.txt", "audio_*", "*_audio"]:
        remaining_files.extend(glob.glob(pattern))

    if remaining_files:
        print(f"\n⚠️  Remaining files that might be generated:")
        for file in remaining_files:
            print(f"   - {file}")
    else:
        print(f"\n✨ All generated files cleaned up successfully!")


def confirm_cleanup():
    """Ask for confirmation before cleanup"""
    print("⚠️  WARNING: This will delete ALL generated files!")
    print("   - Audio files (*.mp3)")
    print("   - Story scripts (*_script.txt)")
    print("   - Audio directories (audio_output/, interactive_audio/, etc.)")
    print("   - Complete story files")
    print()

    response = input("Are you sure you want to continue? (yes/no): ").strip().lower()
    return response in ["yes", "y"]


if __name__ == "__main__":
    if confirm_cleanup():
        cleanup_generated_files()
    else:
        print("❌ Cleanup cancelled.")
