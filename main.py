from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn

app = FastAPI(title="Peer Pressure Assessment Quiz")

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

# Quiz data
quiz_questions = {
    1: {
        "question": "Bạn thấy bạn bè đạt học bổng danh giá, còn mình thì không. Bạn sẽ làm gì?",
        "options": {
            "A": "Chúc mừng họ và xem đó là động lực để cố gắng hơn.",
            "B": "So sánh bản thân với họ và cảm thấy áp lực nhưng vẫn cố gắng.",
            "C": "Trách bản thân vì không đủ giỏi và cảm thấy thất vọng.",
            "D": "Nghĩ rằng họ chỉ may mắn và không thực sự giỏi hơn mình."
        },
        "scores": {"A": 3, "B": 2, "C": 1, "D": 0}
    },
    2: {
        "question": "Bạn bè của bạn đang tham gia nhiều hoạt động ngoại khóa và đạt được nhiều thành tựu. Bạn cảm thấy thế nào?",
        "options": {
            "A": "Tôi sẽ cân nhắc tham gia nếu thấy phù hợp với bản thân.",
            "B": "Cảm thấy một chút áp lực nhưng vẫn theo đuổi mục tiêu của mình.",
            "C": "Vội vàng đăng ký nhiều hoạt động để không bị thua kém.",
            "D": "Cảm thấy tự ti và không muốn tham gia bất kỳ hoạt động nào."
        },
        "scores": {"A": 3, "B": 2, "C": 1, "D": 0}
    },
    3: {
        "question": "Khi thấy bạn bè khoe cuộc sống \"sang chảnh\" trên mạng xã hội, bạn sẽ làm gì?",
        "options": {
            "A": "Hiểu rằng đó chỉ là một phần cuộc sống của họ và không ảnh hưởng đến mình.",
            "B": "Cảm thấy hơi chạnh lòng nhưng không để nó ảnh hưởng đến tâm trạng.",
            "C": "Bắt đầu so sánh cuộc sống của mình với họ và cảm thấy áp lực.",
            "D": "Cố gắng tạo ra một hình ảnh hào nhoáng trên mạng xã hội để không bị tụt lại."
        },
        "scores": {"A": 3, "B": 2, "C": 1, "D": 0}
    },
    4: {
        "question": "Gia đình bạn thường so sánh bạn với con của bạn bè họ. Bạn sẽ phản ứng thế nào?",
        "options": {
            "A": "Hiểu rằng mỗi người có một con đường riêng và tập trung vào mục tiêu của mình.",
            "B": "Thấy hơi áp lực nhưng vẫn cố gắng phát triển bản thân.",
            "C": "Cảm thấy tổn thương và tự trách bản thân.",
            "D": "Phản ứng tiêu cực, cãi lại hoặc tránh xa gia đình."
        },
        "scores": {"A": 3, "B": 2, "C": 1, "D": 0}
    },
    5: {
        "question": "Khi bạn bè xung quanh đều có việc làm thêm, bạn sẽ làm gì?",
        "options": {
            "A": "Tìm hiểu xem có công việc nào phù hợp với mình không.",
            "B": "Học cách quản lý thời gian tốt hơn để có thể vừa học vừa làm.",
            "C": "Cảm thấy áp lực và tìm việc ngay cả khi chưa sẵn sàng.",
            "D": "Nghĩ rằng mình vô dụng vì không có việc làm thêm."
        },
        "scores": {"A": 3, "B": 2, "C": 1, "D": 0}
    },
    6: {
        "question": "Bạn nhận được một lời mời tham gia vào một nhóm bạn sành điệu nhưng phải chi tiêu nhiều tiền. Bạn sẽ quyết định thế nào?",
        "options": {
            "A": "Chỉ tham gia nếu không ảnh hưởng đến tài chính cá nhân.",
            "B": "Thỉnh thoảng đi cùng nhưng kiểm soát chi tiêu hợp lý.",
            "C": "Cố gắng chạy theo để không bị lạc lõng.",
            "D": "Vay tiền hoặc tiêu quá mức để theo kịp họ."
        },
        "scores": {"A": 3, "B": 2, "C": 1, "D": 0}
    },
    7: {
        "question": "Bạn có một người bạn đạt nhiều thành công và luôn muốn bạn làm theo họ. Bạn sẽ làm gì?",
        "options": {
            "A": "Học hỏi từ họ nhưng vẫn giữ vững con đường riêng của mình.",
            "B": "Cảm thấy áp lực nhưng vẫn cố gắng theo đuổi điều mình thích.",
            "C": "Thay đổi hoàn toàn để giống họ, dù không thực sự thích.",
            "D": "Cắt đứt quan hệ vì cảm thấy bị áp đặt."
        },
        "scores": {"A": 3, "B": 2, "C": 1, "D": 0}
    },
    8: {
        "question": "Khi thấy bạn bè có người yêu, bạn sẽ phản ứng thế nào?",
        "options": {
            "A": "Vẫn tận hưởng cuộc sống độc thân và chờ duyên đến.",
            "B": "Có chút mong muốn nhưng không để nó trở thành áp lực.",
            "C": "Cảm thấy lạc lõng và vội vàng tìm người yêu để không bị tụt lại.",
            "D": "Cho rằng mình kém cỏi vì vẫn còn độc thân."
        },
        "scores": {"A": 3, "B": 2, "C": 1, "D": 0}
    },
    9: {
        "question": "Bạn thấy bạn bè có kỹ năng tốt hơn mình trong một lĩnh vực quan trọng. Bạn sẽ làm gì?",
        "options": {
            "A": "Cố gắng học hỏi và cải thiện kỹ năng của bản thân.",
            "B": "Tập trung vào điểm mạnh của mình thay vì so sánh.",
            "C": "Cảm thấy tự ti và nghĩ rằng mình không thể giỏi như họ.",
            "D": "Bỏ cuộc vì cho rằng mình không có năng khiếu."
        },
        "scores": {"A": 3, "B": 2, "C": 1, "D": 0}
    },
    10: {
        "question": "Nếu một người bạn liên tục khoe khoang về thành tích của họ, bạn sẽ phản ứng thế nào?",
        "options": {
            "A": "Chúc mừng họ và không để nó ảnh hưởng đến mình.",
            "B": "Lắng nghe nhưng không quá quan tâm.",
            "C": "Cảm thấy ghen tị và khó chịu.",
            "D": "Cắt đứt liên lạc với họ vì cảm thấy bị áp lực."
        },
        "scores": {"A": 3, "B": 2, "C": 1, "D": 0}
    }
}

# Assessment scoring ranges
assessment_ranges = [
    {"min": 25, "max": 30, "assessment": "Bạn kiểm soát rất tốt áp lực đồng trang lứa."},
    {"min": 18, "max": 24, "assessment": "Bạn có một số áp lực nhưng vẫn giữ được sự cân bằng."},
    {"min": 10, "max": 17, "assessment": "Bạn đang bị ảnh hưởng đáng kể bởi áp lực đồng trang lứa."},
    {"min": 0, "max": 9, "assessment": "Bạn có thể đang chịu áp lực lớn và cần tìm cách giải tỏa."}
]

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "questions": quiz_questions})

@app.get("/api/questions")
async def get_questions():
    return JSONResponse(content=quiz_questions)

@app.post("/api/submit", response_model=QuizResult)
async def submit_quiz(submission: QuizSubmission):
    # Validate submission
    if len(submission.answers) != len(quiz_questions):
        raise HTTPException(status_code=400, detail="Please answer all questions")
    
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
                "index.html", 
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