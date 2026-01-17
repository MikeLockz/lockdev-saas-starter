from vertexai.generative_models import GenerativeModel


class AIService:
    def __init__(self):
        self.initialized = False
        try:
            # vertexai.init(project=settings.GCP_PROJECT_ID)
            self.model = GenerativeModel("gemini-1.5-flash")
            self.initialized = True
        except Exception:
            self.model = None

    async def summarize_text(self, text: str) -> str:
        """
        Summarizes the given text using Gemini.
        """
        if not self.initialized or not self.model:
            return f"Summary (Mocked): {text[:100]}..."

        try:
            response = await self.model.generate_content_async(
                f"Please provide a concise summary of the following text:\n\n{text}",
                request_options={"timeout": 30},
            )
            return response.text
        except Exception as e:
            return f"Error generating summary: {e!s}"


ai_service = AIService()
