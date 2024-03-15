import torch
from torch import cuda, bfloat16

import transformers
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification

from langchain_community.llms import HuggingFacePipeline
import whisper

import time
import requests
import fitz

class NER:
    class NERAll:
        def __init__(self):
            self.tokenizer = AutoTokenizer.from_pretrained("d4data/biomedical-ner-all")
            self.model = AutoModelForTokenClassification.from_pretrained("d4data/biomedical-ner-all")
            if torch.cuda.is_available():
                self.pipe = pipeline("ner", model=self.model, tokenizer=self.tokenizer, aggregation_strategy="simple", device = 0)
            else:
                self.pipe = pipeline("ner", model=self.model, tokenizer=self.tokenizer, aggregation_strategy="simple")

        def __call__(self,text):
            return self.pipe(text)

    class BioBERT:
        def __init__(self):
            self.d_pipe = pipeline("token-classification", model="alvaroalon2/biobert_diseases_ner", torch_dtype = bfloat16)
            self.c_pipe = pipeline("token-classification", model="alvaroalon2/biobert_chemical_ner", torch_dtype = bfloat16)
            self.g_pipe = pipeline("token-classification", model="alvaroalon2/biobert_genetic_ner", torch_dtype = bfloat16)

        def _filter(self,entity_list):
            return [i for i in entity_list if i['entity']!='0']
        def __call__(self,text):
            return self._filter(self.d_pipe(text) + self.c_pipe(text) + self.g_pipe(text))



    def __init__(self, model = 'biobert'):
        if model == 'all':
            self.ner = NER.NERAll()
        elif model == 'biobert':
            self.ner = NER.BioBERT()
        else:
            raise f"{model} is not a valid value for model. Use all/biobert"

    def _process(self,o):
        result = []
        s = ""
        si,ei = 0,0
        for i in o:
            if i['word'].startswith("##"):
                s+= i['word'][2:]
                ei= i['end']
            else:
                if s:
                    result.append((s,si,ei))
                si = i['start']
                s = i['word']
                ei = i['end']
        if s:
            result.append((s,si,ei))
        return result

    def __call__(self, text):
        return self._process(self.ner(text))

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

class Summarizer:

    def __init__(self):
        self.ner = NER()
        self.llm = self.__build_llm()
        self.transcribe = SpeechRecognition()

    def __build_llm(self):
        model_id = "meta-llama/Llama-2-13b-chat-hf"
        device = f'cuda:{cuda.current_device()}' if cuda.is_available() else 'cpu'

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

    def meaning(self,word, better_meanings,debug):
        try:
            api_url = f"https://www.dictionaryapi.com/api/v3/references/medical/json/{word}?key=b488197c-37b5-4148-beb8-5c69b84a4f2f"
            response = requests.get(api_url).json()
            results = " \n".join([" \n ".join(i['shortdef']) for i in response if 'shortdef' in i])
            if not better_meanings: return results

            template = f"""
<s>[INST] <<SYS>>
You will be given a word and dictionary meanings for the word. Give a short understandable description in layman terms. It must be very short and direct.
You need not explain all dictonary meanings. Use dictionary meanings just for reference. The answer must be a single short paragraph.
<</SYS>>
Word: {word}
Dictionary Meanings: {results}
Answer:[/INST]
"""
            result = self.llm.invoke(template)
            result = result[result.find("\n"):]
            if debug: print(result+"\n---------------------------------------------\n")
            return result
        except:
            return ""

    def patient_abstract(self, documents, text, summaries):
        document_content = ""
        for document in documents:
            doc = fitz.open(document)
            for page in doc:
                text = page.get_text()
                document_content += text + "\n"

        summaries = "\n".join(summaries)
        text= "\n".join(text)
        
        template = f"""
<s>[INST] <<SYS>>
You will be given all patient reports and summaries of conversation between patients and doctors. You need to generate a short description about the patient in about 100 to 200 words.
Just directly give the summary do not add anything else. Directly start with summary, dont say anything like "here is the summary".
Dont create anything on your own. The output must only be from the given conversation and documents.
<</SYS>>
Reports: 
{document_content}
{text}

Conversation Summaries: {summaries}
Answer:[/INST]
"""
        return self.llm.invoke(template)
    
    def get_doctor_suggestions(self,conversation):
        template = f"""
<s>[INST] <<SYS>>
You will be given a conversation between a doctor and a patient. You need to compile a short list of suggestions or advices the doctor has said to the patient.
Do not make up anything on your own. Only give a short list of what the doctor adviced the patient to do.
It is for the patient to easily see what they must follow. If there is no suggestions, tell that there were no suggestions, do not make things up.
<</SYS>>
{conversation}
[/INST]
"""
        return self.llm.invoke(template)
    
    def __call__(self, audio, debug = False, better_meanings = True):
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
        t = time.time()
        ner_out = self.ner(patient_summary)
        if debug: print(f"Time taken for ner {time.time()-t}",ner_out,sep="\n")
        t = time.time()
        suggestions = self.get_doctor_suggestions(conversation)
        if debug: print(f"Time taken for suggestions {time.time()-t}",suggestions,sep="\n")

        return {
            'patientSummary': {
                'summaryText': patient_summary,
                'indices': [[i[1],i[2]] for i in ner_out],
                'meanings': [self.meaning(i[0],better_meanings,debug) for i in ner_out]
            },
            'doctorSummary': doctor_summary,
            'suggestions': suggestions
        }