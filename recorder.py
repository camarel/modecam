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
    chunk     = 1024  # number of frames per chunks
    channels  = 1     # number of audio channels
    rate      = 16000 # frames per second
    sf        = pyaudio.paInt16 # bits per frame


    def __init__(self, bot, dev_index):
        self.bot = bot
        self.dev_index = int(dev_index)


    def sendAudio(self, wav):
        wav.seek(0)

        # converting to mp3
        mp3 = BytesIO()
        sound = AudioSegment.from_file(wav, format='wav')
        sound.export(mp3, format='mp3')
        mp3.seek(0)

        self.bot.sendAudio(mp3)

        # close streams
        mp3.close()


    def start(self):
        thread = Thread(target = self.record)
        thread.start()


    def record(self):
        logger.info('start to record audio')
        self.listening = True
        pa = pyaudio.PyAudio()

        # prepare wave
        wav = BytesIO()
        wf = wave.open(wav, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(pa.get_sample_size(self.sf))
        wf.setframerate(self.rate)

        stream = pa.open(format=self.sf,
                                  channels=self.channels,
                                  rate=self.rate,
                                  input_device_index=self.dev_index,
                                  input=True,
                                  frames_per_buffer=self.chunk)

        # current = time.time()
        # maxTime = time.time() + self.max_sec

        # record audio
        while self.listening:
            # current = time.time()
            data = stream.read(self.chunk, exception_on_overflow = False)
            wf.writeframes(data)

        logger.info('stop recording audio')

        # closing audio
        stream.stop_stream()
        stream.close()
        pa.terminate()
        wf.close()

        self.sendAudio(wav)
        wav.close()

        logger.info('finished audio recording')


    def stop(self):
        self.listening = False

