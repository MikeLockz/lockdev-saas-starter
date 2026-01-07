"""
Unit tests for AI Service (Vertex AI integration).

Tests the summarize_text function with mocked Vertex AI responses.
"""

from unittest.mock import Mock, patch

import pytest

from src.services.ai import SummaryResponse, summarize_text


@pytest.mark.asyncio
async def test_summarize_text_success():
    """Test successful text summarization with mocked Vertex AI response."""
    # Mock response data
    mock_response_json = {
        "summary": "This is a test summary of the input text.",
        "key_points": ["Point 1", "Point 2", "Point 3"],
        "confidence": 0.95,
    }

    # Create mock response object
    mock_response = Mock()
    mock_response.text = str(mock_response_json).replace("'", '"')  # Convert to JSON string

    # Create mock model
    mock_model = Mock()
    mock_model.generate_content = Mock(return_value=mock_response)

    # Patch the GenerativeModel class
    with patch("src.services.ai.GenerativeModel", return_value=mock_model):
        result = await summarize_text("This is a test text to summarize.")

        # Verify the result
        assert isinstance(result, SummaryResponse)
        assert result.summary == "This is a test summary of the input text."
        assert len(result.key_points) == 3
        assert result.confidence == 0.95

        # Verify the model was called
        mock_model.generate_content.assert_called_once()


@pytest.mark.asyncio
async def test_summarize_text_empty_input():
    """Test that empty input raises ValueError."""
    with pytest.raises(ValueError, match="Text cannot be empty"):
        await summarize_text("")

    with pytest.raises(ValueError, match="Text cannot be empty"):
        await summarize_text("   ")


@pytest.mark.asyncio
async def test_summarize_text_too_long():
    """Test that text exceeding max length raises ValueError."""
    long_text = "a" * 100_001  # Exceed the 100k limit

    with pytest.raises(ValueError, match="Text too long"):
        await summarize_text(long_text)


@pytest.mark.asyncio
async def test_summarize_text_api_failure():
    """Test error handling when Vertex AI API fails."""
    # Create mock model that raises an exception
    mock_model = Mock()
    mock_model.generate_content = Mock(side_effect=Exception("API connection failed"))

    with patch("src.services.ai.GenerativeModel", return_value=mock_model):
        with pytest.raises(RuntimeError, match="AI service error"):
            await summarize_text("Test text")


@pytest.mark.asyncio
async def test_summarize_text_empty_response():
    """Test error handling when API returns empty response."""
    # Create mock response with empty text
    mock_response = Mock()
    mock_response.text = ""

    mock_model = Mock()
    mock_model.generate_content = Mock(return_value=mock_response)

    with patch("src.services.ai.GenerativeModel", return_value=mock_model):
        with pytest.raises(RuntimeError, match="Empty response"):
            await summarize_text("Test text")


@pytest.mark.asyncio
async def test_summarize_text_invalid_json():
    """Test error handling when API returns invalid JSON."""
    # Create mock response with invalid JSON
    mock_response = Mock()
    mock_response.text = "This is not valid JSON"

    mock_model = Mock()
    mock_model.generate_content = Mock(return_value=mock_response)

    with patch("src.services.ai.GenerativeModel", return_value=mock_model):
        with pytest.raises(RuntimeError, match="Failed to parse JSON"):
            await summarize_text("Test text")


@pytest.mark.asyncio
async def test_summarize_text_invalid_schema():
    """Test error handling when API returns JSON that doesn't match schema."""
    # Create mock response with JSON missing required fields
    mock_response = Mock()
    mock_response.text = '{"summary": "Test", "confidence": 0.9}'  # Missing key_points

    mock_model = Mock()
    mock_model.generate_content = Mock(return_value=mock_response)

    with patch("src.services.ai.GenerativeModel", return_value=mock_model):
        with pytest.raises(RuntimeError, match="AI service error"):
            await summarize_text("Test text")


@pytest.mark.asyncio
async def test_summarize_text_model_initialization():
    """Test that the correct model is initialized."""
    mock_response_json = {
        "summary": "Test summary",
        "key_points": ["Point 1"],
        "confidence": 0.9,
    }

    mock_response = Mock()
    mock_response.text = str(mock_response_json).replace("'", '"')

    mock_model = Mock()
    mock_model.generate_content = Mock(return_value=mock_response)

    mock_generative_model_class = Mock(return_value=mock_model)

    with patch("src.services.ai.GenerativeModel", mock_generative_model_class):
        await summarize_text("Test text")

        # Verify the model was initialized with correct model name
        mock_generative_model_class.assert_called_once_with("gemini-1.5-pro")


@pytest.mark.asyncio
async def test_summarize_text_generation_config():
    """Test that generation config and safety settings are passed."""
    mock_response_json = {
        "summary": "Test summary",
        "key_points": ["Point 1"],
        "confidence": 0.9,
    }

    mock_response = Mock()
    mock_response.text = str(mock_response_json).replace("'", '"')

    mock_model = Mock()
    mock_model.generate_content = Mock(return_value=mock_response)

    with patch("src.services.ai.GenerativeModel", return_value=mock_model):
        await summarize_text("Test text")

        # Get the call arguments
        call_args = mock_model.generate_content.call_args

        # Verify generation_config was passed
        assert "generation_config" in call_args.kwargs
        assert call_args.kwargs["generation_config"] is not None

        # Verify safety settings were passed
        assert "safety_settings" in call_args.kwargs
        assert call_args.kwargs["safety_settings"] is not None
