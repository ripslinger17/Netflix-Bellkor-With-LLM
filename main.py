from fastapi import FastAPI
from pydantic import BaseModel
from agent import (process_message)

app = FastAPI()

class ChatInput(BaseModel):
    question: str
    session_id: str

@app.post("/chat")
def chat_endpoint(request: ChatInput):
    """
    Receive a chat message and return the AI response.
    """
    response = process_message(
        user_input=request.question,
        session_id=request.session_id
    )
    return {"response": response}

@app.get("/")
def root():
    return {"message": "API is healthy!"}