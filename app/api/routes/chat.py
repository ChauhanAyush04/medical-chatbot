from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from app.models.database import ChatSession, ChatMessage
from app.schemas.chat import ChatSessionResponse
from app.api.dependencies import get_db
from app.utils.logger import logger
from uuid import uuid4

router = APIRouter()

@router.post("/sessions", response_model=ChatSessionResponse)
async def create_session(db: Session = Depends(get_db)):
    """Create new chat session"""
    try:
        session = ChatSession(
            session_id=str(uuid4()),
            title="New Chat"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        logger.info(f"Created session: {session.session_id}")
        return session
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_session(session_id: str, db: Session = Depends(get_db)):
    """Get chat session with messages"""
    try:
        session = db.query(ChatSession).options(
            joinedload(ChatSession.messages)
        ).filter(
            ChatSession.session_id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        logger.info(f"Retrieved session {session_id} with {len(session.messages)} messages")
        return session
    except Exception as e:
        logger.error(f"Error fetching session: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sessions", response_model=list[ChatSessionResponse])
async def list_sessions(db: Session = Depends(get_db)):
    """List all chat sessions with message counts"""
    try:
        sessions = db.query(ChatSession).options(
            joinedload(ChatSession.messages)
        ).order_by(
            ChatSession.updated_at.desc()
        ).all()
        
        logger.info(f"Retrieved {len(sessions)} sessions")
        for session in sessions:
            logger.debug(f"  Session {session.session_id}: {len(session.messages)} messages")
        
        return sessions
    except Exception as e:
        logger.error(f"Error listing sessions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, db: Session = Depends(get_db)):
    """Delete chat session"""
    try:
        session = db.query(ChatSession).filter(
            ChatSession.session_id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        db.delete(session)
        db.commit()
        logger.info(f"Deleted session: {session_id}")
        return {"message": "Session deleted"}
    except Exception as e:
        logger.error(f"Error deleting session: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
