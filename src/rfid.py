import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import signal
import time
 
continue_reading = True
 
# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print ("Ctrl+C captured, ending read.")
    continue_reading = False
    GPIO.cleanup()
 
# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)
 
# Create an object of the class MFRC522
MIFAREReader = SimpleMFRC522()
 
# Welcome message
print ("Welcome to the MFRC522 data read example")
print ("Press Ctrl-C to stop.")
 
# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:    
    # Get the UID of the card
    uid = MIFAREReader.read()[0]
    print(f"aqui - {uid}, {type(uid)}")
 
    # If we have the UID, continue
    if uid:
        my_uid = 454270145892
        
        #Configure LED Output Pin
        LED = 18
        GPIO.setup(LED, GPIO.OUT)
        GPIO.output(LED, GPIO.LOW)
        
        #Check to see if card UID read matches your card UID
        if uid == my_uid:                #Open the Doggy Door if matching UIDs
            print("Access Granted")
            GPIO.output(LED, GPIO.HIGH)  #Turn on LED
            time.sleep(5)                #Wait 5 Seconds
            GPIO.output(LED, GPIO.LOW)   #Turn off LED
            
        else:                            #Don't open if UIDs don't match
            print("Access Denied, YOU SHALL NOT PASS!")