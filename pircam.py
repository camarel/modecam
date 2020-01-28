import RPi.GPIO as GPIO
import time
import cv2

from threading import Thread
from io import BytesIO


class Pircam:
    image_width  = 1280
    image_height = 720

    def __init__(self, bot, pir_pin, camera_port):
        self.bot = bot
        self.pin = int(pir_pin)

        # init pir sensor
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin, GPIO.IN)

        # init camera
        self.camera = cv2.VideoCapture(int(camera_port))
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.image_width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.image_height)


    def takePicture(self):
        print('taking picture')
        return_value, image = self.camera.read()
        cv2.imwrite('test.jpg', image) 


    def start(self):
        print('start observer thread')
        thread = Thread(target = self.observe)
        thread.start()


    def observe(self):
        print('observering')
        self.observing = True

        while self.observing:
            if 0 == GPIO.input(self.pin):
                print('-')
            else:
                print('detected movement')
                self.takePicture()
            time.sleep(1)

        print('Stop observing')

    def stop(self):
        self.observing = False

