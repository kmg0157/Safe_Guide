import Jetson.GPIO as GPIO
import time

class Siren:
    def __init__(self):
        self.BUZZER = 12
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.BUZZER, GPIO.OUT)

    def start_notice(self,order):
        try:
            while True:
                GPIO.output(self.BUZZER, GPIO.HIGH)
                time.sleep(3)
                GPIO.output(self.BUZZER, GPIO.LOW)
                time.sleep(0.5)

                # Check for user input
                if order == 'END':
                    break
        finally:
            GPIO.cleanup()

def main():
    s = Siren()
    s.start_notice()

if __name__ == "__main__":
    main()
