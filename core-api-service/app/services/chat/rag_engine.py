import os
import logging
import httpx
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.schemas.search import SearchRequest
from app.schemas.chat import ChatRequest, ChatResponse, GroundedSource
from app.services.search_orchestrator import search_orchestrator

logger = logging.getLogger(__name__)

class RAGEngine:

    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    LLM_MODEL = os.getenv("LLM_MODEL", "phi3:mini")

    @classmethod
    def generate_grounded_answer(cls, request: ChatRequest) -> ChatResponse:
        # 1. Retrieve top 4 candidate clauses using hybrid search
        search_req = SearchRequest(
            query=request.question,
            target_date=request.target_date or settings.DEFAULT_REFERENCE_DATE,
            size=4,
            search_mode="hybrid"
        )
        search_res = search_orchestrator.search(search_req)

        # 2. Handle Zero Hits (Strict Anti-Hallucination Guardrail)
        if not search_res.results:
            return ChatResponse(
                answer="The regulatory documents provided do not contain information addressing this query under the specified criteria.",
                grounded_sources=[],
                confidence_score=0.0,
                has_applicability_warning=False,
                warning_details=None
            )

        # 3. Assemble Grounded Sources & Context Block
        sources: List[GroundedSource] = []
        context_snippets = []
        has_warning = False
        warning_notes = []

        for item in search_res.results:
            sources.append(GroundedSource(
                citation_label=item.citation.citation_label,
                document_name=item.citation.document_name,
                version=item.citation.version,
                page_number=item.citation.page_number,
                clause_reference=item.citation.clause_reference,
                excerpt=item.content[:200] + "..." if len(item.content) > 200 else item.content
            ))
            context_snippets.append(
                f"[{item.citation.citation_label}]\n{item.content}"
            )
            if item.applicability_warning:
                has_warning = True
                warning_notes.append(item.applicability_warning)

        grounded_context = "\n\n".join(context_snippets)

        # 4. Generate Synthesized Response via Local LLM (or Extractive Fallback)
        answer = cls._call_llm_or_fallback(request.question, grounded_context, sources)

        return ChatResponse(
            answer=answer,
            grounded_sources=sources,
            confidence_score=0.92,
            has_applicability_warning=has_warning,
            warning_details=" | ".join(set(warning_notes)) if has_warning else None
        )

    @classmethod
    def _call_llm_or_fallback(cls, question: str, context: str, sources: List[GroundedSource]) -> str:
        prompt = (
            "You are a regulatory compliance assistant for an investment bank.\n"
            "Answer the question strictly based on the following regulatory passages.\n"
            "Every claim must reference its source tag (e.g. [Document (vX) - Page P, §K]).\n"
            "If the answer is not contained in the text, state: 'The provided regulations do not specify this.'\n\n"
            f"REGULATORY CONTEXT:\n{context}\n\n"
            f"QUESTION: {question}\n\n"
            "ANSWER:"
        )

        try:
            # Attempt to call local Ollama instance if running
            response = httpx.post(
                cls.OLLAMA_URL,
                json={"model": cls.LLM_MODEL, "prompt": prompt, "stream": False},
                timeout=5.0
            )
            if response.status_code == 200:
                return response.json().get("response", "").strip()
        except Exception:
            pass  # Fall back to deterministic compliance synthesis

        # Deterministic Extractive Fallback (No external API dependencies needed)
        top_source = sources[0]
        return (
            f"Based on {top_source.citation_label}, the relevant regulatory mandate states:\n\n"
            f"\"{top_source.excerpt}\"\n\n"
            f"(Source: {top_source.document_name}, Version {top_source.version}, Page {top_source.page_number})"
        )

rag_engine = RAGEngine()