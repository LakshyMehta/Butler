import speech_recognition as sr
import pyttsx3
import smtplib  
import ssl     

def initialize_systems():
    """
    Initializes the speech recognizer and the text-to-speech engine.
    """
    recognizer = sr.Recognizer()
    engine = pyttsx3.init()
    return recognizer, engine

def speak_text(engine, text):
    """
    Uses the text-to-speech engine to say the given text aloud.
    """
    print(f"Bot: {text}")
    engine.say(text)
    engine.runAndWait()

def listen_for_input(recognizer, engine, prompt):
    """
    Prompts the user, listens for audio, and returns the recognized text.
    """
    speak_text(engine, prompt)
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
        except sr.WaitTimeoutError:
            return None

    try:
        print("Recognizing...")
        recognized_text = recognizer.recognize_google(audio)
        print(f"You said: {recognized_text}")
        return recognized_text
    except sr.UnknownValueError:
        speak_text(engine, "Sorry, I could not understand that.")
        return None
    except sr.RequestError as e:
        speak_text(engine, f"Recognition service error; {e}")
        return None

def send_email(sender_email, password, receiver_email, subject, message_body):
    """
    Connects to the SMTP server and sends the email.
    """
    # Combine subject and body into a single message string
    message = f"Subject: {subject}\n\n{message_body}"
    
    # Use port 465 for SSL
    port = 465  
    smtp_server = "smtp.gmail.com"

    # Create a secure SSL context
    context = ssl.create_default_context()

    try:
        # Use a with statement to automatically handle the connection
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def main():
    """
    Main function to run the speech-to-email bot.
    """
    recognizer, engine = initialize_systems()

    # --- IMPORTANT: CONFIGURE YOUR CREDENTIALS HERE ---
    # Enter your email address and the 16-character App Password you generated
    SENDER_EMAIL = "lakshy280719@gmail.com"
    SENDER_PASSWORD = "your_16_character_app_password" 
    # ----------------------------------------------------

    if SENDER_EMAIL == "your_email@gmail.com" or SENDER_PASSWORD == "your_16_character_app_password":
        speak_text(engine, "Please configure your email and app password inside the script before running.")
        return

    speak_text(engine, "Hello! Let's send an email. To cancel at any time, just say 'cancel'.")

    # 1. Get Recipient's Email
    receiver = None
    while not receiver:
        raw_receiver = listen_for_input(recognizer, engine, "Who is the recipient? Please say their full email address.")
        if raw_receiver:
            if 'cancel' in raw_receiver.lower():
                speak_text(engine, "Operation cancelled. Goodbye.")
                return
            # Clean up common speech recognition errors for emails
            receiver = raw_receiver.lower().replace(" ", "").replace("attherate", "@").replace("dot", ".")
            speak_text(engine, f"The recipient is {receiver}. Is that correct? Say yes or no.")
            confirmation = listen_for_input(recognizer, engine, "")
            if confirmation and 'yes' in confirmation.lower():
                break
            else:
                receiver = None # Reset and ask again
                speak_text(engine, "Let's try that again.")
        else:
            speak_text(engine, "I didn't catch that. Let's try again.")


    # 2. Get the Subject
    subject = None
    while not subject:
        subject = listen_for_input(recognizer, engine, "What is the subject of the email?")
        if subject and 'cancel' in subject.lower():
            speak_text(engine, "Operation cancelled. Goodbye.")
            return

    # 3. Get the Message Body
    body = None
    while not body:
        body = listen_for_input(recognizer, engine, "What should the message say?")
        if body and 'cancel' in body.lower():
            speak_text(engine, "Operation cancelled. Goodbye.")
            return

    # 4. Confirm and Send
    speak_text(engine, f"Alright. I will send an email to {receiver} with the subject {subject}. The message is: {body}. Should I send it? Say yes or no.")
    final_confirmation = listen_for_input(recognizer, engine, "")

    if final_confirmation and 'yes' in final_confirmation.lower():
        speak_text(engine, "Sending the email now...")
        success = send_email(SENDER_EMAIL, SENDER_PASSWORD, receiver, subject, body)
        if success:
            speak_text(engine, "The email was sent successfully!")
        else:
            speak_text(engine, "Sorry, there was a problem and I could not send the email. Please check the console for errors.")
    else:
        speak_text(engine, "Okay, I will not send the email. Goodbye.")

if __name__ == "__main__":
    main()