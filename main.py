from model import Summarizer

import os
import dotenv
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
dotenv.load_dotenv()
from pymongo import MongoClient
from tempfile import TemporaryDirectory

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

    temp_dir = TemporaryDirectory()

    for i,doc in enumerate(documents):
        file = doc['content']
        with open(os.path.join(temp_dir.name,doc['fileName']),"wb") as f:
            f.write(file)
    l = os.listdir(temp_dir.name)
    print(l)
    print(summaries)
    summary = summarizer.patient_abstract(documents=l, summaries=summaries)

    patient_collection.update_one({'patientId':patientId},{'$set':{'profileSummary':summary}})

    temp_dir.cleanup()
    return summary



if "__main__" == __name__:
    summarizer = Summarizer()
    uvicorn.run(app,host="0.0.0.0",port = 8000)