from typing import Dict, Any, List, Optional, AsyncIterator
from backend.app.rag.retriever import RealEstateRetriever
from backend.app.rag.query_rewriter import QueryRewriter
from backend.app.rag.prompt_templates import SYSTEM_INSTRUCTION, format_rag_prompt
from backend.app.llm.llm_factory import LLMFactory
from backend.app.database.repositories import ConversationRepository
from backend.app.schemas.chat_schema import ChatResponse, SourceReference
from backend.app.core.logging import logger


class RAGPipeline:
    def __init__(self):
        self.retriever = RealEstateRetriever()

    def process_query(
        self,
        query: str,
        session_id: str = "default_session",
        source_filter: Optional[str] = "all"
    ) -> ChatResponse:
        logger.info("[RAGPipeline] Processing question for session '%s': %s", session_id, query)
        
        # 1. Fetch recent history for conversational memory
        history = ConversationRepository.get_recent_messages(session_id=session_id, limit=6)
        history_str = ""
        if history:
            history_lines = [f"{msg['role'].upper()}: {msg['content']}" for msg in history[-4:]]
            history_str = "\n".join(history_lines)

        # 2. Context-aware query rewriting
        search_query = QueryRewriter.rewrite_query(query, history)

        # 3. Retrieve relevant verified context
        retrieval_result = self.retriever.retrieve(
            query=search_query,
            source_filter=source_filter,
            top_k=5
        )
        docs = retrieval_result["documents"]
        sources: List[SourceReference] = retrieval_result["sources"]

        # 4. Assemble context text
        context_parts = []
        for i, d in enumerate(docs):
            meta = d.get("metadata", {})
            src = meta.get("source", "Real Estate")
            proj = meta.get("project_name", "Property")
            loc = f"{meta.get('city', '')}, {meta.get('country', '')}"
            url = meta.get("source_url", "")
            context_parts.append(
                f"--- Document [{i+1}] | Source: {src} | Project: {proj} | Location: {loc} | URL: {url} ---\n{d.get('text', '')}"
            )
        retrieved_context_str = "\n\n".join(context_parts)

        # 5. Format prompt
        full_prompt = format_rag_prompt(
            query=query,
            retrieved_context=retrieved_context_str,
            chat_history_str=history_str
        )

        # 6. Generate answer using active LLM provider
        provider = LLMFactory.get_provider()
        try:
            answer = provider.generate_response(
                prompt=full_prompt,
                system_instruction=SYSTEM_INSTRUCTION
            )
        except Exception as e:
            logger.error("[RAGPipeline] LLM generation error: %s", e)
            answer = (
                f"I encountered a temporary issue connecting to the AI provider ({provider.get_provider_name()}). "
                "However, verified matching records were found in the knowledge base. Please check the source references below."
            )

        # 7. Persist to conversation history
        sources_dict = [s.model_dump() for s in sources]
        ConversationRepository.add_message(session_id=session_id, role="user", content=query)
        ConversationRepository.add_message(session_id=session_id, role="assistant", content=answer, sources=sources_dict)

        return ChatResponse(
            session_id=session_id,
            answer=answer,
            sources=sources,
            retrieved_documents=len(docs),
            provider_used=provider.get_provider_name()
        )

    async def process_query_stream(
        self,
        query: str,
        session_id: str = "default_session",
        source_filter: Optional[str] = "all"
    ) -> AsyncIterator[Dict[str, Any]]:
        logger.info("[RAGPipeline] Starting streaming query for session '%s'", session_id)
        
        # 1. Fetch recent history
        history = ConversationRepository.get_recent_messages(session_id=session_id, limit=6)
        history_str = ""
        if history:
            history_lines = [f"{msg['role'].upper()}: {msg['content']}" for msg in history[-4:]]
            history_str = "\n".join(history_lines)

        # 2. Context-aware query rewrite
        search_query = QueryRewriter.rewrite_query(query, history)

        # 3. Retrieve documents
        retrieval_result = self.retriever.retrieve(
            query=search_query,
            source_filter=source_filter,
            top_k=5
        )
        docs = retrieval_result["documents"]
        sources: List[SourceReference] = retrieval_result["sources"]

        # Yield metadata first (sources, document count)
        yield {
            "type": "metadata",
            "session_id": session_id,
            "sources": [s.model_dump() for s in sources],
            "retrieved_documents": len(docs),
            "provider": LLMFactory.get_active_provider_name()
        }

        # 4. Assemble context text
        context_parts = []
        for i, d in enumerate(docs):
            meta = d.get("metadata", {})
            src = meta.get("source", "Real Estate")
            proj = meta.get("project_name", "Property")
            loc = f"{meta.get('city', '')}, {meta.get('country', '')}"
            url = meta.get("source_url", "")
            context_parts.append(
                f"--- Document [{i+1}] | Source: {src} | Project: {proj} | Location: {loc} | URL: {url} ---\n{d.get('text', '')}"
            )
        retrieved_context_str = "\n\n".join(context_parts)

        # 5. Format prompt
        full_prompt = format_rag_prompt(
            query=query,
            retrieved_context=retrieved_context_str,
            chat_history_str=history_str
        )

        # 6. Stream generation from provider
        provider = LLMFactory.get_provider()
        full_answer_accumulator = []
        async for chunk in provider.generate_stream(prompt=full_prompt, system_instruction=SYSTEM_INSTRUCTION):
            full_answer_accumulator.append(chunk)
            yield {
                "type": "chunk",
                "delta": chunk
            }

        # 7. Persist complete answer
        complete_answer = "".join(full_answer_accumulator)
        sources_dict = [s.model_dump() for s in sources]
        ConversationRepository.add_message(session_id=session_id, role="user", content=query)
        ConversationRepository.add_message(session_id=session_id, role="assistant", content=complete_answer, sources=sources_dict)

        yield {
            "type": "done",
            "full_answer": complete_answer
        }
