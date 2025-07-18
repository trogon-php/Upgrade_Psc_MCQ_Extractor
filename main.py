from fastapi import FastAPI, File, UploadFile, BackgroundTasks, Form ,HTTPException
from fastapi.responses import JSONResponse, FileResponse ,RedirectResponse
from fastapi.staticfiles import StaticFiles
import os
from mcq_extractor.batch_processor import MCQBatchProcessor
import uuid
from datetime import datetime
import json 
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()
api_key = os.getenv("API_KEY")


########################################## CALLING CONVERSION FUNCTION ##########################################
# function for the conversion process call 
def process_file(file_path: str, result_file_name: str, uuid: str, customInput: str):
   if not os.path.isfile(file_path):
    print(f"❌ File not found: {file_path}")
    # return
    # Simulate a time-consuming task
   processor = MCQBatchProcessor(api_key)
   questions = processor.process_pdf_in_batches(file_path, customInput)


   if questions == []:
      print("No questions found ")
      update_metadata(uuid, "Processed , No questions found")
    #   return JSONResponse(content={"message": "No questions found"}, status_code=200)

   

    # Write some result file after processing finishes
   final_json = json.dumps(questions, indent=2, ensure_ascii=False)
   with open(result_file_name, "w", encoding='utf-8') as f:
      f.write(final_json)

   print(f"Processing done, result saved as {result_file_name}")
   update_metadata(uuid, "Processed")
#    return JSONResponse(content={"message": "Processing done, result saved as {result_file_name}"}, status_code=200)


########################################## UPDATE METADATA ##########################################
def update_metadata(uuid: str, status: str):
    print("update")
    with open("metadata/metadata_list.json", "r") as f:
        metadata_list = json.load(f)
    
    # Find and update specific metadata
    for metadata in metadata_list:
         if metadata["uuid"] == uuid:
               metadata.update({"status": status})
               break
    
    # Write back to file
    with open("metadata/metadata_list.json", "w") as f:
         json.dump(metadata_list, f, indent=2)

########################################## SAVING METADATA ##########################################
def save_metadata(metadata):
    print("hello")
    try:
        with open("metadata/metadata_list.json", "r") as f:
            existing_data = json.load(f)
            if not isinstance(existing_data, list):
                existing_data = []
    except json.JSONDecodeError:
        existing_data = []

    existing_data.append(metadata)

    with open("metadata/metadata_list.json", "w") as f:
        json.dump(existing_data, f, indent=4)

########################################## LOADING METADATA ##########################################
@app.get("/metadata")
def load_metadata():
    try:
        with open("metadata/metadata_list.json", "r") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

########################################## Mount static files ##########################################
directory = os.path.join(os.path.dirname(__file__), 'static')
app.mount('/static', StaticFiles(directory=directory), name='static')

########################################## Ensure uploads directory exists ##########################################
uploadSave_Directory = os.path.join(os.path.dirname(__file__), 'tempUploads')
os.makedirs(uploadSave_Directory, exist_ok=True)

@app.get('/')
async def read_root():
    return JSONResponse(content={'message': 'Welcome to the MCQ Extractor!'}, status_code=200)

##########################################  ##########################################
@app.get("/upload")
async def serve_index():
    # Serve the 'index.html' file from the 'static' folder
    return FileResponse(os.path.join("static", "index.html"))

########################################## Upload file ##########################################
@app.post('/upload')
async def upload_file( background_tasks: BackgroundTasks, customInput: str = Form(...), file: UploadFile = File(...) ):
    unique_id = str(uuid.uuid4())
    file_name = unique_id+".pdf"
    file_location = os.path.join(uploadSave_Directory, file_name ) # file.filename is the name of the file , name is taken from the temporary storage of UploadFile
    with open(file_location, 'wb') as buffer:
        buffer.write(file.file.read())

    json_file_path = os.path.join(os.path.dirname(__file__)+"/Outputs/"+unique_id+".json")

    metadata = {
        "uuid": unique_id,
        "original_filename": file.filename,
        "pdf_filepath": file_location,
        "json_filepath": json_file_path,
        "status":"Processing",
        "upload_timestamp": datetime.utcnow().isoformat() + "Z",
    }
    save_metadata(metadata)

    print("Before adding background task")
    background_tasks.add_task(process_file, file_location, json_file_path, unique_id, customInput)
    print("After adding background task")

    return RedirectResponse(url=f"""metadata/{unique_id}""",status_code=302)

@app.get("/metadata/{uuid}")
async def get_status(uuid: str):
    print("calling metadata function for uuid: ", uuid)
    metadata_list = load_metadata()
    metadata = next((item for item in metadata_list if item["uuid"] == uuid), None)
    if not metadata:
        return JSONResponse(content={"status":0,"message":"Metadata not found","metadata":[]},status_code=200)

    return JSONResponse(content={"status":1,'message': 'File Uploaded Succesfully', 'metadata': metadata}, status_code=200)

@app.get("/json/{uuid}")
async def get_json(uuid:str):
   print("getting json srting for uuid :" ,uuid)
   metadata_list=load_metadata()
   metadata = next((item for item in metadata_list if item["uuid"] == uuid), None)

   # Ensuring the metadata is available.
    if not metadata:
        return JSONResponse(content={"status":0,"message":"Metadata not found","metadata":[]},status_code=200)
       
   # Ensure the file exists
    if not os.path.isfile(metadata["json_filepath"]):
        print(f"❌ File not found: {metadata["json_filepath"]}")
        return JSONResponse(content={"status":0,"message":"File not found","data":[]},status_code=200)

    with open(metadata["json_filepath"], "r", encoding="utf-8") as f:
        data = json.load(f)

    return JSONResponse(content={"status":1,'message': 'File Processed Succesfully',"data":data},status_code=200)
