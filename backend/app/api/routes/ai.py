from fastapi import APIRouter, status
from app.schemas.ai import (
    PersonalizedGuideRequest, PersonalizedGuideResponse,
    ChatRequest, ChatResponse,
    GeneralIdeasRequest, GeneralIdeasResponse
)
from app.ai.llm_service import generate_personalized_guide, chat_with_assistant, generate_general_ideas
from app.services.persistence_service import save_selected_project_and_guide, save_chat_turn

router = APIRouter(prefix="/api", tags=["Generative AI"])

@router.post("/projects/personalized-guide", response_model=PersonalizedGuideResponse, status_code=status.HTTP_200_OK)
async def get_personalized_guide(request: PersonalizedGuideRequest):
    guide_response = await generate_personalized_guide(request)
    if guide_response.success:
        save_selected_project_and_guide(
            project_id=request.project_id,
            guide_data=guide_response.dict()
        )
    return guide_response

@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_with_ai(request: ChatRequest):
    chat_response = await chat_with_assistant(request)
    if chat_response.success and chat_response.message:
        save_chat_turn(
            user_message=request.message,
            assistant_response=chat_response.message,
            project_id=request.project_id
        )
    return chat_response

@router.post("/general-ideas", response_model=GeneralIdeasResponse, status_code=status.HTTP_200_OK)
async def get_general_ideas(request: GeneralIdeasRequest):
    return await generate_general_ideas(request)
