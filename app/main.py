from fastapi import FastAPI
import socket

app = FastAPI()

"""
Summary:
    This function returns a JSON response with a message and the hostname of the container.
    The hostname will help identify which container is responding to the request between
    multiple instances of the same container.    
"""
@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI", "hostname": socket.gethostname()}