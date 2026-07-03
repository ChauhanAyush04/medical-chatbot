from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class ChatMessageResponse(BaseModel):
    id: int
    user_query: str
    bot_response: str
    sources: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatSessionResponse(BaseModel):
    id: int
    session_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageResponse] = []
    
    class Config:
        from_attributes = True

class MedicalSearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=1000)
    session_id: Optional[str] = None

class MedicalSearchResponse(BaseModel):
    query: str
    answer: str
    sources: List[str]
    confidence_score: int = 100