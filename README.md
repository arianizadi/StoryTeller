# StoryTeller - AI-Powered Story Generation with Voice

A Python application that generates engaging stories using MiniMax's AI models and converts them into audio with distinct character voices.

<!-- Play Example Audio -->
<audio controls>
  <source src="./example_story.mp3" type="audio/mpeg">
</audio>

## Features

- **AI Story Generation**: Uses MiniMax-M1 model to create engaging stories with multiple characters
- **Character Management**: Define custom characters with unique voice settings
- **Text-to-Speech**: Convert story dialogue into audio using MiniMax's TTS API
- **Voice Customization**: Adjust speed, volume, pitch, and emotion for each character
- **Multiple Audio Formats**: Support for both HTTP API and WebSocket streaming
- **Story Scripting**: Generate detailed scripts with audio file references
- **Real-time Playback**: Play generated audio files directly (optional)

## Prerequisites

- Python 3.7 or higher
- MiniMax API credentials (API Key and Group ID)
- Audio playback libraries (optional)

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your MiniMax API credentials**:

   Create a `.env` file in the project directory:

   ```
   mini=your_api_key_here
   group=your_group_id_here
   ```

   Or set environment variables:

   ```bash
   export mini='your_api_key_here'
   export group='your_group_id_here'
   ```

## Rate Limits and API Usage

### MiniMax API Rate Limits

The application uses two MiniMax APIs with the following rate limits:

- **Chat Completion (MiniMax-M1)**: 120 RPM, 720,000 TPM
- **Text-to-Speech (speech-02-hd)**: 60 RPM, 20,000 TPM

### Built-in Rate Limiting Protection

The application includes automatic rate limiting protection:

- **Conservative Limits**: Uses 100 RPM for chat and 50 RPM for TTS (below official limits)
- **Automatic Delays**: Adds delays between requests to prevent hitting limits
- **Retry Logic**: Automatically retries failed requests due to rate limits
- **Progress Indicators**: Shows waiting times when rate limiting is active

### Tips for Avoiding Rate Limits

1. **Story Length**: Keep stories under 500 words to reduce token usage
2. **Character Count**: Limit to 3-4 characters to reduce TTS requests
3. **Batch Processing**: Generate audio for multiple stories with breaks between
4. **Monitor Usage**: Watch for rate limit warnings in the console output

### What Happens When Rate Limited

- The app will automatically wait and retry once
- Progress messages will show waiting times
- If limits are consistently hit, consider reducing story complexity

## Cost Optimization

### Smart Model Selection

The application uses intelligent model selection to optimize costs:

- **Story Generation**: Uses `MiniMax-M1` (thinking model) for creative, high-quality stories
- **Name Analysis**: Uses `MiniMax-ABAB5.5s` (fast/cheap model) for character name analysis
- **Simple Tasks**: Uses `MiniMax-ABAB5.5s` for any other AI tasks

### Cost Comparison

| Model           | Input Cost (per 1M tokens) | Output Cost (per 1M tokens) | Use Case                    | Quality               |
| --------------- | -------------------------- | --------------------------- | --------------------------- | --------------------- |
| MiniMax-M1      | $0.40                      | $2.20                       | Story generation            | High (thinking model) |
| MiniMax-Text-01 | $0.20                      | $1.10                       | Name analysis, simple tasks | Good (fast model)     |

**Cost savings**: Using MiniMax-Text-01 for name analysis saves **~2x** on input costs and **~2x** on output costs compared to MiniMax-M1.

### TTS Cost Comparison

| Model           | Cost per character | Use Case           | Quality      |
| --------------- | ------------------ | ------------------ | ------------ |
| speech-02-hd    | $0.0001            | High-quality audio | HD quality   |
| speech-02-turbo | $0.00006           | Fast generation    | Good quality |

**Cost savings**: Using speech-02-turbo saves **40%** compared to speech-02-hd.

### Automatic Cost Tracking

The application automatically tracks API usage and costs:

```bash
📊 API USAGE SUMMARY
============================================================
Total API calls: 12
Total tokens used: 2,847
Estimated total cost: $0.0062

📈 Breakdown by Model:
  MiniMax-M1:
    Calls: 1
    Description: Top-Tier Model: 80K CoT Length x 1M Input
    Tokens: 1,234
      Input: 864 tokens
      Output: 370 tokens
    Cost: $0.0009
    Input cost: $0.400/1M tokens
    Output cost: $2.200/1M tokens
  MiniMax-Text-01:
    Calls: 11
    Description: Text model, new model architecture, 1000k content length
    Tokens: 1,613
      Input: 1,129 tokens
      Output: 484 tokens
    Cost: $0.0008
    Input cost: $0.200/1M tokens
    Output cost: $1.100/1M tokens

💰 Cost Optimization:
  Most expensive model: MiniMax-M1 ($0.0009)
  Most used model: MiniMax-Text-01 (11 calls)
  Potential savings using MiniMax-Text-01: $0.0001
============================================================
```

### Cost Optimization Features

1. **Model Caching**: Repeated name analysis uses cached results
2. **Smart Fallbacks**: Falls back to pattern matching if AI analysis fails
3. **Usage Statistics**: Real-time cost tracking and breakdown
4. **Optimization Suggestions**: Shows potential savings

### Testing Cost Optimization

Run the cost optimization test:

```bash
python test_cost_optimization.py
```

This demonstrates:

- Model selection differences
- Cost tracking in action
- Performance comparisons
- Optimization suggestions

## Usage

### Basic Usage

Run the main application:

```bash
python main.py
```

This will:

1. Generate a fantasy story with the theme "friendship and courage"
2. Parse the story into character dialogue segments
3. Generate audio files for each character's dialogue
4. Create a story script file
5. Play a sample audio file

### Interactive Interface

For a user-friendly interface:

```bash
python interactive_storyteller.py
```

This provides:

- Menu-driven story creation
- Character management
- Audio generation options
- Real-time story viewing

### Custom Story Generation

```python
from main import MiniMaxStoryTeller, Character

# Initialize the storyteller
storyteller = MiniMaxStoryTeller(API_KEY, GROUP_ID)

# Add custom characters
storyteller.add_character(Character(
    "Wizard",
    "A wise and powerful magic user",
    "Wise_Woman",
    0.9, 1.0, 0.0, "mysterious"
))

# Generate a custom story
story = storyteller.generate_story(
    genre="sci-fi",
    theme="exploration and discovery",
    characters=["hero", "friend", "wizard"],
    length="long"
)

# Parse and generate audio
segments = storyteller.parse_story_into_segments(story)
audio_files = storyteller.generate_full_story_audio()
```

### Character Configuration

Each character can be customized with:

- **name**: Character's name
- **description**: Character's personality/role
- **voice_id**: MiniMax voice ID (e.g., "Wise_Woman", "male-qn-qingse")
- **speed**: Speech speed (0.5 - 2.0)
- **volume**: Volume level (0.0 - 2.0)
- **pitch**: Pitch adjustment (-1.0 to 1.0)
- **emotion**: Emotional tone ("happy", "sad", "angry", "calm", etc.)

### Available Voice IDs

Some popular MiniMax voice IDs:

- `English_expressive_narrator` - Professional narrator voice
- `English_radiant_girl` - Young, friendly female voice
- `English_CalmWoman` - Calm, mature female voice
- `English_Graceful_Lady` - Elegant female voice
- `English_magnetic_voiced_man` - Charismatic male voice
- `English_Trustworth_Man` - Reliable male voice
- `English_ReservedYoungMan` - Young male voice
- `English_ManWithDeepVoice` - Deep, powerful voice (great for villains)
- `English_WiseScholar` - Wise, scholarly voice
- `English_PlayfulGirl` - Young, playful voice

**Note**: These English voice IDs are confirmed to work with the current MiniMax API. You can run `python get_available_voices.py` to see all 333+ available voices in your account.

## API Integration

### MiniMax Chat Completion

The app uses MiniMax-M1 for story generation with:

- Temperature: 0.8 (creative but coherent)
- Max tokens: 2000
- Structured prompts for character dialogue

### MiniMax Text-to-Speech

Two TTS methods are supported:

1. **HTTP API** (synchronous):

   - Model: `speech-02-hd`
   - Format: MP3
   - Sample rate: 32kHz
   - Bitrate: 128kbps

2. **WebSocket Streaming** (asynchronous):
   - Real-time audio generation
   - Better for long stories
   - Reduced latency

## Output Files

The application generates several output files:

- **audio_output/**: Directory containing MP3 audio files
- **story_script.txt**: Complete script with character dialogue and audio references
- **Individual audio files**: Named by character and timestamp

## Advanced Features

### Streaming Audio Generation

For better performance with long stories:

```python
import asyncio

async def generate_streaming_audio():
    audio_files = await storyteller.generate_full_story_audio_streaming()
    return audio_files

# Run the async function
audio_files = asyncio.run(generate_streaming_audio())
```

### Custom Story Prompts

Modify the story generation prompt:

```python
def custom_prompt(genre, theme, characters):
    return f"""Create a {genre} story about {theme}.
    Include these characters: {', '.join(characters)}
    Make it engaging and include lots of dialogue."""
```

### Audio Playback

Play generated audio files:

```python
# Play a specific audio file
storyteller.play_audio_file("audio_output/Hero_1234567890.mp3")

# Play all audio files in sequence
for segment in storyteller.story_segments:
    if segment.audio_file:
        storyteller.play_audio_file(segment.audio_file)
```

## Testing

Test your setup and API connectivity:

```bash
python test_setup.py
```

This will verify:

- All required dependencies are installed
- API credentials are properly configured
- API connection is working
- Character creation functionality

## Error Handling

The application includes comprehensive error handling for:

- API authentication failures
- Network connectivity issues
- Audio generation failures
- File I/O errors

## Troubleshooting

### Common Issues

1. **API Key Error**: Ensure your MiniMax API credentials are correctly set in `.env` file
2. **Audio Playback**: Install `pydub` and `simpleaudio` for audio playback
3. **WebSocket Issues**: Check firewall settings for WebSocket connections
4. **Memory Issues**: For very long stories, use streaming audio generation

### Dependencies

If you encounter import errors:

```bash
# Install audio dependencies
pip install pydub simpleaudio

# On macOS, you might need:
brew install ffmpeg

# On Ubuntu/Debian:
sudo apt-get install ffmpeg
```

## Example Output

### Generated Story

```
NARRATOR: In a mystical forest where ancient trees whispered secrets to the wind, a young hero named Alex stood at the edge of an enchanted clearing.

HERO: I can feel the magic in the air. Something important is about to happen.

FRIEND: Don't be afraid, Alex. We're in this together.

VILLAIN: Foolish children! You dare to enter my domain?
```

### Story Script

```
STORY SCRIPT
==================================================

Segment 1:
Character: Narrator
Voice: Wise_Woman
Text: In a mystical forest where ancient trees whispered secrets to the wind...
Audio: audio_output/Narrator_1234567890.mp3
------------------------------

Segment 2:
Character: Hero
Voice: male-qn-qingse
Text: I can feel the magic in the air. Something important is about to happen.
Audio: audio_output/Hero_1234567891.mp3
------------------------------
```

## Contributing

Feel free to contribute by:

- Adding new character voices
- Improving story generation prompts
- Adding new audio formats
- Enhancing the user interface

## License

This project is open source and available under the MIT License.

## Support

For issues related to:

- MiniMax API: Check the [MiniMax API documentation](https://api.minimax.io/)
- Audio playback: Check the [pydub documentation](https://github.com/jiaaro/pydub)
- General issues: Open an issue in the project repository

## 🎵 Audio Creator Scripts

After generating individual audio files for each story segment, you can combine them into a single MP3 file for easy listening.

### Quick Start

```bash
# Simple interactive script (uses audio_output by default)
python create_story_audio.py

# Simple interactive script with custom directory
python create_story_audio.py my_audio_files

# Command-line script with options
python audio_creator.py --play

# Command-line script with custom directory
python audio_creator.py my_audio_files --play
```

### Audio Creator Features

- **Flexible Directories**: Specify any directory containing audio files
- **Automatic Ordering**: Uses `story_script.txt` to determine the correct sequence
- **Custom Pauses**: Add pauses between segments (0.5s, 1.0s, or no pauses)
- **Playback**: Optionally play the combined audio immediately
- **Multiple Formats**: Supports different output filenames

### Command Line Options

```bash
# Basic usage with default directory (audio_output)
python audio_creator.py --play

# Specify custom directory
python audio_creator.py my_audio_files --play

# List available audio files in a directory
python audio_creator.py my_audio_files --list

# Create with custom pause duration
python audio_creator.py my_audio_files --pause 1000

# Custom output filename
python audio_creator.py my_audio_files --output "my_story.mp3"

# Use different input directory
python audio_creator.py interactive_audio --play
```

### Example Usage

1. **Generate story and audio files**:

   ```bash
   python main.py
   ```

2. **Combine into single MP3** (interactive):

   ```bash
   python create_story_audio.py
   # or with custom directory
   python create_story_audio.py interactive_audio
   ```

3. **Or use command line**:
   ```bash
   python audio_creator.py --play --pause 500
   # or with custom directory
   python audio_creator.py my_audio_files --play --pause 500
   ```

The combined audio file will be saved as `complete_story.mp3` (or your custom filename) and can be played in any media player.
