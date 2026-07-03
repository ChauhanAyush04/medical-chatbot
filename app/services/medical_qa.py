import asyncio
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from app.config import Settings
from app.utils.logger import logger

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


settings = Settings()

class MedicalQAService:
    """Medical QA service with conversation memory"""
    
    def __init__(self):
        self.embeddings = None
        self.db = None
        self.llm = None
        self._initialize()
    
    def _initialize(self):
        """Initialize FAISS and LLM"""
        try:
            logger.info("Initializing MedicalQAService...")
            
            self.embeddings = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL,
                model_kwargs={"device": "cpu"}
            )
            
            self.db = FAISS.load_local(
                settings.FAISS_PATH,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            logger.info(f"✓ FAISS loaded with {self.db.index.ntotal} vectors")
            
            self.llm = ChatGroq(
                model=settings.LLM_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
                api_key=settings.GROQ_API_KEY
            )
            logger.info("✓ LLM initialized")
        
        except Exception as e:
            logger.error(f"Initialization error: {str(e)}", exc_info=True)
            raise
    
    async def search(self, query: str, chat_history: list = None) -> dict:
        try:
            logger.info(f"🔍 Received query: {query}")
            logger.info(f"📝 Chat history provided: {chat_history is not None and len(chat_history) > 0}")
            
            # Convert chat history to LangChain messages
            history = []
            if chat_history:
                logger.info(f"📚 Converting {len(chat_history)} history items to messages...")
                for i, msg in enumerate(chat_history):
                    if msg.get("user_query"):
                        history.append(HumanMessage(content=msg["user_query"]))
                        logger.debug(f"  [{i}] User: {msg['user_query'][:50]}...")
                    if msg.get("bot_response"):
                        history.append(AIMessage(content=msg["bot_response"][:100]))
                        logger.debug(f"  [{i}] Bot: {msg['bot_response'][:50]}...")
            
            logger.info(f"✅ Total LangChain messages: {len(history)}")

            # Retriever
            retriever = self.db.as_retriever(
                search_kwargs={"k": settings.TOP_K}
            )

            # History-aware prompt - rewrites questions using context
            contextualize_q_prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """Given the chat history and the latest user question, 
rewrite the question into a standalone question that maintains all important context.

If the user is asking a follow-up question (like "what is its cause?"), 
make sure the rewritten question explicitly references what "it" refers to.

Do NOT answer the question.
Return ONLY the rewritten question.""",
                    ),
                    MessagesPlaceholder("chat_history"),
                    ("human", "{input}"),
                ]
            )

            history_aware_retriever = create_history_aware_retriever(
                self.llm,
                retriever,
                contextualize_q_prompt,
            )

            # QA Prompt - uses context AND history
            qa_prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """You are an evidence-based medical assistant. Your role is to provide accurate medical information.

CRITICAL RULES:
1. Use ONLY the retrieved medical context to answer.
2. Never use outside medical knowledge.
3. Never invent information.
4. Never say "I recall" or "Based on previous medical context".
5. Use chat history to resolve references like "it", "that disease", "earlier", "mentioned before", etc.
6. If the answer is not in the retrieved documents, respond: "I don't have enough information in the provided medical knowledge to answer that question."
7. Always cite the source when providing information.

Current Medical Context from Documents:
{context}

Answer the user's question based ONLY on the above medical context.""",
                    ),
                    MessagesPlaceholder("chat_history"),
                    ("human", "{input}"),
                ]
            )

            question_answer_chain = create_stuff_documents_chain(
                self.llm,
                qa_prompt,
            )

            rag_chain = create_retrieval_chain(
                history_aware_retriever,
                question_answer_chain,
            )

            logger.info("🚀 Invoking RAG chain with history...")
            response = await asyncio.to_thread(
                rag_chain.invoke,
                {
                    "input": query,
                    "chat_history": history,
                },
            )

            answer = response["answer"]
            docs = response["context"]

            sources = list(
                {
                    doc.metadata.get("source", "Unknown")
                        for doc in docs
                }
            )

            logger.info(f"✅ Answer generated from {len(sources)} source(s)")
            logger.info(f"📄 Sources: {sources}")

            return {
                "answer": answer,
                "sources": sources,
                "confidence": 100,
            }

        except Exception as e:
            logger.error(f"❌ Search error: {str(e)}", exc_info=True)
            raise


# Initialize the service instance at module load time
qa_service = MedicalQAService()
