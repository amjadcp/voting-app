from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
from bson.objectid import ObjectId
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Initialize FastAPI and MongoDB client
app = FastAPI()
client = MongoClient(os.getenv('URI'))  # Replace with your MongoDB URI
db = client[os.getenv('DB')]  # Replace with your database name
candidates_collection = db[os.getenv('COLLECTION')]  # Replace with your collection name

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_votes(request: Request):
    candidates = list(candidates_collection.find())
    return templates.TemplateResponse("vote.html", {
        "request": request,
        "candidate1": candidates[0] if len(candidates) > 0 else {},
        "candidate2": candidates[1] if len(candidates) > 1 else {},
    })

class VoteRequest(BaseModel):
    ID: str
@app.post("/vote")
async def vote(vote_request: VoteRequest):
    candidate = candidates_collection.find_one_and_update(
        {"ID": vote_request.ID},
        {"$inc": {"votes": 1}},
        return_document=True
    )
    return {
        'success': True,
        'candidate': candidate['candidate']
    }

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)