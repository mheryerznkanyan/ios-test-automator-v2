"""Test generation routes"""
import asyncio
from typing import List

from fastapi import APIRouter, HTTPException, Request

from app.core.config import settings
from app.schemas.test_schemas import (
    AppContext,
    TestGenerationRequest,
    TestGenerationResponse,
    RAGTestGenerationRequest,
)

router = APIRouter()


@router.post("/generate-test", response_model=TestGenerationResponse)
async def generate_test(request: Request, body: TestGenerationRequest):
    """Generate a single test using the injected TestGenerator."""
    generator = request.app.state.test_generator
    try:
        return await asyncio.to_thread(generator.run, body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error generating test: {exc}")


@router.post("/generate-test-with-rag", response_model=TestGenerationResponse)
async def generate_test_with_rag(request: Request, body: RAGTestGenerationRequest):
    """Generate a test using RAG to automatically retrieve context from the codebase."""
    rag_service = request.app.state.rag_service

    test_type = body.test_type.lower().strip()
    if test_type not in {"unit", "ui"}:
        raise HTTPException(status_code=400, detail="test_type must be 'unit' or 'ui'")

    rag_context = rag_service.query(body.test_description, k=body.rag_top_k)

    code_snippets_text = "\n\n".join(
        f"// {s['kind']} from {s['path']}\n{s['content']}"
        for s in rag_context["code_snippets"]
    )

    # Use caller-supplied app_name → fallback to config default
    resolved_app_name = body.app_name or settings.default_app_name

    app_context = AppContext(
        app_name=resolved_app_name,
        screens=rag_context["screens"],
        accessibility_ids=rag_context["accessibility_ids"],
        source_code_snippets=code_snippets_text or None,
    )

    wrapped = TestGenerationRequest(
        test_description=body.test_description,
        test_type=test_type,
        app_context=app_context,
        class_name=body.class_name,
        include_comments=body.include_comments,
    )

    response = await generate_test(request, wrapped)

    response.metadata["rag_enabled"] = True
    response.metadata["rag_context"] = {
        "accessibility_ids_found": len(rag_context.get("accessibility_ids", [])),
        "screens_found": len(rag_context.get("screens", [])),
        "code_snippets_used": len(rag_context.get("code_snippets", [])),
        "total_docs_retrieved": rag_context.get("total_docs_retrieved", 0),
    }
    if "error" in rag_context:
        response.metadata["rag_error"] = rag_context["error"]

    return response


@router.post("/generate-tests-batch")
async def generate_tests_batch(request: Request, bodies: List[TestGenerationRequest]):
    """Generate multiple tests in parallel using asyncio.gather.

    Capped at ``settings.batch_max_size`` requests per call.
    """
    if len(bodies) > settings.batch_max_size:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Batch size {len(bodies)} exceeds the maximum of "
                f"{settings.batch_max_size}. Split your request into smaller batches."
            ),
        )

    generator = request.app.state.test_generator

    results_raw = await asyncio.gather(
        *[asyncio.to_thread(generator.run, req) for req in bodies],
        return_exceptions=True,
    )

    results = []
    errors = []
    for idx, item in enumerate(results_raw):
        if isinstance(item, Exception):
            errors.append({
                "index": idx,
                "error": str(item),
                "description": (bodies[idx].test_description or "")[:100],
            })
        else:
            results.append(item)

    return {
        "generated": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors,
    }
