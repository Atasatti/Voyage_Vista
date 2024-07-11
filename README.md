                            How to Start this project:

Create Environment:
    python -m venv env
    
Install Related Libraries in that environment:
    pip install fastapi motor jinja2 uvicorn itsdangerous

Activate the evironment:
    env\Scripts\activate

Start the uvicorn server:
    uvicorn main:app --reload

Deactivate the evironment:
    deactivate