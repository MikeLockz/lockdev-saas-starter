from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.ai import AIService


@pytest.mark.asyncio
async def test_ai_service_fallback():
    service = AIService()
    # Should fallback to mock summary if not initialized
    summary = await service.summarize_text(
        "Hello world this is a long text to summarize"
    )
    assert summary.startswith("Summary (Mocked):")


@pytest.mark.asyncio
async def test_ai_service_success():
    service = AIService()
    service.initialized = True
    mock_model = MagicMock()
    mock_model.generate_content_async = AsyncMock()
    mock_response = MagicMock()
    mock_response.text = "Success Summary"
    mock_model.generate_content_async.return_value = mock_response
    service.model = mock_model

    summary = await service.summarize_text("Test text")
    assert summary == "Success Summary"
