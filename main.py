from summary import Summarizer

import os
import dotenv
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
dotenv.load_dotenv()
from pymongo import MongoClient
from tempfile import TemporaryDirectory

from deep_translator import GoogleTranslator

import pytesseract
from PIL import Image

app = FastAPI()

client = MongoClient(os.environ.get('MONGO_URI'))
db = client["medical-simplify"]

collection = db['conv-summaries']
ehr_collection = db['patient-ehr']
patient_collection = db['patient-datas']

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/')
def root():
    return "Medical Summary Bot API"

@app.post('/translated')
async def get_answer(text: str = Form(...), lang: str = Form(...)):
    try:
        res = GoogleTranslator(source='en',target=lang).translate(text)
        return {'status': 'success', 'text': res}
    except:
        return {'status': 'error','text': text}

@app.post('/process')
async def get_answer(patientId: int = Form(...), hospitalId: int = Form(...), doctorName: str = Form(...), date: str = Form(...), audio_file: UploadFile = File(...)):
    print("starting..")
    with open(audio_file.filename,'wb') as f:
        f.write(audio_file.file.read())
    result = summarizer(audio_file.filename,debug = True, better_meanings = True)
    os.remove(audio_file.filename)
    collection.insert_one({
        "patientId": patientId,
        "hospitalId": hospitalId,
        "doctorName": doctorName,
        "doctorSummary": result["doctorSummary"],
        "patientSummary": result["patientSummary"],
        "suggestions": result["suggestions"],
        "Date": date
    })
    print("ended..")
    
    suggestions = result['suggestions']
    patient_collection.update_one({'patientId':patientId},{'$set':{'suggestions':suggestions}})

    return {"Status":200}


@app.post('/update_summary')
async def update_summary(patientId:int = Form(...)):
    summaries  = collection.find({'patientId':patientId})
    summaries = [i['doctorSummary'] for i in summaries]

    documents = ehr_collection.find({"patientId":patientId,'fileType':"pdf"})
    images = ehr_collection.find({"patientId":patientId,'fileType':"image"})

    temp_dir = TemporaryDirectory()
    img_dir = TemporaryDirectory()

    for doc in documents:
        file = doc['content']
        with open(os.path.join(temp_dir.name,doc['fileName']),"wb") as f:
            f.write(file)
    l = [os.path.join(temp_dir.name,i) for i in os.listdir(temp_dir.name)]

    ocr_text = []
    for img in images:
        file = img['content']
        with open(os.path.join(img_dir.name,img['fileName']),"wb") as f:
            f.write(file)
        ocr_text.append(pytesseract.image_to_string(Image.open(os.path.join(img_dir.name,img['fileName']))))

    summary = summarizer.patient_abstract(documents=l, text= ocr_text, summaries=summaries)

    patient_collection.update_one({'patientId':patientId},{'$set':{'profileSummary':summary}})

    img_dir.cleanup()
    temp_dir.cleanup()
    return summary



if "__main__" == __name__:
    summarizer = Summarizer()
    uvicorn.run(app,host="0.0.0.0",port = 8000)