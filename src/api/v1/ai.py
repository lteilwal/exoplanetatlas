"""
API Endpoints for Gemini + MCP Exoplanet AI Service.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.schemas.ai import (
    AIChatRequest,
    AIChatResponse,
    PlanetAISummaryResponse,
    PlanetQARequest,
    PlanetQAResponse,
)
from src.services.ai_service import (
    ask_planet_question_ai,
    general_chat_ai,
    generate_planet_summary_ai,
)
from src.services.planet_service import get_planet_by_id_or_name

router = APIRouter(prefix="/ai", tags=["Gemini + MCP AI Service"])


@router.get(
    "/planets/{planet_name}/summary",
    response_model=PlanetAISummaryResponse,
    summary="Generate factual natural-language summary via Gemini + MCP tools",
)
def get_planet_ai_summary(
    planet_name: str,
    db: Session = Depends(get_db),
) -> PlanetAISummaryResponse:
    """
    Generate a factual, grounded narrative summary of an exoplanet
    using Gemini backed by Model Context Protocol (MCP) database tools.
    """
    planet = get_planet_by_id_or_name(db, planet_name)
    if not planet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Planet '{planet_name}' was not found in the database.",
        )

    summary_text, key_facts, tools_used = generate_planet_summary_ai(planet.name)

    return PlanetAISummaryResponse(
        planet_name=planet.name,
        summary=summary_text,
        key_facts=key_facts,
        tools_used=tools_used,
    )


@router.post(
    "/planets/{planet_name}/qa",
    response_model=PlanetQAResponse,
    summary="Ask questions about a planet answered by Gemini via MCP tools",
)
def ask_planet_ai_question(
    planet_name: str,
    request: PlanetQARequest,
    db: Session = Depends(get_db),
) -> PlanetQAResponse:
    """
    Answer user questions regarding an exoplanet.
    Gemini retrieves scientific records via MCP tools; missing data is explicitly stated.
    """
    planet = get_planet_by_id_or_name(db, planet_name)
    if not planet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Planet '{planet_name}' was not found in the database.",
        )

    answer_text, tools_used, data_points = ask_planet_question_ai(
        planet_name=planet.name,
        question=request.question,
    )

    return PlanetQAResponse(
        planet_name=planet.name,
        question=request.question,
        answer=answer_text,
        tools_used=tools_used,
        data_points_used=data_points,
    )


@router.post(
    "/chat",
    response_model=AIChatResponse,
    summary="General scientific exoplanet inquiry using Gemini + MCP",
)
def chat_exoplanet_ai(
    request: AIChatRequest,
) -> AIChatResponse:
    """
    General conversational endpoint powered by Gemini with full access to MCP database tools.
    """
    response_text, tools_used = general_chat_ai(
        message=request.message,
        context_planet=request.context_planet,
    )

    return AIChatResponse(
        message=request.message,
        response=response_text,
        tools_used=tools_used,
    )
