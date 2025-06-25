#!/usr/bin/env python3
"""
Test script to demonstrate cost optimization features
Shows the difference between using expensive vs cheap models
"""

import os
from main import MiniMaxStoryTeller, Character


def test_cost_optimization():
    """Test the cost optimization features"""
    print("🧪 TESTING COST OPTIMIZATION")
    print("=" * 60)

    # Load environment variables
    API_KEY = os.getenv("mini")
    GROUP_ID = os.getenv("group")

    if not API_KEY or not GROUP_ID:
        print(
            "❌ Missing API credentials. Please set 'mini' and 'group' environment variables."
        )
        return

    # Create storyteller instance
    storyteller = MiniMaxStoryTeller(API_KEY, GROUP_ID)

    print("📊 Model Configuration:")
    print(
        f"  Story Generation: {storyteller.MODELS['story_generation']} (Thinking model)"
    )
    print(f"  Name Analysis: {storyteller.MODELS['name_analysis']} (Fast/cheap model)")
    print(f"  Simple Tasks: {storyteller.MODELS['simple_tasks']} (Fast/cheap model)")

    print("\n💰 Cost Comparison (Official MiniMax Pricing):")
    print(f"  MiniMax-M1:")
    print(f"    Input: ${storyteller.MODEL_COSTS['MiniMax-M1']['input']:.3f}/1M tokens")
    print(
        f"    Output: ${storyteller.MODEL_COSTS['MiniMax-M1']['output']:.3f}/1M tokens"
    )
    print(f"    Description: {storyteller.MODEL_COSTS['MiniMax-M1']['description']}")

    print(f"  MiniMax-Text-01:")
    print(
        f"    Input: ${storyteller.MODEL_COSTS['MiniMax-Text-01']['input']:.3f}/1M tokens"
    )
    print(
        f"    Output: ${storyteller.MODEL_COSTS['MiniMax-Text-01']['output']:.3f}/1M tokens"
    )
    print(
        f"    Description: {storyteller.MODEL_COSTS['MiniMax-Text-01']['description']}"
    )

    # Calculate cost difference
    m1_avg_cost = (
        storyteller.MODEL_COSTS["MiniMax-M1"]["input"]
        + storyteller.MODEL_COSTS["MiniMax-M1"]["output"]
    ) / 2
    text01_avg_cost = (
        storyteller.MODEL_COSTS["MiniMax-Text-01"]["input"]
        + storyteller.MODEL_COSTS["MiniMax-Text-01"]["output"]
    ) / 2
    cost_ratio = m1_avg_cost / text01_avg_cost

    print(
        f"\n  Cost difference: MiniMax-M1 is {cost_ratio:.1f}x more expensive than MiniMax-Text-01"
    )
    print(
        f"  Savings: Using MiniMax-Text-01 saves {(cost_ratio-1)*100:.0f}% on text operations"
    )

    # Test name analysis with different names
    test_names = [
        "Kael",
        "Elara",
        "Voryn",
        "Thalos",
        "Luna",
        "Marcus",
        "Shadow",
        "Sage",
    ]

    print(f"\n🔍 Testing AI Name Analysis ({len(test_names)} names):")
    for name in test_names:
        print(f"  Analyzing: {name}")
        analysis = storyteller.analyze_character_name_with_ai(name)
        print(
            f"    Result: {analysis['gender']}, {analysis['personality_trait']}, confidence: {analysis['confidence']}"
        )

    # Test story generation (this will use the expensive model)
    print(f"\n📖 Testing Story Generation (using thinking model):")
    story = storyteller.generate_story(
        genre="fantasy",
        theme="friendship and courage",
        characters=["hero", "friend", "villain"],
        length="medium",
    )

    if story:
        print(f"  ✅ Story generated successfully ({len(story.split())} words)")

        # Parse and analyze character names
        print(f"\n🎭 Testing Character Name Mapping:")
        segments = storyteller.parse_story_into_segments(story)
        for i, segment in enumerate(segments[:5]):  # Show first 5 segments
            print(f"  {i+1}. {segment.character.name} → {segment.character.voice_id}")
    else:
        print(f"  ❌ Story generation failed")

    # Display final usage statistics
    print(f"\n📊 FINAL USAGE STATISTICS:")
    storyteller.print_usage_summary()

    print(f"\n✅ Cost optimization test completed!")
    print(f"💡 Key benefits:")
    print(f"   - Story generation uses expensive thinking model for creativity")
    print(f"   - Name analysis uses cheap fast model for efficiency")
    print(f"   - Automatic cost tracking and optimization suggestions")
    print(f"   - Caching reduces repeated API calls")


if __name__ == "__main__":
    test_cost_optimization()
