#Import Base modules from FastAPI and relevant dependencies
from fastapi import FastAPI
from fastapi.params import Body
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel

#Import std modules
import os
import sys
import json

#init std modules
os.environ["MKL_NUM_THREADS"] = "8"
os.environ["NUMEXPR_NUM_THREADS"] = "8"
os.environ["OMP_NUM_THREADS"] = "8"

#Import custom modules
import pyshorteners as sh
import uuid

#Import custom routes

#Import and initialize database
from pymongo import MongoClient


client = MongoClient()
db = client["urlShortener"]
urls = db["urls"]

#init FastAPI and middleware
app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Shortening Module
def short(url: str):
    return sh.Shortener().tinyurl.short(url)

#init pydantic models
class Payload(BaseModel):
    url: str = ""

@app.post("/urlShortener")
def urlShortener(payload: Payload):
    """
    This api endpoint takes an input of a URL and returns the original url,
    a shortened url and the UUID given to it

    """
    shortURL= short(payload.url)
    url_obj = {"id":uuid.uuid4() ,"url": payload.url, "shortURL": shortURL}
    out = urls.insert_one({"id":str(uuid.uuid4()) ,"url": payload.url, "shortURL": shortURL})
    
    return {"msg":"success","output":(url_obj)}

@app.get("/retrieveAllUrls")
def urlRetrievers():
    """
    This api endpoint takes an input of a URL and returns all the URLS
    
    """
    outputs = [i["url"] for i in urls.find({})]
    return {"msg":"success","output":outputs}

@app.post("/urlDelete")
def urlDeleter(payload: Payload):
    """
    This api endpoint takes an input of a URL and allows the deletion of a URL 
    when given the shorturl
    takes an input of url
    
    """
    urls.delete_one({"shortURL":payload.url})
    return {"msg":"success"}

@app.post("/urlUpdate")
def urlUpdater(payload: Payload):
    """
    This api endpoint takes an input of a URL and allows the update of a URL 
    when given the shorturl
    takes an input of url
    
    """
    urls.update_one({"shortURL":payload.url},{"$set":{"url":payload.url}})
    return {"msg":"success"}

@app.post("/urlVerify")
def urlVerifier(payload: Payload):
    """
    This api endpoint takes an input of a URL and allows the verification of a URL 
    when given the shorturl
    takes an input of url
    
    """
    if urls.find_one({"shortURL":payload.url}):
        return {"msg":"success","output":output}
    return {"msg":"URL does not exist"}


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=80)