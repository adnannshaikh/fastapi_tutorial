from fastapi import FastAPI,Path,HTTPException,Query
import json

app = FastAPI()

def load_json_data():
    with open('patients.json','r') as f:
        data = json.load(f)

        return data

@app.get("/")
def hello():
    return {'message':'Patient Management System API'}

@app.get('/about')
def about():
    return {'meassage':'API to manage patient record'}

@app.get('/view')
def view():
    data = load_json_data()

    return data


@app.get('/patient/{patient_id}')
def view_patient(patient_id:str = Path(...,description="ID of the patient in the DB",example='P001')):
    data = load_json_data()

    if patient_id in data:
        return data[patient_id]
    else:
        raise HTTPException(status_code=404,detail='Not present in DB')


@app.get('/sort')
def sort_patient(sort_by:str = Query(...,description="Sorting -> Height,Weight,BMI"),order:str = Query('asc')):
   
    valid_field = ['height','weight','bmi']

    if sort_by not in valid_field:
        raise HTTPException(status_code=400,detail = f"invalid field select from {valid_field}")
    if order not in ['asc','desc']:
        raise HTTPException(status_code=400,detail = f"invalid order select from {['asc','desc']}")
    
    data = load_json_data()
    sorted_order = True if order=='desc' else False
    sorted_data = sorted(data.values(),key=lambda x:x.get(sort_by,0),reverse=sorted_order)

    return sorted_data


