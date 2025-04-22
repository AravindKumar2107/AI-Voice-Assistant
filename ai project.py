import tkinter as tk
from tkinter import messagebox
import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import os
import time
import subprocess
from ecapture import ecapture as ec
import json
import requests
import pywhatkit
import pyjokes
import threading

# Initialize the speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Speak function
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Greeting based on time
def wishMe():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        greeting = "Hello, Good Morning"
    elif 12 <= hour < 18:
        greeting = "Hello, Good Afternoon"
    else:
        greeting = "Hello, Good Evening"
    speak(greeting)
    status_label.config(text=greeting)

# Function to take voice input
def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        status_label.config(text="Listening...")
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=5)
            statement = r.recognize_google(audio, language='en-in')
            status_label.config(text=f"You said: {statement}")
            return statement.lower()
        except sr.WaitTimeoutError:
            status_label.config(text="Listening timed out. Please try again.")
            speak("Listening timed out. Please try again.")
            return "none"
        except sr.UnknownValueError:
            status_label.config(text="Sorry, I didn’t catch that.")
            speak("Sorry, I didn’t catch that.")
            return "none"
        except Exception as e:
            status_label.config(text="Error occurred.")
            speak("Something went wrong.")
            return "none"

# Function to handle command
def process(statement):
    global listening
    if statement == "none" or statement.strip() == "":
        # If nothing is understood, try again
        if listening:
            root.after(1000, threaded_listen)
        return

    if "good bye" in statement or "ok bye" in statement or "stop" in statement or "exit" in statement:
        speak("Your personal assistant is shutting down. Goodbye.")
        root.quit()

    elif 'wikipedia' in statement:
        speak('Searching Wikipedia...')
        statement = statement.replace("wikipedia", "")
        results = wikipedia.summary(statement, sentences=3)
        speak("According to Wikipedia")
        status_label.config(text=results)
        speak(results)

    elif 'open youtube' in statement:
        webbrowser.open_new_tab("https://www.youtube.com")
        speak("YouTube is open now")

    elif 'play song' in statement or 'play music' in statement:
        speak("What song should I play?")
        song = takeCommand()
        if song != "none":
            speak(f"Playing {song} on YouTube")
            pywhatkit.playonyt(song)

    elif 'google search' in statement:
        speak("What do you want to search on Google?")
        query = takeCommand()
        if query != "none":
            speak(f"Searching {query}")
            webbrowser.open(f"https://www.google.com/search?q={query}")

    elif 'open google' in statement:
        webbrowser.open_new_tab("https://www.google.com")
        speak("Google Chrome is open now")

    elif 'open gmail' in statement:
        webbrowser.open_new_tab("https://mail.google.com")
        speak("Google Mail is open now")

    elif "weather" in statement:
        speak("What's the city name?")
        city_name = takeCommand()
        if city_name != "none":
            api_key = "8ef61edcf1c576d65d836254e11ea420"  # Replace with your actual key
            base_url = "https://api.openweathermap.org/data/2.5/weather?"
            complete_url = base_url + "appid=" + api_key + "&q=" + city_name
            response = requests.get(complete_url)
            x = response.json()
            if x["cod"] != "404":
                y = x["main"]
                temp = y["temp"]
                humidity = y["humidity"]
                z = x["weather"]
                description = z[0]["description"]
                speak(f"Temperature: {temp}K, Humidity: {humidity}%, Description: {description}")
            else:
                speak("City not found.")

    elif 'time' in statement:
        strTime = datetime.datetime.now().strftime("%H:%M:%S")
        speak(f"The time is {strTime}")

    elif 'who are you' in statement or 'what can you do' in statement:
        info = "I am your personal assistant. I can open websites, search Wikipedia, play music, check weather, tell jokes, and answer questions."
        speak(info)
        status_label.config(text=info)

    elif "open stackoverflow" in statement:
        webbrowser.open_new_tab("https://stackoverflow.com")
        speak("Here is Stack Overflow")

    elif 'news' in statement:
        webbrowser.open_new_tab("https://timesofindia.indiatimes.com/home/headlines")
        speak("Here are some headlines from the Times of India.")

    elif "camera" in statement or "take a photo" in statement:
        ec.capture(0, "Camera", "img.jpg")

    elif 'search' in statement:
        query = statement.replace("search", "")
        webbrowser.open_new_tab(query)

    elif 'tell me a joke' in statement or 'make me laugh' in statement:
        joke = pyjokes.get_joke()
        speak("Here's a joke for you.")
        status_label.config(text=joke)
        speak(joke)

    elif 'ask' in statement or 'tell me' in statement:
        speak("What would you like to ask?")
        question = takeCommand()
        if question != "none":
            try:
                response = requests.get(f"https://api.duckduckgo.com/?q={question}&format=json").json()
                answer = response.get("AbstractText")
                if answer:
                    speak("Here's what I found:")
                    speak(answer)
                    print(answer)
                    status_label.config(text=answer)
                else:
                    speak("Sorry, no answer found. Showing Google results.")
                    webbrowser.open(f"https://www.google.com/search?q={question}")
            except:
                speak("I had trouble looking that up.")
    else:
        speak("I'm sorry, I didn't understand that.")
    
    # Loop back and listen again if not stopped
    if listening:
        root.after(1000, threaded_listen)

# Start/Stop Handlers
def threaded_listen():
    if listening:
        threading.Thread(target=lambda: process(takeCommand()), daemon=True).start()

def start_listening():
    global listening
    listening = True
    status_label.config(text="Listening started...")
    speak("How can I help you?")
    threaded_listen()

def stop_listening():
    global listening
    listening = False
    status_label.config(text="Listening stopped.")
    speak("Listening has been paused.")

# ========== GUI ==========

root = tk.Tk()
root.title("AI Voice Assistant")
root.geometry("550x400")
root.config(bg="#121212")

title_label = tk.Label(root, text="AI Personal Voice Assistant", font=("Helvetica", 20, "bold"), bg="#121212", fg="white")
title_label.pack(pady=15)

status_label = tk.Label(root, text="Click the mic to start speaking...", font=("Helvetica", 12), bg="#121212", fg="cyan")
status_label.pack(pady=10)

mic_button = tk.Button(root, text="🎤 Start Listening", font=("Helvetica", 14), bg="#1f1f1f", fg="white", command=start_listening)
mic_button.pack(pady=25)

stop_button = tk.Button(root, text="🛑 Stop Listening", font=("Helvetica", 14), bg="darkred", fg="white", command=stop_listening)
stop_button.pack(pady=5)

# Initial greeting
speak("Loading your personal assistant")
wishMe()

# Launch GUI
root.mainloop()