import whisper
import sounddevice as sd
import numpy as np
import os
import json
from scipy.io.wavfile import write
from dotenv import load_dotenv
from openai import OpenAI

#environment variable
load_dotenv()
client = OpenAI(api_key=os.getenv("openai_key"))

print("[✨] Loading Whisper model (small)...")
try:
    model = whisper.load_model("small")
    print("[✅] Whisper model loaded.")
except Exception as e:
    print(f"[❌] Error loading Whisper model: {e}")
    print("Please ensure 'whisper' is installed correctly and has access to download models.")
    exit(1)

# Audio recording settings
SAMPLE_RATE = 16000
DURATION = 5  # seconds for command recording

def record_audio(duration=DURATION, samplerate=SAMPLE_RATE, output_file="temp_command.wav"):
    """Records audio for a specified duration and saves it to a WAV file."""
    print("[🎤] Listening for command...")
    try:
        audio = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1, dtype='float32')
        sd.wait() 
        audio = np.squeeze(audio) 

        # Optional: Handle very low volume (adjust threshold as needed)
        if np.max(np.abs(audio)) < 0.01:
            print("[⚠️] Low volume detected. Please speak louder.")
            return None

        # Convert to int16 for WAV file saving (standard for audio)
        write(output_file, samplerate, audio.astype(np.int16))
        return output_file
    except Exception as e:
        print(f"[❌] Error during audio recording: {e}")
        return None

def transcribe_audio(file_path):
    """Transcribes audio from a file using the Whisper model."""
    print("[🔍] Transcribing audio...")
    try:
        result = model.transcribe(file_path)
        # Print the raw result from Whisper ---
        print(f"[DEBUG] Whisper raw result type: {type(result)}")
        if isinstance(result, dict):
            print(f"[DEBUG] Whisper result['text'] type: {type(result.get('text'))}")
            return str(result.get("text", "")) # Ensure it's a string, even if None or other type
        else:
            print(f"[DEBUG] Whisper result is not a dictionary. Raw result: {result}")
            return "" # Return empty string if unexpected result type
    except Exception as e:
        print(f"[❌] Error during transcription: {e}")
        return ""

def parse_command(text: str):
    """
    Parses user command text into a structured JSON object using GPT.
    Expected JSON format examples:
    - {"action": "play_playlist", "name": "playlist name"} (e.g., "play lazy lamhe playlist")
    - {"action": "search", "query": "latest news"}
    - {"action": "weather", "name": "city name"} (e.g., "what's the weather in New York")
    """
    print("[🤖] Parsing command via GPT...")
    content = None # Initialize content to None
    try:
        response = client.chat.completions.create(
            model="gpt-4o", # Using gpt-4o for potentially better parsing
            messages=[
                {"role": "system", "content": """You are an AI assistant that understands natural language commands and converts them into structured JSON objects.
                 Your goal is to extract the user's intent (action) and relevant parameters.
                 
                 Available actions and their parameters:
                 - "play_playlist": {"action": "play_playlist", "name": "playlist name"} (e.g., "play lazy lamhe playlist")
                 - "search": {"action": "search", "query": "search query"} (e.g., "search for cat videos")
                 - "weather": {"action": "weather", "name": "city name"} (e.g., "what's the weather in New York")
                 
                 If you cannot determine a clear action or required parameters, return an empty JSON object: {}.
                 DO NOT include any prose, explanations, or text outside the JSON object.
                 """},
                {"role": "user", "content": f"My command: {text}"}
            ],
            response_format={"type": "json_object"} # Ensure JSON output
        )
        content = response.choices[0].message.content

        if content is None:
            print("[❌] GPT response content was None. Cannot parse.")
            return None

        print(f"[GPT Response Raw]: {content}") # For debugging

        parsed_json = json.loads(content)
        return parsed_json
    except json.JSONDecodeError as e:
        print(f"[❌] Failed to parse GPT response as JSON. Error: {e}")
        if content is not None:
            print(f"[❌] Content that caused error: {content}")
        return None
    except Exception as e:
        print(f"[❌] An unexpected error occurred during command parsing: {e}")
        return None

def listen_and_parse():
    """Records audio, transcribes it, and then parses it into a command."""
    audio_file = record_audio()
    if not audio_file:
        return None

    text = transcribe_audio(audio_file)
    
    # --- IMPORTANT: Type check and conversion for 'text' ---
    # This ensures 'text' is always a string before .strip() is called.
    if not isinstance(text, str):
        print(f"[⚠️] WARNING: Transcription result was not a string. Type: {type(text)}. Attempting conversion.")
        text = str(text) # Force convert to string

    print(f"[🗣️] User said: '{text}'")
    
    # Clean up the temporary audio file
    if os.path.exists(audio_file):
        os.remove(audio_file)

    if not text.strip(): # This line should now be safe
        print("[⚠️] No discernible speech. Please try again.")
        return None

    return parse_command(text)

if __name__ == "__main__":
    # Example usage for testing listener.py
    print("Testing listener.py...")
    command = listen_and_parse()
    if command:
        print("[✅] Parsed command:", command)
    else:
        print("[⚠️] No valid command was parsed.")

