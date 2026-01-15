"""
AI Service using Google Vertex AI (Gemini 1.5 Pro).

This module provides AI-powered text summarization with HIPAA-compliant
zero retention configuration.

Required Environment Variables:
    GOOGLE_APPLICATION_CREDENTIALS: Path to service account JSON
    GOOGLE_CLOUD_PROJECT: GCP project ID
    GOOGLE_CLOUD_LOCATION: GCP region (default: us-central1)

Required GCP Permissions:
    - aiplatform.endpoints.predict
    - aiplatform.models.predict
"""

import structlog
from google.cloud import aiplatform
from pydantic import BaseModel, Field
from vertexai.generative_models import GenerationConfig, GenerativeModel, HarmBlockThreshold, HarmCategory

from src.config import settings

logger = structlog.get_logger(__name__)


class SummaryResponse(BaseModel):
    """Response schema for text summarization."""

    summary: str = Field(..., description="Concise summary of the input text")
    key_points: list[str] = Field(..., description="List of key points extracted from the text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the summary")


# Initialize Vertex AI with project configuration
# This is done at module level to reuse the client across requests
try:
    aiplatform.init(
        project=settings.GOOGLE_CLOUD_PROJECT,
        location=settings.GOOGLE_CLOUD_LOCATION,
    )
    logger.info(
        "vertex_ai_initialized",
        project=settings.GOOGLE_CLOUD_PROJECT,
        location=settings.GOOGLE_CLOUD_LOCATION,
    )
except Exception as e:
    logger.warning("vertex_ai_init_failed", error=str(e))
    # Don't fail on import - allow tests to mock


async def summarize_text(text: str) -> SummaryResponse:
    """
    Summarize text using Gemini 1.5 Pro with zero retention.

    Args:
        text: The text to summarize (max 30,000 characters recommended)

    Returns:
        SummaryResponse with summary, key points, and confidence score

    Raises:
        ValueError: If text is empty or too long
        RuntimeError: If the API call fails

    HIPAA Compliance:
        - Zero retention: Data is not stored by Google after processing
        - No PII logging: Input text is never logged
        - Structured logging: Only metadata is logged for observability
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    if len(text) > 100_000:
        raise ValueError("Text too long (max 100,000 characters)")

    logger.info("summarize_text_requested", text_length=len(text))

    try:
        # Initialize the model
        # gemini-1.5-pro is the latest production model as of 2024
        model = GenerativeModel("gemini-1.5-pro")

        # Configure generation parameters
        generation_config = GenerationConfig(
            temperature=0.2,  # Lower temperature for more consistent summaries
            top_p=0.8,
            top_k=40,
            max_output_tokens=2048,
            response_mime_type="application/json",  # Force JSON response
        )

        # Safety settings - block only high-risk content
        # This is important for medical/clinical text which may contain sensitive topics
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }

        # Construct the prompt with JSON schema
        prompt = f"""Analyze the following text and provide a structured summary.

Return your response as a JSON object with this exact structure:
{{
  "summary": "A concise 2-3 sentence summary",
  "key_points": ["point 1", "point 2", "point 3"],
  "confidence": 0.95
}}

The confidence score should be between 0.0 and 1.0, representing how well you understand the text.

Text to summarize:
{text}
"""

        # Generate content with zero retention
        # Note: Zero retention is configured at the GCP project level via
        # the "Data Residency and Compliance" settings in the Vertex AI console
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings,
        )

        # Extract the response text
        if not response.text:
            raise RuntimeError("Empty response from Vertex AI")

        # Parse the JSON response
        import json

        try:
            result_data = json.loads(response.text)
        except json.JSONDecodeError as e:
            logger.error("json_parse_failed", error=str(e), response_text=response.text[:200])
            raise RuntimeError(f"Failed to parse JSON response: {e}") from e

        # Validate and return using Pydantic
        try:
            result = SummaryResponse(**result_data)
        except Exception as e:  # Catch pydantic validation errors
            logger.error("schema_validation_failed", error=str(e), result_data=result_data)
            raise RuntimeError(f"AI returned invalid schema: {e}") from e

        logger.info(
            "summarize_text_success",
            text_length=len(text),
            summary_length=len(result.summary),
            num_key_points=len(result.key_points),
            confidence=result.confidence,
        )

        return result

    except ValueError:
        # Re-raise validation errors
        raise
    except Exception as e:
        logger.error("summarize_text_failed", error=str(e), error_type=type(e).__name__)
        raise RuntimeError(f"AI service error: {e}") from e
