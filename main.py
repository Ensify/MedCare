from summary import Summarizer

import os
import dotenv
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
dotenv.load_dotenv()
from pymongo import MongoClient

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
    result = summarizer(audio_file.filename, debug = True)
    os.remove(audio_file.filename)
    collection.insert_one({
        "patientId": patientId,
        "hospitalId": hospitalId,
        "doctorName": doctorName,
        "doctorSummary": result["doctorSummary"],
        "patientSummary": result["patientSummary"]
    })
    print("ended..")

    return {"Status":200}



if "__main__" == __name__:
    summarizer = Summarizer()
    uvicorn.run(app,host="0.0.0.0",port = 8000)