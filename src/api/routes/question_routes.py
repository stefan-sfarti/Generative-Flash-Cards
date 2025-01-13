from fastapi import APIRouter, Depends, HTTPException
from src.domain.models import Question, GenerationRequest, QuestionDifficulty
from src.application.question_service import DefaultQuestionService
from src.api.dependencies.dependencies import get_question_service

router = APIRouter()

@router.post("/questions", response_model=Question)
async def generate_question(request: GenerationRequest, question_service: DefaultQuestionService = Depends(get_question_service)):
    try:
        question = await question_service.get_question(request)
        return question
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/questions/cache", status_code=202)
async def generate_and_cache(request: GenerationRequest, count: int, question_service: DefaultQuestionService = Depends(get_question_service)):
      try:
          await question_service.generate_and_cache_questions(request, count)
      except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while caching questions {str(e)}")