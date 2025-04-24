# Day I don't know of learning Ai/ml code from ChatGPT and implementing as I learn
import asyncio
import edge_tts
import pygame
import os
import uuid
import time
import speech_recognition as sr
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Path of the Chrome webdriver
driverPath = r"D:\Thursday-AI\Prototypes\chromedriver-win64\chromedriver.exe"
chromePath = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# TTS(Voice mod)
VOICE = "en-GB-SoniaNeural"

# Initializing Pygame for audio
pygame.mixer.init()

# Async f() for edge-tts + pygame setup
async def speak(text):
    outputFile = f"tts_output_{uuid.uuid4()}.mp3"
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(outputFile)

    pygame.mixer.music.load(outputFile)
    pygame.mixer.music.play()

    # Wait for audio to end
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    pygame.mixer.music.stop()
    pygame.mixer.music.unload()

    os.remove(outputFile)

# I DON'T KNOW WHAT THIS IS(Blocking wrapper for async TTS)
def speakBlocking(text):
    asyncio.run(speak(text))

# Voice recognition module f()
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("I am listening. . .")
        audio = recognizer.listen(source, phrase_time_limit=4)
        try:
            return recognizer.recognize_google(audio).lower()
        except:
            return " "

# Chrome options
chromeOptions = Options()
chromeOptions.add_argument("--start-maximized")
chromeOptions.binary_location = chromePath

# Starting the chrome driver
service = Service(driverPath)
driver = webdriver.Chrome(service=service, options=chromeOptions)

# Open the WhatsApp Web path
driver.get("https://web.whatsapp.com")
speakBlocking("Boos, WhatsApp fired and up, please scan the code to log in.")

# f() to check text from a specific user
def chatForMessage(personName,messageText):
    try:
        chat = driver.find_element(By.XPATH, '//div[contains@class, "message-in"]//span[@dir="ltr"]')
        chat.click()
        time.sleep(2)

        # gets all incoming texts
        messages = driver.find_elements(By.XPATH, '//div[contains(@class, "message-in")]//span[@dir="ltr"]')
        lastMsg = messages[-1].text if messages else ""

        if messageText.lower() in lastMsg.lower():
            speakBlocking(f"Boss, incoming message from {personName}. Should I reply?")
            reply = listen()
            if "yes" in reply:
                speakBlocking("What should I say?")
                message = listen()
                inputBox = driver.find_element(By.XPATH, '//div[@title="Type a message"]')
                inputBox.sendKeys(message)
                inputBox.sendKeys(u'\ue007') # for ENTER KEY
                speakBlocking("Text sent.")
            else:
                speakBlocking(f"Okay. Setting a reminder that you have a message from {personName}.")
                with open("reminders.txt", "a") as f:
                    f.write(f"Unread text message from {personName}: {lastMsg}\n")

    except Exception as e:
        print("Error: FATAL OCCURRED BOSS.", e)

# Runtime env
chatForMessage("Rishi", "Boss is busy, ping him if anything important.")

