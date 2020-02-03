import RPi.GPIO as GPIO
import time
import cv2

from threading import Thread
from io import BytesIO

from recorder import Recorder


class Pircam:
    image_width  = 1280
    image_height = 720

    def __init__(self, bot, pir_pin, camera_port, audio_index):
        self.bot = bot
        self.pin = int(pir_pin)
        self.camera_port = int(camera_port)
        self.audio_index = int(audio_index)

        # init pir sensor
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin, GPIO.IN)

        self.recorder = Recorder(self.bot, self.audio_index)


    def takePictures(self):
        print('taking picture')
        frames = 0
        loop = 0

        self.recorder.start()

        camera = cv2.VideoCapture(self.camera_port)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.image_width)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.image_height)

        # camera.set(cv2.CAP_PROP_BRIGHTNESS, 190.0)
        camera.set(cv2.CAP_PROP_SATURATION, 50.0)

        while 1 == GPIO.input(self.pin):
            return_value, image = camera.read()

            if frames == 0:
                is_success, imbuffer = cv2.imencode(".jpg", image)
                io_buf = BytesIO(imbuffer)

                self.bot.sendPicture(io_buf)
                if (loop < 2):
                    loop += 1
                    frames = 10
                else:
                    frames = 80

            else:
                frames -= 1

        camera.release()
        self.recorder.stop()


    def startThread(self):
        print('start observer thread')
        thread = Thread(target = self.observe)
        thread.start()


    def observe(self):
        print('observering')
        self.observing = True

        while self.observing:
            if 0 == GPIO.input(self.pin):
                time.sleep(1)
            else:
                self.takePictures()

        print('Stop observing')

    def stop(self):
        self.observing = False

