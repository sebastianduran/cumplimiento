import base64
import json
import urllib.request
import urllib.error


class OllamaClient:
    """Cliente para Ollama API local con soporte de vision."""

    def __init__(self, model_name: str = "llama3.2-vision", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")

    def analyze_image_and_text(self, image_bytes: bytes, prompt: str) -> str:
        """Envia imagen + prompt a Ollama. Retorna respuesta como texto."""
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "images": [image_b64],
            "stream": False,
        }

        url = f"{self.base_url}/api/generate"
        data = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result.get("response", "")
        except urllib.error.URLError as e:
            raise ConnectionError(
                f"No se pudo conectar a Ollama en {self.base_url}. "
                f"Asegurate de que Ollama este corriendo. Error: {e}"
            )

    @staticmethod
    def check_connection(base_url: str = "http://localhost:11434") -> bool:
        """Verifica si Ollama esta corriendo."""
        try:
            req = urllib.request.Request(f"{base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except Exception:
            return False

    @staticmethod
    def list_models(base_url: str = "http://localhost:11434") -> list[str]:
        """Lista los modelos disponibles en Ollama."""
        try:
            req = urllib.request.Request(f"{base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            return []
