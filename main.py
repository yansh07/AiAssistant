import asyncio
import sys
from dotenv import load_dotenv


import wakeword
import listener
import automate

load_dotenv()

async def main_loop():
    print("[✨] AI Assistant is ready.")
    while True:
        print("\n------------------------------------")
        # Step 1: Listen for wake word
        if wakeword.listen_for_wakeword():
            print("[✅] Wake word detected. Proceeding to listen for command.")
            
            # Step 2: Listen for command, transcribe, and parse
            command = listener.listen_and_parse()
            
            if command:
                print(f"[⚙️] Executing command: {command}")
                # Step 3: Perform the action
                await automate.perform_action(command)
            else:
                print("[🚫] Command not understood or no command given.")
                await automate.speak("I didn't understand that. Please try again.")
        else:
            # If listen_for_wakeword returns False (e.g., due to KeyboardInterrupt or error)
            print("[❌] Wake word listening stopped.")
            break # Exit the loop if wakeword listener stops

if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("\n[🛑] Program stopped by user.")
    except Exception as e:
        print(f"[FATAL ERROR] An unhandled exception occurred: {e}")
        sys.exit(1)