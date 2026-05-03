from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ContactForm(BaseModel):
    name: str
    email: str
    message: str

@app.get("/")
def root():
    return {"status": "Backend running 🚀"}

@app.post("/contact")
def submit_form(data: ContactForm):
    print("New form submission:")
    print(data)
    return {"success": True, "message": "Form received"}
