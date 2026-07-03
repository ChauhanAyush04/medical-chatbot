from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.chat import MedicalSearchRequest, MedicalSearchResponse
from app.services.medical_qa import qa_service
from app.api.dependencies import get_db
from app.models.database import ChatSession, ChatMessage
from app.utils.logger import logger
from datetime import datetime
import uuid

router = APIRouter()

@router.post("/search", response_model=MedicalSearchResponse)
async def search_medical_info(
    request: MedicalSearchRequest,
    db: Session = Depends(get_db)
):
    """Search medical information with conversation context"""
    try:
        logger.info(f"Medical search: {request.query[:50]}")
        
        # Create or get session
        session_id = request.session_id or str(uuid.uuid4())
        session = db.query(ChatSession).filter(
            ChatSession.session_id == session_id
        ).first()
        
        if not session:
            session = ChatSession(session_id=session_id)
            db.add(session)
            db.commit()
            logger.info(f"Created new chat session: {session_id}")
        
        # Get chat history if session has messages
        chat_history = []
        if session.messages:
            # Get last 5 messages as context
            chat_history = [
                {
                    "user_query": msg.user_query,
                    "bot_response": msg.bot_response
                }
                for msg in session.messages[-5:]
            ]
            logger.info(f"Retrieved {len(chat_history)} messages from history for session {session_id}")
        
        # Get answer with history context
        result = await qa_service.search(request.query, chat_history)
        
        # Save this exchange to database
        new_message = ChatMessage(
            session_id=session_id,
            user_query=request.query,
            bot_response=result["answer"],
            sources=",".join(result["sources"])
        )
        db.add(new_message)
        db.commit()
        logger.info(f"Saved message to database for session {session_id}")
        
        return MedicalSearchResponse(
            query=request.query,
            answer=result["answer"],
            sources=result["sources"],
            confidence_score=result["confidence"],
            session_id=session_id
        )
    
    except Exception as e:
        logger.error(f"Search error: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
