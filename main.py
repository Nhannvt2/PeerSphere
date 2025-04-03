from fastapi import FastAPI, Request, Form, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import json
from chatbot import *
from quiz_data import *


app = FastAPI(title="PeerSphere - Student Support Platform")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Define models
class QuizAnswer(BaseModel):
    question_id: int
    answer: str  # 'A', 'B', 'C', or 'D'

class QuizSubmission(BaseModel):
    answers: List[QuizAnswer]

class QuizResult(BaseModel):
    total_score: int
    assessment: str
    detailed_scores: Dict[int, int]


class ChatMessage(BaseModel):
    message: str



# Create chatbot instance
chatbot = GeminiChatBot()

# Assessment scoring ranges
assessment_ranges = [
    {"min": 25, "max": 30, "assessment": "Bạn kiểm soát rất tốt áp lực đồng trang lứa."},
    {"min": 18, "max": 24, "assessment": "Bạn có một số áp lực nhưng vẫn giữ được sự cân bằng."},
    {"min": 10, "max": 17, "assessment": "Bạn đang bị ảnh hưởng đáng kể bởi áp lực đồng trang lứa."},
    {"min": 0, "max": 9, "assessment": "Bạn có thể đang chịu áp lực lớn và cần tìm cách giải tỏa."}
]

# WebSocket connection manager for chat
class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/quiz", response_class=HTMLResponse)
async def quiz_page(request: Request):
    return templates.TemplateResponse("quiz.html", {"request": request, "questions": quiz_questions})

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/api/questions")
async def get_questions():
    return JSONResponse(content=quiz_questions)

@app.post("/api/chat", response_model=dict)
async def chat_endpoint(message: ChatMessage):
    try:
        response = chatbot.responses(message.message)
        return {"status": "success", "message": response}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            
            # Process the message through the chatbot
            response = chatbot.responses(data)
            
            # Send the response back
            await manager.send_message(response, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/submit", response_model=QuizResult)
async def submit_quiz(submission: QuizSubmission):
    # Calculate score
    total_score = 0
    detailed_scores = {}
    
    for answer in submission.answers:
        question_id = answer.question_id
        answer_key = answer.answer
        
        if question_id not in quiz_questions:
            raise HTTPException(status_code=400, detail=f"Invalid question ID: {question_id}")
        
        if answer_key not in quiz_questions[question_id]["scores"]:
            raise HTTPException(status_code=400, detail=f"Invalid answer for question {question_id}")
        
        score = quiz_questions[question_id]["scores"][answer_key]
        total_score += score
        detailed_scores[question_id] = score
    
    # Determine assessment
    assessment = ""
    for range_info in assessment_ranges:
        if range_info["min"] <= total_score <= range_info["max"]:
            assessment = range_info["assessment"]
            break
    
    return QuizResult(
        total_score=total_score,
        assessment=assessment,
        detailed_scores=detailed_scores
    )

@app.get("/result", response_class=HTMLResponse)
async def result_page(request: Request, score: int, assessment: str):
    return templates.TemplateResponse(
        "result.html", 
        {
            "request": request, 
            "score": score, 
            "assessment": assessment
        }
    )

# Form submission endpoint (alternative to JSON API)
@app.post("/submit-form", response_class=HTMLResponse)
async def submit_form(request: Request):
    form_data = await request.form()
    
    # Process form data
    total_score = 0
    detailed_scores = {}
    
    for question_id in range(1, len(quiz_questions) + 1):
        answer_key = form_data.get(f"question_{question_id}")
        
        if not answer_key:
            return templates.TemplateResponse(
                "quiz.html", 
                {
                    "request": request, 
                    "questions": quiz_questions,
                    "error": "Vui lòng trả lời tất cả các câu hỏi"
                }
            )
        
        score = quiz_questions[question_id]["scores"][answer_key]
        total_score += score
        detailed_scores[question_id] = score
    
    # Determine assessment
    assessment = ""
    for range_info in assessment_ranges:
        if range_info["min"] <= total_score <= range_info["max"]:
            assessment = range_info["assessment"]
            break
    
    return templates.TemplateResponse(
        "result.html", 
        {
            "request": request, 
            "score": total_score, 
            "assessment": assessment,
            "detailed_scores": detailed_scores
        }
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)