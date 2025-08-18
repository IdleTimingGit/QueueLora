import time
from constants import *
import torch
import numpy as np
import sounddevice as sd
import librosa
import threading

# Example: Using VITS from TTS library (ensure you have a VITS model checkpoint)
from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer

class TTS:
    def __init__(self, signals):
        self.signals = signals
        self.API = self.API(self)
        self.enabled = True
        self.synth = None
        self.sr = 22050  # Default sample rate for VITS
        self.output_device = OUTPUT_DEVICE_INDEX
        self._init_vits()
        self.signals.tts_ready = True

    def _init_vits(self):
        model_name = "tts_models/en/ljspeech/vits"
        manager = ModelManager()
        model_path, config_path, model_item = manager.download_model(model_name)
        # VITS models do not require a separate vocoder
        self.synth = Synthesizer(
            tts_checkpoint=model_path,
            tts_config_path=config_path,
            use_cuda=torch.cuda.is_available()
        )
        self.sr = self.synth.tts_config.audio['sample_rate']

    def play(self, message):
        if not self.enabled:
            return
        if not message.strip():
            return
        self.signals.sio_queue.put(("current_message", message))
        # Synthesize audio (returns numpy array)
        wav = self.synth.tts(message, speaker_name=None)
        # Normalize audio
        wav = librosa.util.normalize(wav)
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
