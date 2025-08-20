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
        self.model_name = "tts_models/en/vctk/vits"  # Male and female voices
        self.speaker = "p232"  # Default male speaker from VCTK
        self.tts = CoquiTTS(self.model_name)
        self.sr = self.tts.synthesizer.tts_config.audio["sample_rate"]
        self.signals.tts_ready = True

    def play(self, message):
        if not self.enabled or not message.strip():
            return
        self.signals.sio_queue.put(("current_message", message))
        # Synthesize audio (returns numpy array)
        wav = self.tts.tts(text=message, speaker=self.speaker)
        # Play audio in a separate thread to avoid blocking
        threading.Thread(target=self._play_audio, args=(wav,), daemon=True).start()

    def _play_audio(self, wav):
        self.audio_started()
        import numpy as np
        # Ensure wav is a numpy array before any processing
        if not isinstance(wav, np.ndarray):
            wav = np.array(wav)

        # Optionally increase speed/pitch by resampling
        SPEEDUP = 1.03  # 1.0 = normal, >1.0 = faster/higher
        if SPEEDUP != 1.0:
            try:
                import scipy.signal
                orig_len = wav.shape[0]
                new_len = int(orig_len / SPEEDUP)
                if wav.ndim == 1:
                    wav = scipy.signal.resample(wav, new_len)
                else:
                    wav = np.stack([scipy.signal.resample(wav[:, ch], new_len) for ch in range(wav.shape[1])], axis=1)
                print(f"[TTS] Increased speed/pitch by {SPEEDUP}x.")
            except ImportError:
                print("[TTS] scipy not installed, cannot change speed/pitch. Install scipy for best results.")

        import sounddevice as sd
        try:
            device_info = sd.query_devices(self.output_device, 'output')
        except Exception as e:
            print(f"[TTS] ERROR: Could not use output device index {self.output_device}: {e}")
            print("[TTS] Please check that the device exists and is not in use by another application.")
            print("[TTS] Available output devices:")
            for idx, dev in enumerate(sd.query_devices()):
                if dev['max_output_channels'] > 0:
                    print(f"  [{idx}] {dev['name']} (channels: {dev['max_output_channels']})")
            return

        channels = device_info['max_output_channels']
        device_name = device_info['name']
        print(f"[TTS] Using device index {self.output_device}: {device_name}")
        print(f"[TTS] Device supports {channels} channels. Audio shape: {getattr(wav, 'shape', 'unknown')}")

        # If mono and device expects stereo, duplicate
        if wav.ndim == 1 and channels == 2:
            wav = np.stack([wav, wav], axis=-1)
        # If stereo and device expects mono, average channels
        elif wav.ndim == 2 and wav.shape[1] == 2 and channels == 1:
            wav = wav.mean(axis=1)
        # If device expects more channels, pad with zeros
        elif wav.ndim == 1 and channels > 1:
            wav = np.tile(wav[:, None], (1, channels))
        elif wav.ndim == 2 and wav.shape[1] < channels:
            pad_width = channels - wav.shape[1]
            wav = np.pad(wav, ((0, 0), (0, pad_width)), mode='constant')

        # Always resample to 48000 Hz for virtual cable compatibility
        target_sr = 48000
        if self.sr != target_sr:
            try:
                import scipy.signal
                duration = wav.shape[0] / self.sr
                new_length = int(duration * target_sr)
                if wav.ndim == 1:
                    wav = scipy.signal.resample(wav, new_length)
                else:
                    wav = np.stack([scipy.signal.resample(wav[:, ch], new_length) for ch in range(wav.shape[1])], axis=1)
                print(f"[TTS] Resampled audio from {self.sr} Hz to {target_sr} Hz.")
            except ImportError:
                print("[TTS] scipy not installed, cannot resample audio. Install scipy for best compatibility.")
        play_sr = target_sr

        print(f"[TTS] Playing audio with shape: {wav.shape}, dtype: {wav.dtype}")
        try:
            sd.play(wav, play_sr, device=self.output_device, blocking=True)
        except Exception as e:
            print(f"[TTS] ERROR: Could not play audio on device {self.output_device}: {e}")
            print("[TTS] This is usually a Windows audio driver/device error. Try rebooting, disabling exclusive mode, or making sure no other app is using the device.")
        finally:
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
