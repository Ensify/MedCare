from torch import cuda
import whisper

class SpeechRecognition:
    def __init__(self):
        device = f'cuda:{cuda.current_device()}' if cuda.is_available() else 'cpu'
        self.model = whisper.load_model("base", device=device)

    def __call__(self, audio_file, response = "text"):
        out = self.model.transcribe(audio_file)
        if response == "text":
          return out["text"]
        else:
          return "\n".join(i['text'] for i in out['segments'])