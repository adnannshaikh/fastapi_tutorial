from fastapi import FastAPI,Path,HTTPException,Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field,computed_field
from typing import Annotated,Literal,Optional
import json

app = FastAPI()

class Patient(BaseModel):
    id:Annotated[str,Field(...,description="ID of patient",examples=['P001'])]
    name:Annotated[str,Field(...,description="Name of the Patient")]
    city:Annotated[str,Field(...,description="Where the Patient resides")]
    age:Annotated[int,Field(...,gt=0,lt=120,description="Age of the patient")]
    gender:Annotated[Literal['male','female'],Field(...,description="gender of the patient")]
    height:Annotated[float,Field(...,gt=0,description='Height of the patient in MTRS')]
    weight:Annotated[float,Field(...,gt=0,description='Weight of the patient in KGS')]
    

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def verdict(self)-> str:
        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Normal'
        else:
            return 'Obese'
        

class PatientUpdate(BaseModel):
    name: Annotated[Optional[str],Field(default=None)]
    city: Annotated[Optional[str],Field(default=None)]
    age: Annotated[Optional[int],Field(default=None,gt=0)]
    gender:Annotated[Optional[Literal['male','female']],Field(default=None)]
    height:Annotated[Optional[float],Field(default=None,gt=0)]
    weight:Annotated[Optional[float],Field(default=None,gt=0)]


def load_json_data():
    with open('patients.json','r') as f:
        data = json.load(f)

        return data
def save_data(data):
    with open('patients.json','w') as f:
        json.dump(data,f)


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

@app.post('/create')
def create_patient(patient:Patient):
    # load existing data
    data = load_json_data()

    # check if the patient already exists
    if patient.id in data:
        raise HTTPException(status_code=400,detail='Patient already exists')
    #if new patient: ADD to the DB
    data[patient.id] = patient.model_dump(exclude=['id'])

    #save into json file
    save_data(data)

    return JSONResponse(status_code=201,content={'Message':'Patient Created Sucessfully'})
    

@app.put('/edit/{patient_id}')
def update_patient(patient_id:str,patient_update:PatientUpdate):
    data = load_json_data()

    if patient_id not in data:
        raise HTTPException(status_code=404,detail="Patient not found")
    
    if patient_id in data:
        existing_patient = data[patient_id]

        # convert pydantic object in dict
        updated_patient_info = patient_update.model_dump(exclude_unset=True)

        for key,value in updated_patient_info.items():
            existing_patient[key] = value
    '''
    As we have update the field but we also have to change the computed field
    so a neat way to do it is to run the Pydantic object model again so that
    it calculates the computed fields
    '''
    # existing_patient -> pydantic object -> updated bmi + verdit -> dict
    existing_patient['id'] = patient_id
    patient_pydantic_object = Patient(**existing_patient)
    existing_patient = patient_pydantic_object.model_dump(exclude='id')
    
    # add this dict to data
    data[patient_id] = existing_patient

    save_data(data)

    return JSONResponse(status_code=200,content="Patient updated")


@app.delete('/delete/{patient_id}')
def delete_patient(patient_id:str):
    data = load_json_data()
    
    if patient_id not in data:
        raise HTTPException(status_code=404,detail='No such patient found')
    
    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200,content={'message':'Deleted Successfully'})