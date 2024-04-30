# MedCare

In the realm of healthcare, one of the most pressing challenges lies in the complexity of Electronic Health Records (EHRs) and the intricate terminology embedded within them. This complexity often obstructs patient comprehension and creates hurdles for healthcare providers, leading to inefficiencies in workflow and potentially compromising patient care. Navigating through dense medical jargon can be overwhelming for patients, hindering their ability to understand their own health conditions and treatment plans. Similarly, healthcare professionals may face difficulties in deciphering and conveying crucial information, impeding effective communication and decision-making processes. 

Medcare is a centralised health care system that offers Enhanced EHRs from doctor patient conversations and generates apt summary in patient perspective and in doctor perspective making it a useful tool for both patient and doctor.

# Implementation Details (IMPORTANT)
Each component is implemented as a microservice and can function as a whole application.

### Summary Generation - ML branch
Please refer to the branch ml for implementation of the LLM microservice which is responsible for summary generation, NER and suggestion extraction.

### Doctor Website - doctor branch
Please refer to the branch doctor for implementation of the doctor website microservice which is the website that will be used by the healthcare providers.

### Patient Website - patient branch
Please refer to the branch patient for implementation of the patient website microservice which is the website that will be used by the patients.

## Features

### 1. Doctor Summary

A short and point-wise summary of symptoms that the patient has said which will be useful information for future diagnostics.

### 2. Patient Summary

A elaborate summary of what the doctor has said to the patient and the advices the doctor has given, in a friendly manner that is in layman terms.

### 3. Named Entity Recognition

Complex medical information and terminology are filtered and contexted meaning is provided, that is, the word will be explained along with its meaning and its usage in the given context.

### 4. Doctor's Suggestions for Patient

The patient can view the important suggestions and advices the doctor has said for the patient to follow making it east to keep track.

## UI Links (Pre-implementation UI)

### Note: This UI is outdated, the current implementation has better UI/UX.

Patient Site: https://velvety-lebkuchen-61f2fa.netlify.app/ (This is just demo UI, depicting the workflow of the application)

Doctor Site: https://ehr-doctor.netlify.app/
