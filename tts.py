
import time
from constants import *
import torch
import numpy as np
import sounddevice as sd
import threading
from TTS.api import TTS as CoquiTTS


class TTS:
    def __init__(self, signals):
        self.signals = signals
        self.API = self.API(self)
        self.enabled = True
        self.output_device = OUTPUT_DEVICE_INDEX
        # Load a local Coqui TTS model (change model_name as needed)
        self.model_name = "tts_models/en/ljspeech/vits"  # Or another local model
        self.tts = CoquiTTS(self.model_name)
        self.sr = self.tts.synthesizer.tts_config.audio["sample_rate"]
        self.signals.tts_ready = True

    def play(self, message):
        if not self.enabled or not message.strip():
            return
        self.signals.sio_queue.put(("current_message", message))
        # Synthesize audio (returns numpy array)
        wav = self.tts.tts(text=message, speaker=None)
        # Play audio in a separate thread to avoid blocking
        threading.Thread(target=self._play_audio, args=(wav,), daemon=True).start()

    def _play_audio(self, wav):
        self.audio_started()
        sd.play(wav, self.sr, device=self.output_device, blocking=True)
        sd.stop()
        self.audio_ended()

    def stop(self):
        sd.stop()
        self.signals.AI_speaking = False

    def audio_started(self):
        self.signals.AI_speaking = True

    def audio_ended(self):
        self.signals.last_message_time = time.time()
        self.signals.AI_speaking = False

    class API:
        def __init__(self, outer):
            self.outer = outer

        def set_TTS_status(self, status):
            self.outer.enabled = status
            if not status:
                self.outer.stop()
            self.outer.signals.sio_queue.put(('TTS_status', status))

        def get_TTS_status(self):
            return self.outer.enabled

        def abort_current(self):
            self.outer.stop()
