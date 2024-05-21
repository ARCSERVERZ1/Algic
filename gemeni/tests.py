from django.test import TestCase

# Create your tests here.


import requests
import pyttsx3

# url = 'https://algic.pythonanywhere.com/gemeni/'
url = 'http://127.0.0.1:8000/gemeni/'

data = {
    "ask":"who is thanos"
}
status = requests.post(url , json = data)

print(status.json())
engine = pyttsx3.init()
engine.setProperty('rate', 200)  # Speed of speech (words per minute)
engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)

# Convert text to speech
text = "Hello, how are you today?"
engine.say(status.json()['response'])

# Wait for the speech to finish
engine.runAndWait()