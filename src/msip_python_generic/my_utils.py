from functools import wraps
import os
import requests
import logging
from fastapi import HTTPException

# Apply a "@auth_check_ldap" decorator to any API that should be authenticated
def auth_check_ldap(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):

        # Call MSIP Authentication service
        request = kwargs["request"]
        auth_header = None
        headers = request.headers
        if "Authorization" in headers:
            auth_header = {"Authorization" : headers["Authorization"]}
        authentication_service_url = os.environ.get("authentication_service_url")
        honda_certificate = "supporting_files/" + os.environ.get("honda_certificate")
        response = requests.get(authentication_service_url, headers=auth_header, verify=honda_certificate)
        
        # Process response
        if response.status_code == 200:
            logging.info(response.text)
        elif response.status_code == 401:
            logging.info("Invalid credentials")
            raise HTTPException(status_code=response.status_code, detail=response.text)
        else:
            logging.info("Unexpected error when authenticating request")
            raise HTTPException(status_code=response.status_code, detail=response.text)
            
        return func(*args, **kwargs)
    return decorated_function