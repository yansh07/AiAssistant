import json
import os
import asyncio
import requests
from dotenv import load_dotenv
from edge_tts import Communicate
from playwright.async_api import async_playwright

import soundfile as sf
import sounddevice as sd

load_dotenv()

# Load links from links.json
with open("links.json", "r") as f:
    LINKS = json.load(f)

async def speak(text: str):
    """
    Converts text to speech using edge_tts, saves to a temporary MP3,
    and plays it using soundfile and sounddevice.
    """
    voice = "en-US-JennyNeural" # A good general English voice
    temp_audio_file = "temp_speech.mp3"

    try:
        # Generate the audio file using edge_tts
        communicate = Communicate(text, voice)
        await communicate.save(temp_audio_file)

        # --- Play the audio using soundfile and sounddevice ---
        if os.path.exists(temp_audio_file):
            # Read the audio data and sample rate from the MP3 file
            data, fs = sf.read(temp_audio_file, dtype='float32')
            
            sd.play(data, fs)
            sd.wait() # Wait until the sound has finished playing
            print(f"[🔊] Played: '{text}'")
        else:
            print(f"[❌] Generated audio file not found: {temp_audio_file}")

    except sf.LibsndfileError as e:
        print(f"[❌] Error reading audio file with soundfile: {e}")
        print("This might indicate missing system libraries for MP3 support (e.g., libsndfile-dev on Linux).")
    except Exception as e:
        print(f"[❌] Error during text-to-speech or audio playback: {e}")
    finally:
        # Clean up: remove the temporary audio file
        if os.path.exists(temp_audio_file):
            os.remove(temp_audio_file)

async def play_youtube_playlist(playlist_name: str):
    """
    Opens a specified YouTube playlist URL in a headless browser.
    Assumes all playlists are under the 'youtube' key in links.json.
    """
    youtube_playlists = LINKS.get("youtube", {})
    url = youtube_playlists.get(playlist_name.lower()) # Case-insensitive lookup

    if url:
        await speak(f"Playing {playlist_name}.")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True) # Run browser in background
            page = await browser.new_page()
            await page.goto(url, wait_until='domcontentloaded') # Wait for page to load
            print(f"[🌐] Opened YouTube playlist: {url}")
            await asyncio.sleep(5) # Keep page open briefly, e.g., to start playback
            await browser.close()
    else:
        await speak(f"Sorry, the playlist '{playlist_name}' was not found in my YouTube links.")

def get_weather(city: str) -> str:
    """
    Fetches current weather data from OpenWeatherMap API for a given city.
    """
    weather_api_key = os.getenv("weather_key") 
    if not weather_api_key:
        return "Weather API key not configured. Please set OPENWEATHER_API_KEY in your .env file."

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric"

    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        if data.get("cod") == 200: # OpenWeatherMap returns 200 for success
            weather_desc = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            return f"The weather in {city} is {weather_desc}, temperature is {temp}°C, and it feels like {feels_like}°C."
        else:
            # Handle cases where API returns non-200 status in its JSON (e.g., city not found)
            return f"Could not retrieve weather data for {city}. API responded with: {data.get('message', 'Unknown error.')}"
    except requests.exceptions.RequestException as e:
        return f"Error connecting to weather service: {e}"
    except json.JSONDecodeError:
        return "Error decoding weather data. The API response was not valid JSON."
    except KeyError as e:
        return f"Unexpected weather data format. Missing key: {e}. Full response: {data}"
    except Exception as e:
        return f"An unexpected error occurred while getting weather: {e}"

async def perform_action(command: dict):
    """
    Performs an action based on the parsed command dictionary from listener.py.
    """
    if not command:
        await speak("I didn't understand the command. Please try again.")
        return

    action_type = command.get("action")

    if action_type == "play_playlist":
        playlist_name = command.get("name")
        if playlist_name:
            await play_youtube_playlist(playlist_name)
        else:
            await speak("Please tell me which playlist to play.")
    
    elif action_type == "search":
        search_query = command.get("query")
        if search_query:
            await speak(f"Searching for {search_query} on YouTube.")
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                # Example: Search on YouTube
                await page.goto(f"https://www.youtube.com/results?search_query={search_query}")
                print(f"[🌐] Opened search results for: {search_query}")
                await asyncio.sleep(5) # Keep open briefly
                await browser.close()
        else:
            await speak("Please tell me what to search for.")

    elif action_type == "weather":
        city = command.get("name")
        if not city:
            await speak("Please specify a city to get the weather for.")
            return
        
        # Call the synchronous get_weather function
        weather_report = get_weather(city)
        await speak(weather_report)

    else:
        await speak(f"I don't know how to perform the action: '{action_type}'.")

if __name__ == "__main__":
    async def test_automate():
        print("Testing automate.py...")
        await speak("Hello, I am your assistant. Testing audio playback.")
    asyncio.run(test_automate())