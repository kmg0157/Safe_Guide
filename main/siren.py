import Jetson.GPIO as GPIO
import time

class Siren:
    def __init__(self):
        self.BUZZER = 12
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.BUZZER, GPIO.OUT)


    def default(self):
        GPIO.output(self.BUZZER, GPIO.LOW)


    def danger_notice(self):
        try:
            while True:
                GPIO.output(self.BUZZER, GPIO.HIGH)
                time.sleep(1)
                GPIO.output(self.BUZZER, GPIO.LOW)
                time.sleep(1)

        finally:
            GPIO.cleanup()

    def warning_notice(self):
        try:
            while True:
                GPIO.output(self.BUZZER, GPIO.HIGH)
                time.sleep(1)
                GPIO.output(self.BUZZER, GPIO.LOW)
                time.sleep(0.5)

        finally:
            GPIO.cleanup()


def main():
    s = Siren()
    s.start_notice()

if __name__ == "__main__":
    main()
