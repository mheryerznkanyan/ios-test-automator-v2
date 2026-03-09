"""Test Generator service - LLM-powered Swift test generation"""
from typing import Dict, Any

from langchain_core.messages import SystemMessage, HumanMessage

from app.core.prompts import XCTEST_SYSTEM_PROMPT, XCUITEST_SYSTEM_PROMPT
from app.schemas.test_schemas import TestGenerationRequest, TestGenerationResponse
from app.utils.swift_utils import strip_code_fences, extract_class_name
from app.utils.validators import (
    build_context_section,
    build_class_name_section,
    validate_xcuitest_contract,
)


class TestGenerator:
    """Test generator using LangChain and Claude — LLM is injected, not constructed here."""

    def __init__(self, llm):
        self._llm = llm

    def run(self, request: TestGenerationRequest) -> TestGenerationResponse:
        """
        Generate a Swift XCTest/XCUITest based on the request.

        Args:
            request: TestGenerationRequest containing test description and context

        Returns:
            TestGenerationResponse with generated Swift code
        """
        test_type = request.test_type.lower().strip()
        if test_type not in {"unit", "ui"}:
            raise ValueError("test_type must be 'unit' or 'ui'")

        system_prompt = XCTEST_SYSTEM_PROMPT if test_type == "unit" else XCUITEST_SYSTEM_PROMPT
        default_class_name = "GeneratedUnitTests" if test_type == "unit" else "GeneratedUITests"

        context_section = build_context_section(request.app_context)
        class_name_section = build_class_name_section(request.class_name)

        user_message = f"""Generate a Swift {('XCTest unit test' if test_type == 'unit' else 'XCUITest UI test')} for the following:

Test Description: {request.test_description}

{context_section}

{class_name_section}

Include comments: {request.include_comments}

Output ONLY Swift code.
"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message),
        ]

        ai_msg = self._llm.invoke(messages)
        swift_code = strip_code_fences(ai_msg.content)

        final_class_name = extract_class_name(swift_code, request.class_name or default_class_name)

        validation_results: Dict[str, Any] = {}
        if test_type == "ui":
            checks = validate_xcuitest_contract(swift_code)
            validation_results = {
                **checks,
                "all_passed": all(checks.values()),
                "failed_checks": [k for k, v in checks.items() if not v],
            }

        return TestGenerationResponse(
            swift_code=swift_code,
            test_type=test_type,
            class_name=final_class_name,
            metadata={
                "provider": "langchain_anthropic",
                "has_context": bool(request.app_context),
                "context_provided": bool(context_section),
                "contract_validation": validation_results if test_type == "ui" else None,
            },
        )
