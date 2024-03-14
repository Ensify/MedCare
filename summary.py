from torch import bfloat16
import transformers
from langchain_community.llms import HuggingFacePipeline
import time

from speech import SpeechRecognition


class Summarizer:

    def __init__(self):
        self.llm = self.__build_llm()
        self.transcribe = SpeechRecognition()

    def __build_llm(self):
        model_id = "meta-llama/Llama-2-13b-chat-hf"

        bnb_config = transformers.BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type='nf4',
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=bfloat16
            )

        model = transformers.AutoModelForCausalLM.from_pretrained(
                model_id,
                quantization_config=bnb_config,
                device_map='auto',
            )

        tokenizer = transformers.AutoTokenizer.from_pretrained(model_id)

        query_pipeline = transformers.pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                torch_dtype=bfloat16,
                device_map="auto"
            )

        return HuggingFacePipeline(pipeline=query_pipeline)

    def annotate_transcript(self,transcript):
        template = f"""
<s>[INST] <<SYS>>
You will be given transcription of a conversation between a doctor and a patient. You need to clean up repeated words in the conversation, split when dialogue starts and when it ends and also annotate who said what.
Just give the annotated conversation alone as the response. Use Doctor: and Patient: as annotation. You need not say that here is annotated conversation, start with output directly
You should never add content or words on your own, never rephrase anything. It should be exact conversation. The conversation must be word to word.
<</SYS>>
{transcript}
[/INST]
"""
        return self.llm.invoke(template)

    def get_patient_summary(self,conversation):
        template = f"""
<s>[INST] <<SYS>>
You are a summary bot who gives summary for medical conversation between a different doctor and a patient to the patient in a more understandable manner.
The summary is for the patient, so refer to the patient in a first person tone. Directly give the summary do not add anything else.
The summary should focus on what the doctor has said. You are telling directly to the patient so use phrases like 'the doctor as said you' , 'you need to', etc.
Only tell included information do not add anything new. Just directly give the summary alone. It must be short paragraph.
<</SYS>>
{conversation}
[/INST]
"""
        return self.llm.invoke(template)

    def get_doctor_summary(self,conversation):
        template = f"""
<s>[INST] <<SYS>>
You are a summary bot who gives summary for medical conversation between a different doctor and a patient to the doctor as short hints.
The summary is for the doctor, so include the medical terms as it is, only give hints. Directly give the summary do not add anything else.
The summary should focus on the symptomps of the patient. Only tell included information do not add anything new.
Just directly give the hints alone. It must be short.
<</SYS>>
{conversation}
[/INST]
"""
        return self.llm.invoke(template)

    def __call__(self, audio, debug = False):
        t = time.time()
        transcript = self.transcribe(audio, response = "all")
        if debug: print(f"Time taken for speech recognition {time.time()-t}",transcript,sep="\n")
        # t = time.time()
        # conversation = self.annotate_transcript(transcript)
        # if debug: print(f"Time taken for annotation {time.time()-t}",conversation,sep="\n")
        conversation = transcript
        t = time.time()
        patient_summary = self.get_patient_summary(conversation)
        if debug: print(f"Time taken for patient summarization {time.time()-t}",patient_summary,sep="\n")
        t = time.time()
        doctor_summary = self.get_doctor_summary(conversation)
        if debug: print(f"Time taken for doctor summarization {time.time()-t}",doctor_summary,sep="\n")

        return {
            'patientSummary': patient_summary,
            'doctorSummary': doctor_summary
        }