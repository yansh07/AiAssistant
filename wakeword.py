import pvporcupine
import sounddevice as sd
import numpy as np
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
PORCUPINE_ACCESS_KEY = os.getenv("PORCUPINE_ACCESS_KEY") 
FRIDAY_WAKEWORD_PATH = os.getenv("FRIDAY_WAKEWORD_PATH") 

# Define the name of your wake word for printing messages
WAKE_WORD_NAME = "Friday" 

# Audio settings
SAMPLE_RATE = 16000
# Porcupine expects a specific frame length, which is usually 512.
# We'll use porcupine.frame_length directly after creation.

def get_porcupine_instance():
    """
    Initializes and returns a Porcupine instance.
    Handles checks for environment variables and proper setup.
    """
    try:
        if not PORCUPINE_ACCESS_KEY:
            raise ValueError("PORCUPINE_ACCESS_KEY not found in .env file. Please add it and ensure it's correct.")
        
        if not FRIDAY_WAKEWORD_PATH:
            raise ValueError("FRIDAY_WAKEWORD_PATH not found in .env file. Please add the path to your 'friday.ppn' file.")

        # Ensure the .ppn file actually exists at the specified path
        if not os.path.exists(FRIDAY_WAKEWORD_PATH):
            raise FileNotFoundError(f"Wake word file not found at: {FRIDAY_WAKEWORD_PATH}. Please check the path.")

        # Initialize Porcupine with your custom keyword
        porcupine = pvporcupine.create(
            access_key=PORCUPINE_ACCESS_KEY,
            keyword_paths=[FRIDAY_WAKEWORD_PATH]
        )
        print(f"[✅] Porcupine initialized successfully for wake word: '{WAKE_WORD_NAME}'")
        return porcupine
    except Exception as e:
        print(f"[❌] Error initializing Porcupine: {e}")
        print("Please ensure your .env variables are correct and the wake word file exists.")
        sys.exit(1) # Exit if Porcupine can't be initialized

def listen_for_wakeword():
    """
    Listens continuously for the specified wake word using Porcupine.
    Returns True if the wake word is detected, False on error or stop.
    """
    porcupine = None
    audio_stream = None
    # Initialize an audio buffer to accumulate data for Porcupine
    audio_buffer = np.array([], dtype=np.int16) 

    try:
        porcupine = get_porcupine_instance() # Get the initialized Porcupine instance
        
        print(f"[👂] Listening for wake word: '{WAKE_WORD_NAME}'...")
        audio_stream = sd.InputStream(
            channels=1, 
            samplerate=porcupine.sample_rate, 
            blocksize=0, # Let sounddevice choose its optimal block size
            dtype='int16' # Ensure audio data type is int16 for Porcupine
        )
        
        with audio_stream:
            while True:
                # Read audio data from the stream. This might return more or less than porcupine.frame_length.
                pcm_data, _ = audio_stream.read(audio_stream.blocksize) 
                
                # Convert to int16 and IMPORTANT: Squeeze to ensure it's always a 1D array
                pcm_data = np.squeeze(pcm_data.astype(np.int16)) 
                
                # Append received PCM data to our buffer
                audio_buffer = np.concatenate((audio_buffer, pcm_data))

                # Process the buffer in chunks of porcupine.frame_length
                while len(audio_buffer) >= porcupine.frame_length:
                    # Get the current frame for Porcupine (exactly porcupine.frame_length long)
                    frame_for_porcupine = audio_buffer[:porcupine.frame_length]
                    
                    # Remove the processed frame from the buffer
                    audio_buffer = audio_buffer[porcupine.frame_length:]

                    # Process the audio frame with Porcupine
                    keyword_index = porcupine.process(frame_for_porcupine.tobytes())
                    
                    # Check if a wake word was detected
                    if keyword_index >= 0:
                        print(f"[✅] Wake word '{WAKE_WORD_NAME}' detected!")
                        audio_buffer = np.array([], dtype=np.int16) # Clear buffer after detection
                        return True # Wake word detected, return control to main loop
                
    except KeyboardInterrupt:
        print("\n[🛑] Stopping wake word listener by user.")
        return False
    except Exception as e:
        print(f"[❌] An error occurred during wake word detection: {e}")
        return False
    finally:
        # Clean up Porcupine instance and audio stream resources
        if porcupine:
            porcupine.delete()
        if audio_stream and not audio_stream.closed: # Check if stream is open before closing
            audio_stream.close()

if __name__ == "__main__":
    # This block allows you to test wakeword.py independently
    print("Testing wakeword.py...")
    if listen_for_wakeword():
        print("Wakeword detected. Listener stopped.")
    else:
        print("No wakeword detected or listener encountered an issue/stopped.")

