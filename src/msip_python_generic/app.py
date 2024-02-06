# Standardized App Logic (Should not be changed) 
import sys
import os
from urllib import request
import requests
sys.dont_write_bytecode = True

# Configure logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Load environment-specific properties
from dotenv import load_dotenv
app_env = os.getenv('ENVIRONMENT', 'DEV')
env_file = f'./properties/{app_env}.env'
logging.info(f"Loading properties file {env_file}")
load_dotenv(dotenv_path=env_file)

# Configure API server
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from functools import wraps
app = FastAPI()

# ------------------------------ My Imports ------------------------------ #
# If you include external libraries, ensure they are also included in "requirements.txt" or your application may not build properly

from my_utils import auth_check_ldap

# ------------------------------ Local variables and helper functions ------------------------------ #

# Allow HTTPExceptions to return with a text body instead of JSON
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)

# ------------------------------ FastAPI Endpoints ------------------------------ #

# Callable locally and when deployed to OCP
@app.get("/exampleAPI-HealthCheck")
def health_check(request: Request):
 
    logging.info("Health Check")
    return PlainTextResponse("Service is running", status_code=200)

# Callable locally and when deployed to OCP
@app.get("/exampleAPI-ForwardRequest")
def foward_request(request: Request):
 
    logging.info("Forwarding request to another MSIP service")
    
    # Call external API
    honda_certificate = "supporting_files/" + os.environ.get("honda_certificate")
    sample_api_service_url = os.environ.get("sample_api_service_url")
    response = requests.get(sample_api_service_url, verify=honda_certificate)

    # Process response
    if response.ok:
        return JSONResponse(content=response.json())
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

# Callable only when deployed to OCP
@app.get("/exampleAPI-Authenticate")
@auth_check_ldap
def authenticate(request: Request):
 
    logging.info("Calling athenticated API")
    return PlainTextResponse("Authentication Successful", status_code=200)

# Callable only when deployed to OCP
@app.post("/exampleAPI-TestNotification")
def test_notification(request: Request, email: str):
 
    logging.info("Calling Email notification Service")

    # Call notification API
    honda_certificate = "supporting_files/" + os.environ.get("honda_certificate")
    notification_service_url = os.environ.get("notification_service_url")
    post_body = {"to": email, "message":"Testing MSIP Email Notifications"}
    response = requests.post(notification_service_url, json=post_body, verify=honda_certificate)

    # Process response
    if response.ok:
        return PlainTextResponse(f"Email sent to {to_user}", status_code=200)
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

# ------------------------------ Standardized App Logic (Should not be changed) ------------------------------ #

if __name__ == "__main__":

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="debug")
