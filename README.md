**AI Assistant - A Modular, voice-controlled system**🚀  
*-I don't click, I command*

This is a voice-activated AI Assistant that listens to your commands, understands them with **GPT**, executes them using **Playwright**, and responds back to you - like a real assistant should.
It's not Alexa, It's not Siri. It's yours. Built with *open tools*. Runs on locally. Works on your voice.

✨**Features**    
~**🔎 Wake word detection** via Porcupine  
~**🗣 Speech to text** using OpenAI Whisper  
~**❝ ❞ Command parsing** via GPT (openAI API)  
~**🦾 Automation** using Playwright(open browser, search, scrap, etc.)  
~**📖 Text to speech output** via Edge TTS  
~**📏 Modular structure:** easy plugin new commands, functions  
~**🌐 Local-Only design** -no internet dependency except GPT(parsing)  

🤖**Tech Stack:-**  
🛠️**Component** - **Tool**  
1. Wake word - Porcupine(custom keyword model)
2. Speech recognition - OpenAI Whisper(local model "small/medium")
3. Natural Language Parsing - OpenAI GPT API
4. Automation - Playwrigth
5. Text-to-speech - Edge TTS
6. Runtime - Python 3.10+

📂**Folder Structure:-**  
|-main.py #entry point, connects  
|-wakeword.py #porcupine  
|-listener.py #Whisper + parser  
|-automate.py #playwright  
|-requirements.txt  

👨🏻‍💻**How it works:**  
1. **Wake word detect** via porcupine custom model
2. **Your voice is recorded** and passed to whisper
3. **Whisper transcribes the voice to text**
4. **GPT AI parses the text and determines the action**
5. **Playwright runs the automation task**
6. Result is converted into **Speech by Edge TTS**
7. Assistant responds - like a friend who codes.

🛑**KNOWN LIMITATIONS:-**  
1. Currently optimized for single microphone model
2. Mic detection/quality varies across systems
3. GPT API call requires internet connection(for command parsing)
4. No GUI yet - purely CLI and audio-driven
   *-I focused on building intelligence, not appearance - for now*

📈**Future plan:-**  
1. []Add local NLP fallback to replace GPT
2. []Add GUI with Tkinter or React dashboard(post MERN)
3. []Add multi mic/device compatibility
4. []Plugin-style commands(e.g., emails, music)
5. []Dockerize the assistant for deployment

🧗‍♂️**Why this exists:-**  
I built this project not as a clone of something else, but as a milestone of my capability.
I wanted to see if i could connect multiple systems - speech, logic, automation and voice - into a single, usable assistant.    
**AND YES I DID IT 💪🏻**

🪪**LICENSE**  
Personal use. Modify. Improve. Break it. Learn from it. 
This project was made to learn, not to sell.

📋**Credits**  
1. OpenAI Whisper & GPT  
2. Porcupine (by Picovoice)  
3. Microsoft Edge TTS  
4. Playwright  
5. <a href="https://www.github.com/yansh07" target="_blank">Priyanshu</a>
