import pyaudio
import wave
import logging

from io import BytesIO
from pydub import AudioSegment
from threading import Thread

logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class Recorder:
    # audio settings
    chunk     = 1024  # record in chunks of 1024 samples
    channels  = 1     # number of audio channels
    rate      = 16000 # record at 16000 frames per second
    sf        = pyaudio.paInt16 # 16 bits per sample


    def __init__(self, bot, dev_index):
        self.bot = bot
        self.dev_index = int(dev_index)


    def sendAudio(self, recording):
       # creating wave
       wav = BytesIO()
       wf = wave.open(wav, 'wb')
       wf.setnchannels(self.channels)
       wf.setsampwidth(self.p.get_sample_size(self.sf))
       wf.setframerate(self.rate)
       wf.writeframes(recording)
       wf.close()
       wav.seek(0)

       # converting to mp3
       mp3 = BytesIO()
       sound = AudioSegment.from_file(wav, format='wav')
       sound.export(mp3, format='mp3')
       mp3.seek(0)

       self.bot.sendAudio(mp3)

       # close streams
       wav.close()
       mp3.close()


    def start(self):
        thread = Thread(target = self.record)
        thread.start()


    def record(self):
        logger.info('start to record audio')
        self.listening = True

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.sf,
                                  channels=self.channels,
                                  rate=self.rate,
                                  input_device_index=self.dev_index,
                                  input=True,
                                  frames_per_buffer=self.chunk)

        rec = []
        # current = time.time()
        # maxTime = time.time() + self.max_sec

        while self.listening:
            # current = time.time()
            data = self.stream.read(self.chunk, exception_on_overflow = False)
            rec.append(data)

        logger.info('stop recording audio')
        self.sendAudio(b''.join(rec))

        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def stop(self):
        self.listening = False

