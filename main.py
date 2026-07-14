import speech_recognition as sr
import webbrowser
import pyttsx3
import tkinter as tk
from tkinter import messagebox
import datetime
import os
import google.generativeai as genai
from dotenv import load_dotenv



# Optional imports - these features are skipped gracefully if the
# packages aren't installed (pip install wikipedia google-generativeai)
try:
    import wikipedia
    WIKIPEDIA_AVAILABLE = True
except ImportError:
    WIKIPEDIA_AVAILABLE = False


# Load environment variables from .env
load_dotenv()

try:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    if not GEMINI_API_KEY:
        raise ValueError("Gemini API key not found")

    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-flash-latest")
    GEMINI_AVAILABLE = True

except Exception as e:
    print("Gemini Error:", e)
    GEMINI_AVAILABLE = False


# Initialize text-to-speech engine
engine = pyttsx3.init()
recognizer = sr.Recognizer()

# Speak function
def speak(text):
    engine.say(text)
    engine.runAndWait()

# --- Known websites: checked first, so common sites open reliably ---
websites = {
    "google": "https://google.com",
    "youtube": "https://youtube.com",
    "gmail": "https://mail.google.com",
    "facebook": "https://facebook.com",
    "instagram": "https://instagram.com",
    "linkedin": "https://linkedin.com",
    "github": "https://github.com",
    "chatgpt": "https://chat.openai.com",
    "leetcode": "https://leetcode.com",
    "geeksforgeeks": "https://geeksforgeeks.org",
    "amazon": "https://amazon.in",
    "flipkart": "https://flipkart.com",
    "spotify": "https://spotify.com",
    "netflix": "https://netflix.com",
    "twitter": "https://twitter.com",
    "reddit": "https://reddit.com",
}

# --- Desktop applications: edit paths to match your machine ---
applications = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "vscode": r"C:\Users\YourName\AppData\Local\Programs\Microsoft VS Code\Code.exe",
}

# Process voice/text commands
def processCommand(c):
    c = c.lower()

    if c == "open google":
        webbrowser.open("https://google.com")
        speak("Opening Google")

    elif c == "open youtube":
        webbrowser.open("https://youtube.com")
        speak("Opening YouTube")

    elif c == "email":
        webbrowser.open("https://mail.google.com")
        speak("Opening Gmail")

    elif c.startswith("search"):
        query = c.replace("search", "").strip()
        if query:
            webbrowser.open(f"https://www.google.com/search?q={query}")
            speak(f"Searching for {query}")
        else:
            speak("What should I search for?")

    elif c == "time":
        time_str = datetime.datetime.now().strftime("%H:%M:%S")
        speak(f"The time is {time_str}")
        output_text.set(f"Time: {time_str}")

    elif c == "date":
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        speak(f"Today's date is {date_str}")
        output_text.set(f"Date: {date_str}")

    elif c == "play music":
        music_folder = "C:/Users/YourName/Music"  # Change to your music folder
        songs = os.listdir(music_folder)
        if songs:
            os.startfile(os.path.join(music_folder, songs[0]))
            speak("Playing music")
        else:
            speak("No music found")

    elif c.startswith("note"):
        note_content = c.replace("note", "").strip()
        if note_content:
            with open("jarvis_notes.txt", "a") as f:
                f.write(note_content + "\n")
            speak("Note saved")
        else:
            speak("Please say something to note")

    # --- NEW: open <website>, dictionary first, Google search fallback ---
    elif c.startswith("open "):
        site = c.replace("open", "", 1).strip()
        if site in websites:
            webbrowser.open(websites[site])
            speak(f"Opening {site}")
        else:
            webbrowser.open(f"https://www.google.com/search?q={site}")
            speak(f"I couldn't find {site}, searching Google instead.")

    # --- NEW: launch <desktop app> ---
    elif c.startswith("launch "):
        app = c.replace("launch", "", 1).strip()
        if app in applications:
            try:
                os.startfile(applications[app])
                speak(f"Opening {app}")
            except Exception:
                speak(f"I found {app} but couldn't open it. Check the file path.")
        else:
            speak("Application not found.")

    # --- NEW: play <song> on YouTube (checked before "play music" logic above,
    # since "play music" is an exact match it's tried first) ---
    elif c.startswith("play"):
        song = c.replace("play", "", 1).strip()
        if song:
            webbrowser.open(f"https://www.youtube.com/results?search_query={song}")
            speak(f"Playing {song}")
        else:
            speak("What should I play?")

    # --- NEW: who is <person>, via Wikipedia ---
    elif c.startswith("who is") and WIKIPEDIA_AVAILABLE:
        person = c.replace("who is", "", 1).strip()
        try:
            result = wikipedia.summary(person, sentences=2)
            output_text.set(result)
            speak(result)
        except Exception:
            speak("Sorry, I couldn't find information on that.")

    elif c == "exit":
        speak("Goodbye!")
        root.destroy()

    # --- NEW: fallback to Gemini for general conversation, instead of
    # a flat "I didn't understand that" ---
    else:
        if GEMINI_AVAILABLE:
            try:
                response = gemini_model.generate_content(c)
                answer = response.text
                output_text.set(answer)
                speak(answer)
            except Exception as e:
                output_text.set(str(e))
                speak("Sorry, I couldn't answer that.")
        else:
            speak("I didn't understand that")

# Voice command function
def listen_command():
    try:
        with sr.Microphone() as source:
            output_text.set("Listening...")
            root.update()
            audio = recognizer.listen(source, timeout=4, phrase_time_limit=4)
            command = recognizer.recognize_google(audio)
            output_text.set(f"You said: {command}")
            processCommand(command)
    except Exception as e:
        output_text.set(f"Error: {e}")
        speak("Sorry, I couldn't hear you")

# Create GUI
root = tk.Tk()
root.title("Jarvis Assistant")
root.geometry("400x300")
root.config(bg="#1e1e1e")

output_text = tk.StringVar()
output_label = tk.Label(root, textvariable=output_text, fg="white", bg="#1e1e1e", wraplength=350, justify="center")
output_label.pack(pady=20)

listen_button = tk.Button(root, text="🎤 Listen", command=listen_command, font=("Arial", 14), bg="#00bfff", fg="white")
listen_button.pack(pady=10)

exit_button = tk.Button(root, text="❌ Exit", command=root.destroy, font=("Arial", 14), bg="#ff4d4d", fg="white")
exit_button.pack(pady=10)

root.mainloop()
