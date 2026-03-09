"""FastAPI application entry point with lifespan-managed services."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.services.test_generator import TestGenerator
from app.services.rag_service import RAGService
from app.api.routes import health, tests


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and teardown application-level services."""
    from langchain_anthropic import ChatAnthropic

    llm = ChatAnthropic(
        model=settings.anthropic_model,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        api_key=settings.anthropic_api_key,
    )
    app.state.test_generator = TestGenerator(llm=llm)
    app.state.rag_service = RAGService(settings=settings)
    yield
    # teardown (nothing needed for now)


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(tests.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
