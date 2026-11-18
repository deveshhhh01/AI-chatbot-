import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from backend.app.schemas.chat_schema import ChatRequest, ChatResponse
from backend.app.rag.rag_pipeline import RAGPipeline
from backend.app.api.dependencies import get_rag_pipeline
from backend.app.database.repositories import ConversationRepository
from backend.app.core.logging import logger

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
def chat_endpoint(
    request: ChatRequest,
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    try:
        response = pipeline.process_query(
            query=request.message,
            session_id=request.session_id,
            source_filter=request.source_filter
        )
        return response
    except Exception as e:
        logger.error("[ChatEndpoint] Error processing query: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def chat_stream_endpoint(
    request: ChatRequest,
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    async def event_generator():
        try:
            async for event in pipeline.process_query_stream(
                query=request.message,
                session_id=request.session_id,
                source_filter=request.source_filter
            ):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            logger.error("[ChatStreamEndpoint] Error streaming response: %s", e)
            err_data = {"type": "error", "message": str(e)}
            yield f"data: {json.dumps(err_data)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/history/{session_id}")
def get_chat_history(session_id: str):
    messages = ConversationRepository.get_recent_messages(session_id=session_id, limit=50)
    return {
        "session_id": session_id,
        "total_messages": len(messages),
        "messages": messages
    }


@router.get("/conversations")
def list_conversations():
    conversations = ConversationRepository.list_conversations(limit=30)
    return {
        "total": len(conversations),
        "conversations": conversations
    }
