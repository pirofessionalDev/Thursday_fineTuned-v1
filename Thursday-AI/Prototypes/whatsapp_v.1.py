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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Paths
driverPath = r"D:\Thursday-AI\Prototypes\chromedriver-win64\chromedriver.exe"
chromePath = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# TTS setup
VOICE = "en-GB-SoniaNeural"
pygame.mixer.init()


# TTS async function
async def speak(text):
    outputFile = f"tts_output_{uuid.uuid4()}.mp3"
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(outputFile)
    pygame.mixer.music.load(outputFile)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    pygame.mixer.music.unload()  # <- Prevent PermissionError
    os.remove(outputFile)


def speakBlocking(text):
    asyncio.run(speak(text))


# Voice Recognition with retry
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for your response... Please speak!")
        try:
            audio = recognizer.listen(source, phrase_time_limit=5)  # Slightly longer time
            return recognizer.recognize_google(audio).lower()
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that. Please try again.")
            return listen()  # Retry if speech isn't understood
        except sr.RequestError as e:
            print(f"Error with the speech recognition service: {e}")
            return ""


# Chrome options
chromeOptions = Options()
chromeOptions.add_argument("--start-maximized")
chromeOptions.binary_location = chromePath

# WebDriver setup
service = Service(driverPath)
driver = webdriver.Chrome(service=service, options=chromeOptions)

# WhatsApp Web
driver.get("https://web.whatsapp.com")
speakBlocking("Thursday is ready. Please scan the code to log in to WhatsApp.")
input("Press Enter after logging in and scanning the code...")


# Function to check and reply
def chatForMessage(personName):
    try:
        # Wait for the specific contact to be clickable
        contact = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f'//span[@title="{personName}"]'))
        )
        contact.click()
        time.sleep(2)

        # Wait for the message elements to be available
        messages = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "message-in")]//span[@dir="ltr"]'))
        )

        lastMsg = messages[-1].text if messages else ""

        print(f"Last message from {personName}: {lastMsg}")
        speakBlocking(f"{personName} says: {lastMsg}")

        # Ask if user wants to reply
        speakBlocking("Should I reply to this message?")
        reply = listen()
        print(f"Voice response: {reply}")

        if "yes" in reply or "yeah" in reply:
            speakBlocking("You have 15 seconds to type your reply.")

            # Wait for 15 seconds for user input
            start_time = time.time()
            input_message = ""

            while time.time() - start_time < 15:
                input_message = input("Type your message (you have 15 seconds): ")
                if input_message.strip():  # Break if there's any input
                    break

            if input_message.strip():
                # Convert input text into voice and send
                speakBlocking("Converting your message into voice.")
                message = input_message
                inputBox = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@title="Type a message"]'))
                )
                inputBox.send_keys(message)
                inputBox.send_keys(u'\ue007')  # Send Enter key
                speakBlocking("Text sent boss.")
            else:
                speakBlocking("No message typed, I won't send anything.")

        else:
            voicemail = "Thursday, your competition, leave him alone. You might look attractive but I am more than honey."
            inputBox = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@title="Type a message"]'))
            )
            inputBox.send_keys(voicemail)
            inputBox.send_keys(u'\ue007')  # Send Enter key
            speakBlocking("Voicemail sent boss.")

        # Log the message
        with open("reminders.txt", "a") as f:
            f.write(f"Unread message from {personName}: {lastMsg}\n")

    except Exception as e:
        print("Error occurred:", e)


# Run it
chatForMessage("Sureyeahhh")
