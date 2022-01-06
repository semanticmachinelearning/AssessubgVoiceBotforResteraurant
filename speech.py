import collections
import io
import os
import sys
import time
import wave
from array import array
from struct import pack

import playsound as ps
import pyaudio
import webrtcvad
from google.cloud import speech as stt
from google.cloud import texttospeech as tts


class Speech:
    def __init__(self, test_mode, corrections):
        super().__init__()

        self.test_mode = test_mode
        if not self.test_mode:

            self.format = pyaudio.paInt16
            self.sample_rate = 16000
            self.channels = 1
            self.chunk_ms = 30
            self.padding_ms = 500
            self.chunk_size = int(self.sample_rate * self.chunk_ms / 1000)
            self.chunk_bytes = self.chunk_size * 2
            self.padding_chunks = int(self.padding_ms / self.chunk_ms)
            self.num_chunks = int(400 / self.chunk_ms)
            self.num_chunks_end = self.num_chunks * 2
            self.start_offset = int(self.num_chunks * self.chunk_ms * 0.5 * self.sample_rate)
            self.vad = webrtcvad.Vad(2)
            self.pa = pyaudio.PyAudio()
            self.sentence = False
            self.leave = False
            self.input_path = "Data/input.wav"
            self.output_path = "Data/output.mp3"

            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "Data/GoogleCredentials.json"
            self.stt_client = stt.SpeechClient()
            self.tts_client = tts.TextToSpeechClient()
            self.recognition_config = stt.RecognitionConfig(encoding=stt.RecognitionConfig.AudioEncoding.LINEAR16,
                                                            sample_rate_hertz=self.sample_rate, language_code="en-UK",
                                                            audio_channel_count=1)
            self.voice_config = tts.VoiceSelectionParams(language_code="en-UK", ssml_gender=tts.SsmlVoiceGender.FEMALE)
            self.audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3)
            self.voice = None

            voices = self.tts_client.list_voices()
            for voice in voices.voices:
                if voice.name == "en-GB-Wavenet-A":
                    self.voice = voice

            self.corrections = corrections

    def handle_int(self, sig, chunk):
        self.sentence = True
        self.leave = True

    def save_to_file(self, data, sample_width):
        data = pack("<" + ("h" * len(data)), *data)
        wf = wave.open(self.input_path, "wb")
        wf.setnchannels(self.channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(self.sample_rate)
        wf.writeframes(data)
        wf.close()
        print("file saved")

    def normalize(self, snd_data):
        maximum = 32767
        times = float(maximum) / max(abs(i) for i in snd_data)
        r = array("h")
        for i in snd_data:
            r.append(int(i * times))
        return r

    def recognise_speech(self):
        # signal.signal(signal.SIGINT, self.handle_int)
        self.sentence = False
        self.leave = False
        while not self.leave:
            buffer = collections.deque(maxlen=self.padding_chunks)
            triggered = False
            voiced_frames = []
            buffer_flags = [0] * self.num_chunks
            buffer_index = 0

            buffer_flags_end = [0] * self.num_chunks_end
            buffer_index_end = 0
            bufer_in = ""
            raw_data = array("h")
            index = 0
            start_point = 0
            start_time = time.time()
            stream = self.pa.open(format=self.format,
                                  channels=self.channels,
                                  rate=self.sample_rate,
                                  input=True,
                                  start=True,
                                  # input_device=1,
                                  frames_per_buffer=self.chunk_size)

            while not self.sentence and not self.leave:
                chunk = stream.read(self.chunk_size)
                raw_data.extend(array("h", chunk))
                index += self.chunk_size
                time_used = time.time() - start_time
                active = self.vad.is_speech(chunk, self.sample_rate)

                sys.stdout.write('-' if active else '_')
                buffer_flags[buffer_index] = 1 if active else 0
                buffer_index += 1
                buffer_index %= self.num_chunks

                buffer_flags_end[buffer_index_end] = 1 if active else 0
                buffer_index_end += 1
                buffer_index_end %= self.num_chunks_end

                if not triggered:
                    buffer.append(chunk)
                    num_voiced = sum(buffer_flags)
                    if num_voiced > 0.8 * self.num_chunks:
                        sys.stdout.write(' open ')
                        triggered = True
                        start_point = index - self.chunk_size * 20
                        buffer.clear()
                else:
                    buffer.append(chunk)
                    num_unvoiced = self.num_chunks_end - sum(buffer_flags_end)
                    if num_unvoiced > 0.9 * self.num_chunks_end or time_used > 10:
                        sys.stdout.write(' close ')
                        triggered = False
                        self.sentence = True

                sys.stdout.flush()

            print("")

            stream.stop_stream()
            print("done")
            self.sentence = False

            raw_data.reverse()
            for index in range(start_point):
                raw_data.pop()
            raw_data.reverse()
            raw_data = self.normalize(raw_data)
            self.save_to_file(raw_data, 2)
            self.leave = True

        stream.close()

        with io.open(self.input_path, "rb") as audio_file:
            content = audio_file.read()
            audio = stt.RecognitionAudio(content=content)

        response = self.stt_client.recognize(config=self.recognition_config, audio=audio)
        try:
            text = format(response.results[0].alternatives[0].transcript)
        except IndexError:
            text = ""

        os.remove(self.input_path)

        for i in self.corrections:
            if i in text:
                text = text.replace(i, self.corrections[i])

        return text

    # Convert text to speech
    def speak(self, message):
        if self.test_mode:
            print("VoiceBot:", message)
        else:
            synthesis_input = tts.SynthesisInput(text=message)
            response = self.tts_client.synthesize_speech(input=synthesis_input, voice=self.voice_config,
                                                         audio_config=self.audio_config)
            with open(self.output_path, "wb") as out:
                out.write(response.audio_content)

            ps.playsound(self.output_path, True)
            os.remove(self.output_path)
