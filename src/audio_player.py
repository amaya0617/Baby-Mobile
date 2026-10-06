# audio_player.py
import simpleaudio as sa
import threading
import time


class AudioPlayer:
    def __init__(self):
        self.current = None
        self.thread = None
        self.stop_event = threading.Event()
        self.play_obj = None

        self.tracks = {
            "soothing": "audio/soothing.wav",   # crying
            "fun": "audio/fun.wav",             # laughing
            "lullaby": "audio/lullaby.wav"      # sleeping ✅
        }

    def _play_loop(self, wav_path):
        wave = sa.WaveObject.from_wave_file(wav_path)

        while not self.stop_event.is_set():
            self.play_obj = wave.play()

            # Poll instead of blocking
            while self.play_obj.is_playing():
                if self.stop_event.is_set():
                    self.play_obj.stop()
                    return
                time.sleep(0.05)

    def play(self, track_name):
        if self.current == track_name:
            return  # already playing

        self.stop()

        if track_name not in self.tracks:
            print(f"❌ Unknown track: {track_name}")
            return

        self.stop_event.clear()
        self.current = track_name

        self.thread = threading.Thread(
            target=self._play_loop,
            args=(self.tracks[track_name],),
            daemon=True
        )
        self.thread.start()

        print(f"🎵 Playing {track_name}")

    def stop(self):
        if self.current is None:
            return

        self.stop_event.set()

        if self.play_obj and self.play_obj.is_playing():
            self.play_obj.stop()

        self.current = None
        self.thread = None

        print("⏹️ Audio stopped")
