from speech import SpeechRecognition
from summary import Summarizer

stt = SpeechRecognition()
summarizer = Summarizer()

transcript = stt('sample.wav')
summary = summarizer(transcript)

print(summary)