from google import genai


class GeminiClient:
    """Wrapper del SDK google-genai para analisis de imagenes."""

    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def analyze_image_and_text(self, image_bytes: bytes, prompt: str) -> str:
        """Envia imagen + prompt a Gemini. Retorna respuesta como texto."""
        image_part = genai.types.Part.from_bytes(
            data=image_bytes, mime_type="image/png"
        )
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[image_part, prompt],
        )
        return response.text
