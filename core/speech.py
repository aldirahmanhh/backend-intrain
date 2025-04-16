import speech_recognition as sr

def main():
    # Create a Recognizer instance
    recognizer = sr.Recognizer()
    
    # Use the default microphone as the audio source
    with sr.Microphone() as source:
        # Adjust for ambient noise for better accuracy
        print("Adjusting for ambient noise... Please wait.")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Ready to record. Please say something!")
        
        # Listen to the first phrase and extract it into audio data
        audio_data = recognizer.listen(source)
    
    try:
        # Recognize speech using Google Web Speech API
        text = recognizer.recognize_google(audio_data)
        print("You said: " + text)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio.")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")

if __name__ == "__main__":
    main()
