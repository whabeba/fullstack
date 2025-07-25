from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Tuple
import uuid
import os
from datetime import datetime
import asyncio
import numpy as np
from scipy.optimize import minimize_scalar
from scipy.stats import norm
import math
import random
# from emergentintegrations.llm.chat import LlmChat, UserMessage
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

# MongoDB setup
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "personality_test_db")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Collections
sessions_collection = db.sessions
questions_collection = db.questions
answers_collection = db.answers
irt_params_collection = db.irt_parameters

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Big Five dimensions in Arabic
BIG_FIVE_DIMENSIONS = {
    "openness": {
        "name": "الانفتاح على التجارب",
        "description": "الرغبة في التجارب الجديدة والإبداع والخيال",
        "traits": ["الإبداع", "الخيال", "الفضول الفكري", "التنوع", "الاستقلالية"]
    },
    "conscientiousness": {
        "name": "الضمير الحي",
        "description": "التنظيم والمسؤولية والانضباط الذاتي",
        "traits": ["التنظيم", "المسؤولية", "الانضباط", "المثابرة", "الدقة"]
    },
    "extraversion": {
        "name": "الانبساط",
        "description": "الطاقة الاجتماعية والنشاط والتفاؤل",
        "traits": ["الاجتماعية", "الطاقة", "التفاؤل", "الحزم", "النشاط"]
    },
    "agreeableness": {
        "name": "المقبولية",
        "description": "التعاون والثقة والود مع الآخرين",
        "traits": ["التعاون", "الثقة", "التعاطف", "اللطف", "التواضع"]
    },
    "neuroticism": {
        "name": "العصابية",
        "description": "الاستقرار العاطفي والتحكم في المشاعر",
        "traits": ["القلق", "التوتر", "التقلبات المزاجية", "الحساسية", "الضغط النفسي"]
    }
}

# IRT Configuration
IRT_CONFIG = {
    "se_threshold": 0.35,  # Standard Error threshold for stopping
    "min_questions": 5,    # Minimum questions per dimension
    "max_questions": 15,   # Maximum questions per dimension
    "initial_theta": 0.0,  # Initial ability estimate
    "theta_bounds": (-3.0, 3.0)  # Bounds for theta estimation
}

# Pydantic models
class SessionCreate(BaseModel):
    name: str
    age: Optional[int] = None

class SessionResponse(BaseModel):
    session_id: str
    name: str
    status: str
    current_dimension: str
    current_question_number: int
    total_dimensions: int
    dimension_progress: Dict[str, int]

class Question(BaseModel):
    question_id: str
    text: str
    dimension: str
    question_number: int
    reverse_scored: bool = False
    discrimination: float = 1.0
    difficulty: float = 0.0

class AnswerSubmit(BaseModel):
    session_id: str
    question_id: str
    answer: int  # 1-5 scale
    response_time: Optional[float] = None

class PersonalityReport(BaseModel):
    session_id: str
    name: str
    scores: Dict[str, Dict[str, Any]]
    detailed_analysis: str
    recommendations: List[str]
    completion_date: str
    total_questions_asked: int
    measurement_precision: Dict[str, float]

class IRTEngine:
    """IRT (2PL Model) Engine for Adaptive Testing"""
    
    @staticmethod
    def probability_2pl(theta: float, a: float, b: float, response: int) -> float:
        """Calculate probability using 2PL model for Likert scale responses"""
        # Convert 5-point Likert to probability using graded response model approach
        # Simplified: use middle threshold for binary-like calculation
        if response >= 4:  # Strong agree/agree
            z = a * (theta - b)
            return 1 / (1 + np.exp(-z))
        else:  # Neutral/disagree/strong disagree
            z = a * (theta - b)
            return 1 - (1 / (1 + np.exp(-z)))
    
    @staticmethod
    def information_2pl(theta: float, a: float, b: float) -> float:
        """Calculate Fisher Information for 2PL model"""
        z = a * (theta - b)
        p = 1 / (1 + np.exp(-z))
        q = 1 - p
        return (a ** 2) * p * q
    
    @staticmethod
    def estimate_theta(responses: List[Tuple[int, float, float]], 
                      initial_theta: float = 0.0) -> Tuple[float, float]:
        """Estimate theta using Maximum Likelihood Estimation"""
        if not responses:
            return initial_theta, float('inf')
        
        def log_likelihood(theta):
            ll = 0
            for response, a, b in responses:
                p = IRTEngine.probability_2pl(theta, a, b, response)
                # Avoid log(0)
                p = max(min(p, 0.9999), 0.0001)
                ll += np.log(p)
            return -ll  # Negative for minimization
        
        # Find optimal theta
        result = minimize_scalar(log_likelihood, bounds=IRT_CONFIG["theta_bounds"], 
                               method='bounded')
        
        if result.success:
            theta_hat = result.x
            # Calculate standard error using Fisher Information
            total_info = sum(IRTEngine.information_2pl(theta_hat, a, b) 
                           for _, a, b in responses)
            se = 1.0 / np.sqrt(total_info) if total_info > 0 else float('inf')
            return theta_hat, se
        else:
            return initial_theta, float('inf')
    
    @staticmethod
    def select_next_question(available_questions: List[Dict], 
                           current_theta: float) -> Optional[Dict]:
        """Select the most informative question using Fisher Information"""
        if not available_questions:
            return None
        
        best_question = None
        max_info = -1
        
        for question in available_questions:
            a = question.get('discrimination', 1.0)
            b = question.get('difficulty', 0.0)
            info = IRTEngine.information_2pl(current_theta, a, b)
            
            if info > max_info:
                max_info = info
                best_question = question
        
        return best_question

# Generate AI questions with IRT parameters
async def generate_questions_for_dimension(dimension: str, count: int = 20) -> List[Dict]:
    """Generate questions for a specific Big Five dimension using Gemini with IRT parameters"""
    try:
        dimension_info = BIG_FIVE_DIMENSIONS[dimension]
        
        chat = LlmChat(
            api_key=GEMINI_API_KEY,
            session_id=f"question_gen_{dimension}",
            system_message="أنت خبير في علم النفس متخصص في إنشاء أسئلة اختبارات الشخصية باللغة العربية."
        ).with_model("gemini", "gemini-2.0-flash")
        
        prompt = f"""
أنشئ {count} سؤال لقياس بُعد "{dimension_info['name']}" في نموذج الشخصية الخماسي.
الوصف: {dimension_info['description']}
السمات الفرعية: {', '.join(dimension_info['traits'])}

متطلبات الأسئلة:
1. باللغة العربية الفصحى
2. واضحة ومباشرة
3. تقيس البُعد بدقة
4. مناسبة لجميع الأعمار
5. متنوعة في الصياغة وصعوبة القياس
6. بعضها يجب أن يكون عكسي (reverse-scored)
7. تغطي مستويات مختلفة من السمة (منخفض، متوسط، مرتفع)

أرجع النتيجة بتنسيق JSON فقط:
{{
  "questions": [
    {{
      "text": "نص السؤال",
      "reverse_scored": true/false,
      "difficulty_level": "easy/medium/hard"
    }}
  ]
}}
"""
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Parse JSON response
        import json
        try:
            questions_data = json.loads(response)
            questions = []
            for i, q in enumerate(questions_data.get("questions", [])):
                # Assign IRT parameters based on difficulty level
                difficulty_level = q.get("difficulty_level", "medium")
                if difficulty_level == "easy":
                    difficulty = random.uniform(-1.5, -0.5)
                    discrimination = random.uniform(0.8, 1.2)
                elif difficulty_level == "hard":
                    difficulty = random.uniform(0.5, 1.5)
                    discrimination = random.uniform(1.2, 2.0)
                else:  # medium
                    difficulty = random.uniform(-0.5, 0.5)
                    discrimination = random.uniform(1.0, 1.5)
                
                questions.append({
                    "question_id": str(uuid.uuid4()),
                    "text": q["text"],
                    "dimension": dimension,
                    "reverse_scored": q.get("reverse_scored", False),
                    "discrimination": discrimination,
                    "difficulty": difficulty,
                    "difficulty_level": difficulty_level,
                    "question_number": i + 1
                })
            return questions
        except json.JSONDecodeError:
            return []
            
    except Exception as e:
        print(f"Error generating questions for {dimension}: {e}")
        return []

async def initialize_question_bank():
    """Initialize question bank with IRT parameters if not exists"""
    try:
        # Check if questions already exist
        existing_count = await questions_collection.count_documents({})
        if existing_count > 0:
            return
        
        print("Initializing question bank...")
        all_questions = []
        
        for dimension in BIG_FIVE_DIMENSIONS.keys():
            questions = await generate_questions_for_dimension(dimension, count=20)
            all_questions.extend(questions)
        
        if all_questions:
            await questions_collection.insert_many(all_questions)
            print(f"Initialized {len(all_questions)} questions")
    
    except Exception as e:
        print(f"Error initializing question bank: {e}")

# Generate personality report using Gemini
async def generate_personality_report(session_id: str, scores: Dict, 
                                    total_questions: int, precision: Dict) -> Dict:
    """Generate detailed personality report using Gemini"""
    try:
        chat = LlmChat(
            api_key=GEMINI_API_KEY,
            session_id=f"report_gen_{session_id}",
            system_message="أنت خبير في علم النفس متخصص في تحليل الشخصية وكتابة التقارير النفسية باللغة العربية."
        ).with_model("gemini", "gemini-2.0-flash")
        
        # Format scores for the prompt
        scores_text = ""
        precision_text = ""
        for dim, score_data in scores.items():
            dim_name = BIG_FIVE_DIMENSIONS[dim]["name"]
            theta = score_data["theta"]
            level = score_data["level"]
            se = precision.get(dim, 0)
            scores_text += f"- {dim_name}: {theta:.2f} ({level})\n"
            precision_text += f"- {dim_name}: دقة القياس {(1-se)*100:.1f}%\n"
        
        prompt = f"""
بناءً على نتائج اختبار الشخصية التكيفي المتقدم باستخدام نظرية الاستجابة للمفردة (IRT):

نتائج الشخصية:
{scores_text}

دقة القياس:
{precision_text}

عدد الأسئلة المطلوبة: {total_questions} سؤال (بدلاً من 200+ سؤال تقليدي)

المطلوب:
1. تحليل مفصل لكل بُعد مع التركيز على دقة القياس العالية
2. تفسير النتائج في السياق النفسي المعاصر
3. نقاط القوة والتحديات الشخصية
4. التفاعل بين الأبعاد المختلفة
5. توصيات علمية للتطوير الشخصي
6. نصائح للعلاقات والعمل والنمو الشخصي

اكتب التقرير بأسلوب علمي مبسط وودود، مع التأكيد على دقة النتائج بفضل التقنية المتقدمة المستخدمة.
يجب أن يكون التقرير شاملاً (على الأقل 600 كلمة) ومقسماً إلى أقسام واضحة.
"""
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Generate recommendations
        recommendations_prompt = """
بناءً على تحليل الشخصية المتقدم، اقترح 8-12 توصية عملية ومحددة للتطوير الشخصي.
ركز على:
- توصيات قابلة للقياس والتطبيق
- خطوات عملية محددة زمنياً
- استراتيجيات مبنية على نقاط القوة
- طرق التعامل مع التحديات

أرجع النتيجة كقائمة نقاط فقط، كل نقطة في سطر منفصل تبدأ بـ "-"
"""
        
        rec_message = UserMessage(text=recommendations_prompt)
        recommendations_response = await chat.send_message(rec_message)
        
        # Parse recommendations
        recommendations = []
        for line in recommendations_response.split('\n'):
            if line.strip().startswith('-'):
                recommendations.append(line.strip()[1:].strip())
        
        return {
            "detailed_analysis": response,
            "recommendations": recommendations
        }
        
    except Exception as e:
        print(f"Error generating report: {e}")
        return {
            "detailed_analysis": "حدث خطأ في إنشاء التقرير المفصل.",
            "recommendations": ["حاول إعادة إجراء الاختبار مرة أخرى."]
        }

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    await initialize_question_bank()

@app.post("/api/sessions", response_model=SessionResponse)
async def create_session(session_data: SessionCreate):
    """Create a new adaptive test session"""
    try:
        session_id = str(uuid.uuid4())
        
        # Initialize session with IRT tracking
        session = {
            "session_id": session_id,
            "name": session_data.name,
            "age": session_data.age,
            "status": "active",
            "created_at": datetime.utcnow(),
            "current_dimension": "openness",  # Start with first dimension
            "dimension_order": list(BIG_FIVE_DIMENSIONS.keys()),
            "dimension_progress": {dim: 0 for dim in BIG_FIVE_DIMENSIONS.keys()},
            "theta_estimates": {dim: IRT_CONFIG["initial_theta"] for dim in BIG_FIVE_DIMENSIONS.keys()},
            "standard_errors": {dim: float('inf') for dim in BIG_FIVE_DIMENSIONS.keys()},
            "asked_questions": {dim: [] for dim in BIG_FIVE_DIMENSIONS.keys()},
            "total_questions_asked": 0
        }
        
        await sessions_collection.insert_one(session)
        
        return SessionResponse(
            session_id=session_id,
            name=session_data.name,
            status="active",
            current_dimension=session["current_dimension"],
            current_question_number=1,
            total_dimensions=len(BIG_FIVE_DIMENSIONS),
            dimension_progress=session["dimension_progress"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في إنشاء الجلسة: {str(e)}")

@app.get("/api/sessions/{session_id}/question", response_model=Question)
async def get_current_question(session_id: str):
    """Get the next adaptive question for current dimension"""
    try:
        # Get session
        session = await sessions_collection.find_one({"session_id": session_id})
        if not session:
            raise HTTPException(status_code=404, detail="الجلسة غير موجودة")
        
        if session["status"] == "completed":
            raise HTTPException(status_code=400, detail="الاختبار مكتمل بالفعل")
        
        current_dim = session["current_dimension"]
        current_theta = session["theta_estimates"][current_dim]
        asked_questions = session["asked_questions"][current_dim]
        
        # Get available questions for current dimension
        available_questions = []
        async for q in questions_collection.find({
            "dimension": current_dim,
            "question_id": {"$nin": asked_questions}
        }):
            available_questions.append(q)
        
        if not available_questions:
            raise HTTPException(status_code=400, detail="لا توجد أسئلة متاحة لهذا البُعد")
        
        # Select most informative question using IRT
        next_question = IRTEngine.select_next_question(available_questions, current_theta)
        
        if not next_question:
            raise HTTPException(status_code=400, detail="لا يمكن اختيار السؤال التالي")
        
        return Question(
            question_id=next_question["question_id"],
            text=next_question["text"],
            dimension=next_question["dimension"],
            question_number=session["dimension_progress"][current_dim] + 1,
            reverse_scored=next_question.get("reverse_scored", False),
            discrimination=next_question.get("discrimination", 1.0),
            difficulty=next_question.get("difficulty", 0.0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في استرجاع السؤال: {str(e)}")

@app.post("/api/answers")
async def submit_answer(answer_data: AnswerSubmit):
    """Submit answer and update IRT estimates"""
    try:
        # Validate answer range
        if not 1 <= answer_data.answer <= 5:
            raise HTTPException(status_code=400, detail="الإجابة يجب أن تكون بين 1 و 5")
        
        # Get session
        session = await sessions_collection.find_one({"session_id": answer_data.session_id})
        if not session:
            raise HTTPException(status_code=404, detail="الجلسة غير موجودة")
        
        # Get question details
        question = await questions_collection.find_one({"question_id": answer_data.question_id})
        if not question:
            raise HTTPException(status_code=404, detail="السؤال غير موجود")
        
        # Store answer
        answer_doc = {
            "session_id": answer_data.session_id,
            "question_id": answer_data.question_id,
            "answer": answer_data.answer,
            "dimension": question["dimension"],
            "response_time": answer_data.response_time,
            "answered_at": datetime.utcnow()
        }
        await answers_collection.insert_one(answer_doc)
        
        # Update IRT estimates
        current_dim = question["dimension"]
        
        # Get all answers for current dimension
        responses = []
        async for ans in answers_collection.find({
            "session_id": answer_data.session_id,
            "dimension": current_dim
        }):
            ans_question = await questions_collection.find_one({"question_id": ans["question_id"]})
            if ans_question:
                response_value = ans["answer"]
                # Handle reverse scoring
                if ans_question.get("reverse_scored", False):
                    response_value = 6 - response_value
                
                responses.append((
                    response_value,
                    ans_question.get("discrimination", 1.0),
                    ans_question.get("difficulty", 0.0)
                ))
        
        # Update theta estimate using IRT
        new_theta, se = IRTEngine.estimate_theta(responses, session["theta_estimates"][current_dim])
        
        # Update session
        update_data = {
            f"theta_estimates.{current_dim}": new_theta,
            f"standard_errors.{current_dim}": se,
            f"dimension_progress.{current_dim}": len(responses),
            "total_questions_asked": session["total_questions_asked"] + 1
        }
        
        # Add question to asked list
        asked_questions = session["asked_questions"][current_dim] + [answer_data.question_id]
        update_data[f"asked_questions.{current_dim}"] = asked_questions
        
        # Check stopping criteria for current dimension
        should_stop_dimension = (
            se < IRT_CONFIG["se_threshold"] and 
            len(responses) >= IRT_CONFIG["min_questions"]
        ) or len(responses) >= IRT_CONFIG["max_questions"]
        
        if should_stop_dimension:
            # Move to next dimension
            current_dim_index = session["dimension_order"].index(current_dim)
            if current_dim_index < len(session["dimension_order"]) - 1:
                # Move to next dimension
                next_dim = session["dimension_order"][current_dim_index + 1]
                update_data["current_dimension"] = next_dim
                
                await sessions_collection.update_one(
                    {"session_id": answer_data.session_id},
                    {"$set": update_data}
                )
                
                return {
                    "status": "dimension_completed",
                    "completed_dimension": BIG_FIVE_DIMENSIONS[current_dim]["name"],
                    "next_dimension": BIG_FIVE_DIMENSIONS[next_dim]["name"],
                    "theta_estimate": new_theta,
                    "standard_error": se,
                    "questions_asked": len(responses)
                }
            else:
                # All dimensions completed
                update_data["status"] = "completed"
                update_data["completed_at"] = datetime.utcnow()
                
                await sessions_collection.update_one(
                    {"session_id": answer_data.session_id},
                    {"$set": update_data}
                )
                
                return {
                    "status": "test_completed",
                    "message": "تم إكمال جميع أبعاد الاختبار بنجاح!",
                    "total_questions": session["total_questions_asked"] + 1
                }
        else:
            # Continue with current dimension
            await sessions_collection.update_one(
                {"session_id": answer_data.session_id},
                {"$set": update_data}
            )
            
            return {
                "status": "continue",
                "current_dimension": BIG_FIVE_DIMENSIONS[current_dim]["name"],
                "theta_estimate": new_theta,
                "standard_error": se,
                "questions_asked": len(responses),
                "precision": f"{(1-se)*100:.1f}%" if se < 1 else "منخفضة"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في معالجة الإجابة: {str(e)}")

@app.get("/api/sessions/{session_id}/report", response_model=PersonalityReport)
async def get_personality_report(session_id: str):
    """Generate comprehensive personality report using IRT results"""
    try:
        # Get session
        session = await sessions_collection.find_one({"session_id": session_id})
        if not session:
            raise HTTPException(status_code=404, detail="الجلسة غير موجودة")
        
        if session["status"] != "completed":
            raise HTTPException(status_code=400, detail="لم يتم إكمال الاختبار بعد")
        
        # Prepare scores with IRT estimates
        dimension_scores = {}
        measurement_precision = {}
        
        for dimension in BIG_FIVE_DIMENSIONS.keys():
            theta = session["theta_estimates"][dimension]
            se = session["standard_errors"][dimension]
            
            # Convert theta to interpretable scale (0-100)
            # Theta typically ranges from -3 to +3, convert to 0-100 scale
            percentile_score = norm.cdf(theta) * 100
            
            # Determine level
            if percentile_score <= 25:
                level = "منخفض"
            elif percentile_score <= 75:
                level = "متوسط"
            else:
                level = "مرتفع"
            
            dimension_scores[dimension] = {
                "theta": theta,
                "percentile": percentile_score,
                "level": level,
                "name": BIG_FIVE_DIMENSIONS[dimension]["name"],
                "questions_asked": session["dimension_progress"][dimension]
            }
            
            measurement_precision[dimension] = se
        
        # Generate AI report
        report_data = await generate_personality_report(
            session_id, 
            dimension_scores, 
            session["total_questions_asked"],
            measurement_precision
        )
        
        return PersonalityReport(
            session_id=session_id,
            name=session["name"],
            scores=dimension_scores,
            detailed_analysis=report_data["detailed_analysis"],
            recommendations=report_data["recommendations"],
            completion_date=session.get("completed_at", datetime.utcnow()).isoformat(),
            total_questions_asked=session["total_questions_asked"],
            measurement_precision=measurement_precision
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في إنشاء التقرير: {str(e)}")

@app.get("/api/sessions/{session_id}/progress")
async def get_session_progress(session_id: str):
    """Get detailed session progress"""
    try:
        session = await sessions_collection.find_one({"session_id": session_id})
        if not session:
            raise HTTPException(status_code=404, detail="الجلسة غير موجودة")
        
        progress_data = {}
        for dim in BIG_FIVE_DIMENSIONS.keys():
            theta = session["theta_estimates"][dim]
            se = session["standard_errors"][dim]
            questions_asked = session["dimension_progress"][dim]
            
            progress_data[dim] = {
                "name": BIG_FIVE_DIMENSIONS[dim]["name"],
                "theta_estimate": theta,
                "standard_error": se,
                "precision": f"{(1-se)*100:.1f}%" if se < 1 else "منخفضة",
                "questions_asked": questions_asked,
                "completed": se < IRT_CONFIG["se_threshold"] or questions_asked >= IRT_CONFIG["max_questions"]
            }
        
        return {
            "session_id": session_id,
            "current_dimension": session.get("current_dimension"),
            "total_questions_asked": session["total_questions_asked"],
            "status": session["status"],
            "dimensions": progress_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في استرجاع التقدم: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "message": "خدمة اختبار الشخصية التكيفي تعمل بشكل طبيعي",
        "irt_config": IRT_CONFIG
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)