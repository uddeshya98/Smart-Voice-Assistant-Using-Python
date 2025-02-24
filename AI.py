import pyttsx3
import os
os.environ["PYTHON_SOUNDDEVICE"] = "1"
import speech_recognition as sr
import datetime
import webbrowser
import urllib.parse
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import threading

# Initialize text-to-speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

driver = None

def speak(audio):
    """Converts text to speech"""
    engine.say(audio)
    engine.runAndWait()

def takeCommand():
    """Takes microphone input from the user and returns the text output"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 0.8
        r.energy_threshold = 300
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in') 
        print(f"User said: {query}\n")
    except Exception as e:
        speak("Sorry, I didn't get that. Could you please repeat that")
        query = takeCommand()
    return query.lower()

def ask_openai(query):
    """Gets a response from OpenAI's GPT model based on the user query"""
    try:
        response = openai.ChatCompletion.create(   
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": query}]
        )
        return response.choices[0].message['content']
    except Exception as e:
        print(f"Error fetching OpenAI response: {e}")
        return "I couldn't fetch a response from OpenAI."

def searchYouTubeMusic(song_name):
    """Searches YouTube Music for a song based on user input and plays it"""
    global driver
    # Initialize the Chrome WebDriver using ChromeDriverManager
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # Search for the song on YouTube Music
    query = urllib.parse.quote(song_name)
    driver.get(f"https://music.youtube.com/search?q={query}")
    time.sleep(5)  # Wait for the page to load

    # Click on the first search result
    try:
        first_result = driver.find_element(By.XPATH, '//*[@id="contents"]/ytmusic-shelf-renderer[1]//a')
        first_result.click()
        speak(f"Playing {song_name} on YouTube Music")
    except Exception as e:
        speak("Sorry, I couldn't find that song.")
    
    # Keep the browser open
    def keep_browser_open():
        while True:
            time.sleep(1)

    threading.Thread(target=keep_browser_open, daemon=True).start()

def closeBrowser():
    """Closes the currently opened browser window if it exists"""
    global driver
    if driver:
        driver.quit()
        driver = None
        speak("The browser has been closed.")
    else:
        speak("No browser is currently open.")

if __name__ == '__main__':
    speak("Hello, I am JARVIS AI. How can I assist you today?")
    
    while True:
        query = takeCommand()

        if "open youtube" in query:
            webbrowser.open("https://youtube.com")
            speak("Opening YouTube sir...")

        elif "what's the time" in query or "time" in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"Sir, the time is {strTime}")

        elif "exit" in query or "quit" in query:
            speak("Goodbye sir, have a nice day!")
            break

        elif "open google" in query:
            webbrowser.open("https://google.com")
            speak("Opening Google sir...")

        elif "play music" in query or "music" in query or "play song" in query:
            speak("Of course sir, what song would you like to listen to?")
            song_name = takeCommand()  
            searchYouTubeMusic(song_name)

        elif "close the previous tab" in query or "close this tab" in query or "close the tab" in query:
            closeBrowser()  # Close the browser if command is given        

        else:
            # For any other query, use OpenAI to generate a response
            openai_response = ask_openai(query)
            print(f"OpenAI Response: {openai_response}")
            speak(openai_response)
